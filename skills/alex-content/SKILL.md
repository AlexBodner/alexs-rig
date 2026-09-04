---
name: alex-content
description: One entry point for outward-facing work — promo video, social post, blog, docs page or figure. Classifies, routes to the skill that owns that format, and applies the gates content actually needs: the claim before pixels, a cheap preview before the expensive render, and approval before anything is published. Use to take a piece of content end to end.
---

# Alex content (claim → preview → render once → publish)

Composes skills that already own each format. It does **not** restate their craft —
`roboflow-release-promo` owns promo concept and metric hygiene, `trackers-docs` owns the
docs house style, `foundry:create` → `foundry:creator` owns blog/deck/thread outlines,
`alex-viz` and `alex-docs` own the craft rules. This is the seam plus a gate policy.

**Why content needs its own gates.** In code, the expensive step is paid compute; here it
is the **render** and the user's own review time, and the irreversible step is **publishing** —
there is no unpost. The gates sit accordingly.

## Workflow

### 1. Classify and route (silent)

| the deliverable | route to |
|---|---|
| release promo video / social launch | `roboflow-release-promo` |
| blog post, thread, deck, talk abstract | `foundry:create` → `foundry:creator` |
| docs page for trackers / re-ID | `trackers-docs` |
| a figure or annotated clip inside any of the above | craft rules directly |

Always attach the craft: **`alex-viz`** for anything someone will look at, **`alex-docs`**
for anything someone will read.

### 2. 🚦 Gate 1 — the claim, before any pixels

Never produce first and validate after. Present and wait:

- the **headline** and the number behind it, in absolute points with dataset and baseline
  named in the same breath (`roboflow-release-promo` carries the metric hygiene rules)
- **how the claim was falsified**, not just supported: does the baseline visibly fail in
  this window, and does the new method hold there for the right reason?
- for a performance claim, both axes — time **and** memory (`P-full-picture`)
- the **material**: which footage or data, and whether its rights are established
  (an unclear source stops here, not at publish time)

A claim that cannot survive this gate does not get a render.

### 3. Produce the cheap artifact first

**The expensive step runs once, at the end.** Before any full render or full draft:

- a **single frame** or a 2-second clip at final settings — enough to judge crop, colour,
  annotator load, text size at feed scale
- for prose, the **outline** (`foundry:create` already writes one to `.plans/content/`)

Collect every change into **one consolidated pass**. The user has had to enforce this by
hand — *"TWO MORE FIXES to include BEFORE the final render (still render LAST, once)"* —
because each re-render costs minutes and the fixes arrive one at a time. Batch them.

Check the cheap artifact against `alex-viz` before showing it: each fact once, no stacked
annotators, no on-screen text narrating what the frame already shows, and render quality
treated as correctness rather than polish.

### 4. 🚦 Gate 2 — the preview

Show the frame or outline. Ask for **every** change at once, and say plainly that the full
render happens after this gate. Loop here — it is the cheap place to iterate.

### 5. Render or draft, once

Now the expensive pass. If it needs paid compute, `P-run` applies as well.

### 6. 🚦 Gate 3 — publish

Publishing is irreversible and outward-facing (`P-autonomy`). Before asking:

- **accuracy audit** of every on-screen number and caption against the source
  (`roboflow-release-promo` defines the format)
- copy read once for prose that **reads as generated** — generic framing sentences,
  throat-clearing openers, invented jargon (`alex-docs`)
- rights and attribution stated for third-party material

Then ask. Never post, publish or open a public PR without an explicit yes.

## Fail-fast

Stop and ask when: the number that would carry the post is not reproducible from a saved
run; the footage that shows the effect best is material whose rights are unclear; the
honest version of the claim is weaker than the one that was hoped for. That last one is a
decision the user makes, not a wording problem to solve.

## Escape hatches

Every skill above stays callable alone. Use this when you want the whole piece taken end to
end; call `roboflow-release-promo` or `trackers-docs` directly when you are already inside
one format and only need its craft.
