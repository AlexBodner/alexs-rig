#!/usr/bin/env bash
# Create the personal memory (default ~/.alexs-rig/memory, or $ALEXS_RIG_MEMORY) and its first L0.
# Idempotent: existing rules are kept, nothing is seeded.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MEM="${ALEXS_RIG_MEMORY:-$HOME/.alexs-rig/memory}"

python3 "$ROOT/bin/l0-regen" --root "$MEM" >/dev/null
L0="$(python3 "$ROOT/bin/l0-show" --root "$MEM" >/dev/null && echo "$MEM/snapshots/L0.md")"

echo "== Alex's Rig bootstrap =="
echo "memory: $MEM"
echo "L0:     $L0"
echo
echo "Add a standing rule:   python3 $ROOT/bin/principle-upsert --id P-<slug> --text '...'"
echo "Park a todo:           python3 $ROOT/bin/pending-upsert upsert --id T-<slug> --priority P2 --text '...'"
echo "Show what is loaded:   python3 $ROOT/bin/l0-show"
