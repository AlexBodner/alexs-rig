# REVIEW — Alex's Rig **0.1.3** (architecture locked + full Rig hook set)

**Repo:** https://github.com/AlexBodner/alexs-rig  
**Proof matrix:** [docs/INTEGRATION.md](docs/INTEGRATION.md) · **Hooks:** [docs/hooks.md](docs/hooks.md) · **Practices:** [docs/practices.md](docs/practices.md)

Five events: SessionStart, PreCompact, UserPromptSubmit (L0 miss only), PreToolUse secret hygiene (read+write), Stop review nudge (once per session, never `decision: block`). Always-on graph is a pointer, not JSON in L0. Portable agent file is `AGENTS.md`.

Optional polish only: mining `other` noise, live Desktop confirm after plugin install, Claude Diff & Edit spike.
