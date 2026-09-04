---
name: alex-mine-corrections
description: Turn captured turns into standing rules. Read the corrections inbox, keep the real corrections, cluster them, and propose a few general reusable rules with evidence; nothing reaches L0 without explicit approval. Use when the Stop hook reports captured turns, or when the user asks to mine, review or flush corrections.
---

# Mine corrections (Stage 2: LLM flush)

Correction learning is two stages:

1. **Capture (automatic, zero-LLM)** — the `capture_correction.py` UserPromptSubmit hook
   appends every reply you make, with the agent turn it answers, to
   `docs/memory/mining/corrections-inbox.jsonl`. It does **not** decide what is a
   correction; that judgement needs a model.
2. **Flush (this skill, on demand)** — the user runs `/alex-mine-corrections`; the agent
   selects the real corrections, generalizes them into a few reusable principles, and upserts
   them only after the user approves.

**Hard rule: nothing reaches L0 without the user's approval.** Never run `principle-upsert`
or `flush` unprompted.

## Workflow

1. **Read the inbox.**

   ```bash
   python3 bin/corrections list
   ```

   If empty, stop and say so. Optionally pull in history first:

   ```bash
   python3 bin/mine-corrections            # append past Cursor corrections to the inbox
   python3 bin/mine-corrections --workspace my-project --since 2026-08-01
   ```

2. **Select the real corrections first.** The inbox is **unfiltered** — it holds every
   reply, not just corrections, because a regex selects them badly. Measured on blind
   labels across two corpora: **recall 0.07** for the regex, against 0.56 for a model
   reading the same turns. So read each row's `text` next to its `assistant_excerpt` and
   keep only genuine corrections:

   > A turn is a correction when the user **rejects or overrides** what the agent did or
   > proposed, or **reports a defect** in the deliverable. It is **not** a correction when
   > they ask a question (even a sceptical one), request an explanation, give a new
   > instruction, or approve. Turns may be in English or Spanish.

   Most real corrections **report a symptom** ("image quality looks low", "the videos show
   no box", "velocities look really weird") rather than open with a rejection cue — that
   asymmetry is exactly what the regex missed, so do not lean on `no`/`don't`/`instead`.

   Work in batches (~20 rows at a time) rather than one call per row — same judgement, a
   fraction of the cost. `score` and `signals` are hints for ordering, not a filter: never
   skip a row because its score is low, that is the failure being fixed.

3. **Cluster + generalize.** Group the kept corrections by the standing rule they imply
   (not by wording). For each cluster write ONE general, reusable rule — the durable thing
   behind them, not a copy of any single turn. Aim for a handful. Drop one-off task noise
   that implies no standing rule.

4. **Triage each rule: obligation or craft?** This is the step that keeps L0 from filling
   with domain detail.

   | | goes to | test |
   |---|---|---|
   | **Obligation** — the agent must follow it in *any* code or research work | **L0 principle** | would it still apply while debugging an unrelated module? |
   | **Craft** — how to do one kind of task well (visualisation, document writing, a tool) | **a skill** | does it only make sense once you are already doing that task? |

   L0 is always-on and budget-capped, so every domain rule stored there is paid for in
   sessions where it is irrelevant. A skill's body loads only when the task matches, so
   detail is free there. Existing craft skills: `alex-viz` (visual deliverables),
   `alex-docs` (explanatory documents).

   Borderline cases resolve on *obligation vs know-how*, not on topic: keeping a document's
   numbers current when a result changes a conclusion is an obligation (L0), while how to
   structure that document is craft (skill).


5. **Propose with evidence.** Present each proposed rule to the user with:
   - where it would go — an L0 principle (`P-<slug>`) or a section in a named skill,
   - the one-line text,
   - 2–3 verbatim inbox quotes as evidence (with their scores/signals).

   Ask which to accept, edit, or reject. Wait for an explicit answer.

6. **Apply approved only.**

   ```bash
   python3 bin/principle-upsert --id P-<slug> --text "<approved obligation>"
   ```

   For craft, edit the relevant `skills/<name>/SKILL.md` instead — add a section with the
   evidence quotes. If no skill fits, propose creating one rather than defaulting to a
   principle.

7. **Flush + regen.** Once the approved rules are applied:

   ```bash
   python3 bin/corrections flush   # archive the inbox rows (docs/memory/mining/corrections-archive.jsonl)
   python3 bin/l0-regen            # rebuild L0 from active principles
   ```

   Rejected/edited-away rows are archived too — flush clears the whole inbox after promotion.

Slash: `/alex-mine-corrections`. Design: `docs/mining.md`.
