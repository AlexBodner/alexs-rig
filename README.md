# Alex's Rig

A small, honest coding harness for **Claude Code**: standing memory that survives sessions,
a non-blocking supervision layer (batch review, verify, secret hygiene), a loop that **learns
your standing preferences from how you correct the agent**, and incremental codebase-graph
orchestration that stays collision-free across parallel agents.

The name is personal; the mechanism is not — anyone can install it. **v0.2.1**, MIT.

> **Measured, not claimed.** In a with/without ablation, injected non-default preferences
> were followed **100%** of the time with the rig vs **0%** without, at ~2¢/session overhead
> on Opus. On generic good practices the marginal value is ~0 (the model already does them) —
> so store the preferences the model *can't* guess. See [evals/calibrate](evals/calibrate/README.md).

## Install (Claude Code)

```bash
git clone https://github.com/AlexBodner/alexs-rig.git ~/alexs-rig
cd ~/alexs-rig && ./scripts/install.sh
```

That registers the checkout as a local plugin marketplace and installs `alexs-rig@alexs-rig`
(memory + hooks + skills). Confirm with `claude plugin list`, then **start a new session**.
The VS Code/Cursor "Review" checkbox UI is an optional extra (`./scripts/install_review_extension.sh`).

Manual equivalent:

```bash
claude plugin marketplace add ~/alexs-rig
claude plugin install alexs-rig@alexs-rig
```

**Update:** `cd ~/alexs-rig && git pull && claude plugin marketplace update alexs-rig`, then a new session.

## First five minutes

1. **Seed one standing rule** into your global memory (lives at `~/.alexs-rig/memory`, never
   committed into projects):
   ```bash
   python3 ~/alexs-rig/bin/principle-upsert --id P-1 --text "Ask before opening PRs or pushing"
   python3 ~/alexs-rig/bin/l0-regen
   ```
   (The repo ships 8 example principles in `docs/memory/` — copy the ones you like.)
2. **Open any repo, start a session** — your L0 is injected automatically. Ask "what's in my L0?".
3. **Correct the agent as you normally would** ("no, use X instead…"). Corrections are captured
   silently. Later, run `/alex-mine-corrections`: it proposes *general* principles from them,
   **you approve**, they land in L0.

## What runs automatically

| When | What |
|------|------|
| Session start | Injects L0 + a codebase-graph pointer + your per-repo style note; snapshots the worktree as `SESSION_BASE` so review covers only this session's edits |
| Every prompt | Silently captures correction-like turns (zero tokens) into a private inbox |
| Tool use | Best-effort block of `cat`/write of `.env`, keys, credentials — a speed-bump, **not** a security control ([docs/hygiene.md](docs/hygiene.md)) |
| Context compaction | Re-injects L0, graph pointer, style note |
| Turn end | Once per dirty round: reminds you to batch-review, shows last verify status (marked **STALE** if you edited since), nudges when ≥10 corrections are waiting. Never blocks. |

## Skills (the agent sees these; you can also `/alexs-rig:<name>`)

| Skill | Use |
|-------|-----|
| `alex-memory` | Park a todo / progress / standing principle (id-addressable, global) |
| `alex-mine-corrections` | Turn captured corrections into approved principles (approval-gated) |
| `alex-verify` | Run the project's checks; PASS/FAIL surfaced at turn end (informational, not a gate) |
| `alex-structure` | Where does X live / blast radius — queries the codebase graph before grep |
| `alex-graph` | Incrementally update the graph for only changed files (asks first; LLM cost) |
| `alex-session-review` / `alex-pr-review` | Batch review with content-hash "Viewed" — an agent re-edit un-views the file |
| `alex-distill` | Shrink L0 when it overflows (never silent-truncate) |

## Codebase graph, parallel agents

Optional, per repo: build once (`/understand --auto-update`, then `python3 ~/alexs-rig/bin/graph-mark`).
Staleness is git-derived (free); rebuilds are incremental and **ask first**. With several agents
on one project (one worktree each): **seed from main → grow local → re-derive on merge** —
`bin/graph-seed` copies main's graph into a new worktree, the graph is gitignored so it never
collides, and a `post-merge` hook (`scripts/install_git_hooks.sh`) nudges a re-derive of just
the merged diff. Details: [docs/knowledge-graph.md](docs/knowledge-graph.md).

## Style: match the repo, analyze once

`P-style` (ships as an example principle): analyze a repo's comment/docstring conventions **at
most once**, save `.alexs-rig/style.md`, follow it thereafter. SessionStart nudges to create it,
injects it once it exists, and `graph-seed` carries it to new worktrees.

## Benchmarks

- `python3 evals/detector/bench.py` — free, deterministic: correction-detector precision/recall
  (currently 1.00 / 1.00 with pending edits present).
- `python3 evals/calibrate/run.py` — with/without ablation on quality + tokens (dry-run by
  default; real runs need `--run --budget-usd`).

## Layout

`bin/` CLIs (memory, verify, graph, review) · `hooks/` Claude Code hooks · `skills/` · `evals/` ·
`docs/` ([HOW-TO](docs/HOW-TO.md), [hooks](docs/hooks.md), [usage](docs/usage.md),
[architecture](docs/architecture.md)) · `extensions/` optional VS Code Review UI.
Python 3.10+, stdlib only; `python3 -m unittest discover -s tests` and `ruff check .` in CI.

## Design rules

- **Small always-on context** — L0 stays under a token budget; overflow = distill, never truncate.
- **Surface, don't gate** — hooks remind and inform; nothing blocks a turn or a commit.
- **Learn from corrections, but only with approval** — nothing reaches L0 unreviewed.
- **Query the graph, never dump it** — the rig orchestrates understand-anything; no second engine.
- **Honest labels** — secret hygiene is a speed-bump; verify is informational; numbers are measured.

## License

MIT — see [LICENSE](LICENSE).
