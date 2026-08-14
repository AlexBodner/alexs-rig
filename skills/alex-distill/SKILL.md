---
name: alex-distill
description: Shrink L0 when it overflows its token budget — list the largest principles/pending entries and forget or close them at the source. Never silent-truncate. Use when l0-regen reports OVERFLOW or L0 feels bloated.
---

# Alex distill (L0 overflow)

L0 overflow means **distill or forget at the source** — never a bigger dump and never a
silent truncation. L0 is always-on context, so keep it small.

```bash
python3 bin/distill                       # list the largest L0 contributors
python3 bin/principle-forget --id P-…     # drop a stale/duplicate principle
python3 bin/pending-upsert done --id T-…  # close a finished todo
python3 bin/l0-regen                      # rebuild the snapshot
```

Prefer removing what's no longer true over shortening what still matters.
