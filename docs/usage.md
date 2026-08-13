# Usage — Alex's Rig

How it works and the daily loop: [HOW-TO.md](HOW-TO.md). This page is install + CLI reference.

## Install

```bash
git clone https://github.com/AlexBodner/alexs-rig.git
cd alexs-rig   # open THIS folder as the IDE workspace
./scripts/install.sh
```

Needs `code` or `cursor` on PATH. Exit 1 means the Review vsix was not registered. On success, **Reload Window once**. Use the absolute L0 path bootstrap prints.

### First open

1. **Workspace = clone root** (e.g. `/workspace/alexs-rig`), never the parent (`/workspace`).
2. Dismiss first-run sign-in / auto-opened chat if they crowd a laptop screen before you can read L0.
3. Open `"$PWD/docs/memory/snapshots/L0.md"` (absolute). A relative `docs/memory/...` against the wrong root creates a blank unsaved file — memory is not empty.
4. Progress `--path` should be `.` or omitted; do not store machine-specific home paths in committed jsonl.

### Use memory inside another project

```bash
mkdir -p my-app/docs/memory/{snapshots,archive,mining,telemetry}
touch my-app/docs/memory/{PRINCIPLES,PROGRESS,PENDING}.jsonl

# Point CLIs at that project:
python3 /path/to/alexs-rig/bin/principle-upsert --root my-app --id P-1 --text "…"
python3 /path/to/alexs-rig/bin/l0-regen --root my-app
python3 /path/to/alexs-rig/bin/l0-show --root my-app

# Or env (same effect):
export ALEXS_RIG_MEMORY=/absolute/path/to/my-app
python3 /path/to/alexs-rig/bin/l0-regen
```

`--root` / `ALEXS_RIG_MEMORY` may be the **project root** or the `docs/memory` directory itself.

## Commands

| Command | Purpose |
|---------|---------|
| `python3 bin/principle-upsert --id P-… --text "…"` | Add/update standing principle |
| `python3 bin/principle-forget --id P-…` | Archive principle (leaves L0) |
| `python3 bin/progress-upsert --id F-… --status active --summary "…"` | Feature standing |
| `python3 bin/pending-upsert upsert --id T-… --priority P1 --text "…"` | Park a todo |
| `python3 bin/pending-upsert done --id T-…` | Complete todo |
| `python3 bin/l0-regen` | Regenerate `docs/memory/snapshots/L0.md` |
| `python3 bin/l0-show` | Print L0 or exit 1 if missing |
| `python3 bin/mine-corrections --strong-only` | Mine Cursor transcripts → candidates |
| `python3 bin/graph-status` | Whether understand-anything / codemap exist in this repo |
| `python3 bin/session-diff` | Diff since SessionStart (`SESSION_BASE`) |
| `python3 bin/review-mark path` | Fallback CLI: mark that file (UI is Source Control → Review) |
| `python3 bin/review-mark --all` | Fallback CLI: mark every currently pending file |
| `python3 bin/review-pending --name-only` | Fallback CLI: dirty files unmarked or re-touched |
| Hook map | [hooks.md](hooks.md) |

All memory CLIs accept `--root` (and honor `ALEXS_RIG_MEMORY` / `ALEXS_RIG_ROOT`).

## Claude Code plugin

See [claude-plugin-install.md](claude-plugin-install.md). Full map: [hooks.md](hooks.md).

## IDE extensions

See [extensions.md](extensions.md). Viewed for session and PR: **Review** in Source Control. GitHub Pull Requests extension is optional (comments/merge).

## Correction mining

See [mining.md](mining.md) (MVP scope: all Cursor workspaces; optional `--workspace` filter).

```bash
python3 bin/mine-corrections --strong-only
python3 bin/mine-corrections --strong-only --workspace AI-Rig
```

**Empty ≠ broken.** Named clusters auto-upsert; `other` stays candidates-only unless `--apply-other`.

## Knowledge graph

Standing graphs live in the **target repo**, not in L0. SessionStart injects a short pointer (`bin/graph-status`). See [knowledge-graph.md](knowledge-graph.md).

```bash
python3 bin/graph-status
# If missing: /understand --auto-update  and/or  /codemap-py:scan-codebase
```

## Desktop / architecture lock

Human ritual: [desktop-lock.md](desktop-lock.md).

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Agent prompts

| Prompt | Use |
|--------|-----|
| [AGENT_TRY.md](../prompts/AGENT_TRY.md) | Dogfood like a human |
| [AGENT_BOX_VERIFY.md](../prompts/AGENT_BOX_VERIFY.md) | B1–B16 scoreboard |
| [AGENT_SIMULATE_USAGE.md](../prompts/AGENT_SIMULATE_USAGE.md) | Multi-PR usage sim |
| [AGENT_ITERATE.md](../prompts/AGENT_ITERATE.md) | Backlog coding |
