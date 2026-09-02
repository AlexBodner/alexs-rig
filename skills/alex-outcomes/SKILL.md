---
name: alex-outcomes
description: Improve the craft skills from what actually shipped and landed well, not only from corrections. Logs shipped artifacts, attaches how each did, and folds repeated patterns from the winners into alex-viz / alex-docs / alex-api / roboflow-release-promo. Use after publishing something, when attaching a result, or to mine the log.
---

# Alex outcomes (learn from what worked)

Correction mining only ever sees failures. A correction says what to avoid; it never says
what to do, and two artifacts can avoid every known mistake while only one of them lands.
This is the other half: a log of what shipped, what it did, and what the winners have in
common.

## 1. Log what shipped

When something goes out — a post, a blog, a docs page, a release — record it **with the
artifact itself**. The text is the evidence; a log entry without it teaches nothing later.

```bash
python3 bin/shipped add --what "X post: 100m race timing" --channel x --artifact-file draft.md
```

Most of the time the artifact is already in the transcript: the user says "I posted this"
right after the agent produced the final version, so the preceding agent turn holds it.
Take it from there rather than asking them to paste it again.

## 2. Attach the outcome later

There is **no automatic feed** for how a post did. The verdict comes from the user, or from
numbers they pull (impressions, reposts, stars in the two weeks after a release, downloads).
Attach it whenever it arrives:

```bash
python3 bin/shipped outcome S001 --good --evidence "3.1k impressions, 40 reposts"
python3 bin/shipped list --pending      # what still has no verdict
```

Record the **evidence**, not just the verdict. "It did well" six weeks later is a memory;
"3.1k impressions vs ~600 typical" is a fact.

## 3. Mine the winners — only when a pattern repeats

```bash
python3 bin/shipped list --good
```

Read the good ones **together** and look for what they share that the others do not:
opening move, how the claim is stated, length, whether a number leads, what the first frame
shows, whether a limitation is named.

**One success is not a pattern.** A single post that did well is confounded by timing,
topic and luck. Require **at least three** entries showing the same trait before proposing
anything, and say how many support it. If only two, say so and wait — the log keeps.

Compare against the losers too. A trait shared by winners *and* neutral entries explains
nothing; what matters is what separates them.

## 4. Propose into the craft skill, never into L0

These are format-specific: what makes a launch post land is not a rule for any code or
research work. Route them the way the flush triage does:

| pattern about | goes to |
|---|---|
| visuals, renders, annotated clips | `alex-viz` |
| prose, structure, how a document opens | `alex-docs` |
| a library's public surface | `alex-api` |
| launch concept, metric phrasing, footage choice | `roboflow-release-promo` |

Propose the edit with its supporting entries quoted, and **wait for approval** — same
contract as correction mining.

## Honest limits, state them with any finding

- **Survivorship.** The log holds what was shipped. Ideas killed at a gate never appear, so
  it cannot tell you what would have worked.
- **Small n, self-reported.** Verdicts are the user's judgement unless a number is attached.
- **Confounds.** Reception depends on timing, audience and topic at least as much as craft.
  A pattern here is a hypothesis worth trying, not a finding.
