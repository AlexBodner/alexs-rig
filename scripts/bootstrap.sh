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

# Demo upsert so first-timers see memory work (idempotent ids).
python3 bin/principle-upsert --id P-demo --text "Prefer batch review over per-edit stops" >/dev/null
python3 bin/pending-upsert upsert --id T-demo --priority P2 --text "Demo pending — replace after your first real task (or pending-upsert done --id T-demo)" >/dev/null
python3 bin/progress-upsert --id F-proto --status active --summary "Public v0: L0+mining+hooks+skills" --path . >/dev/null
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
echo "Demo memory (already applied: P-demo, T-demo, F-proto --path .):"
sed -n '1,24p' "$L0" | sed 's/^/  /'
echo
echo "More commands:"
echo "  ./bin/principle-upsert --id P-… --text '…'"
echo "  ./bin/pending-upsert upsert --id T-… --priority P1 --text '…'"
echo "  ./bin/pending-upsert done --id T-demo"
echo "  ./bin/l0-regen"
echo "  ./bin/mine-corrections --strong-only   # needs ~/.cursor/projects on this host"
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
