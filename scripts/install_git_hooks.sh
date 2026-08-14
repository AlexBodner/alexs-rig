#!/usr/bin/env bash
# Install Alex's Rig git hooks into a project's .git/hooks (post-merge graph nudge).
# Usage: install_git_hooks.sh [project-dir]   (default: current dir)
set -euo pipefail
RIG_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="${1:-$PWD}"
HOOK_DIR="$PROJECT/.git/hooks"

if [[ ! -d "$PROJECT/.git" ]]; then
  echo "install_git_hooks: $PROJECT is not a git repo (no .git)." >&2
  exit 1
fi
mkdir -p "$HOOK_DIR"
DEST="$HOOK_DIR/post-merge"

if [[ -e "$DEST" ]] && ! grep -q "alexs-rig" "$DEST" 2>/dev/null; then
  echo "install_git_hooks: a post-merge hook already exists at $DEST." >&2
  echo "Add this line to it manually to keep both:" >&2
  echo "  bash \"$RIG_ROOT/hooks/git/post-merge\"" >&2
  exit 1
fi
cp "$RIG_ROOT/hooks/git/post-merge" "$DEST"
chmod +x "$DEST"
echo "Installed post-merge graph nudge → $DEST"
