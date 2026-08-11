#!/usr/bin/env python3
"""SessionStart: print L0 snapshot for injection (Claude Code hook).

Looks for docs/memory/snapshots/L0.md relative to cwd (project), not only plugin root.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def find_l0(start: Path) -> Path | None:
    cur = start.resolve()
    for _ in range(8):
        candidate = cur / "docs" / "memory" / "snapshots" / "L0.md"
        if candidate.is_file():
            return candidate
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def main() -> None:
    l0 = find_l0(Path.cwd())
    if l0 is None:
        # Also try plugin-bundled example
        root = Path(__file__).resolve().parents[1]
        example = root / "docs" / "memory" / "snapshots" / "L0.md"
        l0 = example if example.is_file() else None
    if l0 is None:
        print("Alex's Rig: no docs/memory/snapshots/L0.md found (run bin/l0-regen).", file=sys.stderr)
        return
    text = l0.read_text(encoding="utf-8")
    # Claude hooks often expect additionalContext via stdout JSON on some versions;
    # printing plain text is a proto fallback the user/agent can see in hook output.
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"<alexs-rig-l0>\n{text}\n</alexs-rig-l0>",
        }
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
