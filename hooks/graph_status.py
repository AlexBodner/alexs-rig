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
