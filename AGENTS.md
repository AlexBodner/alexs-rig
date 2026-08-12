# Agent instructions — Alex's Rig

Portable agent file ([AGENTS.md](https://agents.md/)). Humans start at [README.md](README.md). Claude-only notes live in [CLAUDE.md](CLAUDE.md).

## What this is

A thin personal harness: standing L0 memory, batch review, correction mining, and a **pointer** to existing codebase graphs. It does not fork Borda AI-Rig and does not implement a second graph engine.

## Commands

```bash
python3 -m unittest tests.test_memory -v
python3 bin/l0-regen
python3 bin/l0-show
python3 bin/graph-status
python3 hooks/inject_l0.py
```

Memory CLIs take `--root` / `ALEXS_RIG_MEMORY`. Do not hand-edit `docs/memory/snapshots/L0.md`.

## Conventions

- Daily loop: Plan → Edit automatically → batch review (Desktop `+N -M` / IDE SCM). No custom DiffEditor.
- Commit only when the human asks. No silent auto-PR. Push only when they ask (this repo: `go` / `publish`).
- Query understand-anything / codemap-py **before** blind Grep for architecture. Never dump `knowledge-graph.json` into L0 or chat. See [docs/knowledge-graph.md](docs/knowledge-graph.md).
- Keep always-on text small. Details belong in skills (`skills/alex-*`) and [docs/](docs/).
- Python 3.10+; stdlib unittest. No new dependencies without evidence they are required.

## Architecture lock

Read [docs/architecture.md](docs/architecture.md) before reopening hosts, L0, mining, or review surfaces. Why these primitives: [docs/practices.md](docs/practices.md).
