#!/usr/bin/env bash
# Copy the Review UI into local Cursor/VS Code extensions (unpublished).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/extensions/alexs-rig-review"
VER="0.1.0"
if command -v node >/dev/null 2>&1; then
  VER="$(node -p "require('${SRC}/package.json').version")"
fi
NAME="alexbodner.alexs-rig-review-${VER}"

install_into() {
  local dest_root="$1"
  mkdir -p "$dest_root"
  local dest="${dest_root}/${NAME}"
  mkdir -p "$dest"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$SRC"/ "$dest"/
  else
    rm -rf "$dest"
    mkdir -p "$dest"
    cp -R "$SRC"/. "$dest"/
  fi
  echo "✓ Review UI → $dest"
}

installed=0
if [[ -d "${HOME}/.cursor" ]]; then
  install_into "${HOME}/.cursor/extensions"
  installed=1
fi
if [[ -d "${HOME}/.vscode" ]]; then
  install_into "${HOME}/.vscode/extensions"
  installed=1
fi
if [[ "$installed" -eq 0 ]]; then
  echo "No ~/.cursor or ~/.vscode — open Cursor/VS Code once, then re-run." >&2
  exit 1
fi
echo "Reload Window to pick up Review (Source Control sidebar: session + PR)."
