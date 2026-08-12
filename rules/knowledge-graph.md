---
description: Always-on codebase knowledge graph — query before blind search. Do not dump the graph into L0.
alwaysApply: true
---

# Knowledge graph (always-on)

Alex's Rig treats a **standing codebase graph** as the default way to handle architecture, modules, and blast radius.

## Order of operations (every non-trivial code question)

1. **understand-anything** if `.understand-anything/knowledge-graph.json` (or `knowledge-graph.json`) exists — use `/understand-chat`, `/understand-explain`, or targeted reads. Do **not** paste the whole JSON into context.
2. **codemap-py** if `.cache/codemap/*.json` exists — `/codemap-py:query-code` for Python callers, deps, test-impact.
3. Only then Grep/Glob/README walks.

If no graph exists in this repo: say so, then offer `/understand` (with `--auto-update`) and/or `/codemap-py:scan-codebase`. Do not silently skip.

## Never

- Put the graph body into L0 (token budget).
- Build a second graph engine inside Alex's Rig.
- Ignore an existing graph in favor of a full-tree grep for "how is this structured?"
