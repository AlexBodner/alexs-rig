# Agent prompt — try Alex's Rig like a human

Copy everything below the line into a **new agent session** (Grok bots / Composer / Claude) with this repo as the workspace.

Goal: **dogfood the harness**, not rewrite it. Act as a daily user (Alex). Experience the loop. Report friction. Only fix something if it blocks you from finishing the try-out — and say what you changed.

---

## Who you are

You are trying **Alex's Rig** the way a human would on a Tuesday morning: open the repo, bootstrap, touch memory, skim L0, run mining, understand the review loop. You are **not** here to implement the backlog or redesign architecture unless something is broken enough that you cannot finish the walkthrough.

## Before you start

Read only enough to act:

1. `README.md` (Quick start + Daily loop)
2. `docs/usage.md`
3. `docs/workflow.md`

Skip `prompts/AGENT_ITERATE.md` — that is for a different job (improve the harness).

## Walkthrough (do these in order)

### 1. Verify the install

```bash
cd <this-repo>
python3 -m unittest tests.test_memory -v
chmod +x bin/* hooks/inject_l0.py scripts/bootstrap.sh 2>/dev/null || true
./scripts/bootstrap.sh
```

Note what bootstrap actually did vs asked you to do manually.

### 2. Use standing memory like a project owner

Treat this checkout as the project you care about today:

```bash
python3 bin/principle-upsert --id P-DOGFOOD --text "Prefer batch review (Desktop +N -M / IDE SCM) over stop-on-every-edit"
python3 bin/pending-upsert upsert --id T-DOGFOOD --priority P1 --text "Finish one real coding task with Plan → Edit auto → batch review"
python3 bin/progress-upsert --id F-DOGFOOD --status active --summary "Dogfooding Alex's Rig v0"
python3 bin/l0-regen
```

Then **read** `docs/memory/snapshots/L0.md` out loud in your summary (what a human would see at session start). Check that `hooks/inject_l0.py` emits something a SessionStart hook could inject.

### 3. Mine corrections (read-only accept)

```bash
python3 bin/mine-corrections --strong-only
```

Open:

- `docs/memory/mining/principle-candidates.md`
- `docs/memory/mining/patterns.md`

**Do not** call `principle-upsert` on candidates unless a candidate is clearly yours to accept for this dogfood session — and if you do, say why. Default: leave candidates for the human.

### 4. Simulate the daily coding loop (as far as the host allows)

Follow `docs/workflow.md`:

1. Prefer Claude Code **Desktop** if available; else VS Code Claude / Cursor with the same intent.
2. For a **tiny** non-trivial change inside this repo (e.g. a one-line docs clarification in `REVIEW.md` under “Dogfood notes”), use **Plan once → Edit automatically** mindset — not Manual stop-per-edit.
3. Review like a human: Desktop **`+N -M`** / Cmd+Shift+D, or IDE **SCM** / Git Tree Compare. Do **not** invent a custom DiffEditor.
4. **Do not commit or push** unless the human explicitly asked in this chat.
5. Park leftover work with `pending-upsert` and re-run `l0-regen`.

If Desktop / Claude plugin / extensions are unavailable in your environment, **say what you could not try** and what a human should click next. Do not fake those steps.

### 5. Optional: one real micro-task

If (and only if) steps 1–4 worked, pick **one** small improvement that made *your* dogfood smoother (typo in usage, missing chmod note, clearer L0 header). Keep it tiny. Re-run tests. Still no push unless asked.

## What to report back (required)

Write a short **Dogfood report** for the human:

### Done
- Commands you ran and whether they worked
- What L0 looked like after upserts
- Whether mining produced usable candidates or noise

### Felt like me / not like me
- Where the loop matched the README daily loop
- Where you got stuck, confused, or had to read source instead of docs

### Blocked (host / UI)
- Anything you could not verify (Desktop `+N -M`, plugin SessionStart, extensions)

### Should the human do next
- 3 concrete next clicks or commands for Alex — not a redesign

### Changed (if any)
- Files touched; say “none” if pure try-out

## Hard rules

- **UX first** — if docs and CLIs disagree, trust the docs for intent and report the gap.
- **No silent auto-PR / no push** without explicit ask.
- **Mining never auto-applies** principles.
- **Do not** start `AGENT_ITERATE.md` backlog work in this session.
- **Do not** fork or reimplement Borda AI-Rig skills here.
