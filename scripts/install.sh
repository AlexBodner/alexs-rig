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
review_ok=1
"$ROOT/scripts/install_review_extension.sh" || review_ok=0

if [[ "$review_ok" -eq 1 ]]; then
  echo "Reload Window once. Open this folder as the workspace (not a parent)."
  echo "Source Control → Review  |  HOW-TO: $ROOT/docs/HOW-TO.md"
else
  echo
  echo "NOTE: the Review UI (Source Control → Review) is OPTIONAL and was not installed." >&2
  echo "Everything else (memory, hooks, skills) is ready to use without it." >&2
  echo "Add it later, any time, with: ./scripts/install_review_extension.sh" >&2
  echo "(needs the code or cursor CLI on PATH)." >&2
fi
exit 0
