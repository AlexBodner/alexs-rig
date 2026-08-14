---
name: alex-graph
description: Incrementally update the codebase graph for only the files changed since the last build (git-tracked), instead of a full rebuild. The rebuild is LLM-driven, so it ASKS before running. Use when the graph is stale after edits or a merge.
---

# Alex graph (incremental, ask-gated)

Keep the understand-anything graph fresh **without** full rebuilds. The stale set
comes from git (near-free); the rebuild is incremental and only runs **after you
approve** — the harness never spends tokens rebuilding on its own.

## Workflow

1. **See what's stale** (source files changed since the last build):

   ```bash
   python3 bin/graph-mark --stale
   ```

   If the list is empty, stop — the graph is current. If `graph-base not set`,
   there is no build to diff against yet (see "No graph yet" below).

2. **Ask the user before rebuilding.** The update is LLM-driven and spends tokens,
   so confirm: "Update the graph for these N changed files?" Wait for an explicit yes.

3. **On approval, run the INCREMENTAL update** over the changed set only — not a
   full rebuild:

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
- **During development:** SessionStart / PreCompact surface `STALE: N source
  file(s) changed since last build` in the graph pointer once staleness accrues.

## No graph yet

Build it once, then mark the base:

```text
/understand --auto-update
```
```bash
python3 bin/graph-mark
```

Never dump `knowledge-graph.json` into L0 or chat — query it. This skill orchestrates
understand-anything; the Rig does not implement its own graph engine.
