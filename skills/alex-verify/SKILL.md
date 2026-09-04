---
name: alex-verify
description: Run the project's checks and record a non-blocking PASS/FAIL status. Informational only — never a gate. Use to back "verifiable" with a real check result surfaced at Stop.
---

# Alex verify (informational check)

`bin/verify` runs the project's checks and records the result. It never blocks a
turn or a commit — it only makes "verifiable" real by recording a check.

## Run

```bash
python3 bin/verify          # cwd project
python3 bin/verify --root . # explicit root
```

## Resolution

1. `.alexs-rig/verify` (shell command file, or executable) wins.
2. else `tests/`/pytest config → `python -m pytest -q` (fallback `python -m unittest discover -s tests`); `package.json` `test` → `npm test`.

Writes `.alexs-rig/verify-status.json` (`command`, `returncode`, `ok`, `ran_at`,
`summary`) and prints one PASS/FAIL line. The Stop reminder shows the last check
status when that file exists.

## Out of scope

Blocking commits or turns. Inventing a check when none is configured. Full docs: [../../docs/verify.md](../../docs/verify.md).
