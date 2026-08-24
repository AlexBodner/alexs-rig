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

## Replay cases (`cases.py`) — extract, but do not run yet

`cases.py` mines real history for triples **(your prompt → what the agent did → your
correction)**. The correction is the ground truth: it names what went wrong on real work
of yours, so a case can be replayed with the harness on and off and graded on whether the
failure is avoided. Much better construct validity than the arbitrary-rule ablation.

```bash
python3 evals/honest/cases.py --write
```

Two findings from building it, both of which gate running it:

**1 · Leakage.** Roughly half the cases are `seen`: an L0 principle was *derived from that
very correction*. Replaying those measures whether a stored principle gets applied on real
work — worth knowing, but it is **not** evidence of generalisation. Only `unseen` cases
support that claim, and there are few of them.

**2 · The case set is noisy, because the detector's precision is unknown.** Cases are
selected by the detector firing on the third turn, so a follow-up instruction ("now
continue with X") is picked up alongside a genuine correction. Inspecting the current
`unseen` set, several are next-task instructions rather than corrections of a failure.

**So the order matters:** run the blind labelling first (free), keep only the turns you
labelled as genuine corrections, and *then* replay that clean set. Replaying the noisy set
would spend money grading cases where nothing was wrong in the first place.

Extraction also filters host-injected text, skill loads, compaction summaries and our own
headless eval runs — all of which showed up as fake "corrections" in the first pass.

## Result (Claude labels, audited by Alex — kappa 0.51, recalibrated)

| | synthetic bench | honest bench |
|---|---|---|
| precision | 1.00 | **0.73** [0.56–0.86] |
| recall | 1.00 | **0.04** [0.02–0.05] |

The detector catches roughly **4% of real corrections**. The synthetic benchmark claimed
100% because its cases were stereotyped ("no, don't use recursion"); real corrections in
this corpus mostly are not. They are challenging questions ("how did we get to step 84 so
fast? it must be skipping a lot"), contradictions from project knowledge ("me sonaba que
estabamos como en 30/40 frames maximos") and judgements on output ("this looks worse than
the one before") — often in Spanish, rarely with an explicit negation cue. The detector is
negation-centric and English-centric.

Estimated base rate of corrections: **~43% of turns**, not the ~2% the detector fires on.

**These labels were produced by Claude, which also wrote the detector — the exact
circularity this benchmark exists to avoid.** Treat the number as provisional until
audited:

```bash
python3 evals/honest/bench.py audit -n 20
```

It hides the existing label, asks for yours, and reports agreement plus Cohen's kappa.
Above ~0.7 the existing labels are credible; below that, relabel with `label` instead.

The boundary matters more than the sample size here: the labeller counted instructions
carrying a standard ("validate all changes", "mark it None and handle it when averaging")
as corrections. A stricter definition raises recall substantially. Whatever definition you
settle on, state it next to the number.

### After the audit

The first pass was labelled by Claude and audited blind by Alex on 29 items: **76%
agreement, Cohen's kappa 0.51** — below the credibility threshold, and all 7
disagreements pointed the same way (Claude said correction, Alex said not). The bias was
systematic: Claude counted **challenging technical questions** as corrections. Alex's
boundary is narrower — a correction is an explicit **rejection or override** of what the
agent did, not a question, a request for explanation, or a new instruction.

Rescored with Alex's audited labels taking precedence and the rest recalibrated to that
boundary:

| | wide boundary | Alex's boundary |
|---|---|---|
| precision | 0.73 | **0.57** [0.39–0.73] |
| recall | 0.04 | **0.05** [0.03–0.10] |
| base rate | 43% | **22%** |

**The conclusion is robust to the definition**: recall is ~5% either way. Precision drops
to 0.57 — nearly half of what fires is not a correction.

### What this says about the design, not just the detector

The two-stage design rests on "corrections are rare, so detect cheaply and generalise
rarely". **That premise is false**: corrections are ~22% of turns, not ~2%. A filter with
5% recall and 57% precision concentrates only 2.6× over the base rate while missing 95%
of the signal. When the target is not rare, filtering at capture time buys little — it is
probably better to keep recent turns wholesale and let the flush pass, which already runs
an LLM, do the selection.

Remaining caveat: 58 of the 87 labels are still Claude's, recalibrated to Alex's boundary
but not re-audited. A second `audit -n 20` round would confirm whether kappa has moved
above 0.7.

## Regex vs LLM on the same ground truth

`llm_classifier.py` runs an LLM over the *same* labelled turns, so the two are directly
comparable rather than measured on different sets:

| | precision | recall | F1 |
|---|---|---|---|
| regex detector | 0.57 | 0.05 | 0.10 |
| LLM (haiku, batched) | **0.71** | **0.59** | **0.65** |

Twelve times the recall, and better precision too — the regex was both missing signal and
admitting noise. Measured cost: **$0.23 for 87 turns → ~$0.78 per 300-turn flush**. (An
earlier estimate of "a few cents" was wrong by ~15×: every `claude -p` is a full agent
session, not a bare API call. Batching is what keeps it affordable — one session per ~18
turns instead of one per turn, which would have cost ~$17.)

Caveats that travel with these numbers:

* **Correlated bias.** 58 of the 87 labels are Claude's and the classifier is also Claude,
  so an LLM is partly being judged against LLM labels. Alex's 29 audited labels anchor it,
  but the comparison flatters the LLM to an unknown degree.
* **0.59 recall is not good**, only much better. Four corrections in ten are still missed.
* The regex numbers come from the same reweighting, so the *ratio* is the trustworthy part.

**Design consequence:** filtering at capture time is not worth it. Corrections are ~22% of
turns, so a prefilter concentrates at most 1.7× while discarding half the signal; the
measured alternative is to keep turns wholesale and let the flush — which already pays for
a model — do the selection.

### Third pass: intensive re-review with before/after context

After the audit returned kappa 0.51, the remaining Claude labels were re-done with much
richer context — the full agent turn before, and **the agent's reply after**, which is
strong behavioural evidence: if the reply concedes and reverses, the turn was a correction;
if it just answers, it was a question. Five labels changed.

That surfaced the distinction the first pass was missing. A correction rejects the **work
or the deliverable**. It is *not*:

* a **technical disagreement** — *"un frame latente también debería poder estimar la
  velocidad"* (Alex: 0), even though the agent conceded the point;
* a **confirmation** read as a challenge — *"me sonaba que estabamos como en 30/40 frames"*,
  where the agent replied *"tu memoria está bien y coincide"*;
* a **new instruction** about the deliverable — *"in the results table I would put …"*.

But it **is** an assertion about what is wrong, even in question form: *"what maybe is
happening is that adaptive doesn't have an identity threshold…?"* (Alex: 1).

| pass | base rate | precision | recall |
|---|---|---|---|
| v1 — quick, wide boundary | 43% | 0.73 | 0.04 |
| v2 — recalibrated after the audit | 22% | 0.57 | 0.05 |
| **v3 — intensive, with after-context** | **16.6%** | **0.57** | **0.07** |

**The headline is stable across all three**: recall 0.04–0.07. What moved was the base rate
— how many corrections exist — not the fraction the detector catches.

Rescored against v3 labels, the LLM comparison holds:

| | precision | recall | F1 |
|---|---|---|---|
| regex | 0.57 | 0.07 | 0.13 |
| LLM (haiku, batched) | 0.52 | **0.56** | **0.54** |

Eight times the recall at slightly worse precision — the right trade for a flush, where
false positives fall out during clustering and human approval while missed corrections are
gone for good. The baseline is now recomputed from the live labels instead of quoted, so
these two lines can never drift apart again.

**Still outstanding:** 58 of 87 labels are Claude's v3 pass, un-audited. `audit -n 25`
samples only those.
