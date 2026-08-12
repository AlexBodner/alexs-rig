# Correction mining

## Scope decision (MVP — locked for v0)

| Choice | Decision |
|--------|----------|
| Default scan | **All** Cursor workspaces under `~/.cursor/projects/*/agent-transcripts/` |
| Narrowing | Optional `--workspace <substring>` (e.g. `AI-Rig`) |
| Auto-apply | **Never** — write candidates only |
| Strength | Prefer `--strong-only` for human review |

Why all-workspaces default: corrections often span repos; filtering too early hides standing preferences. Use `--workspace` when dogfooding one project.

v1.1 (optional later): default to cwd-derived workspace slug if unambiguous; keep `--workspace` / all-mode flag.

## Commands

```bash
# Memory output root (where candidates are written):
python3 bin/mine-corrections --strong-only
python3 bin/mine-corrections --strong-only --workspace AI-Rig
python3 bin/mine-corrections --strong-only --root /path/to/project

# Transcripts live elsewhere (rare):
python3 bin/mine-corrections --strong-only --transcripts-root ~/.cursor/projects
```

`--root` / `ALEXS_RIG_MEMORY` = **memory** project (same as other CLIs).  
`--transcripts-root` = Cursor projects tree (default `~/.cursor/projects`).

## Outputs

- `docs/memory/mining/corrections.jsonl`
- `docs/memory/mining/patterns.md`
- `docs/memory/mining/principle-candidates.md`

Empty host → honest Status section; not a broken pipeline.

## Accept a candidate

```bash
python3 bin/principle-upsert --id P-… --text "…"
python3 bin/l0-regen
```
