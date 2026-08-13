# Recommended IDE extensions (proto)

**Viewed for session and PR is one extension.** You do not need the GitHub Pull Requests extension to mark files reviewed.

| Extension | ID | Why |
|-----------|-----|-----|
| **Alex's Rig Review** | local `extensions/alexs-rig-review` | One Viewed list: this session **or** the current PR |
| Git Tree Compare | `letmaik.git-tree-compare` | Optional extra branch diffs |
| GitHub Pull Requests | `github.vscode-pull-request-github` | **Optional** — review comments / merge only |
| Claude Diff & Edit | `dfarkash.claude-edits-scm` | Spike: Claude session changed-files sidebar |

```bash
./scripts/install_review_extension.sh   # Review UI; then Reload Window
cursor --install-extension letmaik.git-tree-compare
# optional: cursor --install-extension github.vscode-pull-request-github
# or: code --install-extension …
```

`./scripts/install.sh` runs bootstrap, copies the Review UI, and installs Cursor/Claude plugins. `install_cursor_plugin.sh` / `install_claude_plugin.sh` also run `install_review_extension.sh`.

Dogfood results → fill [spike-checklist.md](spike-checklist.md) and [desktop-lock.md](desktop-lock.md).
