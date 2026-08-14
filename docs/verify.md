# Verify (informational, not a gate)

`bin/verify` runs the project's checks and records the result so the Stop
reminder can show a one-line last-check status. It is **informational** — the
harness never blocks a turn or a commit on it. Stop stays non-blocking.

```bash
python3 bin/verify          # run in the current project
python3 bin/verify --root . # explicit root
```

## Command resolution

1. `.alexs-rig/verify` — a file with a shell command, or an executable. If present, it wins.
2. else auto-detect:
   - `tests/` dir or a pytest config → `python -m pytest -q` (falls back to `python -m unittest discover -s tests` when pytest is not importable).
   - `package.json` with a `test` script → `npm test`.
3. Nothing detected → prints a note and writes no status.

## Output

Writes `.alexs-rig/verify-status.json`:

```json
{"command": "...", "returncode": 0, "ok": true, "ran_at": "<utc iso>", "summary": "<tail ~15 lines>"}
```

and prints one `verify: PASS — <command>` / `verify: FAIL — <command> (returncode N)` line.
It is robust: missing tools do not crash it.

## Surfaced at Stop

When `.alexs-rig/verify-status.json` exists, the existing once-per-dirty-round
Stop reminder appends `last check: PASS/FAIL — <command> (<when>)`. No status
file means no extra line; the reminder never fires just because of verify.
