# Alex's Rig

A coding harness for **Claude Code** that learns your standing preferences from how you
correct the agent, keeps them in a small always-on memory, and gates the decisions that are
expensive or irreversible. The name is personal. The mechanism is not: anyone can install it.
**v0.6.0**, MIT, Python 3.10+, standard library only.

## Measured, including where it failed

The rig's own detector was benchmarked against a synthetic set and reported **precision 1.00,
recall 1.00**. That number was worthless: the same author wrote the detector and its test
cases, then widened the detector until it passed them.

Rebuilt honestly, on 200 real turns labelled blind across two independent corpora:

| | synthetic benchmark | honest benchmark |
|---|---|---|
| precision | 1.00 | **0.57 to 0.70** |
| recall | 1.00 | **0.07** |

The detector was finding **7% of real corrections**, not 100%. The labels were audited blind
by the user and disagreed with the author's at kappa 0.51, which exposed a second bias and
moved the boundary again. Recall held at 0.07 through every relabelling, and across a corpus
the detector had been *fitted to*, which is what makes the result trustworthy rather than
convenient.

**So the design changed.** Corrections turned out to be roughly 22% of turns rather than 2%,
and at that base rate a filter concentrates almost nothing. Capture is now unfiltered and the
selection happens later, where a model reads the turn instead of a regex: **0.56 recall for
the same cost bracket**. Full write-up and the tooling to reproduce it: [evals/honest](evals/honest/README.md).

A separate with/without ablation on injected non-default preferences went from **0/3 to 3/3**
adherence at roughly 2 cents per session. That one is n=3 on a single run with deterministic
grading, so treat it as a smoke test rather than a benchmark: [evals/calibrate](evals/calibrate/README.md).

## Install

```bash
git clone https://github.com/AlexBodner/alexs-rig.git ~/alexs-rig
cd ~/alexs-rig && ./scripts/install.sh
```

That registers the checkout as a local plugin marketplace and installs `alexs-rig@alexs-rig`.
Confirm with `claude plugin list`, then start a new session. Manual equivalent:

```bash
claude plugin marketplace add ~/alexs-rig
claude plugin install alexs-rig@alexs-rig
```

**Update:** `cd ~/alexs-rig && git pull && claude plugin update alexs-rig@alexs-rig`, then a
new session. The version in the manifest has to change or the installed copy is never
refreshed.

## First five minutes

1. **Seed one standing rule.** Memory lives at `~/.alexs-rig/memory` and is never committed
   into your projects.
   ```bash
   python3 ~/alexs-rig/bin/principle-upsert --id P-1 --text "Ask before opening PRs or pushing"
   python3 ~/alexs-rig/bin/l0-regen
   ```
2. **Open any repo and start a session.** Your memory is injected automatically. Ask "what is
   in my L0?" to see it.
3. **Correct the agent as you normally would.** Every reply is captured silently at zero token
   cost. Later, run `/alex-mine-corrections`: it reads them, proposes *general* rules, and
   nothing is stored until you approve it.

## What runs automatically

| When | What |
|------|------|
| Session start | Injects standing memory, a codebase-graph pointer and the per-repo style note. Snapshots the worktree so review covers only this session's edits. |
| Every prompt | Captures your reply with the agent turn it answers, into a private local inbox. No model call, no tokens. |
| Tool use | Best-effort block on reading `.env`, keys and credentials into the transcript. A speed-bump, **not** a security control ([docs/hygiene.md](docs/hygiene.md)). |
| Context compaction | Re-injects memory, graph pointer and style note, so a long session does not drift. |
| Turn end | Once per dirty round: what is still unreviewed, the last verify result (marked **STALE** if you edited since), and a nudge when the inbox is worth flushing. Never blocks. |
| Graph goes stale | Above a threshold of changed files, the graph refreshes on its own. Only the first build asks. |

## The two loops

Both compose skills that already exist rather than replacing them, and both put the gates
where a mistake is still cheap.

**`alex-loop`** takes a coding task end to end. It classifies the work, researches only if the
answer is in the literature rather than the repo, plans, then sends the plan to an adversarial
challenger *before any code exists*. You see a plan that has already been attacked and
self-refuted. After you approve it, the build and its review run without narration. Three
gates: the plan, the pull request, and any expensive compute.

**`alex-content`** takes outward-facing work end to end: promo video, blog, docs page, figure.
Content has a different cost profile, so the gates differ: the claim is validated **before any
pixels**, a single frame or outline is produced **before the expensive render**, and nothing is
published without an explicit yes. Every fix is batched into one consolidated pass, because 63
of the captured corrections were about renders.

