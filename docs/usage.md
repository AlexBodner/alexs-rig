# Usage — Alex's Rig

## Install

```bash
git clone <this-repo-url>
cd alexs-rig   # or alexs-rig-proto
python3 -m unittest tests.test_memory -v
chmod +x bin/* hooks/inject_l0.py scripts/bootstrap.sh
./scripts/bootstrap.sh
```

### Use memory inside another project

Option A — copy layout once:

```bash
mkdir -p my-app/docs/memory/{snapshots,archive,mining,telemetry}
cp -n /path/to/alexs-rig/docs/memory/*.jsonl my-app/docs/memory/ 2>/dev/null || true
touch my-app/docs/memory/{PRINCIPLES,PROGRESS,PENDING}.jsonl
```

Option B — run CLIs with cwd = your project (they look for `docs/memory` under cwd via regen paths in `_memory.py` which is currently **repo-rooted**).

**v0 note:** current CLIs are rooted at the alexs-rig checkout (`bin/_memory.py` → `ROOT = parents[1]`). For multi-project use either:

1. Keep memory **in this repo** while prototyping, or  
2. Ask an agent (see `prompts/AGENT_ITERATE.md`) to add `--root` / `ALEXS_RIG_MEMORY` support so CLIs target any project’s `docs/memory/`.

## Commands

| Command | Purpose |
|---------|---------|
| `python3 bin/principle-upsert --id P-… --text "…"` | Add/update standing principle |
| `python3 bin/principle-forget --id P-…` | Archive principle (leaves L0) |
| `python3 bin/progress-upsert --id F-… --status active --summary "…"` | Feature standing |
| `python3 bin/pending-upsert upsert --id T-… --priority P1 --text "…"` | Park a todo |
| `python3 bin/pending-upsert done --id T-…` | Complete todo |
| `python3 bin/l0-regen` | Regenerate `docs/memory/snapshots/L0.md` |
| `python3 bin/mine-corrections --strong-only` | Mine Cursor transcripts → candidates |
| `python3 hooks/inject_l0.py` | Emit SessionStart JSON with L0 (Claude hook) |

## Claude Code plugin (proto)

Plugin manifests live in `.claude-plugin/plugin.json` with hooks in `hooks/hooks.json`.

Local install (Claude Code) typically:

```bash
# Example — adjust to your Claude plugin local path
claude plugin install --file .   # if supported by your Claude version
# or symlink this repo under your Claude plugins local directory
```

Skills: `skills/alex-memory`, `skills/alex-mine-corrections`.

## IDE extensions

See [extensions.md](extensions.md). Minimum for uncommitted review: built-in SCM + **Git Tree Compare**.

## Correction mining

```bash
python3 bin/mine-corrections --strong-only
# optional filter:
python3 bin/mine-corrections --strong-only --workspace AI-Rig
```

Reads `~/.cursor/projects/*/agent-transcripts/**/*.jsonl` (skips subagents).  
Writes:

- `docs/memory/mining/corrections.jsonl`
- `docs/memory/mining/patterns.md`
- `docs/memory/mining/principle-candidates.md`

**Never** auto-apply candidates — human or agent must call `principle-upsert` after review.

## Tests

```bash
python3 -m unittest tests.test_memory -v
```

## Agent iteration

Use [../prompts/AGENT_ITERATE.md](../prompts/AGENT_ITERATE.md).
