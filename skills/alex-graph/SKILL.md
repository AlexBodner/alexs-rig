---
name: alex-graph
description: Incrementally update the codebase graph for only the files changed since the last build (git-tracked), instead of a full rebuild. Refreshing an existing graph runs without asking; only the first build of a repo asks. Use when the graph is stale after edits or a merge.
---

# Alex graph (incremental)

Keep the understand-anything graph fresh **without** full rebuilds. The stale set comes
from git (near-free) and the update is incremental.

**The first build asks; refreshes do not.** Building a graph from scratch is the expensive,
explicit step — propose it and wait. Once a graph and its `graph-base` exist, keeping it
current is maintenance: refresh the changed files without asking. The SessionStart pointer
says which case you are in.

## Workflow

1. **See what's stale** (source files changed since the last build):

   ```bash
   python3 bin/graph-mark --stale
   ```

   If the list is empty, stop — the graph is current. If `graph-base not set`,
   there is no build to diff against yet (see "No graph yet" below).

2. **Refresh without asking** when a graph already exists — this is maintenance, and the
   cost is bounded by the stale set, not the repo. Say what you refreshed afterwards.
   Only the *first* build of a repo needs approval (see "No graph yet").

3. **Run the INCREMENTAL update** over the changed set only, not a full rebuild:

   ```text
   /understand-diff        # analyze the git diff / changed files into the graph
   # or, if the plugin prefers it: /understand --auto-update
   ```

4. **Re-mark the base** so staleness resets to zero:

   ```bash
   python3 bin/graph-mark
   ```

## Triggers

- **On PR merge:** the installed `post-merge` git hook prints a reminder; run this
  skill when you next open Claude.
- **During development:** SessionStart (also after a compaction) surfaces `STALE: N source file(s)`.
  Below the auto threshold (`ALEXS_RIG_GRAPH_AUTO_AT`, default 10) that line is
  informational; at or above it, refresh on your own initiative.

## Parallel agents / worktrees

Each worktree keeps its own graph and `graph-base` (`.alexs-rig/` is gitignored), so
agents grow their graphs independently — no collisions. On merge you **re-derive**, you
do not git-merge: run this skill on main and it updates only the merged diff. If that
stale set is large (a big merge), update in a few file batches rather than one giant
`/understand-diff`. See `docs/knowledge-graph.md` → "Parallel agents / worktrees".

## No graph yet

This is the one step that needs the user's go-ahead — a first build reads the whole repo
and is not cheap. Propose it, then once approved:

```text
/understand --auto-update
```

Staleness tracking starts by itself the next time a session sees the graph — no
`graph-mark` needed for the first build.

Never dump `knowledge-graph.json` into L0 or chat — query it. This skill orchestrates
understand-anything; the Rig does not implement its own graph engine.
