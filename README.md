# Alex's Rig

Personal AI coding harness for **Claude Code** (Desktop / VS Code / CLI) with a thin **Cursor**-friendly layer: standing memory (L0), surgical upserts, correction mining from chat history, and a daily loop built around **batch review** (not stop-on-every-edit).

**Status:** v0 public prototype — usable, still evolving. Designed so a human *or* an agent (e.g. Grok / Composer) can follow the docs and iterate.

## Who this is for

- You use Claude Code daily and want **standing project memory** that stays small.
- You want **Plan → Edit automatically → review diffs in batch** (`+N -M` on Desktop / SCM in the IDE).
- You want agents to **improve the harness itself** from clear instructions + an agent prompt.

## Quick start (humans)

```bash
git clone https://github.com/YOUR_USER/alexs-rig.git   # after publish
cd alexs-rig
python3 -m unittest tests.test_memory -v
./scripts/bootstrap.sh
```

Then in **your project** (or this repo while dogfooding):

```bash
# Standing memory
python3 /path/to/alexs-rig/bin/principle-upsert --id P-1 --text "Prefer batch review over per-edit stops"
python3 /path/to/alexs-rig/bin/pending-upsert upsert --id T-1 --priority P1 --text "Ship feature X"
python3 /path/to/alexs-rig/bin/l0-regen
open docs/memory/snapshots/L0.md   # if using in-repo memory layout
```

Copy the `docs/memory/` layout into each project you want remembered (or symlink / set `ALEXS_RIG_ROOT` — see [docs/usage.md](docs/usage.md)).

## Daily loop

```text
1. Open Claude Code Desktop (preferred) or VS Code Claude
2. Plan mode for non-trivial work → approve plan once
3. Edit automatically (acceptEdits) — do not use Manual stop-on-each-edit as default
4. Review: Desktop click +N -M (or Cmd+Shift+D) · IDE: SCM / Git Tree Compare
5. Park todos / update progress with bin/*-upsert → L0 regenerates
6. Commit when you ask the agent (no silent auto-PR)
7. PRs: gh pr checkout → review in IDE (GitHub Pull Requests extension OK)
```

Details: [docs/workflow.md](docs/workflow.md) · Extensions: [docs/extensions.md](docs/extensions.md)

## For agents (Grok / Composer / Claude)

1. Read [docs/usage.md](docs/usage.md) and [docs/architecture.md](docs/architecture.md).  
2. Paste the prompt in [prompts/AGENT_ITERATE.md](prompts/AGENT_ITERATE.md) into a new agent session.  
3. Run tests before claiming done: `python3 -m unittest tests.test_memory -v`

## What's included

| Piece | Path |
|-------|------|
| L0 memory engine | `bin/_memory.py`, `bin/*-upsert`, `bin/l0-regen` |
| Correction mining (Cursor transcripts) | `bin/mine-corrections` |
| Claude Code plugin stub + SessionStart L0 inject | `.claude-plugin/`, `hooks/` |
| Skills | `skills/alex-memory/`, `skills/alex-mine-corrections/` |
| Tests | `tests/test_memory.py` |

## Design rules (non-negotiable)

- **UX first** — tomorrow-morning test; no opaque cleverness.
- **L0 stays small** — generated snapshot only; overflow = distill/misuse fix, not silent truncate.
- **Integrate before invent** — Desktop `+N -M`, SCM, Git Tree Compare, PR extension before building a custom DiffEditor.
- **AI-Rig** (Borda) for how-to-build skills — stock or user-modified; this harness does not fork them.
- **Mining never auto-upserts** principles without human accept.

## License

MIT — see [LICENSE](LICENSE).
