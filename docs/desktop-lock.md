# Desktop + architecture lock — human ritual

Agents cannot complete this. Do it on your Mac, then reply **architecture locked** (or list gaps).

## E1 — Desktop Plan → Edit → `+N -M` (required for lock)

1. Open **Claude Code Desktop** on https://github.com/AlexBodner/alexs-rig (this clone).
2. Install plugin if needed: `./scripts/install_claude_plugin.sh` (see [claude-plugin-install.md](claude-plugin-install.md)).
3. Mode: **Plan** once for a tiny change (e.g. one line in `REVIEW.md`).
4. Approve plan → **Edit automatically** (`acceptEdits`) — not Manual stop-per-edit.
5. After edits: click **`+N -M`** (or **Cmd+Shift+D** / Views → session diff).
6. Open ≥1 file diff. Note whether the pane is good enough for daily review.

Fill [spike-checklist.md](spike-checklist.md) E1 table.

## Live SessionStart

1. New Claude session on this repo after plugin install.
2. Confirm L0 / `<alexs-rig-l0>` in context (or ask what L0 contains).
3. If fail: smoke `python3 hooks/inject_l0.py` from repo root.

## E7 / E8 (IDE)

Box agents already passed SCM + Git Tree Compare. On your Mac: confirm the same; optional Claude Diff & Edit spike (E8).

## After E1 + SessionStart feel right

Reply in chat: **architecture locked** — then graduate proto naming/version as you like.
