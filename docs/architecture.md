# Architecture (v0)

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
  Upsert CLIs (surgical, by id)
  Optional: mine-corrections → candidates → human accept
  Claude hooks: SessionStart inject L0
       │
       ▼
Borda AI-Rig skills (stock or user-modified) — how to build
```

## L0 contract

- File: `docs/memory/snapshots/L0.md` — **generated only**
- Budget start: ~1200 tokens (chars/4); on overflow append banner — do not silent-truncate
- Contents: active principles + progress index + pending top-5
- Writes: upsert/forget CLIs only

## Hosts

| Host | Role |
|------|------|
| Claude Code Desktop | Preferred agent loop |
| Claude Code VS Code | Compatible (same plugin/skills) |
| VS Code / Cursor IDE | Uncommitted + PR review surfaces |
| CLI | `/diff` Per-Turn; automation |

## Non-goals (v0)

- Custom DiffEditor / second `/diff` product  
- Auto-upsert from mining  
- Silent auto-PR  
- Replacing AI-Rig  

## Evolution

Agents should improve the harness via PRs/commits following `prompts/AGENT_ITERATE.md`, keeping this architecture unless the user explicitly changes it.
