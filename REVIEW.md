# REVIEW — Alex's Rig **0.1.5** (ready to delegate)

**Repo:** https://github.com/AlexBodner/alexs-rig  
**Proof matrix:** [docs/INTEGRATION.md](docs/INTEGRATION.md) · **Hooks:** [docs/hooks.md](docs/hooks.md) · **How to use:** [docs/HOW-TO.md](docs/HOW-TO.md) · **Agent prompts:** [prompts/README.md](prompts/README.md)

Locked loop: Plan → Edit automatically → batch review. Review UI is a **vsix** (`./scripts/install.sh` + Reload Window once). Source Control → Review covers session and PR Viewed. Five hook events: SessionStart, PreCompact, UserPromptSubmit (L0 miss only), PreToolUse secret hygiene, Stop (once per dirty round, never `decision: block`). Graph is a pointer, not JSON in L0.

Human-only leftover: signed-in SessionStart (“What does my L0 say?”) and Desktop `+N -M`. Optional polish: mining `other` noise, SessionStart notes, Claude Diff & Edit spike.

## Dogfood notes

2026-08-13: folder copy into `~/.vscode/extensions` does not register. vsix + `code`/`cursor --install-extension` does. Viewed check/uncheck works after that.
