# Workflow

## Daily loop

Named loop — do this in order; surfaces below are just where each step lives.

```text
1. Open the **repo folder** as the workspace (File → Open Folder → this clone), not a parent like /workspace.
2. Dismiss first-run noise (Copilot sign-in, auto-opened chat) so the editor is usable.
3. Skim standing state: open the absolute L0 path printed by bootstrap (or `$PWD/docs/memory/snapshots/L0.md` after `cd` into the clone). For architecture questions, query the standing graph first (`bin/graph-status` / `/understand-chat` / `/codemap-py:query-code`) — do not dump the JSON into L0.
4. Plan mode for non-trivial work → approve the plan once.
5. Edit automatically (acceptEdits) — not Manual stop-on-each-edit as the default.
6. Review in batch: Desktop **`+N -M`** / Cmd+Shift+D · IDE: SCM / Git Tree Compare.
7. Park todos / update progress with `bin/*-upsert` → `bin/l0-regen`.
8. Commit when you ask the agent (no silent auto-PR).
9. PRs: `gh pr checkout` → review in IDE (GitHub Pull Requests extension OK).
```

## Surfaces (where each job lives)

| Job | Where |
|-----|--------|
| Plan + code with agent | Claude Code **Desktop** (preferred) or VS Code Claude (compatible) |
| Session diffs | Desktop **`+N -M`** / Cmd+Shift+D |
| Uncommitted review | VS Code/Cursor **SCM** + **Git Tree Compare** |
| PRs | `gh pr checkout` + GitHub Pull Requests extension |
| Standing state | `$PWD/docs/memory/snapshots/L0.md` **from the clone root** (never open a relative path against a parent folder) |
| Codebase graph | understand-anything + codemap-py in the **target repo**; `bin/graph-status` |

## First open (avoid blank L0)

Wrong: workspace is `/workspace` (or `~/Projects`) and you open `docs/memory/snapshots/L0.md` → editor creates an **empty unsaved** file. Memory is not blank; the path missed the repo.

Right:

```bash
cd /path/to/alexs-rig          # the clone itself
test -f docs/memory/snapshots/L0.md || python3 bin/l0-regen
# Prefer an absolute path so the IDE cannot resolve against the wrong root:
open "$PWD/docs/memory/snapshots/L0.md"    # macOS
# or: code "$PWD/docs/memory/snapshots/L0.md"
# or: cursor "$PWD/docs/memory/snapshots/L0.md"
```

Bootstrap prints the same absolute path. Progress rows should use **relative** paths (e.g. `.`) or omit `--path` — never commit a machine-specific absolute home path.

## Permissions

- **Plan** for non-trivial work
- **Edit automatically** while coding (not Manual stop-on-each-edit)
- Agent may **commit when you ask**

## Memory commands

```bash
./bin/principle-upsert --id P-1 --text "…"
./bin/principle-forget --id P-1
./bin/progress-upsert --id F-1 --status active --summary "…" --path .
./bin/pending-upsert upsert --id T-1 --priority P1 --text "…"
./bin/pending-upsert done --id T-1
./bin/l0-regen
./bin/mine-corrections --workspace AI-Rig
```

Accept principles only from `docs/memory/mining/principle-candidates.md` after human review.
