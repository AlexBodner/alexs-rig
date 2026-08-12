# Agent prompt — box verification suite (no Mac Desktop required)

Copy everything below the line into a **new agent session** on a machine with git + python3 (VS Code / Linux box / Grok computer). Workspace = clone of https://github.com/AlexBodner/alexs-rig

Goal: **prove the harness tools** with specific pass/fail checks. Do **not** implement backlog. Do **not** push. End with a scoreboard.

---

## Mission

You have your own computer. Run this **box suite** against Alex's Rig. Every check has an observable pass condition. Skip only what the host truly lacks (say SKIP + why). Do not claim Desktop `+N -M` or live Claude SessionStart — those are human-only.

## Prep

```bash
git clone https://github.com/AlexBodner/alexs-rig.git /tmp/alexs-rig-box || true
cd /tmp/alexs-rig-box   # or this workspace if already the clone
git fetch origin && git checkout main && git pull --ff-only
python3 -m unittest tests.test_memory -v
chmod +x bin/* hooks/inject_l0.py scripts/bootstrap.sh
```

If the workspace already *is* the clone, use that root instead of `/tmp/...`. Record `ROOT=$PWD`.

## Scoreboard format (fill as you go)

For each ID: `PASS` / `FAIL` / `SKIP` — one line evidence.

---

### B1 — Unit tests
Run: `python3 -m unittest tests.test_memory -v`  
**PASS:** all tests OK (note count).

### B2 — Bootstrap demo memory
Run: `./scripts/bootstrap.sh` (answer `N` to extension install if prompted). If `--yes` / `--help` exist, also run those.  
**PASS:** prints absolute `Root:` and absolute L0 path; L0 file exists; L0 contains `P-demo` (or demo principle text); does **not** only print upsert commands without applying them.

### B3 — Absolute L0 path trap
```bash
# Wrong root simulation
mkdir -p /tmp/wrong-ws && cd /tmp/wrong-ws
# Do NOT create docs/memory here
test ! -f docs/memory/snapshots/L0.md
# Right open
test -f "$ROOT/docs/memory/snapshots/L0.md"
```
**PASS:** you document that relative `docs/memory/snapshots/L0.md` from `/tmp/wrong-ws` would be empty/missing, while `$ROOT/docs/.../L0.md` has content. (If an IDE is available, open the absolute path and confirm non-empty.)

### B4 — Principle upsert + idempotent id
```bash
cd "$ROOT"
python3 bin/principle-upsert --id P-BOX --text "Box suite: batch review over per-edit stops"
python3 bin/principle-upsert --id P-BOX --text "Box suite: batch review over per-edit stops (updated)"
python3 bin/l0-regen
grep -c 'P-BOX' docs/memory/snapshots/L0.md   # expect 1
grep 'updated' docs/memory/snapshots/L0.md
```
**PASS:** exactly one `P-BOX` line in L0; text is the updated version.

### B5 — Principle forget archives
```bash
python3 bin/principle-forget --id P-BOX
python3 bin/l0-regen
! grep -q 'P-BOX' docs/memory/snapshots/L0.md
grep -q 'P-BOX' docs/memory/archive/* 2>/dev/null || grep -rq 'P-BOX' docs/memory/archive
```
**PASS:** gone from L0; present under `docs/memory/archive/`.

### B6 — Progress + pending lifecycle
```bash
python3 bin/progress-upsert --id F-BOX --status active --summary "Box verify" --path .
python3 bin/pending-upsert upsert --id T-BOX --priority P1 --text "Finish box suite"
python3 bin/l0-regen
grep -E 'F-BOX|T-BOX' docs/memory/snapshots/L0.md
python3 bin/pending-upsert done --id T-BOX
python3 bin/l0-regen
! grep -q 'T-BOX' docs/memory/snapshots/L0.md
```
**PASS:** both appear after upsert; `T-BOX` leaves L0 after done; progress path is `.` (not a foreign `/Users/...` path).

### B7 — l0-show (if present)
If `bin/l0-show` exists: happy path prints L0; with L0 moved aside, exit ≠ 0 and stderr explains missing.  
**PASS** or **SKIP** (not on main yet).

### B8 — SessionStart inject shape
```bash
python3 hooks/inject_l0.py > /tmp/inject.json
python3 -c "import json,sys; d=json.load(open('/tmp/inject.json')); assert 'hookSpecificOutput' in d or 'additionalContext' in str(d) or 'alexs-rig-l0' in open('/tmp/inject.json').read(); print('ok', list(d)[:8])"
grep -q 'alexs-rig-l0' /tmp/inject.json
```
**PASS:** valid JSON; payload contains `alexs-rig-l0` (or documented equivalent) and real L0 text.

