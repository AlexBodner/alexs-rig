#!/usr/bin/env bash
# cursor-invoke.sh — self-rooted hook runner (avoids cross-plugin PLUGIN_ROOT pollution)
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "cursor-invoke: usage: cursor-invoke.sh <hook-file>" >&2
  exit 0
fi
HOOK_FILE="$1"
shift
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${HERE}/.." && pwd)"
TARGET="${HERE}/${HOOK_FILE}"
export PLUGIN_ROOT="${ROOT}"
export CLAUDE_PLUGIN_ROOT="${ROOT}"
if [[ ! -f "${TARGET}" ]]; then
  exit 0
fi
case "${HOOK_FILE}" in
  *.py) exec python3 "${TARGET}" "$@" ;;
  *.js) exec node "${TARGET}" "$@" ;;
  *) exec bash "${TARGET}" "$@" ;;
esac
