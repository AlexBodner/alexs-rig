# Correction learning

Two stages. Capture is automatic and costs nothing; selection and generalisation happen on
demand with a model, and nothing reaches L0 without your approval.

## Stage 1: capture (every reply, unfiltered)

`hooks/capture_correction.py` runs on `UserPromptSubmit`. For every reply you type it appends
one row to `<memory>/mining/corrections-inbox.jsonl`:

```json
{"ts": "...", "text": "<your reply, redacted>", "score": 4, "signals": ["opener:no,", "negation"],
 "cwd": "...", "assistant_excerpt": "<the agent turn you replied to>", "files": ["a.py"],
 "session_id": "..."}
```

Three things make a row usable later. The **agent turn you reacted to**, tail-read from the
session transcript, because most corrections are deictic ("no, not like that"). The **files
with unreviewed edits**, because that is what the correction is about. And `score`, a
transparent keyword score kept as a ranking hint, not a gate.

Not captured: a session's opening prompt (nothing to correct yet), prompts over 4000
characters (pastes), and host-injected text such as task notifications and system reminders.
Secrets are redacted before writing; the redaction masks values after labels like `API_KEY=`
and any opaque 20+ character token, and leaves ordinary prose alone.

The hook is silent (it never adds model context) and fail-open (it always exits 0).

## Why capture is unfiltered

The first design assumed corrections were rare, so a keyword filter would pre-select them.
Blind labelling of 184 real turns from two corpora ([evals/honest](../evals/honest/README.md))
showed both halves of that premise wrong:

| | Claude Code corpus (n=87) | Cursor corpus (n=97) |
|---|---|---|
| corrections among turns | 17% | 39% |
| keyword filter, precision | 0.57 | 0.70 |
| keyword filter, recall | **0.07** | **0.07** |
| a model over the same turns, recall | 0.56 | not run |

Corrections mostly report a symptom ("the videos show no box") rather than open with a
rejection cue, so widening the regex was never going to work. Capture therefore keeps every
reply and the model does the selecting, once, at flush time, for about $0.78 per 300 turns.
`ALEXS_RIG_CAPTURE_MIN_SCORE=3` restores the filter where a flush has to stay cheap.

## Stage 2: flush (`/alex-mine-corrections`)

The skill reads the inbox in batches, keeps the turns that reject or override what the agent
did or report a defect in the deliverable, clusters them by the standing rule they imply, and
writes one general rule per cluster. Each rule is then triaged:

- an **obligation** that applies to any code or research work goes to L0 as a principle;
- **craft** that only matters while doing one kind of task goes into the matching skill.

Every proposal comes with two or three verbatim quotes as evidence. Only approved rules are
written, then the inbox is archived:

```bash
python3 bin/principle-upsert --id P-<slug> --text "<approved rule>"
python3 bin/corrections flush
```

The Stop hook nudges once when the inbox passes 80 rows.

## History import

`bin/mine-corrections` scans local Cursor transcripts and appends rows in the same shape,
minus the agent excerpt (older transcripts do not carry it). It keeps the keyword filter, so
it finds a small fraction of past corrections. It exists to seed a fresh inbox, not to
replace the live hook.

## Files

- `<memory>/mining/corrections-inbox.jsonl`: captured rows, waiting for a flush
- `<memory>/mining/corrections-archive.jsonl`: flushed rows
- `<memory>/mining/shipped.jsonl`: what shipped and how it did (`bin/shipped`)

All three are runtime files under your memory directory, never committed.
