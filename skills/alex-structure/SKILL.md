---
name: alex-structure
description: Thin structure Q&A for a codebase without always-on knowledge graphs. Use when the user asks how the project is organized, where a concern lives, or for a map of modules.
---

# Alex structure (thin)

**Do not** start understand-anything or build a standing graph unless the user asks.

## Default path (fast)

1. Read `README.md`, then top-level dirs.
2. Prefer existing maps: `docs/`, `ARCHITECTURE*`, `AGENTS.md`, `CLAUDE.md`.
3. For Python: `rg --files -g '*.py' | head` then open package `__init__` / main entrypoints.
4. Answer with a short tree + “where to change X” — not a novel.

## Optional deeper tools (on demand)

- If **codemap-py** / query-code is installed: use it for call/test impact.
- If an MCP knowledge graph is already configured for this repo: query it once; do not enable always-on.
- Otherwise stay on ripgrep + README.

## Out of scope

Standing L0 memory (use `alex-memory`). Diff review (Desktop `+N -M` / SCM). Mining corrections (`alex-mine-corrections`).
