#!/usr/bin/env python3
"""Extract replay cases from real history: (prompt -> agent response -> your correction).

The correction IS the ground truth: it names what the agent got wrong on a real task
of yours. A case can then be replayed with the harness on and off and graded on whether
the failure you had to correct is avoided.

    python3 evals/honest/cases.py            # list candidate cases
    python3 evals/honest/cases.py --write    # save to evals/private/cases.jsonl

Leakage warning, printed with the results: several L0 principles were *derived from
these very corrections*. Cases are therefore split into `seen` (a principle traces back
to this correction) and `unseen`. Only `unseen` measures generalisation; `seen` measures
whether a stored principle actually gets applied on real work — still worth knowing,
but a different claim.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

RIG = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RIG / "hooks"))
import capture_correction as cc  # noqa: E402

OUT = RIG / "evals" / "private" / "cases.jsonl"
TRANSCRIPTS = Path.home() / ".claude" / "projects"
SKIP_CWD = ("/tmp", "/private/tmp", "/var/folders")
# Skills loaded into the user slot are not the user talking.
SKILL_INJECTION = re.compile(
    r"^\s*(Base directory for this skill:|<command-name>|# Working on this research"
    r"|This session is being continued|Caveat:|<local-command)", re.I
)


def is_user_text(t: str) -> bool:
    return not cc.is_system_text(t) and not SKILL_INJECTION.search(t)

# Topic fingerprints of the principles learned from corrections, to flag leakage.
SEEN_TOPICS = {
    "P-cost": r"\b(cost|vram|instance|caro|costar|g6e|a100|gpu)\b",
    "P-precheck": r"\b(confirm|correcto|primero|before.*(run|launch)|validat)\b",
    "P-monitor": r"\b(monitor|still running|sigue corriendo|colab|hung|timeout)\b",
    "P-fair": r"\b(fair|comparison|both|equal|tuned|ambos|justa)\b",
    "P-report-numbers": r"\b(report|table|numbers|precise|tabla|informe)\b",
    "P-doc-lead": r"\b(document|doc|intro|opening|lead|resumen)\b",
    "P-exercise": r"\b(run it|actually run|end to end|smoke|probaste|corriste)\b",
}


def turns(path: str):
    """Ordered (role, text, meta) for one transcript."""
    try:
        lines = open(path, errors="replace").read().splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = o.get("type")
        if t not in ("user", "assistant"):
            continue
        content = (o.get("message") or {}).get("content")
        text = ""
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            text = " ".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
        text = text.strip()
        if text:
            yield t, text, {"ts": str(o.get("timestamp") or ""), "cwd": o.get("cwd", ""),
                            "branch": o.get("gitBranch", ""), "session": o.get("sessionId", "")}


def extract() -> list[dict]:
    cases = []
    for f in sorted(glob.glob(str(TRANSCRIPTS / "*" / "*.jsonl"))):
        seq = list(turns(f))
        # collapse consecutive assistant blocks: the substantive answer usually comes
        # after tool calls, so the first block alone is just a preamble.
        merged = []
        for role, text, meta in seq:
            if merged and role == "assistant" and merged[-1][0] == "assistant":
                merged[-1] = ("assistant", merged[-1][1] + "\n" + text, merged[-1][2])
            else:
                merged.append((role, text, meta))
        seq = merged
        for i in range(len(seq) - 2):
            (r0, prompt, m0), (r1, answer, _), (r2, correction, _) = seq[i], seq[i + 1], seq[i + 2]
            if (r0, r1, r2) != ("user", "assistant", "user"):
                continue
            if str(m0.get("cwd", "")).startswith(SKIP_CWD):
                continue
            if not is_user_text(prompt) or not is_user_text(correction):
                continue
            # the third turn must look like a correction of the second
            if cc.score_correction(correction)[0] < cc.THRESHOLD:
                continue
            # a replayable prompt: a real instruction, not a one-word reply
            if not (40 <= len(prompt) <= 1500) or len(correction) < 25:
                continue
            topics = [k for k, rx in SEEN_TOPICS.items() if re.search(rx, correction, re.I)]
            cases.append({
                "prompt": prompt, "original_answer": answer[:1200], "correction": correction,
                "repo": os.path.basename(m0.get("cwd", "")) or "?", "cwd": m0.get("cwd", ""),
                "branch": m0.get("branch", ""), "ts": m0.get("ts", ""),
                "leak": "seen" if topics else "unseen", "topics": topics,
                "answer_chars": len(answer),
            })
    # de-duplicate by prompt
    out, seen = [], set()
    for c in cases:
        k = re.sub(r"\s+", " ", c["prompt"]).strip().lower()[:100]
        if k in seen:
            continue
        seen.add(k)
        out.append(c)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract replay cases from real history")
    ap.add_argument("--write", action="store_true", help=f"save to {OUT}")
    ap.add_argument("--show", type=int, default=6, help="how many to print")
    args = ap.parse_args()
    cases = extract()
    n_seen = sum(1 for c in cases if c["leak"] == "seen")
    print(f"{len(cases)} replayable cases  ·  {n_seen} seen (principle traces to it) / "
          f"{len(cases) - n_seen} unseen")
    from collections import Counter
    print("repos:", dict(Counter(c["repo"] for c in cases)))
    for c in cases[: args.show]:
        print("\n" + "=" * 74)
        print(f"[{c['leak']}] {c['repo']}  {c['ts'][:16]}  topics={c['topics']}")
        print(f"  PROMPT     : {' '.join(c['prompt'].split())[:220]}")
        print(f"  AGENT DID  : {' '.join(c['original_answer'].split())[:220]}")
        print(f"  YOU FIXED  : {' '.join(c['correction'].split())[:220]}")
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("w", encoding="utf-8") as f:
            for c in cases:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(f"\nwrote {len(cases)} cases -> {OUT}")


if __name__ == "__main__":
    main()
