---
name: alex-api
description: Design public API surfaces from the caller's side — one obvious entry point, names a user would guess, and the same object serving related workflows. Use when adding or reviewing a class, function or module that library users will call.
---

# Alex API (design from the call site)

For anything a library user will import and call. These rules came out of PR review on the
reid/trackers packages; the quotes are the evidence.

## Write the call site first

Before designing the class, write the three lines a user would type. If those lines are
awkward, the design is wrong — no amount of internal tidiness fixes a bad call site.

> "i dont like that API: i would like to do: `# Load dataset once` `crops =
> ReIDCrops("/path/to/crops/train")` `# 71 ms scan, once`"

> "show me how it would be fully used for training and for evaluating, because it would be
> cool to just pass 1 set of things"

## One object for related workflows, not one per workflow

If training and evaluation need the same data with different access patterns, that is one
class with two accessors — not two classes that each rebuild the same scan.

> "i think for the user it would be more useful to load the dataset in just one class and
> have the option to train from it or just evaluate"

> "im still confused by why do we have a specific class for training reid set. Doesnt it
> need quite the same as the reid inference?"

## Name it what the user would guess

A name that describes today's input (`ReIDCrops`) locks the class to that input. Name it
after the role it plays, so the obvious extension does not require a rename.

> "is reidcrops the correct name for that class?"

> "I think that this should be ReidDataset or something like that. Because it can be crops
> (from the tracking case) or images"

## Related

Cross-cutting obligations live in L0 — `P-reuse` (don't duplicate across modules) and
`P-scope` (no unrequested options) both bear on API surface. This file is the design detail.
