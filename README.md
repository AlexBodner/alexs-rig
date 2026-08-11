# Alex's Rig — prototype

Throwaway prototype for review. Living plan: `~/Projects/AI-Rig/.plans/active/`.  
**Start here for review:** [REVIEW.md](REVIEW.md)

## Includes

1. **L0 memory** — `docs/memory/*.jsonl` + upsert CLIs + generated `snapshots/L0.md`
2. **Correction mining** — `bin/mine-corrections` over Cursor `agent-transcripts` (no auto-upsert)
3. **Claude plugin stub** — SessionStart L0 inject + skills
4. **Bootstrap / extensions** — uncommitted + PR review toolchain hints
5. **Tests** — `python3 -m unittest tests.test_memory -v`

## Quick start

```bash
cd ~/Projects/alexs-rig-proto
python3 -m unittest tests.test_memory -v
python3 bin/l0-regen
python3 bin/mine-corrections --strong-only
open docs/memory/snapshots/L0.md
```

Install IDE extensions: see [docs/extensions.md](docs/extensions.md).  
Daily loop: [docs/workflow.md](docs/workflow.md).

## Daily loop (target)

```text
Desktop: Plan → Edit automatically → +N -M → ask agent to commit when ready
IDE:     SCM / Git Tree Compare (uncommitted) · gh pr checkout (PRs)
```
