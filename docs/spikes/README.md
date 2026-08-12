# Spikes — evidence log

Architecture **locked** 2026-08-12. Spikes below are historical / optional polish.

## Freeze evidence

| Spike | Result |
|-------|--------|
| E7 SCM + Git Tree Compare | Pass (box dogfood) — enough for uncommitted IDE |
| Desktop `+N -M` | Accepted as session map under OSS full-review bar |
| Custom DiffEditor | **Won't build** |
| Mining scope | MVP = all workspaces + `--workspace` / `--since` |
| Claude Diff & Edit | Optional convenience — not required for lock |
| Always-on knowledge graph | **Adopted** — understand-anything + codemap-py; SessionStart pointer; not a second engine |

## Optional later

- Live SessionStart confirm on each machine after plugin install
- Claude Diff & Edit dogfood notes
- Mining `other` cluster noise reduction

## 0.1.2 practice pass (2026-08-12)

Verified against [agents.md](https://agents.md/), [Cursor rules](https://cursor.com/docs/rules.md), [Claude hooks](https://code.claude.com/docs/en/hooks.md), [plugins reference](https://code.claude.com/docs/en/plugins-reference), [harness guide](https://capitalandcompute.net/blog/claude-code-harness-guide/):

- Graph pointer via SessionStart (unittest), not graph JSON in L0
- `AGENTS.md` + thin `CLAUDE.md`; Cursor `.mdc` rule alongside `.md`
- Plugin metadata (`homepage`, `repository`, `license`)
- Live Desktop SessionStart still a human confirm after `install_claude_plugin.sh`
