#!/usr/bin/env python3
"""SessionStart: inject L0 + record SESSION_BASE (git HEAD) for optional session-scoped review."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph_status import find_project_root, graph_context_block  # noqa: E402
from session_base import clear_review_mark, clear_stop_reminded  # noqa: E402


def find_l0(start: Path) -> Path | None:
    cur = start.resolve()
    for _ in range(8):
        candidate = cur / "docs" / "memory" / "snapshots" / "L0.md"
        if candidate.is_file():
            return candidate
        if cur.parent == cur:
            break
        cur = cur.parent
    # Fall back to global personal memory so a user with only ~/.alexs-rig
    # still gets L0 injected in any repo.
    global_l0 = Path.home() / ".alexs-rig" / "memory" / "snapshots" / "L0.md"
    if global_l0.is_file():
        return global_l0
    return None


def git_head(cwd: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def write_session_base(project: Path, sha: str) -> Path | None:
    if not sha:
        return None
    dest = project / ".alexs-rig"
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / "SESSION_BASE"
    path.write_text(sha + "\n", encoding="utf-8")
    clear_stop_reminded(project)
    clear_review_mark(project)
    return path


def main() -> None:
    cwd = Path.cwd()
    project = find_project_root(cwd)
    sha = git_head(project)
    session_base = write_session_base(project, sha)

    l0 = find_l0(cwd)
    if l0 is None:
        root = Path(__file__).resolve().parents[1]
        example = root / "docs" / "memory" / "snapshots" / "L0.md"
        l0 = example if example.is_file() else None
    if l0 is None:
        print("Alex's Rig: no docs/memory/snapshots/L0.md found (run bin/l0-regen).", file=sys.stderr)
        parts: list[str] = []
        if session_base:
            parts.append(
                f"<alexs-rig-session>\nSESSION_BASE={sha}\n"
                f"path={session_base}\nCompare later: git diff {sha} --\n</alexs-rig-session>"
            )
        parts.append(graph_context_block(project))
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n".join(parts),
            }
        }
        print(json.dumps(payload))
        return

    text = l0.read_text(encoding="utf-8")
    parts = [f"<alexs-rig-l0>\n{text}\n</alexs-rig-l0>"]
    if sha:
        parts.append(
            f"<alexs-rig-session>\nSESSION_BASE={sha}\n"
            f"Compare uncommitted-since-session-open: git diff {sha} --\n"
            f"(also recorded at .alexs-rig/SESSION_BASE)\n</alexs-rig-session>"
        )
    parts.append(graph_context_block(project))
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(parts),
        }
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
