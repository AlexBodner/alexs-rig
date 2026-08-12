# Usage — Alex's Rig

## Install

```bash
git clone https://github.com/AlexBodner/alexs-rig.git
cd alexs-rig   # open THIS folder as the IDE workspace
python3 -m unittest tests.test_memory -v
chmod +x bin/* hooks/inject_l0.py scripts/*.sh
./scripts/bootstrap.sh          # or: ./scripts/bootstrap.sh --yes
# Use the absolute L0 path bootstrap prints — relative open from a parent folder looks empty.
./scripts/install_claude_plugin.sh   # SessionStart L0 — see docs/claude-plugin-install.md
```

### First open

1. **Workspace = clone root** (e.g. `/workspace/alexs-rig`), never the parent (`/workspace`).
2. Dismiss Copilot sign-in / auto-opened chat if they crowd a laptop screen before you can read L0.
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
| `python3 hooks/inject_l0.py` | Emit SessionStart JSON with L0 (Claude hook) |

All memory CLIs accept `--root` (and honor `ALEXS_RIG_MEMORY` / `ALEXS_RIG_ROOT`).

## Claude Code plugin

See [claude-plugin-install.md](claude-plugin-install.md). Hook: SessionStart → `inject_l0.py`.

## IDE extensions

See [extensions.md](extensions.md). Minimum for uncommitted review: built-in SCM + **Git Tree Compare**.

## Correction mining

See [mining.md](mining.md) (MVP scope: all Cursor workspaces; optional `--workspace` filter).

```bash
python3 bin/mine-corrections --strong-only
python3 bin/mine-corrections --strong-only --workspace AI-Rig
```

**Empty ≠ broken.** **Never** auto-apply candidates.

## Desktop / architecture lock

Human ritual: [desktop-lock.md](desktop-lock.md).

## Tests

```bash
python3 -m unittest tests.test_memory -v
```

## Agent prompts

| Prompt | Use |
|--------|-----|
| [AGENT_TRY.md](../prompts/AGENT_TRY.md) | Dogfood like a human |
| [AGENT_BOX_VERIFY.md](../prompts/AGENT_BOX_VERIFY.md) | B1–B16 scoreboard |
| [AGENT_SIMULATE_USAGE.md](../prompts/AGENT_SIMULATE_USAGE.md) | Multi-PR usage sim |
| [AGENT_ITERATE.md](../prompts/AGENT_ITERATE.md) | Backlog coding |
