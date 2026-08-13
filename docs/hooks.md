# Hooks — what fires, how to test

Alex's Rig uses **five** Claude Code events (Cursor names in parentheses). Not the full catalog.

| Event | Script | What |
|-------|--------|------|
| `SessionStart` (`sessionStart`) | `inject_l0.py` | L0 + graph pointer + `SESSION_BASE`; clears Stop reminder |
| `PreCompact` (`preCompact`) | `reinject_l0.py` | L0 + graph again after compact |
| `UserPromptSubmit` (`beforeSubmitPrompt`) | `prompt_l0_miss.py` | One line **only if this project has no L0** — never dumps L0 |
| `PreToolUse` Bash/Write/Edit (`Shell\|Write\|StrReplace`) | `secret_hygiene.py` | Deny cat/write of `.env` / keys |
| `Stop` (`stop`) | `stop_review.py` | **Once per dirty round**, if pending session files remain: remind `+N -M` and Source Control → Review (Viewed). Never `decision: block` |

Stop uses `.alexs-rig/STOP_REMINDED` so a dirty tree does not loop the turn (Claude `additionalContext` on Stop continues the conversation).

## Offline tests

```bash
python3 -m unittest discover -s tests -v
```

## Smoke without Desktop

```bash
# SessionStart JSON
python3 hooks/inject_l0.py | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'alexs-rig-l0' in d['hookSpecificOutput']['additionalContext']"

# No L0 in a random folder
cd /tmp && python3 /path/to/alexs-rig/hooks/prompt_l0_miss.py

# Deny cat .env
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"cat .env"}}' | python3 hooks/secret_hygiene.py

# Deny Write .env
printf '%s' '{"tool_name":"Write","tool_input":{"file_path":".env"}}' | python3 hooks/secret_hygiene.py

# Stop reminder (needs SESSION_BASE + a dirty file); second run is silent
python3 hooks/stop_review.py <<<'{}'
```

## Live (after install)

```bash
./scripts/install_claude_plugin.sh   # and/or install_cursor_plugin.sh
```

Restart Claude Code / reload Cursor. Then:

1. Open a repo **with** `docs/memory/snapshots/L0.md` — new session should know L0.
2. Open a repo **without** L0 — first prompt should see the miss line, not invented principles.
3. Ask the agent to `cat .env` — should be blocked.
4. Ask it to write `.env` — should be blocked.
5. Make an edit, let the turn finish — first Stop should mention `+N -M`; the next Stop in that session should not loop.
