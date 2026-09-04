# Verify (informational, never a gate)

`bin/verify` runs the project's checks and records the result so the Stop reminder can show a
one-line status. The harness never blocks a turn or a commit on it.

```bash
python3 bin/verify            # current project
python3 bin/verify --root .   # explicit root
```

## Command resolution

1. `.alexs-rig/verify`: an executable, or a file holding one shell command. Wins if present.
2. Otherwise auto-detect: a `tests/` directory or pytest config runs `python -m pytest -q`
   (falls back to `unittest discover` when pytest is not importable); a `package.json` with a
   `test` script runs `npm test`.
3. Nothing detected: prints a note, writes no status.

## What it records

`.alexs-rig/verify-status.json`:

```json
{"command": "...", "returncode": 0, "ok": true, "ran_at": "<utc iso>",
 "summary": "<last 15 lines>", "tree": "<worktree snapshot sha>"}
```

`tree` is the worktree snapshot at the time of the run. At Stop, the reminder compares it with
the current worktree and appends `STALE: edits since; re-run bin/verify` when they differ, so a
green result cannot outlive the code it checked.

Missing tools do not crash it; a timeout (600 s) records a failure with that reason.
