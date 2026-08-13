#!/usr/bin/env python3
"""Stop: once per dirty round, remind batch review if files are still pending.

Never decision:block. additionalContext on Stop continues the turn — so we
mark .alexs-rig/STOP_REMINDED and stay silent after the first nudge until
review-mark clears it (a new pending set can nudge again).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_files import pending_stat  # noqa: E402
from session_base import mark_stop_reminded, stop_reminded_path  # noqa: E402


def review_payload(stat: str) -> dict:
    ctx = (
        "<alexs-rig-review>\n"
        "Unreviewed agent edits (dirty vs SESSION_BASE, unmarked or re-touched). "
        "Batch-review via Desktop +N -M / Cmd+Shift+D. "
        "In Cursor/VS Code: Source Control → Review → open the diff, then check Viewed "
        "(session or PR, same list). Agent re-edits uncheck that file. "
        "Do not commit unless the human asked.\n"
        f"{stat}\n"
        "</alexs-rig-review>"
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": ctx,
        }
    }


def should_remind(data: dict, root: Path, sha: str = "") -> str:
    """Return pending --stat text when a reminder should fire, else empty."""
    del sha
    if data.get("stop_hook_active") is True:
        return ""
    if stop_reminded_path(root).is_file():
        return ""
    return pending_stat(root)


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    root = Path.cwd()
    stat = should_remind(data, root)
    if not stat:
        return
    mark_stop_reminded(root)
    print(json.dumps(review_payload(stat)))


if __name__ == "__main__":
    main()
