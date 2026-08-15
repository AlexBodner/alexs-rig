#!/usr/bin/env python3
"""PreToolUse: deny read/write of denylisted secret paths (Bash/Write/Edit).

Fail-open on parse errors. Exit 0 always; prints JSON deny when clearly dangerous.

NOT a security boundary. This is a best-effort speed-bump against ACCIDENTAL
secret reads/writes landing in the agent transcript, not data-loss-prevention.
It is fail-open, matches a fixed denylist of filenames, and only fires when a
read/write verb it recognizes co-occurs with a denylisted path in the same
string. It is trivially bypassed by any tool not on the recognized-verb list
(e.g. `perl`, `node -e`, `dd`, `jq`, `base64`), by a denylisted path embedded
inside quotes/code strings (e.g. `python -c "open('.env').read()"`), or
simply by renaming/relocating the secret file. For Write/Edit-style tools only
the target path is matched, never the content, so writing a secret's *value*
to a non-denylisted path is not caught. Real protection is a host secret store
/ env injection and simply not committing secrets to the repo — see
docs/hygiene.md.
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

READISH = re.compile(
    r"\b(cat|less|more|head|tail|bat|type|Get-Content|grep|source|xxd|od|strings|awk|sed)\b"
    r"|(?<!\.)\benv\b"
    r"|\bpython3?\s+-c\b"
    r"|(^|[;&|]\s*)\.\s+\S",  # dot-source: `. ./script` or `. .env`
    re.I,
)
WRITISH = re.compile(r"(>>?|\btee\b|\bcp\b|\bmv\b|\btouch\b|\binstall\b|\brm\b)", re.I)
WRITE_TOOLS = {"write", "edit", "strreplace", "notebookedit"}
PATH_KEYS = ("file_path", "path", "notebook_path")


def _haystacks(data: dict, tool: str) -> list[str]:
    out: list[str] = []
    tool_input = data.get("tool_input") or data.get("input") or {}
    if isinstance(tool_input, dict):
        for key in ("command", "cmd", *PATH_KEYS):
            val = tool_input.get(key)
            if isinstance(val, str) and val:
                out.append(val)
        if tool not in WRITE_TOOLS:  # for Write/Edit only the target path matters, never the content
            for val in tool_input.values():
                if isinstance(val, str) and val and val not in out:
                    out.append(val)
    cmd = data.get("command")
    if isinstance(cmd, str) and cmd:
        out.append(cmd)
    return out


def _tool_name(data: dict) -> str:
    raw = data.get("tool_name") or data.get("toolName") or data.get("tool") or ""
    return str(raw).strip().lower()


def hits_denylist(text: str) -> bool:
    return any(pat.search(text) for pat in DENY_PATTERNS)


def deny_reason(data: dict) -> str | None:
    """Return a deny message if this tool call touches a secret path, else None."""
    tool = _tool_name(data)
    blobs = _haystacks(data, tool)
    if not blobs:
        return None
    if not any(hits_denylist(b) for b in blobs):
        return None
    cmd = next((b for b in blobs if b), "")
    if tool in WRITE_TOOLS:
        kind = "write"
    elif tool in {"bash", "shell", ""}:
        if READISH.search(cmd):
            kind = "read"
        elif WRITISH.search(cmd):
            kind = "write"
        else:
            return None
    else:
        kind = "access"
    return (
        f"Alex's Rig secret-hygiene: blocked {kind} of denylisted secret path. "
        "Do not cat or write .env / credentials / keys into the agent transcript."
    )


def deny_payload(msg: str) -> dict:
    return {
        "decision": "deny",
        "reason": msg,
        "hookSpecificOutput": {
            "permissionDecision": "deny",
            "permissionDecisionReason": msg,
        },
    }


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return
    if not isinstance(data, dict):
        return
    msg = deny_reason(data)
    if msg:
        print(json.dumps(deny_payload(msg)))


if __name__ == "__main__":
    main()
