# Alex's Rig

A coding harness for **Claude Code**. It learns your standing preferences from how you
correct the agent, keeps them in a small always-on memory, and gates the decisions that are
expensive or irreversible. v0.7.0, MIT, Python 3.10+, standard library only.

These are rules it derived from real corrections, not examples written for a README:

> **Correctness first, scale second.** Validate every new metric and code path on a free
> local case before paying for compute.
>
> **Equal effort on every arm.** If one side gets tuned parameters, the others get the same,
> and the measuring apparatus counts: if swapping the order of the arms changes the result,
> the measurement is biased, not the code.
>
> **Pull the run's config and results off the machine before stopping it.** Any number you
> may cite later has to survive the VM.

Nobody wrote those. They came out of clustering the turns where the agent got corrected, and
none of them reached memory without being approved first.

## The number that matters is the one that went against the author

The correction detector was benchmarked against a synthetic set and reported **1.00 recall**.
That was worthless: the same author wrote the detector and its test cases, then widened the
detector until it passed them.

Rebuilt on 200 real turns, labelled blind, across two independent corpora:

| | synthetic | honest |
|---|---|---|
| precision | 1.00 | 0.57 to 0.70 |
| **recall** | **1.00** | **0.07** |

It was finding 7% of real corrections. The labels were audited blind and disagreed with the
author's at kappa 0.51, which moved the boundary again; recall held at 0.07 through every
relabelling, including on the corpus the detector had been fitted to.

So the design changed. Corrections are roughly 22% of turns, not 2%, and at that base rate a
filter concentrates almost nothing. Capture is now unfiltered and a model does the selecting
later: **0.56 recall** for the same cost. Method and tooling: [evals/honest](evals/honest/README.md).

## What a session looks like

Standing memory arrives before you type anything:

```text
<alexs-rig-l0>
## PRINCIPLES
- [P-run] Paid compute is the last step, not a debugging surface. BEFORE: validate every
  new metric, formula and code path on a free tiny local case ...
- [P-evidence] Verify against the real source before asserting a fact or claiming done ...
</alexs-rig-l0>
<alexs-rig-session>
SESSION_BASE=a54061bc  # review covers only what changed from here
</alexs-rig-session>
```

And the turn ends with what you have not looked at yet, never blocking:

```text
<alexs-rig-review>
Unreviewed agent edits (dirty vs SESSION_BASE, unmarked or re-touched). List them with
bin/review-pending --name-only; mark one reviewed with bin/review-mark <path>. A later
agent edit unmarks that file again.
 bin/shipped | 118 ++++++++++
 README.md   |  40 ++--
last verify: PASS (STALE: edits since; re-run bin/verify)
</alexs-rig-review>
```

## Install

```bash
git clone https://github.com/AlexBodner/alexs-rig.git ~/alexs-rig
cd ~/alexs-rig && ./scripts/install.sh
```

Start a new session. Update with `git pull && claude plugin update alexs-rig@alexs-rig`; the
manifest version has to change or the installed copy is never refreshed.

## What runs without being asked

| When | What |
|------|------|
| Session start | Injects your memory, a codebase-graph pointer and the repo's style note. Snapshots the worktree so review covers only this session. |
| Every prompt | Captures your reply with the agent turn it answers. No model call. |
| Tool use | Best-effort block on reading `.env` and keys into the transcript. A speed-bump, not a security control. |
| Compaction | Re-injects all of the above, so a long session does not drift. |
| Turn end | What is still unreviewed, the last verify result, marked STALE if you edited since. Never blocks. |
| Graph goes stale | Refreshes itself past a threshold. Only the first build asks. |

## Skills

The agent picks these on its own; `/alexs-rig:<name>` invokes one directly.

| | |
|---|---|
| **`alex-loop`** | A coding task end to end. Plan, adversarial challenge of that plan before any code exists, build, review. Gates: the plan, the PR, expensive compute. |
| **`alex-content`** | Outward-facing work end to end. Gates: the claim before pixels, one cheap preview before the expensive render, approval before publishing. |
| `alex-mine-corrections` | Read captured turns, propose general rules. Nothing is stored without approval. |
| `alex-outcomes` | The other half: log what shipped, attach how it did, mine the winners. |
| `alex-memory` · `alex-distill` | Park a principle or todo; shrink memory when it overflows its budget. |
| `alex-modularize` · `alex-api` | Where code should live, in the layout that fits the project. A library's public surface, designed from the caller's side. |
| `alex-structure` · `alex-graph` | Where does X live and what is the blast radius. Refresh the graph for changed files only. |
| `alex-docs` · `alex-viz` · `alex-roboflow-voice` | Craft for documents, visual deliverables, and the Roboflow house voice. |
| `alex-experiments` | ML run hygiene: keep the best-by-validation checkpoint, one run one log, compare like with like. |
| `alex-verify` | Run the project's checks and record the result. Informational, never a gate. |

## Parallel agents

One worktree per agent: seed from main, grow local, re-derive on merge. `bin/graph-seed`
copies main's graph into a new worktree, the graph is gitignored so it never collides, and a
`post-merge` hook re-derives just the merged diff. [docs/knowledge-graph.md](docs/knowledge-graph.md)

## Check the claims yourself

```bash
python3 evals/honest/bench.py sample     # stratified sample of your own turns
python3 evals/honest/bench.py label      # blind, resumable
python3 evals/honest/bench.py score      # precision and recall with intervals
python3 evals/honest/bench.py audit      # spot-check another labeller, reports kappa
```

What you label stays in `evals/private`, which is gitignored. `evals/detector` is kept as the
counter-example: it is what a benchmark looks like when one author writes both sides.

## Design rules

- Memory stays under a token budget. Overflow means distill, never truncate in silence.
- Hooks surface and inform. The one hard block, on reading secrets, is labelled as the
  speed-bump it is.
- Nothing reaches memory without approval.
- Automate what is cheap and reversible, gate what is expensive or irreversible. That single
  rule places every gate in both loops.
- Orchestrate understand-anything rather than shipping a second graph engine.
- Measure the tool itself, and publish the result that goes against you.

MIT, see [LICENSE](LICENSE). Tests and ruff run in CI on Python 3.10 through 3.12.
