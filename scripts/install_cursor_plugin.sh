#!/usr/bin/env bash
# Install this checkout into ~/.cursor/plugins/local/alexs-rig (rsync copy).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${HOME}/.cursor/plugins/local/alexs-rig"
mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
mkdir -p "$DEST"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete --exclude '.git/' --exclude '__pycache__/' --exclude '.venv/' "$ROOT"/ "$DEST"/
else
  cp -R "$ROOT"/. "$DEST"/
  rm -rf "$DEST/.git"
fi
chmod +x "$DEST"/bin/* "$DEST"/hooks/*.py "$DEST"/hooks/cursor-invoke.sh "$DEST"/scripts/*.sh 2>/dev/null || true
"$ROOT/scripts/install_review_extension.sh" || true
echo "✓ Installed Cursor plugin at $DEST"
echo "  Reload Window, then SessionStart should run inject_l0 via cursor-hooks.json"
echo "  Source Control → Review: session or PR, then check Viewed"
