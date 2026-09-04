#!/usr/bin/env python3
"""Stop: once per dirty round, remind batch review if files are still pending.

Never decision:block. additionalContext on Stop continues the turn — so we
mark .alexs-rig/STOP_REMINDED and stay silent after the first nudge until
review-mark (mark_files) or SessionStart clears it. New pending files do
NOT re-nudge on their own.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_correction import inbox_count  # noqa: E402
from review_files import pending_stat  # noqa: E402
from session_base import mark_stop_reminded, stop_reminded_path, worktree_tree_sha  # noqa: E402

# The inbox is now unfiltered, so it fills far faster; nudge on a few days' worth.
INBOX_NUDGE_AT = 80
STALE_SUFFIX = " — STALE: edits since; re-run bin/verify"


def _verify_is_stale(data: dict, root: Path) -> bool:
    """True when the worktree changed since the recorded run (or no tree recorded). Fail-open."""
    stored = data.get("tree")
    if not stored:
        return True
    try:
        return stored != worktree_tree_sha(root)
    except Exception:
        return False


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
    line = f"last check: {verdict} — {data.get('command', '?')} ({data.get('ran_at', '?')})"
    if _verify_is_stale(data, root):
        line += STALE_SUFFIX
    return line


def review_payload(stat: str, root: Path, n_inbox: int = 0) -> dict:
    blocks: list[str] = []
    if stat:
        tail = f"{stat}\n"
        verify = verify_status_line(root)
        if verify:
            tail += f"{verify}\n"
        blocks.append(
            "<alexs-rig-review>\n"
            "Unreviewed agent edits (dirty vs SESSION_BASE, unmarked or re-touched). "
            "List them with bin/review-pending --name-only; mark one reviewed with "
            "bin/review-mark <path>. A later agent edit unmarks that file again. "
            "Do not commit unless the human asked.\n"
            f"{tail}"
            "</alexs-rig-review>"
        )
    if n_inbox >= INBOX_NUDGE_AT:
        blocks.append(
            "<alexs-rig-corrections>\n"
            f"{n_inbox} turns captured for correction mining — run /alex-mine-corrections\n"
            "</alexs-rig-corrections>"
        )
    return {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": "\n".join(blocks),
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
    n_inbox = 0
    if data.get("stop_hook_active") is not True and not stop_reminded_path(root).is_file():
        try:
            n_inbox = inbox_count(root)
        except Exception:
            n_inbox = 0
    if not stat and n_inbox < INBOX_NUDGE_AT:
        return
    mark_stop_reminded(root)
    print(json.dumps(review_payload(stat, root, n_inbox)))


if __name__ == "__main__":
    main()
