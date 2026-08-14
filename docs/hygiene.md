# Secret hygiene

## Not a security control

`secret_hygiene.py` is a best-effort speed-bump against **accidental** secret
reads/writes landing in the agent transcript — it is not data-loss-prevention
and not a security boundary. It is fail-open (parse errors let the call
through), matches a fixed denylist of filenames, and only fires when a
recognized read/write verb co-occurs with a denylisted path in the same
string. It is trivially bypassed by tools it doesn't recognize, by a path
embedded in a quoted string, or by renaming the secret file. Do not rely on
it to keep a determined or compromised agent away from secrets — the real
control is a host secret store / env injection and not committing secrets to
the repo in the first place.

## Locked rules

- `.alexs-rig/` is gitignored (session base SHAs, local telemetry).
- Mining **redacts** obvious secrets before writing candidates.
- Hook `hooks/secret_hygiene.py` (PreToolUse Bash **and** Write/Edit) blocks `cat`/`head`/redirects/`Write` of denylisted paths (`.env`, credentials, keys). `test -f .env` is allowed.
- Prefer path lists + on-demand `git diff` over persisting full patches of secret files.

## Denylist (hook + human)

`.env`, `.env.*`, `credentials.json`, `id_rsa`, `*.pem`, `*.p12`, `secrets.yaml` / `secret.yml`, AWS credentials files.

## If you need a secret in a task

Use the host’s secret store / env injection — do not paste values into chat or L0.
