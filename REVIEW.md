# REVIEW — Alex's Rig v0.1

**Repo:** https://github.com/AlexBodner/alexs-rig  
**Nature:** public proto — say **architecture locked** only after Desktop E1 + SessionStart  
**Plan:** AI-Rig `.plans/active/plan_alexs-rig-vscode-claude-code.md`

## Plan “what we still build” → status

| # | Item | Status |
|---|------|--------|
| 1 | Memory L0 + upsert/forget + md views | Done (`--root` / `ALEXS_RIG_MEMORY`) |
| 2 | SessionStart + post-compact inject | Done (`inject_l0.py`, `reinject_l0.py`) |
| 3 | Bootstrap + dual-host + IDE toolchain docs | Done (`bootstrap --yes`, extensions) |
| 4 | Uncommitted review (integrate first) | Done docs/bootstrap; E7 box-passed; Mac E1 pending |
| 5 | GitHub PR extension in bootstrap | Done |
| 6 | Thin secret-hygiene | Done (`secret_hygiene.py`, [hygiene.md](docs/hygiene.md)) |
| 7 | Thin structure-query skill | Done (`skills/alex-structure`) |
| 8 | Correction mining | Done (+ `--since`, [mining.md](docs/mining.md)) |
| 9 | Commit-when-asked docs | Done ([commit-when-asked.md](docs/commit-when-asked.md)) |
| — | SESSION_BASE on SessionStart | Done (`.alexs-rig/SESSION_BASE`) |
| — | PR checkout skill | Done (`skills/alex-pr-review`) |
| — | CI unittest | Done |

## Intentionally not built (plan non-goals)

Custom DiffEditor, Beads, fork AI-Rig, OpenClaw-scale bootstrap, always-on graph, auto-upsert mining.

## Still human-only

1. [docs/desktop-lock.md](docs/desktop-lock.md) — Plan → Edit → `+N -M`  
2. Live SessionStart after `./scripts/install_claude_plugin.sh`  
3. Accept/reject mining candidates (Mac run already produced `docs/memory/mining/principle-candidates.md`)  
4. Say **architecture locked** → graduate naming/version  

## Verify

```bash
python3 -m unittest tests.test_memory -v
./scripts/bootstrap.sh --help
python3 hooks/inject_l0.py | python3 -m json.tool | head
python3 bin/l0-show | head
```
