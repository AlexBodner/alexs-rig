#!/usr/bin/env bash
# One-shot install from this checkout: memory demo, Review vsix, Cursor/Claude plugins.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
chmod +x "$ROOT"/scripts/*.sh "$ROOT"/bin/* 2>/dev/null || true

"$ROOT/scripts/bootstrap.sh" --yes

if [[ -d "${HOME}/.cursor" ]]; then
  "$ROOT/scripts/install_cursor_plugin.sh"
fi

if [[ -d "${HOME}/.claude" ]] || command -v claude >/dev/null 2>&1; then
  "$ROOT/scripts/install_claude_plugin.sh" || true
fi

echo
if "$ROOT/scripts/install_review_extension.sh"; then
  echo "Done. Reload Window once. Open this folder as the workspace (not a parent)."
  echo "Source Control → Review  |  HOW-TO: $ROOT/docs/HOW-TO.md"
else
  echo "Plugins/memory may be in place, but Source Control → Review will NOT appear" >&2
  echo "until the vsix is registered (folder copy is ignored)." >&2
  exit 1
fi
