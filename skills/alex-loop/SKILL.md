---
name: alex-loop
description: One entry point for a whole task — classify it, research if needed, plan, attack the plan adversarially, then hand off to the right build skill and surface only the polished result. Three gates: the plan, the PR, and any expensive compute. Use to take a task end to end; the individual skills stay callable on their own.
---

# Alex loop (plan → attack → build → review)

Composes skills that already exist. It does **not** reimplement planning, TDD, review or
research — if you want one step, call that skill directly (`/plan`, `/feature`, `/fix`,
`/refactor`, `/develop:review`, `/research:topic`). This is the seam between them plus a
gate policy in one place.

**The policy, and the reason for every choice below:** automate what is cheap and
reversible; gate what is expensive or irreversible. There are exactly three gates, and
each sits where a mistake is still cheap — before code, before publishing, before spending.

## Input

- **task** — what to do, in the user's words
- optional **--no-research**, **--no-challenge** (mirrors `CHALLENGE_ENABLED=false`)

## Workflow

### 1. Classify (silent)

Decide, and say the verdict in one line when you reach the gate — not before:

| signal | route |
|---|---|
| new capability | `feature` |
| something is broken | `fix` (or `debug` first if the cause is unknown) |
| structure/behaviour-preserving | `refactor` |
| the task rests on a method, paper or SOTA question | `research:topic` **first**, then the above |

Skip research when the answer is in this repo rather than in the literature — a search that
tells you what you already have is waste.

### 2. Gather context (silent)

`alex-structure` or the codebase graph. Never blind-grep for architecture.

### 3. Plan (silent)

Run `plan`, and compose the design skills the task actually needs:

- structure or file layout changes → **`alex-modularize`**
- a library's public surface → **`alex-api`** (on a library change these two are one decision)
- a document or report is the deliverable → **`alex-docs`**
- a visual deliverable → **`alex-viz`**

### 4. Attack the plan (silent)

Spawn `foundry:challenger` **on the plan**, before any code exists:

> "Challenge this plan across all 5 dimensions: Assumptions, Missing Cases, Security Risks,
> Architectural Concerns, Complexity Creep. Apply the mandatory refutation step."

Fold surviving findings into the plan. This is the step that makes the gate worth the
user's attention: what reaches them has already been attacked and self-refuted, not a first
draft. `feature`/`fix` run their own challenger later on the *implementation*; this one runs
earlier, on the *decision*.

### 5. 🚦 Gate 1 — the plan

Present, and **wait**:

- the route chosen, one line
- the plan: what changes, in what order, each step leaving the repo working
- for a library, the **call site** the user would type against it
- **what the challenger found**, and how the plan absorbed it
- **risks that remain** — open PRs touching the same files, migrations, anything irreversible

### 6. Build (silent)

Hand the approved plan to `feature` / `fix` / `refactor`. They already run the TDD loop, the
quality stack and `develop:review`, and close the gaps they find — do not duplicate any of
that here, and do not narrate it.

### 7. 🚦 Gate 2 — the result

Never open a PR without asking (`P-autonomy`). Weight the report by what happened:

- **review clean, tests pass** → one line of what changed and what was run, then "open the PR?"
- **anything found** → the full picture: session-scoped diff, what was actually run and
  inspected (`P-exercise`), findings and how each was resolved, what is still open

### 🚦 Gate 3 — expensive compute, whenever it appears

The moment the work needs paid compute, stop and apply `P-run`: validate on a free local
case first, then state instance, VRAM and cost. This gate is not a step in the sequence —
it fires wherever it arises, including mid-build.

## Fail-fast

**Stop and ask; never retry in a loop.** Handing a task back and forth between agents until
it converges is the documented failure mode of these architectures, and it burns budget
while drifting from the goal. Stop when: the plan needs a decision only the user can make;
a build step fails twice the same way; the challenger raises a blocker that changes the
goal rather than the approach.

## Escape hatches

- Every sub-skill stays callable alone; this skill is a convenience, not a gatekeeper.
- The plan persists in `.plans/active/`, so an interrupted run resumes without re-deriving.
- `--no-challenge` skips step 4 when the task is small enough that the attack costs more
  than the mistake would.
