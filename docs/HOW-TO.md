# How to use Alex's Rig

This is the human start-here. Agents also read [AGENTS.md](../AGENTS.md). Hook test steps: [hooks.md](hooks.md).

## How it works

The Rig is a **plugin + a small memory folder**, not a second IDE.

```text
You  →  Claude Code Desktop (or Cursor / VS Code Claude)
            │
            ├─ Hooks (automatic)  inject L0, block secrets, nudge review
            ├─ L0                 standing beliefs for THIS project
            ├─ Skills             /alex-memory, /alex-structure, …
            └─ Graphs             understand-anything + codemap-py (in the project)
```

**L0** (`docs/memory/snapshots/L0.md`) is a generated snapshot of active principles, progress, and pending. Change those via the upsert CLIs, then `l0-regen`. Do not treat `archive/` as current.

**Two surfaces:** Desktop for Plan → Edit automatically → `+N -M`. IDE **Source Control → Review** for session and PR Viewed (one list). No custom DiffEditor. GitHub Pull Requests extension is optional (comments/merge only).

## One-time setup

```bash
git clone https://github.com/AlexBodner/alexs-rig.git
cd alexs-rig
./scripts/install.sh
```

Needs `code` or `cursor` on PATH. If `install.sh` exits 1, Review is not registered — re-run `./scripts/install_review_extension.sh`. On success, **Reload Window once**. Open the **clone folder** as the workspace (not `~/Projects`).

To remember **another repo**, copy `docs/memory/` into it (or `--root` / `ALEXS_RIG_MEMORY` — [usage.md](usage.md)). Then open **that** repo as the workspace so SessionStart finds its L0.

Once per project, for smart codebase handling:

```text
/understand --auto-update
/codemap-py:scan-codebase
```

## What it does automatically

After the plugin is installed and you start a session in a project folder:

| When | Automatic | You still do |
|------|-----------|----------------|
| Session starts | Injects L0 (if present) + a **graph pointer** (not the JSON). Records `SESSION_BASE` (worktree snapshot at session open). | Skim L0 if you care what the agent believes |
| You send a prompt | If this project has **no** L0: one miss line. Does not dump L0 every send. | Ignore the miss, or add memory with `l0-regen --root .` |
| Agent runs Bash / Write / Edit | Blocks `cat` or write of `.env`, keys, credentials. `test -f .env` is allowed. | Use the host secret store; never paste secrets into chat |
| Context compact | Reinjects L0 + graph pointer | Nothing |
| Agent finishes a turn | **Once per dirty round**, if session files are still not Viewed: reminds batch review. Does not block, does not auto-commit. | Desktop `+N -M`; IDE Source Control → Review → check Viewed |
| You run `mine-corrections` | Named clusters upsert into L0; noisy `other` is skipped | Run mining when you want; `--no-apply` for dry-run |

Not automatic: commits, PRs, graph **builds**, inventing principles, running tests on Stop.

## How to use it (daily)

1. Open the **project folder** (the one with `.git` / `docs/memory`).
2. New Claude/Cursor session — L0 should already be in context. Ask “What does my L0 say?” once if you want proof.
3. **Plan** for non-trivial work → approve once → **Edit automatically** (not stop-on-every-edit).
4. When the turn ends, review in **batch**: Desktop `+N -M` / Cmd+Shift+D for the map. In Cursor/VS Code open **Source Control → Review**. Toolbar **session** (this chat) or **pull request** (vs PR base, including local edits). Click a file, then check **Viewed**. If the file changes, it unchecks. Same list for both — not the GitHub PR extension.
5. Park standing state: pending/progress upserts → `l0-regen`. Correct a repeated preference with `principle-upsert`.
6. Commit **when you ask**. PRs: `gh pr checkout` then the same Review view (PR mode).

Slash skills (plugin installed): `/alex-memory`, `/alex-structure`, `/alex-session-review`, `/alex-pr-review`, `/alex-mine-corrections`.

## How to make the most of it

- **Correct once, then write it down.** If you keep saying “batch review, not per-edit,” upsert `P-review` (or run mining). L0 is how tomorrow’s session remembers.
- **Keep L0 small.** Overflow means distill or forget, not a bigger dump. Graph JSON never belongs in L0.
- **Query the graph before grep** for “where does X live?” `/understand-chat` or `/codemap-py:query-code`. If `bin/graph-status` says NO, generate the graph once.
- **Trust hooks for secrets; don’t fight them.** If a `.env` read is blocked, that is the Rig working.
- **One Stop reminder per dirty round is enough.** After it fires, you review and check Viewed; it will not nag every turn.
- **Memory is per project.** Opening a parent folder looks like empty L0. Open the repo root.
- **AI-Rig (Borda) is how to build** (feature/fix/review skills). This harness is memory + supervision habit only — do not fork those skills into this repo.

## What not to expect

Custom DiffEditor, auto-PR, Beads, a second knowledge-graph engine, or Stop that runs the test suite and refuses to end the turn.

## More detail

| Topic | Page |
|-------|------|
| Daily loop (canonical) | [workflow.md](workflow.md) |
| Incremental review | Source Control → Review (session or PR Viewed) · skills `alex-session-review` / `alex-pr-review` |
| Install, `--root`, CLI table | [usage.md](usage.md) |
| Hook events + live test | [hooks.md](hooks.md) |
| Graph habit | [knowledge-graph.md](knowledge-graph.md) |
| Mining | [mining.md](mining.md) |
| Why these primitives | [practices.md](practices.md) |
| Architecture lock | [architecture.md](architecture.md) |
