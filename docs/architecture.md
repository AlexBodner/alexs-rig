# Architecture — **LOCKED** (2026-08-12)

Frozen by human decision after OSS review bar: thorough code review happens anyway; Desktop `+N -M` is the session map, not a substitute for reading the full change.

## Locked product shape

| Topic | Decision |
|-------|----------|
| North star | Daily UX first — tomorrow-morning test |
| Agent host | Claude Code **Desktop** preferred; **VS Code Claude** compatible |
| IDE | SCM + Git Tree Compare for uncommitted; `gh pr checkout` + Diff/Open File for PRs |
| Session review | Desktop **`+N -M`** / Cmd+Shift+D (batch). No custom DiffEditor |
| Permissions | Plan upfront → **Edit automatically**; not Manual stop-per-edit |
| Commits | Agent when asked; no silent auto-PR |
| Memory | Generated L0 only; upsert by id; overflow = warn, never silent truncate |
| Multi-project | `--root` / `ALEXS_RIG_MEMORY` |
| Mining | Candidates only; default all Cursor workspaces; `--workspace` / `--since` optional |
| AI-Rig | Stock or user-modified; Rig does not fork it |
| Structure | Thin on-demand skill — no always-on graph |

## Layers

```text
YOU (OSS: read the real diff / files before ship)
  Desktop: Plan → acceptEdits → +N -M map
  IDE: SCM / Git Tree Compare / PR checkout
       │
       ▼
Alex's Rig — L0 + upserts + mining candidates + SessionStart/PreCompact + hygiene
       │
       ▼
Borda AI-Rig — how to build
```

## Non-goals (still)

Custom DiffEditor, Beads day one, fork AI-Rig, OpenClaw-scale bootstrap, auto-upsert mining, always-on knowledge graph.

## Evolution after lock

Improve via PRs following `prompts/AGENT_ITERATE.md` / `AGENT_SIMULATE_USAGE.md` **without** changing the table above unless you explicitly re-open architecture.
