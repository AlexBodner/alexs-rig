# Evaluations

Three benchmarks, in order of how much to trust them.

## `evals/honest`: the detector against real turns

Real turns from your own Claude Code and Cursor transcripts, labelled with the detector's score
hidden, stratified by whether the detector fires and reweighted to the population. Wilson and
bootstrap intervals, an audit command that reports Cohen's kappa between two labellers, and a
write-up of every pass including the ones that went against the design. This is the evidence
behind the README's numbers. [evals/honest/README.md](honest/README.md)

```bash
python3 evals/honest/bench.py sample     # stratified sample of your own turns
python3 evals/honest/bench.py label      # blind, resumable
python3 evals/honest/bench.py score      # precision and recall with intervals
python3 evals/honest/bench.py audit      # spot-check another labeller, reports kappa
```

Everything it writes lands in `evals/private/`, which is gitignored.

## `evals/calibrate`: does injected memory change behaviour?

Runs each task twice through headless `claude`, plugin off and on, with a non-default rule in
the ON arm's L0 and a deterministic grader. The OFF arm cannot know the rule, so adherence
there is 0 by construction; ON-arm adherence is the memory working. Result: 3 of 3 rules
followed with the plugin, 0 of 3 without, at one repeat per cell. A strong read on a tiny
sample; add `--repeats` before quoting it. [evals/calibrate/README.md](calibrate/README.md)

## `evals/detector`: the synthetic benchmark, kept as a counter-example

24 paraphrased cases written by the detector's author, reporting 1.00 precision and 1.00
recall after the detector was widened until it passed them. That is tuning on the test set,
and the honest benchmark measured the same detector at 0.07 recall on real turns. It stays in
the tree so the failure mode has a name and a file.

## Rules

- Nothing from a real corpus is committed. Real cases live in `evals/private/`.
- Anything that calls a model takes a hard cost ceiling and reports what it spent.
- A number quoted anywhere in this repo traces to a pass described in one of these READMEs.
