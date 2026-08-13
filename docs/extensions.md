# Recommended IDE extensions (proto)

**Viewed for session and PR is one extension.** You do not need the GitHub Pull Requests extension to mark files reviewed.

A **folder copy into `~/.vscode/extensions` does not register**. Install the vsix:

```bash
./scripts/install_review_extension.sh
# packs extensions/alexs-rig-review/*.vsix and runs:
#   cursor --install-extension <vsix> --force
#   code --install-extension <vsix> --force
```

Then **Reload Window once**. Source Control → Review.

| Extension | ID | Why |
|-----------|-----|-----|
| **Alex's Rig Review** | vsix from `extensions/alexs-rig-review` | One Viewed list: this session **or** the current PR |
| Git Tree Compare | `letmaik.git-tree-compare` | Optional extra branch diffs |
| GitHub Pull Requests | `github.vscode-pull-request-github` | **Optional** — review comments / merge only |

`./scripts/install.sh` ends on the vsix install. If `code`/`cursor` are not on PATH, it prints the exact `--install-extension` command and exits 1.

Dogfood results → fill [spike-checklist.md](spike-checklist.md) and [desktop-lock.md](desktop-lock.md).
