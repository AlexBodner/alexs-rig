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

## A comparison must actually be comparable

If a table compares methods, every arm needs the **same metrics**. Reporting IDF1 for one
and HOTA for another is not a comparison — find the comparable figure in the literature, or
say plainly that it does not exist.

> "on the comparison matrix we dont have comparison of metrics at all, for one you report
> idf1 and for the other one just hota, we should have something comparable if it is
> available on internet/literature"

(The cross-cutting obligation is `P-fair`: equal effort on every arm. This is its
reporting side.)

## Organise by the reader's decision, not by chronology

A survey or landscape exists so someone can decide. Order it around that decision, with
data and dates as supporting context — not as the spine.

> "i dont really care about AIC 24 alone, i want the story of the SOTA for deciding what
> should we implement"

> "The timeline is now more slower to read and is also focusing quite much on the data,
> when it should focus more on the algorithmic progression"

## Do not write prose that reads as generated

Generic framing sentences, throat-clearing openers and invented jargon are the tell. If a
phrase would fit any document on any topic, cut it.

> "that part is good to have, but it shouts AI generated"

> "the 'one link at a time' i dont understand what does it mean and the user neither"

## Less text, engineer's voice, no repeated methodology

Three failures show up together in review:

- **Too much text.** Cut before adding. A shorter document that says the same thing is a
  better document, and length is not evidence of effort.
- **Methodology restated in every section.** Explain how something was measured once, then
  reference it. Repetition reads as padding and buries the result.
- **Voice.** It should read as if an engineer wrote it for another engineer — concrete,
  specific, no throat-clearing.

> "its not the tone and redaction that i expect. **It should be less text overall**"

> "the tone of the paragraphs should be natural. **I see a lot of the methodology
> explanation repeated**"

> "the hardware feasibility md that we ship **should look like it was made by an engineer**"

When the document belongs to a project with its own house style, that style wins over this
section — for Roboflow `trackers` / `re-ID` docs pages, use the `trackers-docs` skill.

## Related

Cross-cutting work rules live in L0 (`/alexs-rig:alex-memory`). Note that keeping a
document's *numbers* current when a result changes a conclusion is a standing obligation
(`P-report-numbers`), not craft — it stays in L0. Visual deliverables: `/alexs-rig:alex-viz`.
