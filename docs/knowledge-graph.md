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
- **`/alex-graph`** is the workflow: show the stale set → run understand-anything's
  incremental update (`/understand-diff` / `--auto-update`) over just those files →
  `graph-mark` to reset staleness. **The first build of a repo asks; refreshes do not** —
  building from scratch is an explicit decision, keeping an existing graph current is
  maintenance. The auto threshold is `ALEXS_RIG_GRAPH_AUTO_AT` (default 10 stale files).

Only source files count as stale (`.py`, `.ts`, `.go`, …); docs/data/config changes
don't trigger it. The Rig still orchestrates understand-anything — it does not build
its own graph.

## Parallel agents / worktrees (seed from main, grow local, re-derive on merge)

Several agents on the same project, one worktree each. The graph is a **derived**
artifact, so the rule is: **seed from the integration tree, grow it locally, never
git-merge it, re-derive on main.**

- **Start from main.** A new agent worktree begins from main/develop's already-built
  graph rather than rebuilding from scratch. `bin/graph-seed` filesystem-copies main's
  graph + its `graph-base` into the new worktree (not git — the graph is gitignored),
  so it's free and collision-free. Staleness then tracks only that worktree's edits.

  ```bash
  git worktree add -b feat ../feat && cd ../feat
  python3 /path/to/alexs-rig/bin/graph-seed   # auto-detects the main/develop worktree
  ```
- **Grow local, no collisions.** Each worktree has its own graph and its own
  `graph-base` (`.alexs-rig/` is gitignored, so it's per-worktree). Agents build and
  update their own graph independently — they never touch the same tracked file.
- **Never commit the graph or `.alexs-rig/`.** `scripts/install_git_hooks.sh` adds them
  to the project `.gitignore`. Committing a monolithic `knowledge-graph.json` is exactly
  what 3-way-merges into a collision when two features land — so we don't track it.
- **Merge = re-derive, not git-merge.** When a feature merges to main, main's graph is
  stale; the `post-merge` hook nudges and `/alex-graph` re-derives **only the merged
  diff** (incremental, ask-gated). No JSON is merged, so there is nothing to collide.
- **The one honest conflict:** if two agents changed the **same source file**, that
  file's node is re-analyzed on merge — which mirrors the code conflict you already resolve.

Reusing each agent's analysis *without* re-deriving would need a per-file-sharded graph
store (git-mergeable shards). understand-anything doesn't expose that and the Rig doesn't
reimplement it, so the pragmatic path is re-derive-on-merge.

## Keep L0 small

Graph files can be megabytes. L0 only records the *habit* (`P-graph`). The graph itself stays on disk.
