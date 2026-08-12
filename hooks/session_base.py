#!/usr/bin/env python3
"""SESSION_BASE helpers shared by SessionStart inject and Stop review."""

from __future__ import annotations

import subprocess
from pathlib import Path


def find_session_base(start: Path) -> tuple[Path, str]:
    cur = start.resolve()
    for _ in range(8):
        p = cur / ".alexs-rig" / "SESSION_BASE"
        if p.is_file():
            sha = p.read_text(encoding="utf-8").strip()
            if sha:
                return cur, sha
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve(), ""


def session_diff_stat(root: Path, sha: str) -> str:
    """Return `git diff --stat` since SESSION_BASE, or empty if clean/unavailable."""
    if not sha:
        return ""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "diff", "--stat", sha, "--"],
            capture_output=True,
            text=True,
            check=False,
            timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if out.returncode != 0:
        return ""
    return (out.stdout or "").strip()


def stop_reminded_path(root: Path) -> Path:
    return root / ".alexs-rig" / "STOP_REMINDED"


def clear_stop_reminded(root: Path) -> None:
    p = stop_reminded_path(root)
    if p.is_file():
        p.unlink()


def mark_stop_reminded(root: Path) -> None:
    dest = root / ".alexs-rig"
    dest.mkdir(parents=True, exist_ok=True)
    stop_reminded_path(root).write_text("1\n", encoding="utf-8")
