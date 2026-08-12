# Agent prompt — iterate on Alex's Rig

Copy everything below the line into a **new agent session** with this repo as the workspace.

---

## Mission

You are improving **Alex's Rig** (architecture **locked** — read `docs/architecture.md`). Do not reopen locked decisions.

Read: `README.md`, `AGENTS.md`, `docs/architecture.md`, `docs/INTEGRATION.md`, `docs/practices.md`, `docs/usage.md`, `REVIEW.md`.

Run: `python3 -m unittest discover -s tests -v`

## Constraints

Same as architecture lock: UX first; no DiffEditor; L0 generated; mining auto-upserts named clusters (skip `other`); standing graph via understand-anything + codemap-py (never dump JSON into L0; do not fork those tools); no AI-Rig fork; Desktop preferred; commit when asked; push only if user asked.

## Backlog (post-lock polish — pick highest unfinished)

1. Mining quality — reduce `other` cluster noise; better evidence quotes  
2. Live SessionStart dogfood notes in `docs/spikes/`  
3. Optional Claude Diff & Edit spike notes  
4. Telemetry dashboard — **no** (out of scope unless user insists)

## How to work

Small commits; keep `docs/INTEGRATION.md` accurate if you add features; tests green; end with Done / Not done / How to try.
