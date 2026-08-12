# Harness practices (adopted, not invented)

Alex's Rig follows 2026 agent-harness practice: **small always-on context**, **on-demand skills**, **hooks for guarantees**, **portable AGENTS.md**. Sources below were fetched and read before this page was written.

## Context ledger

| Primitive | Role here | Why |
|-----------|-----------|-----|
| [AGENTS.md](https://agents.md/) | Portable agent instructions (this repo) | Cross-tool standard (Cursor, Claude Code, Codex, Copilot). README stays human-facing. |
| `CLAUDE.md` | Two-line Claude overlay + `@AGENTS.md` | Claude-specific hooks/Desktop notes without duplicating AGENTS.md ([Cursor rules](https://cursor.com/docs/rules.md) treat AGENTS.md as the simple alternative to a rule pile). |
| Plugin `rules/` | One short always-on graph habit | Cursor project rules are `.mdc` with frontmatter ([docs](https://cursor.com/docs/rules.md)). Claude plugin `rules` is not a first-class manifest field; SessionStart is the guarantee. |
| Skills `skills/alex-*` | Workflows loaded when needed | Skill **descriptions** stay in context; bodies load on use ([harness guide](https://capitalandcompute.net/blog/claude-code-harness-guide/)). |
| Hooks | L0 inject, compact reinject, secret block | Only deterministic lane. SessionStart stdout is the documented inject channel ([Claude hooks](https://code.claude.com/docs/en/hooks.md)). |
| understand-anything + codemap-py | Standing codebase graph | Query, don't dump. Graph JSON is megabytes; L0 only stores `P-graph`. |

## What we refuse (same sources)

- A 400-line CLAUDE.md (Anthropic ~200-line ceiling; ignored instructions).
- Dumping `knowledge-graph.json` into L0 or SessionStart.
- A second graph engine, custom DiffEditor, or AI-Rig fork.
- Stop-hook test gates on every turn (wrong for a multi-project personal harness).
- SessionStart matchers that skip `resume` (L0 must survive a resumed session).

## Plugin manifests

Claude Code: `name` is the only required field; `homepage` / `repository` / `license` / `keywords` are documented metadata ([plugins reference](https://code.claude.com/docs/en/plugins-reference)). Unrecognized fields (Cursor's `rules`) are ignored, not fatal.

Cursor: `.cursor-plugin/plugin.json` points at `rules`, `skills`, `commands`, `hooks/cursor-hooks.json`. Official Cursor plugin examples use `.mdc` rules; this repo ships both `.md` (Claude-style) and `.mdc` (Cursor-style) with the same body.
