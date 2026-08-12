# Claude Code — Alex's Rig

@AGENTS.md

Claude-specific (not for other agents):

- SessionStart / PreCompact / UserPromptSubmit / Stop / PreToolUse — see [docs/hooks.md](docs/hooks.md). Smoke: `python3 hooks/inject_l0.py`.
- Desktop review surface is **`+N -M`** / Cmd+Shift+D, not CLI `/diff`.
- Plugin root is `${CLAUDE_PLUGIN_ROOT}`. Install: `./scripts/install_claude_plugin.sh`.
- Personal overrides: `CLAUDE.local.md` (gitignored).
