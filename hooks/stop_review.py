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


def verify_status_line(root: Path) -> str:
    """One-line last-check status from .alexs-rig/verify-status.json, or empty."""
    p = root / ".alexs-rig" / "verify-status.json"
    if not p.is_file():
        return ""
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if not isinstance(data, dict):
        return ""
    verdict = "PASS" if data.get("ok") else "FAIL"
    return f"last check: {verdict} — {data.get('command', '?')} ({data.get('ran_at', '?')})"


def review_payload(stat: str, root: Path) -> dict:
    tail = f"{stat}\n"
    verify = verify_status_line(root)
    if verify:
        tail += f"{verify}\n"
    ctx = (
        "<alexs-rig-review>\n"
        "Unreviewed agent edits (dirty vs SESSION_BASE, unmarked or re-touched). "
        "Batch-review via Desktop +N -M / Cmd+Shift+D. "
        "In Cursor/VS Code: Source Control → Review → open the diff, then check Viewed "
        "(session or PR, same list). Agent re-edits uncheck that file. "
        "Do not commit unless the human asked.\n"
        f"{tail}"
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
    print(json.dumps(review_payload(stat, root)))


if __name__ == "__main__":
    main()
