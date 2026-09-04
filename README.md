# Alex's Rig

A coding harness for **Claude Code**. It learns your standing preferences from how you
correct the agent, keeps them in a small always-on memory, and gates the decisions that are
expensive or irreversible. v0.7.0, MIT, Python 3.10+, standard library only.

## What it does

- **Standing memory.** Your rules injected at session start and after compaction, under a
  token budget. Overflow means distilling, never truncating in silence.
- **Learns from your corrections.** Every reply captured at no token cost. On demand a model
  clusters them into general rules. Nothing stored without your approval.
- **`alex-loop`.** A coding task from plan to merged: plan, adversarial challenge of that
  plan before any code exists, build, review.
- **`alex-content`.** A video, blog or figure from claim to published: validate the claim,
  one cheap preview, then render once.
- **Gates only where it hurts.** The plan, the pull request, paid compute, the render, the
  post. Everything cheap and reversible runs without asking.
- **Skills that carry your house rules.** Where code lives, how an API reads from the call
  site, how a document opens, what makes a demo legible, how an ML run keeps its best
  checkpoint.
- **Review scoped to the session.** What the agent changed, separated from what you already
  had dirty. Marking a file reviewed un-marks itself when the agent edits it again.
- **A codebase graph that stays out of the way.** Staleness derived from git, free. Only the
  first build asks. One worktree per agent, seeded from main, so they never collide.
- **Two quiet guards.** A speed-bump on reading `.env` and keys into the transcript, and a
  verify result that goes stale the moment you edit after it.

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

## What it learned, unprompted

Four rules it derived by clustering the turns where it got corrected. Nobody wrote them
for the README, and none of them reached memory without being approved first:

> **Add alongside, never restructure to get the job done.** Don't move, rename or reshape
> existing code or parameters to land a change. If a rename looks necessary, flag it, because
> in a library other people depend on that is a breaking change I have to catch line by line.
>
> **Equal effort on every arm.** If one side gets tuned parameters, the others get the same,
> and the measuring apparatus counts: if swapping the order of the arms changes the result,
> the measurement is biased, not the code.
>
> **No silent failures.** If a required input is missing or an assumption breaks, raise a
> clear error instead of degrading quietly or inventing a default.
>
> **Never report something as done without evidence,** and no invented precision. Verify
> against the implementation, the paper or the docs before asserting it, and give a number
> only the digits it earned.

## Install

```bash
git clone https://github.com/AlexBodner/alexs-rig.git ~/alexs-rig
cd ~/alexs-rig && ./scripts/install.sh
```

Start a new session. Update with `git pull && claude plugin update alexs-rig@alexs-rig`; the
manifest version has to change or the installed copy is never refreshed.

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

## Why capture is unfiltered

Selecting which turns are corrections is the hard part, and it is where the obvious design
fails. A keyword filter looks right: corrections seem rare, so catch the ones that open with
"no" or "don't" and skip the rest.

Measured on 200 real turns labelled blind across two corpora, that filter found **7% of them**.
Corrections mostly do not announce themselves. They report a symptom instead: *"image quality
looks low"*, *"the videos show no box"*, *"velocities look really weird"*. And they are not
rare, they are roughly **22% of turns**, a base rate at which a filter concentrates almost
nothing.

| | keyword filter | a model reading the same turns |
|---|---|---|
| precision | 0.57 to 0.70 | 0.52 |
| **recall** | **0.07** | **0.56** |

So capture keeps everything and the selection happens later, once, where a model can read the
turn next to what it was answering. Method, labels and the audit that moved these numbers:
[evals/honest](evals/honest/README.md).

The synthetic benchmark this replaced reported 1.00 recall. It was worthless: the same author
wrote the detector and its test cases, then widened the detector until it passed them. It is
kept in `evals/detector` as the counter-example.

## Check the claims yourself

```bash
python3 evals/honest/bench.py sample     # stratified sample of your own turns
python3 evals/honest/bench.py label      # blind, resumable
python3 evals/honest/bench.py score      # precision and recall with intervals
python3 evals/honest/bench.py audit      # spot-check another labeller, reports kappa
```

What you label stays in `evals/private`, which is gitignored.

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
