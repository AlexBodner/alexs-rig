# REVIEW — Alex's Rig prototype ready for your pass

**Path:** `~/Projects/alexs-rig-proto`  
**Nature:** throwaway/proto — not architecture-frozen product  
**Plan:** `~/Projects/AI-Rig/.plans/active/plan_alexs-rig-vscode-claude-code.md`

## What was built

| Area | Status |
|------|--------|
| L0 memory (jsonl + upsert CLIs + generated `L0.md`) | Done |
| Overflow warning (no silent truncate) | Done |
| Archive on principle supersede / pending done | Done |
| Correction mining from Cursor transcripts | Done (`--strong-only` recommended) |
| Claude plugin stub + SessionStart L0 inject hook | Done (proto) |
| Skills: `alex-memory`, `alex-mine-corrections` | Done |
| Bootstrap + extension list | Done |
| Unit tests (`tests/test_memory.py`) | Done |
| Cursor `.cursor-plugin` stub | Done (docs/skills companion) |

## How to verify (10 min)

```bash
cd ~/Projects/alexs-rig-proto
python3 -m unittest tests.test_memory -v
python3 bin/l0-regen
python3 bin/mine-corrections --strong-only --workspace AI-Rig
open docs/memory/snapshots/L0.md
open docs/memory/mining/principle-candidates.md
```

Optional IDE: install extensions from `docs/extensions.md`, fill `docs/spike-checklist.md`.

## Locked decisions already reflected in seeded principles

See `docs/memory/PRINCIPLES.jsonl` / L0 — seeded from your accept table (not from noisy auto-mining). Mining candidates remain for you to accept/reject.

## Still for you (cannot automate)

1. Desktop dogfood: Plan → acceptEdits → **`+N -M`**  
2. IDE: Git Tree Compare + Claude Diff & Edit spike  
3. Mining scope: all workspaces vs project-only; MVP vs v1.1  
4. Say **architecture locked** → graduate proto → real `alexs-rig`  

## Intentionally not built

Custom DiffEditor, second `/diff` engine, auto-upsert from mining, Beads, fat dashboard.
