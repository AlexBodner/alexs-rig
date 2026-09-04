#!/usr/bin/env python3
"""Detect standing codebase graphs (understand-anything / codemap). Shared by SessionStart inject."""

from __future__ import annotations

import os
from pathlib import Path


def find_project_root(start: Path) -> Path:
    """Where per-project state (.alexs-rig/) lives. A directory holding docs/memory wins over
    a nearer .git, so a vendored or nested repo inside a project does not capture the state;
    otherwise the nearest .git; otherwise ``start``."""
    cur = start.resolve()
    first_git: Path | None = None
    for _ in range(8):
        if (cur / "docs" / "memory").is_dir():
            return cur
        if first_git is None and (cur / ".git").exists():
            first_git = cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return first_git or start.resolve()


def graph_status(project: Path) -> dict:
    ua = project / ".understand-anything" / "knowledge-graph.json"
    if not ua.is_file():
        alt = project / "knowledge-graph.json"
        ua = alt if alt.is_file() else ua
    codemap_dir = project / ".cache" / "codemap"
    codemap_files: list[Path] = []
    if codemap_dir.is_dir():
        codemap_files = sorted(p for p in codemap_dir.glob("*.json") if p.is_file())[:5]
    return {
        "understand_anything": ua.is_file(),
        "understand_path": str(ua) if ua.is_file() else "",
        "understand_bytes": ua.stat().st_size if ua.is_file() else 0,
        "codemap": bool(codemap_files),
        "codemap_path": str(codemap_files[0]) if codemap_files else "",
    }


# Source files whose changes should make the graph stale (skip docs/data/config).
SOURCE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".java", ".go", ".rb",
    ".rs", ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".kt", ".swift", ".php",
    ".scala", ".m", ".mm", ".lua", ".sh",
}


# Once a graph exists, keeping it current is maintenance, not a decision: the initial
# build is the expensive, explicit step and stays the user's call. Past this many stale
# source files the agent refreshes the graph on its own instead of asking every time.
GRAPH_AUTO_UPDATE_AT = int(os.environ.get("ALEXS_RIG_GRAPH_AUTO_AT", "10"))


def graph_base_path(project: Path) -> Path:
    return project / ".alexs-rig" / "graph-base"


def graph_base_sha(project: Path) -> str:
    p = graph_base_path(project)
    if p.is_file():
        return p.read_text(encoding="utf-8").strip()
    return ""


def set_graph_base(project: Path, sha: str) -> Path:
    dest = project / ".alexs-rig"
    dest.mkdir(parents=True, exist_ok=True)
    graph_base_path(project).write_text(sha + "\n", encoding="utf-8")
    return graph_base_path(project)


def _all_stale_source_files(project: Path) -> list[str]:
    """Uncapped list of source files changed (worktree, incl. untracked) since the
    graph was last built. The changed set is git-tracked — near-free, no full rebuild."""
    sha = graph_base_sha(project)
    if not sha:
        return []
    try:
        from session_base import working_tree_diff

        code, text = working_tree_diff(project, sha, name_only=True)
    except Exception:
        return []
    if code != 0:
        return []
    out: list[str] = []
    for line in text.splitlines():
        n = line.strip()
        if not n or n.startswith(".alexs-rig/"):
            continue
        if Path(n).suffix.lower() in SOURCE_EXTS:
            out.append(n)
    return out


def stale_source_files(project: Path, cap: int = 50) -> list[str]:
    """Capped list of stale source files (see ``_all_stale_source_files``)."""
    return _all_stale_source_files(project)[:cap]


def _start_tracking(project: Path) -> bool:
    """Set graph-base from the current worktree. Returns False if it could not be set."""
    try:
        from session_base import worktree_tree_sha

        sha = worktree_tree_sha(project)
    except Exception:
        return False
    if not sha:
        return False
    try:
        set_graph_base(project, sha)
    except OSError:
        return False
    return True


def graph_context_block(project: Path) -> str:
    st = graph_status(project)
    lines = [
        "<alexs-rig-graph>",
        "Always-on codebase graph (do not dump the JSON into chat or L0):",
    ]
    if st["understand_anything"]:
        kb = max(1, st["understand_bytes"] // 1024)
        lines.append(f"- understand-anything: YES ({st['understand_path']}, ~{kb} KiB)")
        lines.append("- Query via /understand-chat or targeted nodes — not the whole file.")
        if graph_base_sha(project):
            stale = _all_stale_source_files(project)
            if stale:
                cap = 50
                count = f"{cap}+" if len(stale) > cap else str(len(stale))
                if len(stale) >= GRAPH_AUTO_UPDATE_AT:
                    lines.append(
                        f"- STALE: {count} source file(s) changed since last build. "
                        "Refresh with /alex-graph now — incremental, only these files, and no "
                        "confirmation needed: maintaining an existing graph is routine."
                    )
                else:
                    lines.append(
                        f"- STALE: {count} source file(s) changed since last build "
                        f"(auto-refresh at {GRAPH_AUTO_UPDATE_AT}; /alex-graph to do it sooner)."
                    )
            else:
                lines.append("- Fresh: no source changes since last build.")
        else:
            # Starting the staleness clock is bookkeeping, not a decision: requiring a
            # manual graph-mark after /understand meant one forgotten step left the whole
            # refresh loop dormant. Mark it the first time a graph is seen.
            started = _start_tracking(project)
            if started:
                lines.append(
                    "- Staleness tracking started now (first time this graph was seen). If the "
                    "graph predates recent work, run /alex-graph once to bring it current."
                )
            else:
                lines.append("- Build base not marked — run bin/graph-mark to track staleness.")
    else:
        lines.append("- understand-anything: NO — run /understand --auto-update in this repo.")
    if st["codemap"]:
        lines.append(f"- codemap-py index: YES ({st['codemap_path']})")
        lines.append("- Python structure: /codemap-py:query-code (rdeps, test-impact, symbol).")
    else:
        lines.append("- codemap-py: NO — for Python repos run /codemap-py:scan-codebase.")
    lines.append("- Before blind Grep/Glob of architecture: query the graph/index first.")
    lines.append("</alexs-rig-graph>")
    return "\n".join(lines)
