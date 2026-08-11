#!/usr/bin/env bash
# Bootstrap sketch for alexs-rig-proto — docs + optional VS Code extension installs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p docs/memory/snapshots docs/memory/archive docs/memory/mining docs/memory/telemetry .alexs-rig
touch docs/memory/PRINCIPLES.jsonl docs/memory/PROGRESS.jsonl docs/memory/PENDING.jsonl

chmod +x bin/principle-upsert bin/principle-forget bin/progress-upsert bin/pending-upsert bin/l0-regen bin/mine-corrections 2>/dev/null || true

python3 bin/l0-regen >/dev/null

echo "== Alex's Rig proto bootstrap =="
echo "Root: $ROOT"
echo
echo "Memory:"
echo "  ./bin/principle-upsert --id P-demo --text 'Prefer batch review over per-edit stops'"
echo "  ./bin/pending-upsert upsert --id T-1 --priority P1 --text 'Dogfood Desktop +N -M'"
echo "  ./bin/l0-regen"
echo "  ./bin/mine-corrections [--workspace AI-Rig]"
echo
echo "Recommended VS Code / Cursor extensions (uncommitted + PR review):"
echo "  Git Tree Compare:     letmaik.git-tree-compare"
echo "  GitHub Pull Requests: github.vscode-pull-request-github"
echo "  Claude Diff & Edit:   dfarkash.claude-edits-scm   # spike"
echo
if command -v cursor >/dev/null 2>&1; then
  read -r -p "Install recommended extensions via cursor CLI now? [y/N] " ans || true
  if [[ "${ans:-}" =~ ^[Yy]$ ]]; then
    cursor --install-extension letmaik.git-tree-compare || true
    cursor --install-extension github.vscode-pull-request-github || true
    cursor --install-extension dfarkash.claude-edits-scm || true
  fi
elif command -v code >/dev/null 2>&1; then
  read -r -p "Install recommended extensions via code CLI now? [y/N] " ans || true
  if [[ "${ans:-}" =~ ^[Yy]$ ]]; then
    code --install-extension letmaik.git-tree-compare || true
    code --install-extension github.vscode-pull-request-github || true
    code --install-extension dfarkash.claude-edits-scm || true
  fi
else
  echo "(No cursor/code CLI on PATH — install extensions from marketplace UI.)"
fi

echo
echo "Done. Open docs/memory/snapshots/L0.md and docs/workflow.md"
