# Claude Code — Alex's Rig

@AGENTS.md

Claude-specific (not for other agents):

- SessionStart / PreCompact hooks inject L0 + a **graph pointer** (not the graph JSON). Smoke: `python3 hooks/inject_l0.py`.
- Desktop review surface is **`+N -M`** / Cmd+Shift+D, not CLI `/diff`.
- Plugin root is `${CLAUDE_PLUGIN_ROOT}`. Install: `./scripts/install_claude_plugin.sh`.
- Personal overrides: `CLAUDE.local.md` (gitignored).
