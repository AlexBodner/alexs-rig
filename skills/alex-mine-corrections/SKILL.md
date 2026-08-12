---
name: alex-mine-corrections
description: Scan local Cursor agent-transcripts for user corrections and propose principle candidates. Never auto-upsert into L0.
---

# Mine corrections

```bash
python3 bin/mine-corrections --strong-only
python3 bin/mine-corrections --strong-only --workspace AI-Rig
python3 bin/mine-corrections --strong-only --since 2026-08-01
```

Open `docs/memory/mining/principle-candidates.md` + `patterns.md`.  
Accept with `principle-upsert` only after human say-so. Then `l0-regen`.

Slash: `/alex-mine-corrections`. Design: `docs/design-correction-mining.md`.