### B9 — Overflow (no silent truncate)
Find how L0 budget is set (env, flag, or constant in `bin/_memory.py`). Force a tiny budget (e.g. env documented in code, or temporarily many principles).  
**PASS:** L0 shows an `OVERFLOW` (or equivalent) banner telling user to distill/forget — content is not silently dropped without warning.

### B10 — Bad args
```bash
python3 bin/principle-upsert ; echo exit=$?
```
**PASS:** usage on stderr/stdout; exit code 2 (or non-zero documented).

### B11 — Mining with **synthetic** transcripts (host-independent)
`mine-corrections` walks `--root/<project>/agent-transcripts/**/*.jsonl` and keeps lines with `role=user` and `message.content` (string or text parts) containing `<user_query>…</user_query>`.

```bash
FAKE_ROOT="$ROOT/.tmp/fake-cursor/projects"
FAKE="$FAKE_ROOT/BoxProj/agent-transcripts"
mkdir -p "$FAKE"
python3 - <<PY
import json
from pathlib import Path
p = Path("$FAKE") / "conv1.jsonl"
row = {
    "role": "user",
    "message": {
        "content": [
            {
                "type": "text",
                "text": "<user_query>Don't stop on every edit — I prefer batch review and Edit automatically after Plan instead.</user_query>",
            }
        ]
    },
}
p.write_text(json.dumps(row) + "\n", encoding="utf-8")
print(p)
PY
python3 bin/mine-corrections --strong-only --root "$FAKE_ROOT"
```

Inspect:

- `transcripts scanned` ≥ 1  
- `docs/memory/mining/principle-candidates.md` exists and records applied/skipped/dry-run status  
- Prefer ≥1 candidate **or** `patterns.md` showing the mined quote — if 0 with scanned≥1, **FAIL** with evidence (shape/heuristic), do not rewrite mining unless the user asked.

**PASS:** pipeline reads the fake tree; not a silent no-op. Empty real `~/.cursor` alone is not enough for PASS here — you must use the fake tree.

### B12 — Empty-host mining honesty
```bash
python3 bin/mine-corrections --strong-only --root /tmp/alexs-rig-empty-cursor-$$
```
**PASS:** stdout/stderr says empty/OK-not-broken (or patterns.md Status section); still writes the three mining files.

### B13 — Plugin manifests parse
```bash
python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); json.load(open('hooks/hooks.json'));
from pathlib import Path
p=Path('.cursor-plugin/plugin.json');
print('cursor-plugin', p.exists());
json.load(open(p)) if p.exists() else None"
test -d skills/alex-memory && test -d skills/alex-mine-corrections
```
**PASS:** JSON loads; both skills dirs exist.

### B14 — Docs name the daily loop
```bash
grep -n 'Daily loop' docs/workflow.md README.md
```
**PASS:** `docs/workflow.md` has a section literally named Daily loop.

### B15 — SCM review path (if git + editor tools allow)
Make a tiny uncommitted edit (e.g. add a line under `REVIEW.md` `## Box suite notes`).  
Run `git status` + `git diff`. If `code`/`cursor` CLI exists, open the file. Prefer Git Tree Compare if already installed — do not require marketplace auth.  
**PASS:** dirty file visible via `git diff`; you describe how a human would open SCM side-by-side. **SKIP** only if no git.

### B16 — Cleanup (required)
```bash
python3 bin/pending-upsert done --id T-BOX 2>/dev/null || true
python3 bin/principle-forget --id P-BOX 2>/dev/null || true
# leave P-demo / seeded principles alone
python3 bin/l0-regen
rm -rf "$ROOT/.tmp/fake-cursor"
```
**PASS:** no push; working tree either clean or only intentional box-note left uncommitted; say what remains dirty.

## Out of scope (do not attempt / do not FAIL the suite for these)

- Claude Code Desktop `+N -M`
- Live Desktop/VS Code Claude SessionStart
- Push / PR / `gh repo create`
- Implementing `--root` memory multi-project
- Accepting mining candidates into principles (unless user said so)

## Final report (required)

```text
Box suite — Alex's Rig
Host: …
Commit: …
B1 … B16: PASS/FAIL/SKIP + one-line evidence
Blocked for human only: …
Changed files (uncommitted): …
```
