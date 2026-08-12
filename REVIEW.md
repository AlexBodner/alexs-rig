# REVIEW — Alex's Rig **0.1.0** (architecture locked)

**Repo:** https://github.com/AlexBodner/alexs-rig  
**Status:** Architecture **locked** 2026-08-12  
**Rationale:** Open-source bar = full code review anyway; Desktop `+N -M` is session change map + IDE/PR for ship. No custom DiffEditor.

## Locked

See [docs/architecture.md](docs/architecture.md).

## Plan build list

All items from the locked plan’s “what we still build” are implemented (memory, hooks, mining, hygiene, structure/PR skills, bootstrap, CI). See prior table in git history if needed.

## Dogfood leftovers (optional polish, not architecture)

- Live SessionStart once on your machine (`./scripts/install_claude_plugin.sh`) if not already
- Mining candidate accept/reject (recommended: reject duplicates of seeded principles)
- Optional Claude Diff & Edit spike for IDE session sidebar convenience

## Non-goals

Custom DiffEditor, Beads, fork AI-Rig, always-on graph, auto-upsert mining.
