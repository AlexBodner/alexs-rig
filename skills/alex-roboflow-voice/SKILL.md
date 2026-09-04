---
name: alex-roboflow-voice
description: The Roboflow house voice for anything written under it or alongside it — READMEs, feasibility reports, release copy, personal repos that carry the same tone. Use when writing or reviewing prose that will be read as Roboflow's, outside the docs pages that trackers-docs already covers.
---

# Alex Roboflow voice

For prose that reads as Roboflow's, wherever it lives. `trackers-docs` owns the docs pages
in `trackers` and `re-ID`: page types, templates, `hl_lines`, frontmatter. This covers the
voice itself, which travels beyond `docs/`.

> "lets make it personal repo so that we can do it fast, but lets use the same tone we use
> in trackers and roboflow in general"

That request is the reason this skill exists. The voice applies to a personal repo shipped
alongside the libraries just as much as to the libraries.

## No em dashes or double hyphens in body prose

They read as AI smell. Restructure the sentence, use a colon or a comma, split into a
heading, or lead with a bold label and a period (`**Prediction.** First match ...`).
Literal `--` inside shell commands and code is fine.

This is the single most recognisable tell, and it is the one rule to apply even when
skimming.

## Cut before you add

Length is not evidence of effort. A shorter document that says the same thing is the better
document.

> "its not the tone and redaction that i expect. It should be less text overall"

Explain a methodology once and then refer back to it. Restating how something was measured
in every section reads as padding and buries the result.

> "the tone of the paragraphs should be natural. I see a lot of the methodology explanation
> repeated"

## Write as an engineer, for an engineer

Concrete and specific. No throat-clearing openers, no framing sentence that would fit any
document on any topic, no invented jargon. If a phrase is generic enough to paste into an
unrelated README, cut it.

> "the hardware feasibility md that we ship should look like it was made by an engineer"

Name the machine, the version, the dataset. "This machine" becomes "Apple M4 MacBook Pro".

## Every number states where it came from

Dataset, split and source in the same breath as the figure. Absolute points rather than
vague percents, and never a relative percent presented as an absolute gain.

Say which model produced it and under what conditions: a number from a fine-tuned model and
one from a stock checkpoint are not interchangeable, and a reader cannot tell them apart
unless you say so.

## Describe what it does, not what it withholds

Never frame something by subtraction or enumerate everything that lives elsewhere. State
the scope positively and link out once.

## Unpack the jargon

A term the reader has to ask about is a term that should have been explained, or replaced.
Internal shorthand that leaked into shipped prose is the usual source.

## Related

`alex-docs` carries the general structure rules for explanatory documents (lead with the
outcome, one standalone narrative). This skill overrides it on voice wherever the artifact
reads as Roboflow's. For docs pages under `trackers` or `re-ID`, `trackers-docs` wins on
everything it specifies.
