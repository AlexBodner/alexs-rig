# Agent prompt — try Alex's Rig like a human

Copy everything below the line into a **new agent session** with this repo as the workspace.

Goal: **dogfood the harness**, not rewrite it. Act as a daily user. Report friction. Only fix something if it blocks the walkthrough — and say what you changed.

---

## Who you are

You are trying **Alex's Rig** the way a human would on a Tuesday morning: install, touch memory, skim L0, review in Source Control → Review. You are **not** here to implement the iterate backlog or redesign architecture unless something is broken enough that you cannot finish.

## Before you start

Read only: `README.md` (Quick start + Daily loop), `docs/HOW-TO.md`, `docs/workflow.md`.

Skip `prompts/AGENT_ITERATE.md`.

## Walkthrough (in order)

### 1. Install

```bash
cd <this-repo>
python3 -m unittest discover -s tests -v
./scripts/install.sh
```

`code` or `cursor` must be on PATH (or usual app locations). Review is a **vsix** — a folder copy is ignored. If `install.sh` **exits 1**, Review is not registered; put the CLI on PATH and re-run `./scripts/install_review_extension.sh`. On success, **Reload Window once** (not every session). Open this clone as the workspace (not a parent).

Note what the script did vs asked you to do.

### 2. Standing memory

```bash
python3 bin/principle-upsert --id P-DOGFOOD --text "Prefer batch review (Desktop +N -M / IDE Review Viewed) over stop-on-every-edit"
python3 bin/pending-upsert upsert --id T-DOGFOOD --priority P1 --text "Finish one real coding task with Plan → Edit auto → batch review"
python3 bin/progress-upsert --id F-DOGFOOD --status active --summary "Dogfooding Alex's Rig" --path .
python3 bin/l0-regen
L0="$PWD/docs/memory/snapshots/L0.md"
test -f "$L0" || { echo "missing L0 at $L0 — wrong cwd?"; exit 1; }
python3 hooks/inject_l0.py | python3 -c "import sys,json; d=json.load(sys.stdin); t=json.dumps(d); assert 'alexs-rig-l0' in t and 'alexs-rig-graph' in t"
```

Read the **absolute** `$L0` file. Do not open a relative `docs/memory/snapshots/L0.md` against a parent folder.

### 3. Mining (do not pollute L0)

```bash
python3 bin/mine-corrections --strong-only --no-apply
```

Read `docs/memory/mining/principle-candidates.md` and `patterns.md`. Do not upsert candidates unless one is clearly a standing preference.

### 4. Daily loop (as far as the host allows)

1. Prefer Claude Code Desktop if present; else Cursor / VS Code Claude.
2. Tiny change (e.g. one line under `REVIEW.md` Dogfood notes). Plan once → Edit automatically.
3. Review: Desktop **`+N -M`** if present. In the IDE: **Source Control → Review** — click a file (native diff), check **Viewed**. Edit the same file again; the box should uncheck. Do **not** invent a DiffEditor.
4. Do not commit or push unless the human asked.
5. Park leftovers with `pending-upsert` + `l0-regen`.

If Desktop / SessionStart / Review sidebar is unavailable, say what you could not try. Do not fake it.

## Report (required)

### Done
Commands; L0 after upserts; whether Review Viewed worked.

### Felt like a daily driver / not
Where HOW-TO matched reality; where you read source instead of docs.

### Blocked
Desktop `+N -M`, SessionStart, Review sidebar, login walls.

### Should the human do next
3 concrete clicks or commands — not a redesign.

### Changed
Files touched, or “none”.

## Hard rules

- UX first — docs win for intent; report CLI/doc gaps.
- No silent auto-PR / no push without explicit ask.
- Mining: `--no-apply` unless the human wants L0 writes.
- Do not start `AGENT_ITERATE.md`.
- Do not fork Borda AI-Rig.
