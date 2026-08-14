# Calibrate — harness impact on quality & tokens (with/without ablation)

Measures the rig's *marginal* effect by running each task twice — plugin **disabled**
(baseline) and **enabled** (treatment) — and comparing behavior and token cost.
Self-contained (headless `claude`), no gated `claude plugin eval` needed.

```bash
python3 evals/calibrate/run.py                             # dry-run: plan + estimate, no spend
python3 evals/calibrate/run.py --run --budget-usd 3 --model claude-opus-4-8
```

## Design — test NON-DEFAULT preferences, grade deterministically

Generic "good practice" tasks (ask before pushing, stay minimal) measure ~nothing: a
modern model already does them, so the rig has nothing to add. The rig's real value is
enforcing preferences the model **wouldn't produce on its own** — so each task carries an
arbitrary rule (`tasks.json` → `rules`) injected into the **ON** arm's L0:

- name every function with a leading underscore,
- end each `def` line with `# rig`,
- return the string `'NOT_SET'` for not-found (never `None`).

Grading is **deterministic** (regex / substring per task) — objective, and free (no judge
model). The OFF arm can't know the rules, so its adherence ≈ 0 by construction; any ON-arm
adherence is the injected memory actually changing behavior.

## Result (3 tasks, 1 repeat, `claude-opus-4-8`)

| task | off (no rig) | on (rig) |
|------|:---:|:---:|
| underscore | 0/1 | 1/1 |
| rigcomment | 0/1 | 1/1 |
| sentinel   | 0/1 | 1/1 |

**Δadherence = +1.00 on every rule.** The rig makes the agent follow a standing preference
**100%** of the time that it follows **0%** of the time without it. Token overhead: the ON
calls cost ~$0.02 more than OFF (the always-on L0/graph/session injection) — ~2¢/session on
Opus. Run cost: ~$1.18.

**Honest bounds:** n=1 per cell — the effect is stark and the baseline ~0 by construction,
so it's a strong read, but add `--repeats` to confirm consistency. And this measures the
rig's value where it *should* pay off (non-default preferences); on generic practices the
marginal value really is ~0. So: store the preferences the model can't guess (your mined
principles, `P-style`), not generic best-practices.

## Cost & privacy

Each arm is a full headless agent session (~$0.20/call on Opus), so `--budget-usd` is a hard
ceiling and the default `--model` is cheap. Committed tasks are synthetic; put any
real-corpus cases in the gitignored `evals/private/`.
