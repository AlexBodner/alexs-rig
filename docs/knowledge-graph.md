# Always-on knowledge graph

Alex's Rig does **not** implement a graph engine. It makes existing graphs **standing default** for codebase handling.

## What “always-on” means

| Does | Does not |
|------|----------|
| SessionStart tells the agent which graphs exist | Dump `knowledge-graph.json` into L0 or chat |
| Always-on rule: query graph before blind Grep | Replace git / diffs / L0 |
| Prefer understand-anything + codemap-py | Fork those tools |

## Setup (once per project)

```bash
# Architecture / component graph (any language understand-anything supports)
/understand --auto-update

# Python structural index
/codemap-py:scan-codebase
```

Artifacts (in the **target repo**, not necessarily alexs-rig):

- `.understand-anything/knowledge-graph.json`
- `.cache/codemap/*.json`

## Daily

`bin/graph-status` (also injected at SessionStart and PreCompact). Then `/understand-chat` or `/codemap-py:query-code`.

Plugin rule: `rules/knowledge-graph.md` (Claude-style) and `rules/knowledge-graph.mdc` (Cursor-style). Same body — keep them in sync.

## Keep L0 small

Graph files can be megabytes. L0 only records the *habit* (`P-graph`). The graph itself stays on disk.
