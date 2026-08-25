---
name: alex-docs
description: Craft rules for explanatory documents — reports, research write-ups, PR descriptions, findings. Lead with what was done and what came of it, and write one standalone narrative rather than an accretion of replies. Use when writing or restructuring a document someone else will read.
---

# Alex docs (explanatory documents)

For anything written to be read by someone who was not in the work: reports, research
write-ups, PR bodies, findings documents.

## Lead with what was done and what came of it

Open with the outcome, not the fix or the mechanism. A reader who was not in the work —
including a non-immersed one — should get **why a result holds** from one or two sentences.

The recurring failure: a document that opens with "the fix" and makes the reader assemble
the story from the middle.

## One standalone narrative, not an accretion of replies

A document written by answering comments one at a time reads as sediment. When it has
drifted that way, **rewrite it rather than patch it again**.

Order: **mechanism → why → tradeoffs → limitations**, plus an explicit section mapping the
explanation to how it is actually implemented (which PR or file does what).

Deep but not verbose. Use tables or bullets for results; prose for the argument. Cut the
history of how the understanding evolved unless it constrains validity — a refuted
hypothesis is worth a line only if it stops a reader repeating it.

## Related

Cross-cutting work rules live in L0 (`/alexs-rig:alex-memory`). Note that keeping a
document's *numbers* current when a result changes a conclusion is a standing obligation
(`P-report-numbers`), not craft — it stays in L0. Visual deliverables: `/alexs-rig:alex-viz`.
