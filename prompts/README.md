# Prompts for agents

| Prompt | Use when |
|--------|----------|
| [AGENT_TRY.md](./AGENT_TRY.md) | Dogfood — try the harness **like a human** (first pass) |
| [AGENT_BOX_VERIFY.md](./AGENT_BOX_VERIFY.md) | Scoreboard — specific PASS/FAIL CLI checks on **its own computer** |
| [AGENT_SIMULATE_USAGE.md](./AGENT_SIMULATE_USAGE.md) | **Real multi-PR project** while forcing Rig rituals (L0 / pending / batch review) |
| [AGENT_ITERATE.md](./AGENT_ITERATE.md) | Improve the harness — single-backlog-item coding without the full usage sim |

## One-liner — try it like me

> Follow `prompts/AGENT_TRY.md` exactly. Dogfood the daily loop; do not implement the iterate backlog. End with the Dogfood report.

## One-liner — box verify (tools)

> Follow `prompts/AGENT_BOX_VERIFY.md` exactly. Run B1–B16; fill the scoreboard; no push; no Desktop claims.

## One-liner — simulate proper usage (multi-PR)

Branches + commits only (default):

> Follow `prompts/AGENT_SIMULATE_USAGE.md` exactly. Default epic PR1–PR4 on this repo. Push/PR: no — leave local branches + ready PR bodies. End with the Usage simulation report.

With publish authorized:

> Follow `prompts/AGENT_SIMULATE_USAGE.md` exactly. Default epic PR1–PR4. You may push branches and open PRs with `gh`. Do not merge. End with the Usage simulation report.

## One-liner — iterate the code

> Follow `prompts/AGENT_ITERATE.md` exactly. Start with backlog item 1. Keep tests green. Summarize Done / Not done / How to try when finished.
