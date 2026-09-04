# Hooks

Six scripts on five Claude Code events. Cursor event names in parentheses; the same scripts
run there through `hooks/cursor-invoke.sh`.

| Event | Script | What it does |
|---|---|---|
| `SessionStart` (`sessionStart`) | `inject_l0.py` | Injects L0 (standing memory), the codebase-graph pointer and the repo style note. Records `SESSION_BASE`, the worktree snapshot review is measured from, on a new session (`startup`, `clear`). Keeps it on `compact`, `resume` and `fork`: the human is mid-task and re-snapshotting would hide every unreviewed edit. |
| `UserPromptSubmit` (`beforeSubmitPrompt`) | `prompt_l0_miss.py` | One line, only when the project has no L0 anywhere. Never dumps L0. |
| `UserPromptSubmit` | `capture_correction.py` | Appends every reply, with the agent turn it answers and the files still unreviewed, to the corrections inbox. Silent, zero tokens, fail-open. |
| `PreToolUse` on `Bash\|Write\|Edit\|NotebookEdit` (`preToolUse` on `Shell\|Write`) | `secret_hygiene.py` | Denies reading or writing denylisted secret paths (`.env`, keys, credentials). A speed-bump, not a security control: [hygiene.md](hygiene.md). |
| `Stop` (`stop`) | `stop_review.py` | Once per dirty round: the unreviewed agent edits since `SESSION_BASE`, the last `bin/verify` result and whether it is stale, and a nudge to mine corrections when the inbox passes 80 rows. Never `decision: block`. |

Compaction has no hook of its own. Claude Code fires `SessionStart` with `source: "compact"`
after compacting, and that is where L0 comes back. A `PreCompact` hook cannot add context;
an earlier version tried and its output was rejected by the host's validator.

Stop uses `.alexs-rig/STOP_REMINDED` so a dirty tree reminds once, not every turn
(`additionalContext` on Stop continues the conversation). `bin/review-mark` and a new session
clear it.

## The output contract

Claude Code validates every hook's stdout. It must be empty or one JSON object, and
`hookSpecificOutput` must carry `hookEventName` for its event. A payload that fails
validation is dropped without telling the model, so the wrong shape is a hook that does
nothing. The deny payload shipped that way for three weeks: a top-level `decision: "deny"`
and no `hookEventName`. Reading `.env` was never actually blocked until v0.8.0.

`tests/test_hooks.py::TestHookContract` now runs every hook against hostile stdin and asserts
the shape, and checks that every command in both manifests points at a file that exists.

Cursor reads flat keys instead (`additional_context`, `permission`, `user_message`). The
hooks emit both shapes in one object; Claude Code logs the extra keys as ignored. The Cursor
side has not been verified live.

## Smoke without a session

```bash
python3 -m unittest discover -s tests -v

# SessionStart, as Claude sends it after a compaction
echo '{"source":"compact"}' | python3 hooks/inject_l0.py | python3 -m json.tool | head

# Deny cat .env; allow the committed template
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"cat .env"}}' | python3 hooks/secret_hygiene.py
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"cat .env.example"}}' | python3 hooks/secret_hygiene.py

# Stop reminder (needs SESSION_BASE and a dirty file); the second run is silent
python3 hooks/stop_review.py <<<'{}'
```

## Live check after install

```bash
./scripts/install_claude_plugin.sh
```

Start a new session. L0 arrives before the first prompt. Ask the agent to `cat .env`: it is
denied. Make an edit and let the turn end: the first Stop lists the file, the next does not.
`claude --debug` writes the validation result of every hook to `~/.claude/debug/`.
