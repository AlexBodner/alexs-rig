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

# Keep per-worktree local state and the DERIVED graph out of git. Committing these
# is exactly what collides across parallel agents / worktrees on merge:
#   .alexs-rig/ (SESSION_BASE, graph-base, reviewed.json, verify-status)
#   the graph output (.understand-anything/, knowledge-graph.json, .cache/codemap/)
# The graph is re-derived on main after a merge (never git-merged), so it must not be tracked.
GITIGNORE="$PROJECT/.gitignore"
MARKER="# alexs-rig: per-worktree local state + derived graph (do not commit)"
if [[ ! -f "$GITIGNORE" ]] || ! grep -qF "$MARKER" "$GITIGNORE"; then
  {
    printf '\n%s\n' "$MARKER"
    printf '%s\n' ".alexs-rig/" ".understand-anything/" "knowledge-graph.json" ".cache/codemap/"
  } >> "$GITIGNORE"
  echo "Added graph/state entries to $GITIGNORE (keeps parallel-agent trees collision-free)."
else
  echo "Graph/state gitignore entries already present in $GITIGNORE."
fi
