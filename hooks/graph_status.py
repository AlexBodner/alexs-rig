#!/usr/bin/env python3
"""Detect standing codebase graphs (understand-anything / codemap). Shared by SessionStart inject."""

from __future__ import annotations

from pathlib import Path


def find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(8):
        if (cur / ".git").exists() or (cur / "docs" / "memory").is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start.resolve()


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
                lines.append(
                    f"- STALE: {count} source file(s) changed since last build "
                    "→ /alex-graph updates only those (incremental, asks first)."
                )
            else:
                lines.append("- Fresh: no source changes since last build.")
        else:
            lines.append("- Build base not marked — run /alex-graph (or bin/graph-mark) to track staleness.")
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
