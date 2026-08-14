# Agent prompt — own computer + GUI (clone from GitHub)

Copy everything below the line into a **new** agent that has a real desktop (terminal + mouse). Workspace need not exist yet.

---

You have your own computer with GUI control. Install and use **Alex's Rig** like a human on a Tuesday morning, then report friction. Do not rewrite the product, open PRs, or start a backlog.

Repo: https://github.com/AlexBodner/alexs-rig
Branch: `main` (v0.1.5 or later)
After clone, humans start at `docs/HOW-TO.md`.

## Hard rules

- Do not push, force-push, or open PRs.
- Do not commit unless a local commit is the only way to finish a check — if you commit, say so and do not push.
- Do not invent a custom DiffEditor.
- Do not fork Borda AI-Rig or start `prompts/AGENT_ITERATE.md`.
- If a GUI step is impossible, mark it BLOCKED. Do not fake it.
- Reload Window only after install or a vsix update — not every chat.

## 1. Install

```bash
git clone https://github.com/AlexBodner/alexs-rig.git
cd alexs-rig
./scripts/install.sh
```

`code` or `cursor` must be on PATH (or usual app locations). Review is a **vsix**; a folder copy is ignored. If `install.sh` exits 1, put the CLI on PATH and re-run `./scripts/install_review_extension.sh`. On success, **Reload Window once**. Open the **clone folder** as the workspace (not a parent).

Prefer Cursor if both exist; also try Claude Desktop if installed.

## 2. Read only enough

`README.md`, `docs/HOW-TO.md`, `docs/workflow.md`. Follow HOW-TO. If docs and CLIs disagree, trust docs for intent and report the gap.

## 3. Memory

```bash
python3 -m unittest discover -s tests -v
python3 bin/principle-upsert --id P-DOGFOOD --text "Prefer batch review (Desktop +N -M / IDE Review Viewed) over stop-on-every-edit"
python3 bin/pending-upsert upsert --id T-DOGFOOD --priority P1 --text "Finish one tiny task with Plan → Edit auto → batch review"
python3 bin/progress-upsert --id F-DOGFOOD --status active --summary "Dogfooding Alex's Rig" --path .
python3 bin/l0-regen
python3 hooks/inject_l0.py
```

Open the absolute `$PWD/docs/memory/snapshots/L0.md`. Quote what a human would see. Confirm inject JSON has `alexs-rig-l0` and `alexs-rig-graph` (pointer only).

## 4. Live session (required if the host can)

New Cursor or Claude chat in this folder. Ask: “What does my L0 say?” Report whether L0 appeared without pasting. Login walls = BLOCKED, not FAIL-the-product.

## 5. Review Viewed

Tiny harmless docs tweak (e.g. dated Dogfood notes on `REVIEW.md`). Plan once → Edit automatically.

- Desktop: `+N -M` if present.
- IDE: Source Control → Review. Click file → native diff → check Viewed. Edit the same file → box unchecks.
- PR toolbar: only if this branch has a PR.

Do not commit.

## 6. Mining

```bash
python3 bin/mine-corrections --strong-only --no-apply
```

Say whether candidates are useful or empty-host honest. Do not upsert junk.

## 7. Report

### Done
Install, tests, L0, Viewed check/uncheck.

### Felt like a daily driver / not
Specific clicks that matched or missed HOW-TO.

### Blocked
Login, missing Review view, no Desktop.

### Should Alex do next
3 clicks or commands.

### Changed
Files, or none.

Tone: blunt, specific, UX first.
