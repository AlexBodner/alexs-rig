#!/usr/bin/env python3
"""Stop: once per session, remind batch review if SESSION_BASE has a diff.

Never decision:block. additionalContext on Stop continues the turn — so we
mark .alexs-rig/STOP_REMINDED and stay silent after the first nudge.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from session_base import (  # noqa: E402
    find_session_base,
    mark_stop_reminded,
    session_diff_stat,
    stop_reminded_path,
)


def review_payload(stat: str) -> dict:
    ctx = (
        "<alexs-rig-review>\n"
        "Uncommitted changes since session open (SESSION_BASE). "
        "Batch-review via Desktop +N -M / Cmd+Shift+D or IDE SCM — do not skip. "
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


def should_remind(data: dict, root: Path, sha: str) -> str:
    """Return diff --stat text when a reminder should fire, else empty."""
    if data.get("stop_hook_active") is True:
        return ""
    if not sha:
        return ""
    if stop_reminded_path(root).is_file():
        return ""
    return session_diff_stat(root, sha)


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    root, sha = find_session_base(Path.cwd())
    stat = should_remind(data, root, sha)
    if not stat:
        return
    mark_stop_reminded(root)
    print(json.dumps(review_payload(stat)))


if __name__ == "__main__":
    main()
