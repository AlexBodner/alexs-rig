---
name: alex-mine-corrections
description: Scan local Cursor agent-transcripts for user corrections and propose principle candidates. Never auto-upsert into L0.
---

# Mine corrections (proto)

1. From the alexs-rig-proto (or project) root:

```bash
python3 bin/mine-corrections --strong-only
# optional: --workspace AI-Rig
```

2. Open `docs/memory/mining/principle-candidates.md` and `patterns.md`.
3. For each accepted candidate, run `principle-upsert` with a stable id.
4. Run `l0-regen`. Do **not** write principles without human accept.

Privacy: local-only; outputs may be gitignored under mining jsonl if sensitive.
