#!/usr/bin/env python3
"""Per-file review marks (GitHub Viewed): path → content hash. Stale hash = pending again."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from session_base import clear_stop_reminded, find_session_base, working_tree_diff

REVIEWED_NAME = "reviewed.json"


def reviewed_path(root: Path) -> Path:
    return root / ".alexs-rig" / REVIEWED_NAME


def load_reviewed(root: Path) -> dict[str, str]:
    p = reviewed_path(root)
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}


def save_reviewed(root: Path, mapping: dict[str, str]) -> None:
    dest = root / ".alexs-rig"
    dest.mkdir(parents=True, exist_ok=True)
    tmp = dest / f".{REVIEWED_NAME}.{os.getpid()}.tmp"
    tmp.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, reviewed_path(root))


def relpath(root: Path, raw: str | Path) -> str:
    p = Path(raw)
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    try:
        return p.relative_to(root.resolve()).as_posix()
    except ValueError:
        return Path(raw).as_posix()


def file_digest(root: Path, rel: str) -> str:
    """git hash-object of the file, or empty if missing (deleted)."""
    path = root / rel
    if not path.is_file():
        return ""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "hash-object", str(path)],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if out.returncode != 0:
        return ""
    return out.stdout.strip()


def dirty_names(root: Path) -> list[str]:
    """Paths that differ from SESSION_BASE (or empty if no base)."""
    _root, sha = find_session_base(root)
    if not sha:
        sha = _head(root)
    if not sha:
        return []
    code, text = working_tree_diff(root, sha, name_only=True)
    if code != 0:
        return []
    names = []
    for line in text.splitlines():
        n = line.strip()
        if n and not n.startswith(".alexs-rig/"):
            names.append(n)
    return names


def _head(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def pending_names(root: Path) -> list[str]:
    """Dirty files that are unmarked, or whose content changed since the mark."""
    mapping = load_reviewed(root)
    out: list[str] = []
    for rel in dirty_names(root):
        digest = file_digest(root, rel)
        if mapping.get(rel) == digest:
            continue
        out.append(rel)
    return out


def mark_files(root: Path, rels: list[str]) -> list[str]:
    mapping = load_reviewed(root)
    marked: list[str] = []
    for rel in rels:
        rel = rel.replace("\\", "/")
        while rel.startswith("./"):  # not lstrip("./"): that strips characters and eats ".github/"
            rel = rel[2:]
        mapping[rel] = file_digest(root, rel)
        marked.append(rel)
    save_reviewed(root, mapping)
    clear_stop_reminded(root)
    return marked


def mark_all_pending(root: Path) -> list[str]:
    return mark_files(root, pending_names(root))


def pending_stat(root: Path) -> str:
    names = pending_names(root)
    if not names:
        return ""
    _root, sha = find_session_base(root)
    if not sha:
        sha = _head(root)
    if not sha:
        return "\n".join(names)
    code, text = working_tree_diff(root, sha, stat=True, paths=names)
    if code != 0:
        return "\n".join(names)
    return text.strip()
