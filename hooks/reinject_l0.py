#!/usr/bin/env python3
"""PreCompact / PostCompact: re-inject L0 + graph pointer so they survive compaction."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graph_status import find_project_root, graph_context_block  # noqa: E402
from inject_l0 import find_l0, style_context_block  # noqa: E402


def main() -> None:
    event = "PreCompact"
    raw = sys.stdin.read().strip()
    if raw:
        try:
            data = json.loads(raw)
            event = str(data.get("hook_event_name") or data.get("hookEventName") or event)
        except json.JSONDecodeError:
            pass

    project = find_project_root(Path.cwd())
    parts: list[str] = []
    l0 = find_l0(Path.cwd())
    if l0 is None:
        root = Path(__file__).resolve().parents[1]
        example = root / "docs" / "memory" / "snapshots" / "L0.md"
        l0 = example if example.is_file() else None
    if l0 is not None:
        text = l0.read_text(encoding="utf-8")
        parts.append(
            f"<alexs-rig-l0 compact-reinject>\n{text}\n</alexs-rig-l0>\n"
            "Standing memory re-injected after compaction — prefer L0 over stale chat beliefs."
        )
    parts.append(graph_context_block(project))
    style = style_context_block(project)
    if style:
        parts.append(style)
    payload = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": "\n".join(parts),
        }
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
