# REVIEW — Alex's Rig prototype ready for your pass

**Path:** clone of https://github.com/AlexBodner/alexs-rig (local dir may vary)  
**Nature:** throwaway/proto — not architecture-frozen product  
**Plan:** AI-Rig `.plans/active/plan_alexs-rig-vscode-claude-code.md` (author machine)

## Verification (agent-run 2026-08-11)

All automated checks **passed**:

- `unittest` (3/3)
- L0 regen
- principle upsert → forget (removed from L0)
- pending upsert → done (archived, removed from L0)
- `mine-corrections --strong-only` (AI-Rig transcripts)
- SessionStart hook JSON + L0 context
- Overflow banner at low budget
- Bootstrap script smoke
- Plugin/hook JSON manifests

**Not verified here (needs your UI):** Desktop `+N -M` pane, VS Code extension installs, live Claude plugin SessionStart in Desktop app.

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
cd /path/to/alexs-rig   # the clone root, not its parent
python3 -m unittest tests.test_memory -v
python3 bin/l0-regen
python3 bin/mine-corrections --strong-only --workspace AI-Rig
open "$PWD/docs/memory/snapshots/L0.md"
open "$PWD/docs/memory/mining/principle-candidates.md"
```

Optional IDE: install extensions from `docs/extensions.md`, fill `docs/spike-checklist.md`.

## Locked decisions already reflected in seeded principles

See `docs/memory/PRINCIPLES.jsonl` / L0 — seeded from your accept table (not from noisy auto-mining). Mining candidates remain for you to accept/reject.

## Still for you (cannot automate)

1. Desktop dogfood: Plan → acceptEdits → **`+N -M`** (or Cmd+Shift+D) on this repo  
2. Live SessionStart: install/symlink local Claude plugin; confirm L0 lands in context  
3. Mining on your Mac (where Cursor transcripts live): `python3 bin/mine-corrections --strong-only` → skim candidates  
4. IDE: Claude Diff & Edit spike if desired  
5. Say **architecture locked** → graduate proto  

## Dogfood notes

Box VS Code pass (2026-08-11): unittest + bootstrap + upserts + inject_l0 + SCM/Git Tree Compare worked; Desktop `+N -M` and live SessionStart not verified on that host; empty mining on host without `~/.cursor` is expected. Friction follow-ups in-repo: absolute L0 open path, portable `F-proto` `--path .`, named Daily loop, bootstrap **runs** demo upserts, mining empty-host banner.

## Intentionally not built

Custom DiffEditor, second `/diff` engine, auto-upsert from mining, Beads, fat dashboard.
