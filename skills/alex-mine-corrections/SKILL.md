---
name: alex-mine-corrections
description: Scan local Cursor agent-transcripts for user corrections and auto-upsert named-cluster principles into L0. Skips noisy `other`. Use --no-apply for candidates-only.
---

# Mine corrections

```bash
python3 bin/mine-corrections --strong-only
python3 bin/mine-corrections --strong-only --no-apply
python3 bin/mine-corrections --strong-only --workspace AI-Rig
python3 bin/mine-corrections --strong-only --since 2026-08-01
```

Named clusters (`review_batch`, `commit_git`, …) upsert as `P-mine-<cluster>` unless already covered in L0.  
`other` is skipped unless `--apply-other`.

Slash: `/alex-mine-corrections`. Design: `docs/mining.md`.
