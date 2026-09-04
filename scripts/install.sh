#!/usr/bin/env bash
# One-shot install from this checkout: memory demo, Cursor/Claude plugins, and the
# (optional) Review vsix. Core setup always succeeds; the Review UI is a bonus step
# that only needs the code/cursor CLI and can be added later on its own.
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
echo "Core install done: memory + hooks + skills are ready to use."
echo
echo "Start a new session so the hooks load. Batch review from the CLI:"
echo "  python3 $ROOT/bin/review-pending --name-only"
exit 0
