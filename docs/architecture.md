# Architecture (v0.1)

## Goals

Standing memory + review habit for Claude Code daily work, without rebuilding DiffEditors or forking Borda AI-Rig.

## Layers

```text
YOU
  Desktop (Plan + acceptEdits + +N -M)  ·  IDE (SCM / PR / extensions)
       │
       ▼
Alex's Rig
  L0 snapshot (generated) ← PRINCIPLES / PROGRESS / PENDING jsonl
  Upsert CLIs (--root / ALEXS_RIG_MEMORY)
  mine-corrections → candidates → human accept
  Claude hooks: SessionStart L0+SESSION_BASE · PreCompact reinject · Bash secret-hygiene
  Skills: alex-memory · alex-mine-corrections · alex-structure · alex-pr-review
       │
       ▼
Borda AI-Rig skills (stock or user-modified) — how to build
```

## L0 contract

- File: `docs/memory/snapshots/L0.md` — **generated only**
- Budget start: ~1200 tokens (chars/4); on overflow append banner — do not silent-truncate
- Contents: active principles + progress index + pending top-5
- Writes: upsert/forget CLIs only
- Multi-project: `--root` or `ALEXS_RIG_MEMORY`

## Hosts

| Host | Role |
|------|------|
| Claude Code Desktop | Preferred agent loop |
| Claude Code VS Code | Compatible (same plugin/skills) |
| VS Code / Cursor IDE | Uncommitted + PR review surfaces |
| CLI | Optional automation |

## Review ladder (locked)

1. Desktop `+N -M`  
2. SCM + Git Tree Compare  
3. Spike Claude Diff & Edit  
4. Only then thin Rig session-review skill/view  

## Non-goals (v0)

- Custom DiffEditor / second `/diff` product  
- Auto-upsert from mining  
- Silent auto-PR  
- Replacing AI-Rig  
- Always-on knowledge graph (structure skill is thin/on-demand)  

## Human gate

Architecture freeze waits on [desktop-lock.md](desktop-lock.md) (E1 + live SessionStart). Until then: usable v0.1 proto, not frozen product.
