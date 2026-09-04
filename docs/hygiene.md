# Secret hygiene

## Not a security control

`hooks/secret_hygiene.py` is a best-effort speed-bump against **accidental** reads and writes
of secret files landing in the agent transcript. It is fail-open, matches a fixed denylist of
filenames, and only fires when a read or write verb it recognises appears in the same command
as a denylisted path. Any tool it does not recognise, a path inside a quoted string, or a
renamed file gets through. The real control is a host secret store and never committing
secrets in the first place.

## Denylist

`.env` and `.env.<name>` (but not `.env.example`, `.env.sample`, `.env.template`,
`.env.dist`), `credentials.json`, `id_rsa`, `*.pem`, `*.p12`, `secrets.yaml`, AWS credential
files. `test -f .env` is allowed; `cat`, `grep`, `source`, redirects and `Write`/`Edit` of
those paths are denied.

## Redaction of stored text

Everything the harness writes from your prompts (the corrections inbox, the shipped log) goes
through `redact()` in `bin/_memory.py`. It masks the value after a label such as `API_KEY=`
or `password:`, bearer tokens and well-known key prefixes, and any run of 20 or more mixed
letters and digits. Labels and ordinary words stay, so the text remains readable.

The first version replaced the label and left the value. A Roboflow API key pasted into a
Cursor prompt was stored, and then committed, as `ROBOFLOW_[REDACTED]=<the key>`. The key was
revoked, the file is gone from the tree, and the test suite now checks that exact line.

## If you need a secret in a task

Use the host's secret store or environment injection. Do not paste values into chat or L0.
