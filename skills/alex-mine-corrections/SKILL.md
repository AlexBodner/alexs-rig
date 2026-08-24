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
   wording). For each cluster, write ONE general, reusable rule — the durable thing behind the
   corrections, not a copy of any single turn. Aim for a handful, not one per row. Drop one-off
   task noise that implies no standing rule.

3. **Triage each rule: obligation or craft?** This is the step that keeps L0 from filling
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

4. **Propose with evidence.** Present each proposed rule to the user with:
   - where it would go — an L0 principle (`P-<slug>`) or a section in a named skill,
   - the one-line text,
   - 2–3 verbatim inbox quotes as evidence (with their scores/signals).

   Ask which to accept, edit, or reject. Wait for an explicit answer.

5. **Apply approved only.**

   ```bash
   python3 bin/principle-upsert --id P-<slug> --text "<approved obligation>"
   ```

   For craft, edit the relevant `skills/<name>/SKILL.md` instead — add a section with the
   evidence quotes. If no skill fits, propose creating one rather than defaulting to a
   principle.

6. **Flush + regen.** Once the approved rules are applied:

   ```bash
   python3 bin/corrections flush   # archive the inbox rows (docs/memory/mining/corrections-archive.jsonl)
   python3 bin/l0-regen            # rebuild L0 from active principles
   ```

   Rejected/edited-away rows are archived too — flush clears the whole inbox after promotion.

Slash: `/alex-mine-corrections`. Design: `docs/mining.md`, `docs/design-correction-mining.md`.
