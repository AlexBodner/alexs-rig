---
name: alex-memory
description: Surgical updates to Alex's Rig L0 memory (principles, progress, pending). Use when parking todos, updating feature standing, or recording a standing principle after a correction.
---

# Alex memory (proto)

Do **not** read/rewrite whole memory files by hand. Use project CLIs from repo root:

```bash
python3 bin/principle-upsert --id P-… --text "…"
python3 bin/principle-forget --id P-…
python3 bin/progress-upsert --id F-… --status active --summary "…"
python3 bin/pending-upsert upsert --id T-… --priority P1 --text "…"
python3 bin/pending-upsert done --id T-…
python3 bin/l0-regen
```

After upserts, skim `docs/memory/snapshots/L0.md` (generated). Active beliefs only — never treat `archive/` as current.

For mining Cursor corrections into candidates (human accept only):

```bash
python3 bin/mine-corrections --strong-only
# then review docs/memory/mining/principle-candidates.md
```
