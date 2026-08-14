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

## Keeping it fresh (incremental, ask-gated)

The graph goes stale as code changes. The Rig tracks the stale set from **git**
(near-free) and updates only what changed — never a full rebuild, and never
without asking (the rebuild is LLM-driven).

- **`bin/graph-mark`** records `graph-base` = the worktree snapshot the graph was
  last built against. Run it right after a build.
- **`bin/graph-mark --stale`** lists the source files changed since then.
- SessionStart / PreCompact surface `STALE: N source file(s)` in the graph pointer.
- The **`post-merge` git hook** (`scripts/install_git_hooks.sh`) nudges after a merge.
- **`/alex-graph`** is the workflow: show the stale set → **ask you** → run
  understand-anything's incremental update (`/understand-diff` / `--auto-update`)
  over just those files → `graph-mark` to reset staleness.

Only source files count as stale (`.py`, `.ts`, `.go`, …); docs/data/config changes
don't trigger it. The Rig still orchestrates understand-anything — it does not build
its own graph.

## Keep L0 small

Graph files can be megabytes. L0 only records the *habit* (`P-graph`). The graph itself stays on disk.
