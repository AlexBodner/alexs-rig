# Multi-agent (native first)

Architecture lock: prefer **native** worktrees + Claude agents — no custom session registry day one.

| Need | Do |
|------|-----|
| Parallel tasks | Claude Desktop **New session** / worktrees ([docs](https://code.claude.com/docs/en/worktrees)) |
| Isolate git | `git worktree add` or Desktop cloud/local isolation |
| Tell folders apart | One worktree/folder per session; rename tabs |
| Registry file | **Defer** — only if native mental model breaks |

Standing memory (L0) is **per project** via `--root` / `ALEXS_RIG_MEMORY`, not a global multi-agent dashboard.
