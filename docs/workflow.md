# Workflow (proto)

## Surfaces

| Job | Where |
|-----|--------|
| Plan + code with agent | Claude Code **Desktop** (preferred) or VS Code Claude (compatible) |
| Session diffs | Desktop **`+N -M`** / Cmd+Shift+D |
| Uncommitted review | VS Code/Cursor **SCM** + **Git Tree Compare** |
| PRs | `gh pr checkout` + GitHub Pull Requests extension |
| Standing state | `docs/memory/snapshots/L0.md` |

## Permissions

- **Plan** for non-trivial work  
- **Edit automatically** while coding (not Manual stop-on-each-edit)  
- Agent may **commit when you ask**

## Memory commands

```bash
./bin/principle-upsert --id P-1 --text "…"
./bin/principle-forget --id P-1
./bin/progress-upsert --id F-1 --status active --summary "…"
./bin/pending-upsert upsert --id T-1 --priority P1 --text "…"
./bin/pending-upsert done --id T-1
./bin/l0-regen
./bin/mine-corrections --workspace AI-Rig
```

Accept principles only from `docs/memory/mining/principle-candidates.md` after human review.
