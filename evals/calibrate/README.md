# Calibrate — harness impact on quality & tokens (with/without ablation)

Measures the rig's *marginal* effect by running each task twice — plugin **disabled**
(baseline) and **enabled** (treatment) — and comparing graded quality and token cost.
Self-contained (headless `claude`), no gated `claude plugin eval` needed.

```bash
python3 evals/calibrate/run.py                          # dry-run: plan + estimate, no spend
python3 evals/calibrate/run.py --run --budget-usd 0.50  # real run, hard cost ceiling
```

- Dry-run by default; `--run` requires a positive `--budget-usd`.
- Both arms + the grader use a cheap model by default (`--model`, `--judge-model`).
- Tasks are **synthetic** (`tasks.json`) — no real conversations. Reports print locally.

## What the first run taught us (read before trusting numbers)

A 4-task, single, `haiku` run showed **~0 quality delta and a small token overhead**
(+~$0.003/task for the always-on L0). That result is **not evidence the rig doesn't
help** — it's a measurement-design problem:

- **n=4, one run, binary grader → noise dominates.** A single task flip swung the mean.
  Real numbers need more tasks and **repeats** to average variance.
- **The starter tasks test *generic* good practices** (ask before pushing, use a branch,
  raise on bad input) that a modern base model **already does without the rig** — so the
  baseline scored well and the principles had nothing to add. To measure the rig's real
  value, tasks must encode **non-default / project-specific** preferences the model would
  *not* guess (e.g. an arbitrary convention that only lives in L0).
- **`haiku` may use injected principles differently than the model you actually run.**

So: treat `tasks.json` as a *starting point*, add non-default-preference cases, run with
repeats on your real model, and set a budget. The token-overhead figure is the one
credible read from a cheap run; the quality figure needs the above to mean anything.

## Cost & privacy

Each arm is a full headless agent session, so a run costs more than a bare API call
(the trial hit ~$0.50). `--budget-usd` is a hard ceiling. Keep committed tasks synthetic;
put any real-corpus cases in the gitignored `evals/private/`.
