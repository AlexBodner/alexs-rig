# Desktop ritual (post-lock)

Architecture is **locked**. This page is the habit reminder, not a freeze gate.

## Daily

1. Open the **clone folder** as the workspace.
2. Claude Code **Desktop**: Plan → Edit automatically → click **`+N -M`** (or Cmd+Shift+D) as a map of what changed.
3. For OSS / ship: read the real files or full git/PR diff in the IDE as you already do.
4. Park standing state with upserts → `l0-regen` / `l0-show`.
5. Commit / PR only when you ask the agent.

## SessionStart

```bash
./scripts/install_claude_plugin.sh
```

New session should carry L0 (+ SESSION_BASE). Smoke: `python3 hooks/inject_l0.py`.
