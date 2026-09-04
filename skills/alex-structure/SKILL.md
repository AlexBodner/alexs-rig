---
name: alex-structure
description: Always-on codebase map. Use for architecture, where a concern lives, blast radius, or module relationships. Prefers understand-anything + codemap-py; grep is fallback.
---

# Alex structure (always-on graph)

Standing graphs live in the **project**, not in L0.

## 1. Status

```bash
python3 bin/graph-status
```

## 2. Query (do not dump JSON)

| Graph | When | How |
|-------|------|-----|
| understand-anything | architecture, components, tours | `/understand-chat`, `/understand-explain`, `/understand-dashboard` |
| codemap-py | Python callers, deps, test impact | `/codemap-py:query-code` |
| neither | first time in this repo | `/understand --auto-update` and/or `/codemap-py:scan-codebase` |

## 3. Fallback

README + `docs/` + targeted Grep only after the graph/index miss.

## Out of scope

L0 memory (`alex-memory`). Diffs (
