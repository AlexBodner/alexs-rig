# Agent prompt — iterate on Alex's Rig

Copy everything below the line into a **new Grok / Composer / Claude** agent session (or Grok bots app) with this repo as the workspace.

---

## Mission

You are improving **Alex's Rig**, a public personal harness for Claude Code + IDE review + standing L0 memory.

Read first (in order):

1. `README.md`
2. `docs/architecture.md`
3. `docs/usage.md`
4. `docs/workflow.md`
5. `REVIEW.md` (known gaps)

Then run:

```bash
python3 -m unittest tests.test_memory -v
```

Do not claim success if tests fail.

## Product constraints (do not violate)

1. **UX first** — tomorrow-morning test; simple, reviewable, understandable.
2. **No custom DiffEditor** unless native Desktop `+N -M`, SCM, Git Tree Compare, and Claude Diff & Edit all fail a documented spike.
3. **L0** = generated snapshot only; upsert by id; overflow = distill/warn, never silent truncate; no SUPERSEDED in L0.
4. **Mining** proposes candidates only — never auto-`principle-upsert` without explicit user accept in the task.
5. **AI-Rig** (Borda) remains how-to-build; do not fork or reimplement develop/foundry/oss inside this repo.
6. **Hosts:** Desktop preferred; keep Claude plugin/skills compatible with VS Code Claude; IDE for uncommitted/PR review.
7. **Commits:** agent may commit when the user asks; no silent auto-PR.
8. **Public GitHub:** only mutate remotes if the user explicitly asked to publish/push in this session.

## Priority backlog (pick the highest unfinished item)

Unless the user specifies otherwise, work top-down:

1. **Multi-project memory root** — add `ALEXS_RIG_MEMORY` or `--root` so CLIs operate on any project’s `docs/memory/` (not only this repo). Update `docs/usage.md` + tests.
2. **Bootstrap DX** — non-interactive `./scripts/bootstrap.sh --yes` to install recommended extensions when `cursor`/`code` CLI exists; document manual path otherwise.
3. **Claude plugin install docs** — exact steps for Desktop + VS Code Claude local plugin install for *this* repo layout; verify SessionStart hook shape against current Claude Code docs.
4. **Mining quality** — reduce `other` cluster noise; optional `--since` date; write a short `docs/mining.md`.
5. **IDE uncommitted review** — document the winning extension path from spikes; if gaps remain, thin skill that opens `git diff` / multi-diff — still no fat DiffEditor.
6. **Agent-facing CI** — GitHub Action running `unittest` on push (only if repo is on GitHub).

## How to work

- Prefer small commits with clear messages.
- Keep Markdown prose unwrapped (one line per paragraph) per project style if editing AI-Rig-related docs; in this repo, stay consistent with existing files.
- After code changes: run `python3 -m unittest tests.test_memory -v`.
- Update `README.md` / `docs/usage.md` when behavior changes.
- End with a short **Done / Not done / How to try** summary for the human.

## Out of scope unless user insists

- Understand-anything as always-on agent memory  
- OpenClaw-scale bootstrap  
- Beads / OpenSpec day one  
- Rewriting Borda AI-Rig  

## Success criteria for a turn

- Tests green  
- Docs match behavior  
- User can follow `docs/usage.md` without reading chat history  
- No violation of product constraints above  
