---
name: alex-pr-review
description: Open a GitHub PR for proper IDE review (checkout → Diff / Open File). Use when reviewing a pull request, not for uncommitted session diffs.
---

# Alex PR review

Happy path (avoid weak PR-sidebar-only diffs):

```bash
gh pr checkout <n>
# then in VS Code / Cursor:
#   - Source Control or Git Tree Compare vs main
#   - Open Diff for change-focused view
#   - Open File for real source (F12, full-file context)
```

| Goal | Do |
|------|-----|
| Left = base, right = changed | Checkout first → Open Diff (`diffEditor.renderSideBySide: true`) |
| Real file navigation | After checkout → **Open File** (not only the virtual PR tab) |
| Skip extension UI | `gh pr checkout` + SCM / Git Tree Compare |
| Comments / merge | GitHub Pull Requests extension **after** checkout |

**Not for:** uncommitted session review → Desktop **`+N -M`** or IDE SCM (no PR required).

Agent may `gh pr create` / commit **only when the user asks** — no silent auto-PR.
