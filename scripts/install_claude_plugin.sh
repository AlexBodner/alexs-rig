#!/usr/bin/env bash
# Register this checkout as a local Claude Code plugin (SessionStart → inject_l0.py).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Alex's Rig — Claude plugin install"
echo "Plugin root: $ROOT"
echo

if command -v claude >/dev/null 2>&1; then
  echo "Trying: claude plugin install --file \"$ROOT\""
  if claude plugin install --file "$ROOT" 2>/dev/null; then
    echo "✓ Installed via claude plugin install"
    echo "Restart Claude Code Desktop / VS Code Claude session and check SessionStart for <alexs-rig-l0>."
    exit 0
  fi
  echo "(claude plugin install --file failed or unsupported — using manual path)"
fi

# Manual: symlink into Claude local plugins if that layout exists
CANDIDATES=(
  "${HOME}/.claude/plugins/local/alexs-rig"
  "${HOME}/.claude/plugins/alexs-rig"
)
for dest in "${CANDIDATES[@]}"; do
  parent="$(dirname "$dest")"
  if [[ -d "$parent" ]]; then
    rm -rf "$dest"
    ln -s "$ROOT" "$dest"
    echo "✓ Symlinked $dest → $ROOT"
    echo "Restart Claude Code; SessionStart should run:"
    echo "  python3 \"\${CLAUDE_PLUGIN_ROOT}/hooks/inject_l0.py\""
    echo "Smoke (from a project with docs/memory/snapshots/L0.md):"
    echo "  cd <project> && python3 \"$ROOT/hooks/inject_l0.py\" | head -c 200"
    exit 0
  fi
done

echo "Manual steps:"
echo "  1. Claude Code → /plugin or Settings → enable local plugin from:"
echo "       $ROOT"
echo "  2. Confirm hooks/hooks.json SessionStart points at hooks/inject_l0.py"
echo "  3. From a project that has memory:"
echo "       python3 $ROOT/hooks/inject_l0.py"
echo "     Expect JSON with alexs-rig-l0 wrapping L0.md"
echo "  4. New Claude session on that project — L0 should appear in context"
echo
echo "Also see docs/claude-plugin-install.md"
exit 1
