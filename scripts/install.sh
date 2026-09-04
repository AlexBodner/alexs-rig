#!/usr/bin/env bash
# One-shot install from this checkout: personal memory, then the Claude Code and Cursor plugins.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
chmod +x "$ROOT"/scripts/*.sh "$ROOT"/bin/* "$ROOT"/hooks/*.py "$ROOT"/hooks/*.sh 2>/dev/null || true

"$ROOT/scripts/bootstrap.sh"

if [[ -d "${HOME}/.cursor" ]]; then
  "$ROOT/scripts/install_cursor_plugin.sh"
fi

if [[ -d "${HOME}/.claude" ]] || command -v claude >/dev/null 2>&1; then
  "$ROOT/scripts/install_claude_plugin.sh" || true
fi

echo
echo "Done. Start a new Claude Code session: standing memory arrives before your first prompt."
