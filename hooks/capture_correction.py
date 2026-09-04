#!/usr/bin/env python3
"""UserPromptSubmit: capture every reply, with the agent turn it answers, for later mining.

Stage 1 of correction learning. APPENDS every reply you make to
``<memoryroot>/mining/corrections-inbox.jsonl``, scored but unfiltered: selecting the real
corrections is the flush pass's job, because a keyword score cannot do it (measured on 184
blind-labelled turns from two corpora: recall 0.07 for the score, 0.56 for a model reading the
same turns; see evals/honest). Silent by design: it never adds model context and always exits
0 (fail-open, a capture error must not crash a session). Stage 2 is the on-demand
``/alex-mine-corrections`` skill, the only path from raw turns to approved principles.

The score below survives as a ranking hint. It looks for the grammar of rejection ("no,",
"don't", "instead"); real corrections mostly report a symptom instead ("the videos show no
box"), which is exactly why it is no longer a gate.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_HOOKS = Path(__file__).resolve().parent
sys.path.insert(0, str(_HOOKS))
sys.path.insert(0, str(_HOOKS.parent / "bin"))
import _memory as mem  # noqa: E402

STRONG_OPENER = re.compile(r"^\s*no,", re.I)
SOFT_OPENER = re.compile(r"^\s*(nope\b|wait,|actually,|hmm,|ugh)", re.I)
# Strong correction moves (+2): reverse a change, replace X with Y, "no need to".
REVERSAL = re.compile(r"\b(revert|undo|roll ?back|rollback|(?:you|it|that) broke|broke the)\b", re.I)
REPLACE = re.compile(r"\b(instead of|rather than)\b", re.I)
PROHIBITION = re.compile(r"\b(no need|don'?t bother)\b", re.I)
# Softer cues (+1). NEGATION covers any n't contraction (shouldn't, can't, isn't, …).
NEGATION = re.compile(r"\b(\w+n'?t|do not|does not|did not|not)\b", re.I)
RULE_VERB = re.compile(r"\b(should|shouldn'?t|must|mustn'?t|always|never)\b", re.I)
PREFERENCE = re.compile(r"\b(i want|i'd prefer|i prefer|i'd like|instead|rather than|just)\b", re.I)

THRESHOLD = 3
# Capture gate. Corrections are 17% to 39% of turns depending on corpus, and the score>=3
# filter found 7% of them at 0.57 to 0.70 precision, while a model over unfiltered turns
# found 56% (about $0.78 per 300-turn flush). So the score is kept as metadata for ranking
# and no longer gates capture. Set ALEXS_RIG_CAPTURE_MIN_SCORE=3 to restore filtering where
# a flush pass has to stay cheap (API-key setups), accepting the recall loss.
MIN_SCORE = int(os.environ.get("ALEXS_RIG_CAPTURE_MIN_SCORE", "0"))
# A real correction is short; a giant paste (git log/diff) is not one — skip it entirely.
MAX_PROMPT_CHARS = 4000
# Cap the stored text so one row can't bloat the inbox.
STORE_CHARS = 1500

_PLUS_TWO = ((REVERSAL, "reversal"), (REPLACE, "replace"), (PROHIBITION, "prohibition"))
_PLUS_ONE = ((NEGATION, "negation"), (RULE_VERB, "rule_verb"), (PREFERENCE, "preference"))


def score_correction(text: str, pending: bool = False) -> tuple[int, list[str]]:
    """Weighted, transparent score. Returns (score, signals).

    Weights: strong "no," opener +3, soft opener +2; reversal/replace/prohibition +2;
    negation/rule-verb/preference +1; and +1 when there are fresh unreviewed edits
    (``pending`` — corrections almost always land while the agent's edits are unreviewed).
    """
    score = 0
    signals: list[str] = []
    if STRONG_OPENER.search(text):
        score += 3
        signals.append("opener:no,")
    elif SOFT_OPENER.search(text):
        score += 2
        signals.append("opener:soft")
    for rx, name in _PLUS_TWO:
        if rx.search(text):
            score += 2
            signals.append(name)
    for rx, name in _PLUS_ONE:
        if rx.search(text):
            score += 1
            signals.append(name)
    if pending:
        score += 1
        signals.append("pending")
    return score, signals


# Claude Code injects text into the prompt slot (task notifications, reminders,
# interrupt notices). Those are not the user's words — never capture them.
SYSTEM_PREFIXES = (
    "<task-notification",
    "<system-reminder",
    "<local-command",
    "<command-name",
    "[Request interrupted",
    "Caveat:",
)
# How much of the agent's preceding turn to keep — enough to make "no, not like
# that" interpretable, small enough to stay cheap.
EXCERPT_CHARS = 700
TRANSCRIPT_TAIL_BYTES = 262144


def is_system_text(text: str) -> bool:
    """True when the prompt is host-injected rather than typed by the user."""
    head = text.lstrip()[:40]
    return any(head.startswith(p) for p in SYSTEM_PREFIXES)


def last_assistant_excerpt(transcript_path: str | None) -> str:
    """The agent turn the user is reacting to — the missing half of a correction.

    Tail-reads the session transcript (cheap, bounded) and returns the most recent
    assistant text. Empty string on any problem: context is a bonus, never a blocker.
    """
    if not transcript_path:
        return ""
    try:
        p = Path(transcript_path)
        if not p.is_file():
            return ""
        size = p.stat().st_size
        with p.open("rb") as f:
            if size > TRANSCRIPT_TAIL_BYTES:
                f.seek(size - TRANSCRIPT_TAIL_BYTES)
                f.readline()  # drop the partial line
            chunk = f.read().decode("utf-8", errors="replace")
        for line in reversed(chunk.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "assistant" or obj.get("isSidechain"):
                continue  # subagent (sidechain) turns are not what the user is replying to
            content = (obj.get("message") or {}).get("content")
            parts = []
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                parts += [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
            text = " ".join(t for t in parts if t).strip()
            if text:
                return text[:EXCERPT_CHARS]
    except (OSError, ValueError):
        return ""
    return ""


def find_memory_root(start: Path) -> Path | None:
    """Walk up for a ``docs/memory`` dir (same locate pattern as inject_l0), then
    fall back to the global personal memory at ~/.alexs-rig/memory if it exists."""
    cur = start.resolve()
    for _ in range(8):
        cand = cur / "docs" / "memory"
        if cand.is_dir():
            return cand
        if cur.parent == cur:
            break
        cur = cur.parent
    global_mem = Path.home() / ".alexs-rig" / "memory"
    if global_mem.is_dir():
        return global_mem
    return None


def inbox_path(memory_root: Path) -> Path:
    return memory_root / "mining" / "corrections-inbox.jsonl"


def inbox_count(start: Path) -> int:
    root = find_memory_root(Path(start))
    if root is None:
        return 0
    p = inbox_path(root)
    if not p.is_file():
        return 0
    return sum(1 for line in p.read_text(encoding="utf-8").splitlines() if line.strip())


def _pending_files(cwd: Path, cap: int = 10) -> list[str]:
    """Files the agent edited but you have not reviewed — what the correction is about."""
    try:
        from review_files import pending_names  # noqa: E402

        return pending_names(cwd)[:cap]
    except Exception:
        return []


def append_row(inbox: Path, row: dict) -> None:
    inbox.parent.mkdir(parents=True, exist_ok=True)
    with inbox.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        if not isinstance(data, dict):
            return
        prompt = str(data.get("prompt") or "").strip()
        if not prompt or len(prompt) > MAX_PROMPT_CHARS or is_system_text(prompt):
            return
        cwd = Path(data.get("cwd") or os.getcwd())
        memory_root = find_memory_root(cwd)
        if memory_root is None:
            return
        # Only replies can be corrections: a session's opening prompt has nothing to
        # correct. This costs no recall and drops a large share of the volume.
        excerpt = last_assistant_excerpt(data.get("transcript_path"))
        if not excerpt:
            return
        files = _pending_files(cwd)
        score, signals = score_correction(prompt, pending=bool(files))
        if score < MIN_SCORE:
            return
        row = {
            "ts": mem.utc_now(),
            "text": mem.redact(prompt[:STORE_CHARS]),
            "score": score,
            "signals": signals,
            "cwd": str(cwd),
            # Context: without these a correction like "no, not like that" is uninterpretable.
            "assistant_excerpt": mem.redact(excerpt),
            "files": files,
            "session_id": str(data.get("session_id") or ""),
        }
        append_row(inbox_path(memory_root), row)
    except Exception:
        # Fail-open: capture must never crash a session.
        return


if __name__ == "__main__":
    main()
