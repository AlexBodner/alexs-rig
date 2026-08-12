#!/usr/bin/env python3
"""PreToolUse(Bash): warn/deny obvious secret-path reads or cat of denylisted files.

Fail-open on parse errors. Exit 0 always for Cursor/Claude compatibility;
prints JSON deny when clearly dangerous.
"""

from __future__ import annotations

import json
import re
import sys

DENY_PATTERNS = [
    re.compile(r"(^|[/\s])\.env(\.|$)"),
    re.compile(r"(^|[/\s])\.env\.[a-z0-9_-]+", re.I),
    re.compile(r"credentials\.json", re.I),
    re.compile(r"id_rsa(\.pub)?"),
    re.compile(r"\.pem(\s|$)"),
    re.compile(r"\.p12(\s|$)"),
    re.compile(r"secrets?\.ya?ml", re.I),
    re.compile(r"aws.?credentials", re.I),
]

READISH = re.compile(r"\b(cat|less|more|head|tail|bat|type|Get-Content)\b", re.I)


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return

    cmd = ""
    tool_input = data.get("tool_input") or data.get("input") or {}
    if isinstance(tool_input, dict):
        cmd = str(tool_input.get("command") or tool_input.get("cmd") or "")
    if not cmd:
        cmd = str(data.get("command") or "")

    if not cmd or not READISH.search(cmd):
        return

    for pat in DENY_PATTERNS:
        if pat.search(cmd):
            msg = (
                "Alex's Rig secret-hygiene: blocked read of denylisted secret path. "
                "Do not cat .env / credentials / keys into the agent transcript."
            )
            # Claude Code hook deny shape (best-effort; hosts differ)
            out = {
                "decision": "deny",
                "reason": msg,
                "hookSpecificOutput": {
                    "permissionDecision": "deny",
                    "permissionDecisionReason": msg,
                },
            }
            print(json.dumps(out))
            return


if __name__ == "__main__":
    main()
