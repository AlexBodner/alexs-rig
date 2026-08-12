# Alex's Rig

Personal AI coding harness for **Claude Code** (Desktop / VS Code / CLI) with a thin **Cursor**-friendly layer: standing memory (L0), surgical upserts, correction mining from chat history, and a daily loop built around **batch review** (not stop-on-every-edit).

**Status:** v0 public prototype — usable, still evolving. Designed so a human *or* an agent (e.g. Grok / Composer) can follow the docs and iterate.

## Who this is for

- You use Claude Code daily and want **standing project memory** that stays small.
- You want **Plan → Edit automatically → review diffs in batch** (`+N -M` on Desktop / SCM in the IDE).
- You want agents to **improve the harness itself** from clear instructions + an agent prompt.

## Quick start (humans)

```bash
git clone https://github.com/AlexBodner/alexs-rig.git
cd alexs-rig
python3 -m unittest tests.test_memory -v
./scripts/bootstrap.sh
# Open the clone as the workspace folder, then open the absolute L0 path bootstrap prints.
# Wrong workspace root + relative docs/memory/... → empty unsaved file (memory is not blank).
test -f "$PWD/docs/memory/snapshots/L0.md" && open "$PWD/docs/memory/snapshots/L0.md"  # macOS; or: code/cursor "$PWD/..."
```

Then in **your project** (or this repo while dogfooding):

```bash
# Standing memory
python3 /path/to/alexs-rig/bin/principle-upsert --id P-1 --text "Prefer batch review over per-edit stops"
python3 /path/to/alexs-rig/bin/pending-upsert upsert --id T-1 --priority P1 --text "Ship feature X"
python3 /path/to/alexs-rig/bin/progress-upsert --id F-1 --status active --summary "…" --path .
python3 /path/to/alexs-rig/bin/l0-regen
open "$PWD/docs/memory/snapshots/L0.md"   # absolute; only after cd into the memory-owning repo
```

Copy the `docs/memory/` layout into each project you want remembered (or symlink / set `ALEXS_RIG_ROOT` — see [docs/usage.md](docs/usage.md)).

## Daily loop

Canonical copy lives in [docs/workflow.md](docs/workflow.md) (section **Daily loop**). Short form:

```text
1. Open the clone folder as the workspace (not a parent like /workspace)
2. Dismiss Copilot sign-in / auto-opened chat if they steal the first screen
3. Skim L0 via absolute path under the clone
4. Plan once → Edit automatically → batch review (+N -M / SCM)
5. Upsert pending/progress → l0-regen
6. Commit when you ask; PRs via gh pr checkout + IDE
```

Details: [docs/workflow.md](docs/workflow.md) · Extensions: [docs/extensions.md](docs/extensions.md)

## For agents (Grok / Composer / Claude)

**Try it like a human (default):** paste [prompts/AGENT_TRY.md](prompts/AGENT_TRY.md) — dogfood the daily loop; report friction; do not start the backlog.

**Box scoreboard (agent’s own computer):** paste [prompts/AGENT_BOX_VERIFY.md](prompts/AGENT_BOX_VERIFY.md) — B1–B16 PASS/FAIL; includes fake Cursor transcripts so mining isn’t host-blocked.

**Simulate proper usage (multi-PR):** paste [prompts/AGENT_SIMULATE_USAGE.md](prompts/AGENT_SIMULATE_USAGE.md) — real feature PRs while forcing L0 / pending / batch review rituals.

**Improve the harness:** paste [prompts/AGENT_ITERATE.md](prompts/AGENT_ITERATE.md) after a try-out pass.

## What's included

| Piece | Path |
|-------|------|
| L0 memory engine | `bin/_memory.py`, `bin/*-upsert`, `bin/l0-regen`, `bin/l0-show` |
| Multi-project root | `--root` / `ALEXS_RIG_MEMORY` |
| Correction mining | `bin/mine-corrections` (`--strong-only`, `--since`, `--workspace`) |
| Claude hooks | SessionStart L0+SESSION_BASE, PreCompact reinject, Bash secret-hygiene |
| Skills | `alex-memory`, `alex-mine-corrections`, `alex-structure`, `alex-pr-review` |
| Tests + CI | `tests/test_memory.py`, `.github/workflows/test.yml` |

## Design rules (non-negotiable)

- **UX first** — tomorrow-morning test; no opaque cleverness.
- **L0 stays small** — generated snapshot only; overflow = distill/misuse fix, not silent truncate.
- **Integrate before invent** — Desktop `+N -M`, SCM, Git Tree Compare, PR extension before building a custom DiffEditor.
- **AI-Rig** (Borda) for how-to-build skills — stock or user-modified; this harness does not fork them.
- **Mining never auto-upserts** principles without human accept.

## License

MIT — see [LICENSE](LICENSE).
