#!/usr/bin/env python3
"""UserPromptSubmit: cheap (zero-LLM) capture of correction-like turns.

Stage 1 of correction learning. Scores the user prompt with a small transparent
weighted heuristic and, if it clears the threshold, APPENDS a raw row to
``<memoryroot>/mining/corrections-inbox.jsonl``. Silent by design: it never adds
model context and always exits 0 (fail-open — a capture error must not crash a
session). Stage 2 is the on-demand ``/alex-mine-corrections`` flush skill, which
is the only path from raw corrections to approved principles.

Detector grounding (real Cursor history): corrections overwhelmingly OPEN with
"no," (also nope/wait,/actually,/hmm,). Dominant cues: don't/not, should/must,
always/never, i want/prefer, instead/rather than, just/no need. The cheapest
high-precision signal is a short reply-to-the-agent starting with "no," plus any
negation or rule verb.
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
SOFT_OPENER = re.compile(r"^\s*(nope\b|wait,|actually,|hmm,)", re.I)
NEGATION = re.compile(r"\b(don'?t|do not|does not|doesn'?t|not|isn'?t|won'?t)\b", re.I)
RULE_VERB = re.compile(r"\b(should|must|always|never)\b", re.I)
PREFERENCE = re.compile(r"\b(i want|i'd prefer|i prefer|i'd like|instead|rather than|just|no need)\b", re.I)

THRESHOLD = 3


def score_correction(text: str, pending: bool = False) -> tuple[int, list[str]]:
    """Weighted, transparent score. Returns (score, signals).

    Weights: strong "no," opener +3, soft opener +2, negation +1, rule verb +1,
    preference +1, and +1 when there are fresh unreviewed edits (``pending``).
    """
    score = 0
    signals: list[str] = []
    if STRONG_OPENER.search(text):
        score += 3
        signals.append("opener:no,")
    elif SOFT_OPENER.search(text):
        score += 2
        signals.append("opener:soft")
    if NEGATION.search(text):
        score += 1
        signals.append("negation")
    if RULE_VERB.search(text):
        score += 1
        signals.append("rule_verb")
    if PREFERENCE.search(text):
        score += 1
        signals.append("preference")
    if pending:
        score += 1
        signals.append("pending")
    return score, signals


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


def _pending(cwd: Path) -> bool:
    try:
        from review_files import pending_names  # noqa: E402

        return bool(pending_names(cwd))
    except Exception:
        return False


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
        if not prompt:
            return
        cwd = Path(data.get("cwd") or os.getcwd())
        memory_root = find_memory_root(cwd)
        if memory_root is None:
            return
        score, signals = score_correction(prompt, pending=_pending(cwd))
        if score < THRESHOLD:
            return
        row = {
            "ts": mem.utc_now(),
            "text": mem.redact(prompt),
            "score": score,
            "signals": signals,
            "cwd": str(cwd),
        }
        append_row(inbox_path(memory_root), row)
    except Exception:
        # Fail-open: capture must never crash a session.
        return


if __name__ == "__main__":
    main()
