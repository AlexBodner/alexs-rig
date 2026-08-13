#!/usr/bin/env bash
# One-shot install from this checkout: memory demo, Review UI, Cursor/Claude plugins.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
chmod +x "$ROOT"/scripts/*.sh "$ROOT"/bin/* 2>/dev/null || true

"$ROOT/scripts/bootstrap.sh" --yes
"$ROOT/scripts/install_review_extension.sh" || true

if [[ -d "${HOME}/.cursor" ]]; then
  "$ROOT/scripts/install_cursor_plugin.sh"
fi

if [[ -d "${HOME}/.claude" ]] || command -v claude >/dev/null 2>&1; then
  "$ROOT/scripts/install_claude_plugin.sh" || true
fi

echo
echo "Done. Reload Cursor and/or restart Claude Code."
echo "Open this folder as the workspace (not a parent)."
echo "Source Control → Review  |  HOW-TO: $ROOT/docs/HOW-TO.md"
