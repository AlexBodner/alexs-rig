# Correction learning (two-stage)

Replaces the old hardcoded-template auto-upsert. Corrections are learned in two stages: a **cheap
zero-LLM capture** that just accumulates raw signals, and an **on-demand LLM flush** that
generalizes them into principles **you approve**. Nothing reaches L0 without approval.

## Stage 1 — capture (cheap, automatic)

`hooks/capture_correction.py` runs on `UserPromptSubmit` (alongside `prompt_l0_miss.py`). It scores
the prompt with a small transparent weighted heuristic and, above threshold, appends one raw row to
`docs/memory/mining/corrections-inbox.jsonl`. It is **silent** — no model context, always exits 0
(fail-open).

Row shape:

```json
{"ts": "...", "text": "<redacted prompt>", "score": 4, "signals": ["opener:no,", "negation"], "cwd": "..."}
```

### Detector (grounded in real Cursor history)

Corrections overwhelmingly **open with "no,"** (also `nope`/`wait,`/`actually,`/`hmm,`). The cheapest
high-precision signal is a short reply-to-the-agent starting with "no," plus any negation or rule
verb. Weights (threshold **3**):

| Signal | Match | Weight |
|--------|-------|--------|
| Strong opener | starts with `no,` | +3 |
| Soft opener | starts with `nope`/`wait,`/`actually,`/`hmm,` | +2 |
| Negation | `don't`, `not`, `doesn't`, … | +1 |
| Rule verb | `should`, `must`, `always`, `never` | +1 |
| Preference | `i want`, `i prefer`, `instead`, `rather than`, `just`, `no need` | +1 |
| Pending edits | there are fresh unreviewed edits (`review_files.pending_names`) | +1 |

(No `again` keyword — in this history it means "re-run again", not repetition.)

### Optional bulk import (history)

`bin/mine-corrections` is the historical counterpart to the hook: it scans local Cursor
`agent-transcripts` and appends the SAME kind of raw rows to the inbox using the SAME detector. It
does **not** upsert principles and has no templates.

```bash
python3 bin/mine-corrections                          # append past corrections to the inbox
python3 bin/mine-corrections --workspace AI-Rig
python3 bin/mine-corrections --since 2026-08-01
python3 bin/mine-corrections --root /path/to/project  # target memory project
```

Empty host (no `~/.cursor/projects`) → honest note; not a broken pipeline.

## Inbox CLI

```bash
python3 bin/corrections list     # count + rows
python3 bin/corrections flush    # move rows to corrections-archive.jsonl, empty inbox
```

`list`/`flush` never generalize — that is the flush skill's job.

## Stage 2 — flush (on demand, LLM, approval-gated)

Run `/alex-mine-corrections` (skill: `skills/alex-mine-corrections/SKILL.md`). The agent reads the
inbox, **clusters** the raw corrections, synthesizes a handful of **general, reusable** principles
(not templates), and presents them **with evidence quotes**. Only the ones you approve are written:

```text
principle-upsert --id P-<slug> --text "<approved principle>"   # accepted only
corrections flush                                              # archive the inbox
l0-regen                                                       # rebuild L0
```

The Stop hook nudges once (`N corrections captured — run /alex-mine-corrections`) when the inbox
reaches 10 rows.

## Files

- `docs/memory/mining/corrections-inbox.jsonl` — captured raw rows (gitignored)
- `docs/memory/mining/corrections-archive.jsonl` — flushed rows (gitignored)
