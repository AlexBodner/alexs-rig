#!/usr/bin/env bash
# Bootstrap for alexs-rig — docs + optional VS Code extension installs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
L0="$ROOT/docs/memory/snapshots/L0.md"
WORKFLOW="$ROOT/docs/workflow.md"

mkdir -p docs/memory/snapshots docs/memory/archive docs/memory/mining docs/memory/telemetry .alexs-rig
touch docs/memory/PRINCIPLES.jsonl docs/memory/PROGRESS.jsonl docs/memory/PENDING.jsonl

chmod +x bin/principle-upsert bin/principle-forget bin/progress-upsert bin/pending-upsert bin/l0-regen bin/mine-corrections 2>/dev/null || true

python3 bin/l0-regen >/dev/null

echo "== Alex's Rig bootstrap =="
echo "Root: $ROOT"
echo
echo "Daily loop: see $WORKFLOW (section \"Daily loop\")."
echo
echo "First open:"
echo "  1. File → Open Folder → this clone ($ROOT), not a parent directory."
echo "  2. Dismiss Copilot sign-in / auto-opened chat if they eat the screen."
echo "  3. Open L0 with an absolute path (relative paths against /workspace look blank):"
echo "       $L0"
echo
echo "Memory:"
echo "  ./bin/principle-upsert --id P-demo --text 'Prefer batch review over per-edit stops'"
echo "  ./bin/pending-upsert upsert --id T-1 --priority P1 --text 'Dogfood Desktop +N -M'"
echo "  ./bin/progress-upsert --id F-1 --status active --summary '…' --path ."
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
echo "Done."
echo "  L0:       $L0"
echo "  Workflow: $WORKFLOW"
