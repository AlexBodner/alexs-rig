# Alex's Rig

Personal AI coding harness for **Claude Code** (Desktop / VS Code / CLI) with a thin **Cursor**-friendly layer: standing memory (L0), surgical upserts, correction mining from chat history, an always-on codebase graph habit (understand-anything + codemap-py), and a daily loop built around **batch review** (not stop-on-every-edit).

**Status:** v0.1.5 — **architecture locked**; Review UI installed as a vsix (folder copy is not enough).

**Start here:** [docs/HOW-TO.md](docs/HOW-TO.md) — how it works, what is automatic, how to use it, how to get the most out of it.

## Who this is for

- You use Claude Code daily and want **standing project memory** that stays small.
- You want **Plan → Edit automatically → review diffs in batch** (`+N -M` on Desktop / SCM in the IDE).
- You want agents to **improve the harness itself** from clear instructions + an agent prompt.

## Quick start (humans)

`code` or `cursor` must be on PATH (or in the usual app locations). Review is a **vsix**; a folder copy is ignored.

```bash
git clone https://github.com/AlexBodner/alexs-rig.git
cd alexs-rig
./scripts/install.sh
```

If that command **exits 1**, Source Control → Review is not registered — put `code`/`cursor` on PATH and re-run `./scripts/install_review_extension.sh`. On success, **Reload Window once** (not every session). Open this clone as the workspace folder.

```bash
test -f "$PWD/docs/memory/snapshots/L0.md" && open "$PWD/docs/memory/snapshots/L0.md"  # macOS; or: cursor "$PWD/..."
```

Then keep **one** personal standing memory (the CLIs default to global `~/.alexs-rig/memory`):

```bash
# Standing memory (no --root needed → global ~/.alexs-rig/memory)
python3 /path/to/alexs-rig/bin/principle-upsert --id P-1 --text "Prefer batch review over per-edit stops"
python3 /path/to/alexs-rig/bin/pending-upsert upsert --id T-1 --priority P1 --text "Ship feature X"
python3 /path/to/alexs-rig/bin/progress-upsert --id F-1 --status active --summary "…" --path .
python3 /path/to/alexs-rig/bin/l0-regen
python3 /path/to/alexs-rig/bin/l0-show
```

Standing memory should live in **one** place — global `~/.alexs-rig/memory`, or a private
memory repo pointed to by `ALEXS_RIG_MEMORY` — **not** committed into each project. The
`docs/memory/` in this repo is an **example/template**; project-local memory need not be
committed. See [docs/usage.md](docs/usage.md).

## Daily loop

Canonical copy lives in [docs/workflow.md](docs/workflow.md) (section **Daily loop**). How it works / automatic vs you: [docs/HOW-TO.md](docs/HOW-TO.md). Short form:

```text
1. Open the clone folder as the workspace (not a parent like /workspace)
2. Dismiss first-run sign-in / auto-opened chat if they steal the first screen
3. Skim L0 via absolute path under the clone
4. Plan once → Edit automatically → batch review (+N -M / Source Control → Review)
5. Upsert pending/progress → l0-regen
6. Commit when you ask; PRs via gh pr checkout + IDE
```

Details: [docs/workflow.md](docs/workflow.md) · Extensions: [docs/extensions.md](docs/extensions.md) · Practices: [docs/practices.md](docs/practices.md)

## For agents (Grok / Composer / Claude)

Ready to delegate. One-liners live in [prompts/README.md](prompts/README.md).

**Try it like a human (default):** paste [prompts/AGENT_TRY.md](prompts/AGENT_TRY.md) — dogfood the daily loop; report friction; do not start the backlog.

**Own computer + GUI:** paste [prompts/AGENT_COMPUTER.md](prompts/AGENT_COMPUTER.md) — clone, `./scripts/install.sh`, Review Viewed, SessionStart if signed in.

**Box scoreboard (CLI):** paste [prompts/AGENT_BOX_VERIFY.md](prompts/AGENT_BOX_VERIFY.md) — B1–B17 PASS/FAIL.

**Simulate proper usage (multi-PR):** paste [prompts/AGENT_SIMULATE_USAGE.md](prompts/AGENT_SIMULATE_USAGE.md) — remaining polish PRs + Rig rituals.

**Improve the harness:** paste [prompts/AGENT_ITERATE.md](prompts/AGENT_ITERATE.md) after a try-out pass.

## What's included

| Piece | Path |
|-------|------|
| L0 + upserts + distill + show | `bin/l0-*`, `*-upsert`, `distill` |
| Session diff since SessionStart | `bin/session-diff` |
| Incremental review (per-file Viewed) | Source Control → Review (session or PR); CLI fallback `bin/review-mark` / `bin/review-pending` |
| Global / multi-project root | global `~/.alexs-rig/memory`, `--root`, `ALEXS_RIG_MEMORY` |
| Mining | `bin/mine-corrections` |
| Graph status (SessionStart pointer) | `bin/graph-status`, `rules/knowledge-graph.md` + `.mdc` |
| Portable agent instructions | `AGENTS.md`, `CLAUDE.md` |
| How to use (humans) | [docs/HOW-TO.md](docs/HOW-TO.md) |
| Claude + Cursor hooks | `hooks/hooks.json`, `hooks/cursor-hooks.json`, [docs/hooks.md](docs/hooks.md) |
| Skills + slash commands | `skills/alex-*`, `commands/alex-*.md` |
| Bootstrap / install | `scripts/install.sh` (or `bootstrap.sh` + `install_cursor_plugin.sh` / `install_claude_plugin.sh`) |
| Integration proof | [docs/INTEGRATION.md](docs/INTEGRATION.md) |

## Design rules (non-negotiable)

- **UX first** — tomorrow-morning test; no opaque cleverness.
- **L0 stays small** — generated snapshot only; overflow = distill/misuse fix, not silent truncate.
- **Integrate before invent** — Desktop `+N -M`, Review Viewed (session + PR), Git Tree Compare before building a custom DiffEditor.
- **AI-Rig** (Borda) for how-to-build skills — stock or user-modified; this harness does not fork them.
- **Mining auto-upserts named clusters** into L0; skips `other` and duplicates. `--no-apply` for candidates-only.
- **Query the standing graph first** — understand-anything + codemap-py; never dump graph JSON into L0. See [docs/knowledge-graph.md](docs/knowledge-graph.md).

## License

MIT — see [LICENSE](LICENSE).
