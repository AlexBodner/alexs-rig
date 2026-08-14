# Agent prompt — simulate proper daily usage (multi-PR project)

Copy everything below the line into a **new agent session** with https://github.com/AlexBodner/alexs-rig as the workspace (or a fresh clone).

This is **not** dogfood-only and **not** a bare verify suite. You will ship **several real feature PRs** while using Alex's Rig the way a human should on a real Tuesday: L0 → Plan → Edit → batch review → upsert → commit → PR.

---

## Mission

Act as a developer whose **standing memory and review habit** are Alex's Rig. Complete a multi-PR project using the harness tools on every non-trivial step. Success = good PRs **and** honest proof you used the Rig (not that you only coded).

### Default project (unless the human overrides in the chat)

**Target repo:** this alexs-rig checkout.  
**Epic:** land the next harness capabilities as **separate PRs** (one concern per branch):

| PR | Branch (suggested) | Scope |
|----|--------------------|--------|
| PR1 | `feat/mining-other` | Reduce mining `other` cluster noise; tests + `docs/mining.md` |
| PR2 | `feat/sessionstart-notes` | Live SessionStart dogfood notes in `docs/spikes/` (do not fake Desktop) |
| PR3 | `feat/prompt-sync` | Keep `prompts/AGENT_*.md` aligned with `install.sh` + Review vsix if you find drift |
| PR4 | `feat/review-empty-state` | Review view empty-state / CLI-not-found messaging only if you hit a real gap |

PR1–PR4 from older prompts (memory `--root`, bootstrap `--yes`, `l0-show`, CI) **already shipped** — do not rebuild them.

Do **PR1 → PR2 → PR3 → PR4** in order unless blocked. Prefer finishing 2–3 solid PRs over half-doing all four.

### Override

If the human names another repo or epic, use that instead — but **keep the Rig rituals below** unchanged.

## Hard constraints

1. Read `README.md`, `docs/workflow.md` (Daily loop), `docs/usage.md`, `docs/architecture.md` before coding.
2. **UX first**; no custom DiffEditor.
3. L0 = generated only; mining auto-upserts named clusters (skip `other`; `--no-apply` to disable). Query standing understand-anything / codemap-py graphs before blind Grep; never dump graph JSON into L0.
4. Do not fork/reimplement Borda AI-Rig skills inside this repo.
5. **Push / open PRs only if** the human’s paste explicitly allows it (see one-liner). Otherwise: commits on local branches + ready PR bodies in the final report.
6. One PR = one branch = one focused diff. No kitchen-sink branches.
7. Tests green on every PR that touches Python: `python3 -m unittest tests.test_memory -v` (and any new tests you add).

## Rig rituals (mandatory — this is the simulation)

### R0 — Session open (once)

```bash
cd <clone-root>    # workspace = clone, not parent
./scripts/install.sh      # needs code/cursor on PATH for Review vsix; else bootstrap.sh --yes + say Review skipped
# skim absolute L0:
test -f "$PWD/docs/memory/snapshots/L0.md" && sed -n '1,40p' "$PWD/docs/memory/snapshots/L0.md"
python3 hooks/inject_l0.py | head -c 400; echo
```

Then upsert epic standing state:

```bash
python3 bin/progress-upsert --id F-USAGE-SIM --status active --summary "Simulate proper Rig usage via multi-PR epic" --path .
python3 bin/pending-upsert upsert --id T-PR1 --priority P1 --text "PR1: mining other-cluster noise"
python3 bin/pending-upsert upsert --id T-PR2 --priority P1 --text "PR2: SessionStart dogfood notes"
python3 bin/pending-upsert upsert --id T-PR3 --priority P2 --text "PR3: keep AGENT_* prompts in sync"
python3 bin/pending-upsert upsert --id T-PR4 --priority P2 --text "PR4: Review empty-state only if a real gap"
python3 bin/l0-regen
```

### R1 — Per PR (repeat for each)

1. **Plan** in chat (short): goal, files, out-of-scope, test plan. Do not start coding until the plan is written.
2. `git checkout main && git pull --ff-only` (if remote available) → `git checkout -b <branch>`.
3. Implement with **Edit automatically** mindset (batch changes; no theatrical stop-per-file).
4. **Batch review before commit:**
   ```bash
   git status
   git diff
   # IDE: Source Control → Review (Viewed). Else git diff. No custom DiffEditor.
   ```
5. Run tests; fix until green.
6. **Memory bookkeeping before commit:**
   ```bash
   python3 bin/progress-upsert --id F-USAGE-SIM --status active --summary "…what’s true now…" --path .
   python3 bin/pending-upsert done --id T-PRN    # the one you finished
   # park leftovers:
   python3 bin/pending-upsert upsert --id T-… --priority P2 --text "…"
   python3 bin/l0-regen
   sed -n '1,50p' "$PWD/docs/memory/snapshots/L0.md"
   ```
7. Commit on the feature branch (clear message). Include code + docs + tests. Prefer **not** committing noisy `docs/memory/mining/*` unless the PR is about mining.
8. If authorized: `git push -u origin HEAD` and `gh pr create` with Summary + Test plan. If not: leave branch local and paste a ready PR body in the report.
9. Merge only if the human asked. Default: leave PRs open / branches unmerged.

### R2 — Between PRs

Skim L0 again. Start the next pending `T-PR*`. Do not pile PR2 work onto PR1’s branch.

### R3 — Session close

```bash
python3 bin/mine-corrections --strong-only   # real ~/.cursor if present; else note empty-host honesty
# Do NOT principle-upsert candidates unless human accepted text in chat
python3 bin/l0-regen
```

Write the **Usage simulation report** (below).

## What “proper usage” means (grade yourself)

You **fail the simulation** (even if code is good) if you:

- Never read/update L0 during the session
- Ship multiple unrelated concerns on one branch
- Skip `git diff` / batch review before commit
- Auto-apply mining candidates
- Claim Desktop `+N -M` without doing it

You **pass the simulation** if each merged-or-opened PR has: plan → diff review → tests → pending/progress/`l0-regen` → commit → (optional) PR.

## Final report (required)

```text
Usage simulation — Alex's Rig
Host / commit base: …
Authorization: push/PR yes|no

## Rig fidelity
- L0 skimmed at open: Y/N
- Pending used as task board: Y/N
- Batch review before each commit: Y/N (how)
- Mining: ran / empty host / skipped — candidates auto-applied? N

## PRs
For each: branch, title, URL or “local only”, tests, 1–3 bullet summary

## L0 after session
Paste first ~40 lines of docs/memory/snapshots/L0.md

## Human next
What only a human should do (Desktop review, merge buttons, accept principles)
```
