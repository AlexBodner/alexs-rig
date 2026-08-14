# PRINCIPLES

Generated view — prefer upsert CLIs for edits.

- **P-ux**: Daily UX first — tomorrow-morning test; plain standing files; invisible complexity under CLIs
- **P-review**: Prefer batch review (Desktop +N -M / IDE SCM) over stop-on-every-edit; Edit automatically after Plan
- **P-hosts**: Desktop preferred for agent loop; harness compatible with VS Code Claude; IDE for uncommitted and PR review
- **P-commit**: Agent may commit when asked; no silent auto-PR
- **P-memory**: L0 is a generated snapshot of active principles/progress/pending only; upsert by id; never mix SUPERSEDED into L0
- **P-airig**: Borda AI-Rig skills (stock or modified) for how-to-build; Alex's Rig owns memory and supervision habit only
- **P-demo**: Prefer batch review over per-edit stops
- **P-arch-lock**: Architecture locked 2026-08-12: +N -M is session map; OSS bar = full code/PR review; no custom DiffEditor; do not reopen hosts/L0/mining/commit rules without explicit ask
- **P-mining**: Mine Cursor conversations for corrections; auto-upsert named-cluster templates; skip other; --no-apply for candidates-only
- **P-graph**: Query standing understand-anything / codemap-py graphs before blind Grep; never dump graph JSON into L0 or chat
- **P-scope**: Do exactly what's asked with the simplest, most generalizable solution. Don't add scope, abstractions, or options that weren't requested; if something can be shorter without changing behavior, prefer that.
- **P-verify**: Verify against the real source (implementation, paper, docs) before asserting a fact or claiming done. Don't guess or invent.
- **P-confirm**: Ask for explicit confirmation before heavy or outward-facing git actions (opening PRs, pushing, merging) and before any change that alters results/behavior. Read-only and additive work proceeds without asking.
- **P-branch**: Never commit straight to develop/main. Cut a fresh branch from main, land via PR, and don't open the PR unless asked.
- **P-additive**: Prefer additive, surgical changes. Don't move, rename, or restructure existing code or params to accomplish a task; add alongside and flag if a rename seems needed.
- **P-loud**: No silent failures. If a required input is missing or an assumption breaks, raise a clear error instead of degrading silently or guessing a default.
- **P-honest**: Report honestly — no false precision (e.g. spurious decimal places) and no claiming verified/done without evidence.
- **P-finish**: Work through the agreed plan without stopping for trivial confirmations, but still gate the heavy or irreversible steps under P-confirm.
