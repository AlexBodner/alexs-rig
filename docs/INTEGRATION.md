# Integration matrix — plan → code

Every item from the locked plan’s **What we still build** (+ locked companions) must map here. Empty cell = bug.

| Plan feature | Integrated path |
|--------------|-----------------|
| L0 generated snapshot | `bin/l0-regen`, `docs/memory/snapshots/L0.md` |
| Upsert / forget | `bin/principle-upsert`, `principle-forget`, `progress-upsert`, `pending-upsert` |
| Distill on overflow | `bin/distill` + overflow banner in L0 |
| Human md views | `docs/memory/{PRINCIPLES,PROGRESS,PENDING}.md` |
| Multi-project root | `--root` / `ALEXS_RIG_MEMORY` in `_memory.py` |
| SessionStart L0 inject | `hooks/inject_l0.py`, `hooks/hooks.json` |
| SESSION_BASE | `.alexs-rig/SESSION_BASE` via `inject_l0.py` |
| PreCompact reinject | `hooks/reinject_l0.py` |
| Cursor hooks | `hooks/cursor-hooks.json` + `cursor-invoke.sh` |
| Bootstrap + extensions | `scripts/install.sh`, `scripts/bootstrap.sh`, `scripts/install_review_extension.sh`, `.vscode/extensions.json`, `docs/extensions.md` |
| Uncommitted review | Desktop `+N -M`; Source Control → Review (session or PR Viewed); `bin/session-diff`; skills `alex-session-review` / `alex-pr-review` |
| PR review path | `gh pr checkout` + Source Control → Review (PR mode); skill `alex-pr-review` |
| Secret hygiene | `hooks/secret_hygiene.py` (Bash **and** Write/Edit), `docs/hygiene.md` |
| Prompt L0 miss | `hooks/prompt_l0_miss.py` (`UserPromptSubmit` / Cursor `beforeSubmitPrompt`) |
| Stop review nudge | `hooks/stop_review.py` (once per dirty round; never blocks) |
| Hook map + live test | `docs/hooks.md` |
| Structure skill | `skills/alex-structure` |
| Always-on knowledge graph | `rules/knowledge-graph.md` + `.mdc`, `hooks/graph_status.py`, `bin/graph-status`, SessionStart + PreCompact inject, `docs/knowledge-graph.md`, `P-graph` |
| Portable agent file | `AGENTS.md` + thin `CLAUDE.md` (`@AGENTS.md`) |
| Human how-to | `docs/HOW-TO.md` |
| Harness practice notes | `docs/practices.md` |
| Correction mining CLI | `bin/mine-corrections` (default `--apply` named clusters) |
| Correction mining skill | `skills/alex-mine-corrections` |
| Skills (auto-loaded, slash-invocable) | `skills/alex-*` |
| Commit-when-asked | `docs/commit-when-asked.md`, `P-commit` |
| Multi-agent native | `docs/multi-agent.md` |
| CI | `.github/workflows/test.yml` |
| Architecture lock | `docs/architecture.md`, `P-arch-lock` |
| Agent prompts | `prompts/README.md`, `AGENT_TRY.md`, `AGENT_COMPUTER.md`, `AGENT_BOX_VERIFY.md`, `AGENT_SIMULATE_USAGE.md`, `AGENT_ITERATE.md` |

## Verify integration

```bash
python3 -m unittest discover -s tests -v
python3 bin/distill | head
python3 hooks/inject_l0.py | python3 -c "import sys,json; d=json.dumps(json.load(sys.stdin)); assert 'alexs-rig-l0' in d and 'alexs-rig-graph' in d"
python3 bin/graph-status | grep -q alexs-rig-graph
python3 -c "import json; json.load(open('hooks/hooks.json')); json.load(open('hooks/cursor-hooks.json'))"
test -f skills/alex-session-review/SKILL.md
test -f skills/alex-memory/SKILL.md
test -f AGENTS.md && test -f CLAUDE.md && test -f rules/knowledge-graph.mdc
test -f scripts/install.sh && test -f scripts/pack_review_vsix.py && test -f extensions/alexs-rig-review/package.json
test -f prompts/AGENT_COMPUTER.md && test -f prompts/AGENT_TRY.md
./scripts/bootstrap.sh --help
```
