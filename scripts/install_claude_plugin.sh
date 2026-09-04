#!/usr/bin/env bash
# Register this checkout as a local Claude Code plugin (marketplace + install).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Alex's Rig — Claude plugin install"
echo "Plugin root: $ROOT"
echo
echo
if command -v claude >/dev/null 2>&1; then
  # Proven path: register this checkout as a local marketplace, then install from it.
  echo "Registering local marketplace: claude plugin marketplace add \"$ROOT\""
  claude plugin marketplace add "$ROOT" >/dev/null 2>&1 || claude plugin marketplace update alexs-rig >/dev/null 2>&1 || true
  if claude plugin install alexs-rig@alexs-rig 2>/dev/null || claude plugin enable alexs-rig@alexs-rig 2>/dev/null; then
    echo "✓ Installed: alexs-rig@alexs-rig (claude plugin list to confirm)"
    echo "Start a NEW Claude Code session; SessionStart injects <alexs-rig-l0>."
    echo "Update later: git pull && claude plugin marketplace update alexs-rig && claude plugin update alexs-rig@alexs-rig"
    exit 0
  fi
  echo "(marketplace install failed — using manual path)"
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
echo "Also see docs/hooks.md"
exit 1
