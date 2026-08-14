---
name: alex-mine-corrections
description: Stage-2 flush — read the corrections inbox captured cheaply from your turns, cluster it, and synthesize GENERAL reusable principles. Nothing reaches L0 without your explicit approval.
---

# Mine corrections (Stage 2: LLM flush)

Correction learning is two stages:

1. **Capture (cheap, automatic, zero-LLM)** — the `capture_correction.py` UserPromptSubmit
   hook and the optional `bin/mine-corrections` importer append raw correction-like turns to
   `docs/memory/mining/corrections-inbox.jsonl`. No generalization happens there.
2. **Flush (this skill, on demand)** — you run `/alex-mine-corrections`; I read the inbox,
   generalize it into a few reusable principles, and — only after you approve — upsert them.

**Hard rule: nothing reaches L0 without your approval.** I never `principle-upsert` or `flush`
on my own.

## Workflow

1. **Read the inbox.**

   ```bash
   python3 bin/corrections list
   ```

   If empty, stop and say so. Optionally pull in history first:

   ```bash
   python3 bin/mine-corrections            # append past Cursor corrections to the inbox
   python3 bin/mine-corrections --workspace AI-Rig --since 2026-08-01
   ```

2. **Cluster + generalize.** Group the raw rows by the standing rule they imply (not by exact
   wording). For each cluster, write ONE general, reusable principle — the durable rule behind
   the corrections, not a copy of any single turn. Aim for a handful, not one per row. Drop
   one-off task noise that implies no standing rule.

3. **Propose with evidence.** Present each proposed principle to the user with:
   - a suggested stable `--id` (e.g. `P-<slug>`),
   - the one-line principle text,
   - 2–3 verbatim inbox quotes as evidence (with their scores/signals).

   Ask which to accept, edit, or reject. Wait for an explicit answer.

4. **Apply approved only.** For each accepted principle:

   ```bash
   python3 bin/principle-upsert --id P-<slug> --text "<approved general principle>"
   ```

5. **Flush + regen.** Once the approved principles are upserted:

   ```bash
   python3 bin/corrections flush   # archive the inbox rows (docs/memory/mining/corrections-archive.jsonl)
   python3 bin/l0-regen            # rebuild L0 from active principles
   ```

   Rejected/edited-away rows are archived too — flush clears the whole inbox after promotion.

Slash: `/alex-mine-corrections`. Design: `docs/mining.md`, `docs/design-correction-mining.md`.
