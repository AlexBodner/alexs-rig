# Secret hygiene

## Locked rules

- `.alexs-rig/` is gitignored (session base SHAs, local telemetry).
- Mining **redacts** obvious secrets before writing candidates.
- Hook `hooks/secret_hygiene.py` (PreToolUse Bash **and** Write/Edit) blocks `cat`/`head`/redirects/`Write` of denylisted paths (`.env`, credentials, keys). `test -f .env` is allowed.
- Prefer path lists + on-demand `git diff` over persisting full patches of secret files.

## Denylist (hook + human)

`.env`, `.env.*`, `credentials.json`, `id_rsa`, `*.pem`, `*.p12`, `secrets.yaml` / `secret.yml`, AWS credentials files.

## If you need a secret in a task

Use the host’s secret store / env injection — do not paste values into chat or L0.
