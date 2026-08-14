# Evaluating & benchmarking Alex's Rig

Two tiers, chosen to keep **cost near zero** and **your conversations private**.

## Tier 1 — deterministic benchmarks (free, no tokens, no real data)

Whatever is pure logic gets benchmarked deterministically. No model is called.

```bash
python3 evals/detector/bench.py
```

The **correction-capture detector** is a Python heuristic, so we score it against a
**synthetic** labeled set (`evals/detector/dataset.jsonl` — paraphrased patterns, not
anyone's real turns) and report precision / recall / F1 at the capture threshold, for
both `pending=False` (text only) and `pending=True` (fresh unreviewed edits present).

Current result (24 synthetic cases):

| context | precision | recall | f1 |
|---------|-----------|--------|----|
| text only        | 1.00 | 0.58 | 0.74 |
| + pending edits  | 1.00 | 0.67 | 0.80 |

Read: the detector is **precision-first** (no false positives) but misses corrections
that don't open with "no,"/"actually," etc. Use this to tune signals/threshold — raising
recall trades away precision.

## Tier 2 — LLM evals (cost tokens — opt in, budgeted)

For behavior that genuinely depends on the model (skills, and the *effect* of memory),
Claude Code's native runner scores cases against the plugin, with a no-plugin baseline:

```bash
claude plugin eval alexs-rig@alexs-rig \
  --ablation with-without \   # measures the rig's marginal value vs no plugin
  --judge-model haiku \       # cheap grader
  --max-cost-usd 0.50 \       # hard ceiling — aborts if breached
  --no-publish                # keep the report LOCAL, never upload
```

Guardrails (non-negotiable here):

- **Privacy** — eval cases committed to this repo are **synthetic only**. Any benchmark
  built from your real corpus lives in `evals/private/` (gitignored) and never leaves your
  machine. `--no-publish` keeps reports local.
- **Cost** — always pass `--max-cost-usd` and keep the case count small; each case runs the
  agent twice under `--ablation`. Prefer Tier 1 wherever the thing under test is deterministic.

No LLM eval cases ship yet — add them under `evals/<skill>/` when a specific skill is worth
the spend.
