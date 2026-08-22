# Honest detector benchmark — real turns, blind labels

The synthetic benchmark in `evals/detector/` reports precision 1.00 / recall 1.00, and
that number should not be trusted: the same author wrote the detector **and** its test
cases, and after measuring recall 0.67 the detector was widened until it passed **the
same 24 cases**. That is tuning on the test set. This benchmark exists to replace it
with a number that survives scrutiny.

## What makes it honest

| problem in the synthetic bench | what this does instead |
|---|---|
| cases invented by the detector's author | real turns from your own Claude Code transcripts |
| tuned on its own test set | Claude Code history was never used to fit the detector (signals came from Cursor history + synthetic cases), so the whole pool is held out |
| author also labels | **you** label, and the detector's score is never shown while labelling |
| deictic turns judged without context | each turn is shown next to the agent turn it replies to |
| rare positives ignored | stratified sampling by whether the detector fires, reweighted to the population |
| results could leak private work | everything lands in `evals/private/` (gitignored) |

## Run it

```bash
python3 evals/honest/bench.py sample   # stratified sample -> evals/private/sample.jsonl
python3 evals/honest/bench.py label    # blind labelling, resumable ([q] saves and quits)
python3 evals/honest/bench.py score --examples
```

Roughly 90 turns to label, a few seconds each. `label` is resumable, so it can be done
in passes.

## Design

Corrections are **rare** — the detector fires on ~2% of turns. A uniform sample would
be almost all negatives and would estimate recall terribly. So the pool is split into
two strata:

* **fires** (score ≥ threshold) — small, so it is labelled as a **census**: no sampling
  error on the precision side.
* **quiet** (below threshold) — large, so a random sample stands in for it.

Estimates are then reweighted to population size: precision is the positive rate inside
*fires*; recall compares estimated true positives against the estimated corrections
hiding in *quiet*. Precision gets a Wilson interval, recall and F1 a bootstrap over the
labelled turns.

## Limitations (state these with the numbers)

* **The `pending` signal cannot be replayed.** Whether unreviewed edits existed at that
  moment depends on git state that is gone, so this measures the **text-only** detector.
  Live behaviour is at least this good, never worse.
* **One labeller, not blind to the project.** You know your own turns; there is no
  second annotator and no inter-annotator agreement.
* **"Correction" is a judgement call.** The definition shown while labelling is the
  whole spec; a different reading would move the numbers.
* **Same person authored the corrections and the labels.** Independent of the detector,
  but not independent of the correction style itself.
* **Sample size.** ~31 firing turns caps how tight the precision interval can get; the
  reported CI is the honest width, not a rounding error.
