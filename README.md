# Alex's Rig

A coding harness for **Claude Code**. It keeps your standing rules in a small always-on memory,
distills new ones from the turns where you corrected the agent (with your approval before
anything is stored), and gates the decisions that are expensive or irreversible.
v0.8.0, MIT, Python 3.10+, standard library only.

## What it does

- **Standing memory.** Your rules arrive before your first prompt and again after every
  compaction, under a token budget. Overflow means distilling, never truncating in silence.
- **Distills rules from your corrections.** Every reply is captured at no token cost, next to
  the agent turn it answers. On demand a model clusters them into general rules. Nothing is
  stored without your approval.
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
  had dirty. Marking a file reviewed un-marks itself when the agent edits it again. The
  baseline survives compaction and resume.
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
SESSION_BASE=a54061bc9aeddcd0229a65b4bd3b531482617ed3
</alexs-rig-session>
```

And the turn ends with what you have not looked at yet, never blocking:

```text
<alexs-rig-review>
Unreviewed agent edits (dirty vs SESSION_BASE, unmarked or re-touched). List them with
bin/review-pending --name-only; mark one reviewed with bin/review-mark <path>. A later
agent edit unmarks that file again. Do not commit unless the human asked.
 bin/shipped | 118 ++++++++++
 README.md   |  40 ++--
last check: PASS — pytest -q (2026-09-04T19:02:11Z) — STALE: edits since; re-run bin/verify
</alexs-rig-review>
```

## Rules it distilled from real corrections

Four of the rules the mining pass proposed after clustering turns where the agent had been
corrected, then approved and stored. The wording here is the author's; the stored text is in
[docs/memory/PRINCIPLES.jsonl](docs/memory/PRINCIPLES.jsonl), which ships as the example
memory a fresh install gets.

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

Start a new session. Requires Claude Code; the same hooks are wired for Cursor but that side
has not been verified live. The graph features drive the `understand-anything` plugin.
`alex-loop` and `alex-content` call other plugins' skills (a plan, feature, fix and review
workflow, an adversarial challenger, a research skill) and need them installed to run every
step.

Every reply you type is appended, after redaction, to a corrections inbox under your memory
directory, outside any repo. Treat that file as sensitive. Updating, memory locations and the
CLI reference: [docs/usage.md](docs/usage.md).

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
| `alex-docs` · `alex-viz` | Craft for documents and visual deliverables. |
| `alex-roboflow-voice` | An example of a house-voice skill: the rules one employer's prose follows. |
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

Measured on 184 real turns from two corpora, labelled with the detector's score hidden, that
filter found **7% of them**. Corrections mostly do not announce themselves. They report a
symptom instead: *"image quality looks low"*, *"the videos show no box"*, *"velocities look
really weird"*. And they are not rare: 17% of turns in one corpus, 39% in the other, a base
rate at which a filter concentrates almost nothing.

Recall is the number that matters here. A false positive is dropped during clustering; a
missed correction is gone for good.

| Claude Code corpus, n=87 | keyword filter | a model reading the same turns |
|---|---|---|
| precision | 0.57 | 0.52 |
| **recall** | **0.07** | **0.56** |

The Cursor corpus (n=97) gave the filter 0.70 precision and the same 0.07 recall. So capture
keeps everything and the selection happens later, once, where a model can read the turn next
to what it was answering. Most labels are a model's, spot-audited by hand: the first audit
returned kappa 0.51 and moved the boundary of what counts as a correction, and that pass is
part of the record. Method, labels and all three passes: [evals/honest](evals/honest/README.md).

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

- Automate what is cheap and reversible, gate what is expensive or irreversible. That single
  rule places every gate in both loops.
- Hooks surface and inform, and fail open. The one hard block, on reading secrets, is
  labelled as the speed-bump it is. Every hook's output shape is tested: JSON the host
  rejects is a hook that silently does nothing.
- Nothing reaches memory without approval.
- Orchestrate understand-anything rather than shipping a second graph engine.
- Measure the tool itself, and publish the result that goes against you.

MIT, see [LICENSE](LICENSE). Tests and ruff run in CI on Python 3.10 through 3.12.
