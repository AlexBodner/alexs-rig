---
name: alex-pr-review
description: Review a GitHub PR in the same Source Control Review list as session files (Viewed checkbox). Checkout first. Comments/merge stay on GitHub.
---

# Alex PR review

Same file list as session review. Do not use the GitHub Pull Requests extension for Viewed.

```bash
gh pr checkout <n>
```

Then **Source Control → Review**. Toolbar **pull request** (default on a PR branch). Click file → native diff. Check Viewed.

| Goal | Do |
|------|----|
| Left = PR base, right = worktree (incl. local edits) | Review view, PR mode |
| Only this session’s delta | Review view, session mode |
| Real file navigation | Open File after the diff |
| Comments / approve / merge | GitHub website, or optional GitHub Pull Requests extension |

Agent may `gh pr create` / commit **only when the user asks** — no silent auto-PR.
