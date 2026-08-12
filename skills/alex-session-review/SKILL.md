---
name: alex-session-review
description: Review uncommitted changes since SessionStart (SESSION_BASE) or via IDE SCM. Use after agent edits before commit. Not a DiffEditor — points at native surfaces.
---

# Alex session review (thin)

Architecture lock: Desktop **`+N -M`** is the primary session map. This skill is the IDE/CLI companion.

## Desktop (preferred while coding)

Click the **`+N -M`** chip (or **Cmd+Shift+D**) after edits.

## CLI / IDE

```bash
# Since SessionStart (written by inject_l0.py):
python3 /path/to/alexs-rig/bin/session-diff --stat
python3 /path/to/alexs-rig/bin/session-diff

# Or full working tree:
git status
git diff
```

Then open **SCM** or **Git Tree Compare** for side-by-side / Open File.

## Not this skill

- PR review → `alex-pr-review` / `gh pr checkout`
- Standing memory → `alex-memory`
- Building a custom DiffEditor → **forbidden**
