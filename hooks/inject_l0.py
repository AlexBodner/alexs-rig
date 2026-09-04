#!/usr/bin/env python3
"""SessionStart: inject L0 + graph pointer + style note, and keep the review baseline honest.

SessionStart is the only hook that can add context after compaction (Claude Code fires it
with ``source: "compact"``; PreCompact output is not injected). It also fires on
``resume``, ``clear`` and ``fork``. The review baseline (``.alexs-rig/SESSION_BASE``) may
only move on a genuinely new session: after a compaction or resume the human is mid-task,
and re-snapshotting would bake every unreviewed agent edit into the base and silently
empty the review queue.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph_status import find_project_root, graph_context_block  # noqa: E402
from session_base import clear_review_mark, clear_stop_reminded, worktree_tree_sha  # noqa: E402

# Sources that continue an existing session rather than open a new one.
KEEP_BASE_SOURCES = {"compact", "resume", "fork"}


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


def session_base_path(project: Path) -> Path:
    return project / ".alexs-rig" / "SESSION_BASE"


def write_session_base(project: Path, sha: str) -> Path | None:
    if not sha:
        return None
    path = session_base_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sha + "\n", encoding="utf-8")
    clear_stop_reminded(project)
    clear_review_mark(project)
    return path


def read_source(data: dict) -> str:
    """Claude Code sends ``source``; Cursor's preCompact only names the event."""
    event = str(data.get("hook_event_name") or data.get("hookEventName") or "")
    if event.lower() == "precompact":
        return "compact"
    return str(data.get("source") or "startup")


def resolve_session_base(project: Path, source: str) -> str:
    """Return the sha the session should review against, snapshotting only when a new
    session opens (or nothing was recorded yet). Continuing sources keep the old base."""
    if source in KEEP_BASE_SOURCES:
        p = session_base_path(project)
        if p.is_file():
            existing = p.read_text(encoding="utf-8").strip()
            if existing:
                return existing
    sha = worktree_tree_sha(project) or git_head(project)
    write_session_base(project, sha)
    return sha


def style_context_block(project: Path) -> str:
    """Per-repo style note (P-style). If the note exists, inject it. If it does not yet
    AND this is a real repo, nudge to create it once — the reliable trigger for the
    once-per-repo analysis; the nudge disappears as soon as .alexs-rig/style.md is written."""
    p = project / ".alexs-rig" / "style.md"
    if p.is_file():
        try:
            note = p.read_text(encoding="utf-8").strip()
        except OSError:
            note = ""
        if note:
            return f"<alexs-rig-style>\n{note}\n</alexs-rig-style>"
    if (project / ".git").exists():
        return (
            "<alexs-rig-style-todo>\n"
            "No repo style note yet. Per P-style, on your first substantive edit here, analyze "
            "this repo's conventions once (comment density, docstring format, naming, imports) and "
            "save a short note to .alexs-rig/style.md — then follow it instead of re-analyzing. "
            "This nudge stops once the note exists.\n"
            "</alexs-rig-style-todo>"
        )
    return ""


def l0_block(cwd: Path, source: str) -> str:
    l0 = find_l0(cwd)
    if l0 is None:
        root = Path(__file__).resolve().parents[1]
        example = root / "docs" / "memory" / "snapshots" / "L0.md"
        l0 = example if example.is_file() else None
    if l0 is None:
        print("Alex's Rig: no docs/memory/snapshots/L0.md found (run bin/l0-regen).", file=sys.stderr)
        return ""
    text = l0.read_text(encoding="utf-8")
    if source == "compact":
        return (
            f"<alexs-rig-l0 compact-reinject>\n{text}\n</alexs-rig-l0>\n"
            "Standing memory re-injected after compaction — prefer L0 over stale chat beliefs."
        )
    return f"<alexs-rig-l0>\n{text}\n</alexs-rig-l0>"


def read_stdin() -> dict:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except (OSError, json.JSONDecodeError):
        data = {}
    return data if isinstance(data, dict) else {}


def main() -> None:
    data = read_stdin()
    source = read_source(data)
    cwd = Path.cwd()
    project = find_project_root(cwd)
    sha = resolve_session_base(project, source)

    parts: list[str] = []
    l0 = l0_block(cwd, source)
    if l0:
        parts.append(l0)
    if sha:
        parts.append(
            f"<alexs-rig-session>\nSESSION_BASE={sha}\n"
            f"Compare uncommitted-since-session-open: git diff {sha} --\n"
            f"(also recorded at .alexs-rig/SESSION_BASE)\n</alexs-rig-session>"
        )
    parts.append(graph_context_block(project))
    style = style_context_block(project)
    if style:
        parts.append(style)
    context = "\n".join(parts)
    payload = {
        "additional_context": context,  # Cursor's native sessionStart key; ignored by Claude Code
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        },
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
