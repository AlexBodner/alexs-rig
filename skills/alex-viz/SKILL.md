---
name: alex-viz
description: Craft rules for visual deliverables — annotated video, overlays, figures, demo renders. Show each fact once, render the intermediate signal a decision is made from, and establish media provenance before anything outward-facing. Use when producing or reviewing a visualization.
---

# Alex viz (visual deliverables)

Craft for anything someone will *look at*: annotated video, overlays, figures, demo
renders. These came out of real review corrections; the quotes are the evidence.

## Show each fact exactly once

No stacked annotators on the same object, and no on-screen text narrating what the frame
already shows. If an annotation needs a projection to be correct, **project it properly**
rather than adding a second annotator beside it as a workaround.

> "no, the circle in the foot + the bbox is too much. i would keep the bbox or use a circle
> annotator but projecting it properly."

> "I would remove the text from the bottom that 'narrates what its happening' from the
> visualization, with the clock and list its enough."

The failure mode is additive: each element was reasonable on its own, and nobody removed
the one it made redundant.

## Render the signal the decision is made from

When a pipeline decides something from a derived signal, give that signal **its own view**
so the decision can be checked — before, or alongside, folding it into the final composite.
A viewer cannot audit a detection they never see the evidence for.

> "I also want to see what are we using to detect the gunshot in a separate visualization
> and maybe then we can include it small on the bottom part"

> "are we using the part of the wave where it starts?"

Small inset in the final render is fine; skipping it is not.

## Establish provenance before outward-facing use

Before putting third-party media into anything published or shared, establish and state
its **source, event, and usage rights** — unprompted, not when asked. This is an
obligation, not a preference: it is the one item here that can create a real problem
rather than a worse figure.

## Render quality is correctness, not cosmetics

Low resolution, choppy motion, washed-out colour and a crop that cuts the action are
**defects** — catch them before delivering, the same way you would a wrong number. Open the
output and look at it; a render that completes successfully can still be unusable.

> "image quality looks low on the video"

> "this doesnt look smooth at all. We could also annotate it in the video and make it a
> lower frame rate"

> "red should be more scarlet red, now its too pastel in the triangle"

> "so all tracks thick is also croping, it shouldnt do"

## A demo must read at a glance to someone who wasn't in the work

Camera placement, spacing between objects and contrast serve **comprehension**, not
aesthetics. A render can be technically perfect and still fail: if the point-of-view hides
the action, or two objects sit so close that a viewer cannot tell which one is being
tracked, the demo does not make its point.

> "the pov of the duck, it's really cool… but its placement is blocking the vision"

> "maybe we should have the pov camera from the other side, because now its blocking the hand"

> "i would have balls a little bit closer **so that people gets it** that it only keeps
> track of the one that we like"

> "the annotation for the fetch ball doesnt read clearly"

Judge the frame as a stranger would, at the size it will actually be seen. The question is
never "does this look good" but "does someone who was not here understand what is being
shown".

## Related

Cross-cutting work rules live in L0 (`/alexs-rig:alex-memory`); this file is the
domain detail. Document structure is `/alexs-rig:alex-docs`.
