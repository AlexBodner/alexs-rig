# Claude Code notes

@AGENTS.md

- Hooks: SessionStart (also fires after compaction with `source: compact`), UserPromptSubmit,
  PreToolUse, Stop. Map and output contract: [docs/hooks.md](docs/hooks.md).
- Plugin root is `${CLAUDE_PLUGIN_ROOT}`. Install: `./scripts/install_claude_plugin.sh`.
  A same-version cache is never refreshed: bump `.claude-plugin/plugin.json` to ship.
- Personal overrides: `CLAUDE.local.md` (gitignored).
