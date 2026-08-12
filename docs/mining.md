# Correction mining

## Scope (v0.1.1+)

| Choice | Decision |
|--------|----------|
| Default scan | **All** Cursor workspaces under `~/.cursor/projects/*/agent-transcripts/` |
| Narrowing | Optional `--workspace <substring>` (e.g. `AI-Rig`) |
| Auto-apply | **On by default** for named clusters (`review_batch`, `commit_git`, …) |
| Skip | `other` cluster (noise) unless `--apply-other` |
| Skip | Templates already covered by an existing L0 principle |
| Dry-run | `--no-apply` writes candidates only |

Why skip `other`: that bucket is mostly tracebacks and one-off task text, not standing rules.

## Commands

```bash
python3 bin/mine-corrections --strong-only              # mine + auto-upsert named clusters
python3 bin/mine-corrections --strong-only --no-apply   # candidates only
python3 bin/mine-corrections --strong-only --workspace AI-Rig
python3 bin/mine-corrections --strong-only --since 2026-08-01
python3 bin/mine-corrections --strong-only --root /path/to/project
python3 bin/mine-corrections --strong-only --apply-other   # include noisy cluster (rarely what you want)
```

`--root` / `ALEXS_RIG_MEMORY` = **memory** project.  
`--transcripts-root` = Cursor projects tree (default `~/.cursor/projects`).

Applied ids are stable: `P-mine-review_batch`, `P-mine-commit_git`, … Re-runs upsert the same id. Forget with `principle-forget --id P-mine-…`.

## Outputs

- `docs/memory/mining/corrections.jsonl`
- `docs/memory/mining/patterns.md`
- `docs/memory/mining/principle-candidates.md` (status: applied / skipped / dry-run)

Empty host → honest Status section; not a broken pipeline.
