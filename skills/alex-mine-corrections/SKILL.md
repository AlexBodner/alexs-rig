---
name: alex-mine-corrections
description: Stage-2 flush — read the captured turns, pick out the real corrections, cluster them, and synthesize GENERAL reusable principles. Nothing reaches L0 without your explicit approval.
---

# Mine corrections (Stage 2: LLM flush)

Correction learning is two stages:

1. **Capture (automatic, zero-LLM)** — the `capture_correction.py` UserPromptSubmit hook
   appends every reply you make, with the agent turn it answers, to
   `docs/memory/mining/corrections-inbox.jsonl`. It does **not** decide what is a
   correction; that judgement needs a model.
2. **Flush (this skill, on demand)** — you run `/alex-mine-corrections`; I select the real
   corrections, generalize them into a few reusable principles, and — only after you
   approve — upsert them.

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

2. **Select the real corrections first.** The inbox is **unfiltered** — it holds every
   reply, not just corrections, because a regex selects them badly (measured on blind
   labels: 0.05 recall vs 0.59 for a model reading the same turns). So read each row's
   `text` next to its `assistant_excerpt` and keep only genuine corrections:

   > A turn is a correction when the user **rejects or overrides** what the agent did or
   > proposed, or declares something wrong. It is **not** a correction when they ask a
   > question (even a sceptical one), request an explanation, give a new instruction, or
   > approve. Turns may be in English or Spanish.

   Work in batches (~20 rows at a time) rather than one call per row — same judgement,
   a fraction of the cost. `score` and `signals` are hints for ordering, not a filter:
   never skip a row because its score is low, that is exactly the failure being fixed.

3. **Cluster + generalize.** Group the kept corrections by the standing rule they imply
   (not by wording). For each cluster write ONE general, reusable principle — the durable
   rule behind them, not a copy of any single turn. Aim for a handful. Drop one-off task
   noise that implies no standing rule.


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