## Skills

The agent selects these on its own. You can also invoke one directly with `/alexs-rig:<name>`.

**Memory and learning**

| Skill | Use |
|-------|-----|
| `alex-memory` | Park a todo, progress note or standing principle. Id-addressable, global. |
| `alex-mine-corrections` | Read the captured turns, select the real corrections, propose general rules. Approval-gated. |
| `alex-outcomes` | The other half: log what shipped, attach how it did, fold repeated winning patterns into the craft skills. |
| `alex-distill` | Shrink memory when it overflows its budget. Merge or retire, never silent-truncate. |

**Planning and building**

| Skill | Use |
|-------|-----|
| `alex-loop` | One entry for a coding task. Plan, adversarial challenge, build, review. Three gates. |
| `alex-modularize` | Decide where code should live before writing it, in the layout that fits the kind of project, with a move order that keeps pull requests clean. |
| `alex-api` | Design a library's public surface from the caller's side. |
| `alex-structure` | Where does X live, what is the blast radius. Queries the graph before reaching for grep. |

**Craft**

| Skill | Use |
|-------|-----|
| `alex-content` | One entry for outward-facing work. Claim, preview, render once, publish. |
| `alex-docs` | Explanatory documents: lead with the outcome, one standalone narrative, cut before adding. |
| `alex-viz` | Visual deliverables: show each fact once, render the signal a decision is made from, and make it read at a glance. |
| `alex-roboflow-voice` | The Roboflow house voice beyond docs pages. No AI-smell punctuation, numbers state their source. |
| `alex-experiments` | ML run hygiene: keep the best-by-validation checkpoint, one run one log, compare like with like. |

**Review and verification**

| Skill | Use |
|-------|-----|
| `alex-verify` | Run the project's checks and record the result. Informational, surfaced at turn end, never a gate. |
| `bin/review-pending` | Not a skill: lists what the agent changed this session and has not been reviewed. The turn-end nudge is built on it. |
| `alex-graph` | Refresh the codebase graph for only the files that changed. |

## Codebase graph and parallel agents

Optional, per repo. Build once with `/understand --auto-update`; staleness tracking then starts
by itself the first time a session sees the graph. Staleness is derived from git and costs
nothing, and refreshes are incremental. Only the first build asks.

With several agents on one project, one worktree each: **seed from main, grow local, re-derive
on merge.** `bin/graph-seed` copies main's graph into a new worktree, the graph is gitignored
so it never collides, and a `post-merge` hook nudges a re-derive of just the merged diff.
Details in [docs/knowledge-graph.md](docs/knowledge-graph.md).

## Style: match the repo, analyze once

`P-style` ships as an example principle. Analyze a repo's comment and docstring conventions **at
most once**, save `.alexs-rig/style.md`, follow it thereafter. Session start nudges you to create
it, injects it once it exists, and `graph-seed` carries it into new worktrees.

## Reproduce the benchmarks

```bash
python3 evals/honest/bench.py sample     # stratified sample of your own real turns
python3 evals/honest/bench.py label      # blind labelling, resumable
python3 evals/honest/bench.py score      # precision and recall with confidence intervals
python3 evals/honest/bench.py audit      # spot-check someone else's labels, reports kappa
python3 evals/honest/llm_classifier.py   # the same ground truth, model instead of regex
```

Everything you label stays in `evals/private`, which is gitignored. The synthetic benchmark in
`evals/detector` is kept only as the counter-example: it is what a benchmark looks like when the
author writes both sides.

## Layout

`bin/` command-line tools for memory, verify, graph and review. `hooks/` the Claude Code hooks.
`skills/` `evals/` `docs/`.
`python3 -m unittest discover -s tests` and `ruff check .` run in CI on Python 3.10 through 3.12.

## Design rules

- **Small always-on context.** Memory stays under a token budget. Overflow means distill, never
  truncate in silence.
- **Surface, do not gate.** Hooks remind and inform. Nothing blocks a turn or a commit, and the
  one hard block, on reading secrets, is labelled as the speed-bump it is.
- **Learn from corrections, only with approval.** Nothing reaches memory unreviewed.
- **Automate what is cheap and reversible, gate what is expensive or irreversible.** That single
  rule places every gate in the loops.
- **Query the graph, never dump it.** The rig orchestrates understand-anything rather than
  shipping a second engine.
- **Measure the tool itself, and publish the result that goes against you.** The honest
  benchmark exists because the flattering one was wrong.

## License

MIT, see [LICENSE](LICENSE).
