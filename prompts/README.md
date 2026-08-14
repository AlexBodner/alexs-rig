# Prompts for agents

Architecture is **locked**. Product on `main` is installable (`./scripts/install.sh` + Review vsix). Do not reopen `docs/architecture.md`.

| Prompt | Give this when |
|--------|----------------|
| [AGENT_TRY.md](./AGENT_TRY.md) | Repo already open — dogfood like a human |
| [AGENT_COMPUTER.md](./AGENT_COMPUTER.md) | Own computer + GUI — clone from GitHub, click Review / SessionStart |
| [AGENT_BOX_VERIFY.md](./AGENT_BOX_VERIFY.md) | CLI scoreboard (B1–B17), no Desktop claims |
| [AGENT_SIMULATE_USAGE.md](./AGENT_SIMULATE_USAGE.md) | Multi-PR while forcing Rig rituals (remaining polish only) |
| [AGENT_ITERATE.md](./AGENT_ITERATE.md) | One backlog item — mining `other`, SessionStart notes, or spike notes |

## Delegate (copy one)

**Try (workspace is this clone):**

> Follow `prompts/AGENT_TRY.md` exactly. Dogfood the daily loop; do not implement the iterate backlog. End with the Dogfood report.

**Own computer + mouse:**

> Follow `prompts/AGENT_COMPUTER.md` exactly. Clone https://github.com/AlexBodner/alexs-rig, run `./scripts/install.sh`, try Source Control → Review and “What does my L0 say?”. No push. End with the report.

**Box verify (tools only):**

> Follow `prompts/AGENT_BOX_VERIFY.md` exactly. Run B1–B17; fill the scoreboard; no push; no Desktop claims.

**Simulate usage (multi-PR):**

> Follow `prompts/AGENT_SIMULATE_USAGE.md` exactly. Default epic is post-lock polish (not the shipped `--root` / bootstrap / l0-show / CI work). Push/PR: no — leave local branches + ready PR bodies. End with the Usage simulation report.

**Iterate:**

> Follow `prompts/AGENT_ITERATE.md` exactly. Start with backlog item 1. Keep tests green. Summarize Done / Not done / How to try when finished.
