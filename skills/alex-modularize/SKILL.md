---
name: alex-modularize
description: Plan where code should live before writing it — responsibilities, files, directories and the move order that keeps PRs clean, in the layout that fits the kind of project (published library, research repo, applied demo). Use before implementing a feature that adds more than one file, before refactoring layout, or when a review flags duplication or a class doing too much.
---

# Alex modularize (plan the structure first)

Structure decided while typing is structure nobody chose. This skill produces a
**file-by-file plan** you approve before any code moves — the recurring ask:

> "yes please. First plan the modules and what you are going to move file by file so that
> we dont miss anything and that prs stay clean"

Sibling skills: `alex-structure` reads the existing map, `alex-api` designs the public
surface. This one decides **where things live**.

## Input

- **goal** — what is being built or reorganised
- **constraints** — package boundaries, release order, what must not move yet
- **done_when** — the acceptance statement

## Workflow

### 1. Read the existing structure — never guess it

Query the codebase graph (`alex-structure`) or list the tree. Write down the convention
already in use *before* proposing anything, and name which kind of project it is (step 3)
— the same change lands differently in a published package than in a demo repo.

**Convention is not the same as drift.** `P-style` says match the repo's conventions, and
that holds for anything deliberate: naming, import idioms, how modules are split. It does
not extend to accumulated mess — root clutter, committed outputs, a directory that became
a dumping ground. When the existing layout *is* the problem, say so plainly and propose
the clean target instead of replicating it; that is the one case where this skill
overrides matching what is there.

### 2. Name the responsibilities

List every distinct job the change involves, in one line each. This is the Single
Responsibility pass and it is done in prose, before files exist. Two jobs that always
change together are one responsibility; one job that two callers need for different
reasons is two.

### 3. Place each responsibility — layout depends on the kind of project

There is no single tree. Identify which of these the repo is (look at what already exists;
do not impose the wrong one), then place responsibilities inside that shape.

**Published library** — `trackers`, `re-ID`. Someone installs it and imports it, so the
public surface and the boundary between concerns are the point.

```text
src/<package>/
  <concern>/            # core, cli, eval, io, datasets, annotators, utils…
    __init__.py         # the public exports of this concern
    base.py             # the abstraction, when there is more than one implementation
    <thing>.py          # one file per concrete implementation
    _helpers.py         # private to the concern, underscore-prefixed
tests/<concern>/        # mirrors the package tree
```

**Research repo** — `internal-signals-context-compression`. The load-bearing split is
**reusable method vs one-off exploration**, and mixing them is a review failure:

```text
src/                    # the method: what a result depends on, and what tests cover
experiments/            # one directory per experiment; scripts, configs, findings
knowledge-base/         # literature notes, decisions
tests/ · docs/ · scripts/
```

> A PR that "bundles a library change with three exploratory experiment suites" is two
> changes wearing one hat — the suites are the lab notebook that chose the variant,
> evidence rather than product.

**Applied / demo project** — a pipeline someone runs, not a package someone imports.
Top-level directories are **stages or deliverables**, not layers:

```text
common/                 # shared across stages
<stage>/                # player_stats, pass_alternatives, simulator, training, evaluation…
  run.py · render.py    # the entry points someone actually calls
scripts/ · docs/ · tests/
```

This is the shape that fits, **not a repo to copy**. The applied repos here
(`world_cup_projects`, `tpf_project`) drifted, and their drift is the useful part — these
are the failure modes to plan against, measured:

- **Docs and notes pile up at the root.** `tpf_project` has 34 loose root files
  (`FINDINGS.md`, `GCP_LAUNCH.md`, `DESIGN_DECISIONS.md`, `INSTRUCCIONES_GCP.md`…). Notes
  belong in `docs/`; the root holds README, LICENSE, config and nothing else.
- **Outputs get committed.** `tpf_project` versions 434 files under `data/` and results
  directories. Generated artifacts belong in `.gitignore` with the command that rebuilds
  them written down — a repo that carries its outputs cannot tell you which code produced
  them.
- **Tests never start.** `tpf_project` has none. An applied project still needs the few
  tests that pin the pipeline's contract, even if it will never be published.

Rules that hold in **all three** and decide the hard cases:

- **A subpackage starts when a thing needs a second file**, not before. One file is a
  module; do not create a directory for it.
- **A file earns its existence** by holding one responsibility someone would look for by
  that name. Splitting a 60-line module into three files is not modularity.
- **Depth follows the domain, not the call graph.** `core/botsort/tracker.py` because
  BoT-SORT is a thing; not `core/trackers/impl/v2/`.
- **Private by default** in a library; in a demo repo the equivalent is keeping the entry
  point obvious and the helpers beside it.
- **Tests mirror whatever shape the repo has** — the point is that a reader can guess the
  test path from the source path, not that it looks like `src/`.

### 4. Run the failure-mode checks

Each of these is a correction that has been made more than once — check them explicitly
and say what you found:

| check | the question | the correction behind it |
|---|---|---|
| **Duplication** | does this already exist in another module or sibling package? | *"we have general functions … duplicated with small changes that could be shared"* · *"why do we implement this protocol and not just import it from reid?"* |
| **Speculative abstraction** | is this base class earning its place today, or is it scaffolding for an imagined second case? | *"i didnt want to introduce another abstraction class, cant it be part of reid model?"* |
| **Wrong home** | would someone look for this here? | *"botsort tracklet went to tune folder instead of to botsort folder"* · *"isnt it kinda duplication and placed in the wrong places?"* |
| **Overloaded class** | is this class doing only its job? | *"ReIDTrainDataset has still too much code, is it implementing what it belongs to him?"* |
| **Name locks the input** | does the name describe the role, or today's data? | *"is reidcrops the correct name for that class?"* |
| **Old layer survives** | what does this replace, and is that being deleted in the same change? | *"lets remove the old layering and have the clean version"* |

SOLID applies where it earns its keep — SRP and dependency inversion usually do; an
interface with one implementation usually does not. The counterweight is `P-scope`: no
abstraction that today's code does not need.

### 5. Emit the plan

Two parts, both concrete:

**The target tree** — a plain directory listing with a one-line note per new or moved
file. Not a graph, not a diagram:

> "i need a better directory structure format because i cant really understand that graph"

**The move order** — numbered, each step one PR-sized unit, each stating what moves,
what imports break, and what gets deleted. Order so that every step leaves the repo
working: introduce, migrate callers, delete the old path.

### 6. Gate

Present the plan and **wait for approval** before moving anything. Then implement in the
stated order, one step per commit, so the diff of each step is readable on its own
(`P-diff`).

## Fail-fast

Stop and ask instead of guessing when: the change crosses a package boundary and the
release order matters; two existing modules already do the job and it is unclear which
is canonical; the plan would move a file that an open PR is also touching.

## After

Re-check the structure against the plan before calling it done — the same "explain the
whole structure and abstractions to see if there is still duplication" pass the user asks
for, done by you first.
