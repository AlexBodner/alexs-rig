#!/usr/bin/env bash
# Register the Review UI with Cursor/VS Code via a real .vsix (folder copy is not enough).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/extensions/alexs-rig-review"
VER="$(python3 -c "import json; print(json.load(open('${SRC}/package.json'))['version'])")"
VSIX="${SRC}/alexs-rig-review-${VER}.vsix"

python3 "$ROOT/scripts/pack_review_vsix.py" --out "$VSIX"
echo "Packed $VSIX"

find_clis() {
  local seen="" p
  for p in \
    "$(command -v cursor 2>/dev/null || true)" \
    "$(command -v code 2>/dev/null || true)" \
    "${HOME}/.local/bin/cursor" \
    "${HOME}/.local/bin/code" \
    /Applications/Cursor.app/Contents/Resources/app/bin/cursor \
    "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" \
    /usr/share/code/bin/code \
    /usr/bin/code \
    /usr/bin/cursor \
    /snap/bin/code
  do
    [[ -n "$p" && -x "$p" ]] || continue
    case " $seen " in
      *" $p "*) continue ;;
    esac
    seen="$seen $p"
    printf '%s\n' "$p"
  done
}

ok=0
while IFS= read -r cli; do
  echo "Installing Review via: $cli --install-extension $VSIX"
  if "$cli" --install-extension "$VSIX" --force; then
    echo "✓ Review registered with $cli"
    ok=1
  else
    echo "✗ $cli failed to install the vsix" >&2
  fi
done < <(find_clis)

if [[ "$ok" -eq 0 ]]; then
  echo "Review UI is NOT registered. Folder copy is ignored by VS Code/Cursor." >&2
  echo "Install the vsix (then Reload Window once):" >&2
  echo "  code --install-extension $VSIX" >&2
  echo "  cursor --install-extension $VSIX" >&2
  echo "Put code or cursor on PATH if the CLI is missing." >&2
  exit 1
fi
echo "Reload Window once. Source Control → Review should appear."
