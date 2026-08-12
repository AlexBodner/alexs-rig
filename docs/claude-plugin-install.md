# Claude plugin install — SessionStart L0

Goal: when a Claude Code session starts on a project that has `docs/memory/snapshots/L0.md`, the SessionStart hook injects `<alexs-rig-l0>…</alexs-rig-l0>` into context.

## Quick path

```bash
cd /path/to/alexs-rig
chmod +x scripts/install_claude_plugin.sh
./scripts/install_claude_plugin.sh
```

Then **restart** Claude Code Desktop (or VS Code Claude) and open a project that already has memory (or this repo after bootstrap).

## Smoke without Desktop

```bash
cd /path/to/project-with-memory
python3 /path/to/alexs-rig/hooks/inject_l0.py | python3 -m json.tool | head
```

Expect JSON with `hookSpecificOutput.additionalContext` containing `alexs-rig-l0`, your L0 body, and `alexs-rig-graph` (pointer only — not the graph JSON).

## Hook wiring

`hooks/hooks.json` (Claude):

```json
"SessionStart" → python3 "${CLAUDE_PLUGIN_ROOT}/hooks/inject_l0.py"
```

`inject_l0.py` walks from **cwd** upward for `docs/memory/snapshots/L0.md` (project memory), then falls back to the plugin checkout’s L0.

## Live Desktop / VS Code Claude check (human)

1. Install plugin (script above or Claude `/plugin` UI → local path = this repo).
2. Open project folder that owns the memory (not a parent `/workspace`).
3. Start a **new** Claude session.
4. Confirm L0 principles appear in session context (or ask: “What does my L0 say?”).
5. If missing: run the smoke command from that project’s cwd; fix path / reinstall plugin.

## Notes

- Claude Code expands `${CLAUDE_PLUGIN_ROOT}` per plugin — do not replace with Cursor’s `cursor-invoke.sh` pattern.
- Multi-project memory: generate L0 in each project via `bin/l0-regen --root /path/to/project` (or `ALEXS_RIG_MEMORY`).
