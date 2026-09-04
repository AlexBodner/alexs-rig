# Usage

Install, where memory lives, and the CLI reference. The hooks are in [hooks.md](hooks.md).

## Install

```bash
git clone https://github.com/AlexBodner/alexs-rig.git ~/alexs-rig
cd ~/alexs-rig && ./scripts/install.sh
```

The script creates your personal memory, registers this checkout as a local Claude Code
plugin marketplace and installs the plugin, and copies the plugin into
`~/.cursor/plugins/local/alexs-rig` if Cursor is present. Start a new session afterwards.

Update:

```bash
git pull && claude plugin marketplace update alexs-rig && claude plugin update alexs-rig@alexs-rig
```

Claude Code compares manifest versions, so an update only lands when
`.claude-plugin/plugin.json` changed version.

## Where memory lives

One personal memory, never committed into each project:

- **Global (default):** `~/.alexs-rig/memory`. Used when no `--root` or env is given and the
  current project has no `docs/memory/` of its own. Any repo you open gets the same L0.
- **A private memory repo:** point `ALEXS_RIG_MEMORY` at a checkout you own. It may be the
  project root (memory under `docs/memory/`) or the `docs/memory` directory itself.
- **Per project:** a `docs/memory/` inside the project wins over the global one. Add it to
  that project's `.gitignore` unless you want it versioned there.

Resolution order for every CLI: `--root`, then `ALEXS_RIG_MEMORY`, then `ALEXS_RIG_ROOT`, then
the nearest `docs/memory/` walking up from the current directory, then the global memory.

The `docs/memory/` committed in this repo is the example a fresh install injects until you
have rules of your own. It holds the author's current principles.

## Commands

Memory:

| Command | Purpose |
|---|---|
| `bin/principle-upsert --id P-<slug> --text "..."` | Add or update a standing rule. The previous text is archived. |
| `bin/principle-forget --id P-<slug>` | Archive a rule. It leaves L0. |
| `bin/pending-upsert upsert --id T-<slug> --priority P1 --text "..."` | Park a todo. `done --id` closes it. |
| `bin/progress-upsert --id F-<slug> --status active --summary "..."` | Standing note on a feature. |
| `bin/l0-regen` / `bin/l0-show` | Rebuild the L0 snapshot from the JSONL sources / print it. |
| `bin/distill` | Largest entries when L0 overflows its budget. Shrink at the source, never truncate. |

Corrections:

| Command | Purpose |
|---|---|
| `bin/corrections list` / `flush` | Show the captured turns / archive them after a mining pass. |
| `bin/mine-corrections [--workspace X] [--since YYYY-MM-DD]` | Import past Cursor turns into the inbox. Keyword-filtered, so low recall; the live hook is the real source. |
| `bin/shipped add\|outcome\|list` | Log what shipped and, later, how it did. Refuses an entry with no artifact. |

Review and verification:

| Command | Purpose |
|---|---|
| `bin/review-pending [--name-only\|--stat]` | Agent edits since `SESSION_BASE` that you have not marked, or touched again after marking. |
| `bin/review-mark <path>...` / `--all` | Mark files reviewed at their current content. A later edit un-marks them. |
| `bin/session-diff [--stat]` | Full diff since the session opened. |
| `bin/verify` | Run the project's checks and record PASS or FAIL for the Stop reminder. Informational, never a gate. |

Codebase graph:

| Command | Purpose |
|---|---|
| `bin/graph-status` | Which graphs exist here and whether they are stale. |
| `bin/graph-mark [--stale]` | Re-mark the graph as current / list stale source files. |
| `bin/graph-seed [--from main]` | Copy the main worktree's graph into a new agent worktree. |
| `scripts/install_git_hooks.sh [project]` | The `post-merge` nudge plus the `.gitignore` lines that keep graph and state per worktree. |

All memory and corrections CLIs take `--root`. `bin/shipped` reads `ALEXS_RIG_MEMORY`.

## Environment variables

| Variable | Default | Effect |
|---|---|---|
| `ALEXS_RIG_MEMORY`, `ALEXS_RIG_ROOT` | unset | Where memory lives (see above). |
| `L0_BUDGET_TOKENS` | 1500 | L0 size above which `l0-regen` appends an OVERFLOW warning. |
| `ALEXS_RIG_CAPTURE_MIN_SCORE` | 0 | Set to 3 to capture only keyword-scored turns where a mining pass must stay cheap. Costs most of the recall. |
| `ALEXS_RIG_GRAPH_AUTO_AT` | 10 | Stale source files after which the graph refresh runs without asking. |

## Tests

```bash
python3 -m unittest discover -s tests -v
ruff check .
```
