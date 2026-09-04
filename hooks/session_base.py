#!/usr/bin/env python3
"""SESSION_BASE (the worktree snapshot a session is reviewed against) + worktree diff helpers."""

from __future__ import annotations

import os
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


def clear_review_mark(root: Path) -> None:
    """A new session starts with an empty review ledger."""
    p = root / ".alexs-rig" / "reviewed.json"
    if p.is_file():
        p.unlink()


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


def _index_env(root: Path, name: str) -> tuple[dict[str, str], Path] | None:
    """Env pointing GIT_INDEX_FILE at a throwaway per-call index under .alexs-rig,
    plus that index path (caller removes it). None when root is not a git repo —
    no repo means no snapshot, and no stray .alexs-rig/ in non-repo dirs."""
    if not (root / ".git").exists():
        return None
    dest = root / ".alexs-rig"
    dest.mkdir(parents=True, exist_ok=True)
    index = dest / f"{name}-{os.getpid()}.index"
    env = dict(os.environ)
    env["GIT_INDEX_FILE"] = str(index)
    return env, index


def _git_add_worktree(root: Path, env: dict[str, str]) -> bool:
    out = subprocess.run(
        ["git", "-C", str(root), "add", "-A", "--", ".", ":!.alexs-rig"],
        env=env,
        capture_output=True,
        check=False,
        timeout=30,
    )
    return out.returncode == 0


def worktree_tree_sha(root: Path) -> str:
    """Snapshot the current worktree (tracked + untracked, minus .alexs-rig) into a
    git tree object; return its sha, or "" on failure (e.g. not a git repo)."""
    idx = _index_env(root, "session-base")
    if idx is None:
        return ""
    env, index = idx
    try:
        if not _git_add_worktree(root, env):
            return ""  # a partial index would snapshot as the empty tree and mark everything dirty
        out = subprocess.run(
            ["git", "-C", str(root), "write-tree"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    finally:
        index.unlink(missing_ok=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def working_tree_diff(
    root: Path,
    sha: str,
    stat: bool = False,
    name_only: bool = False,
    paths: list[str] | None = None,
) -> tuple[int, str]:
    """Diff current worktree (incl. untracked) against a commit/tree SHA."""
    if not sha:
        return 1, ""
    idx = _index_env(root, "review-pending")
    if idx is None:
        return 1, ""
    env, index = idx
    cmd = ["git", "-C", str(root), "diff", "--cached"]
    if stat:
        cmd.append("--stat")
    if name_only:
        cmd.append("--name-only")
    cmd.extend([sha, "--"])
    if paths:
        cmd.extend(paths)
    try:
        if not _git_add_worktree(root, env):
            return 1, ""
        out = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    finally:
        index.unlink(missing_ok=True)
    return out.returncode, out.stdout or ""
