# Agent instructions

Portable agent file ([AGENTS.md](https://agents.md/)). Humans start at [README.md](README.md)
and [docs/usage.md](docs/usage.md). Claude-only notes live in [CLAUDE.md](CLAUDE.md).

## What this is

A Claude Code plugin, Python 3.10+ standard library only. Standing memory (L0) injected by
hooks, correction capture and mining, session-scoped review, a verify status, secret
hygiene, and orchestration of an existing codebase graph (understand-anything). It does not
implement a graph engine of its own.

## Commands

```bash
python3 -m unittest discover -s tests -v   # the suite CI runs
ruff check .
python3 bin/l0-show                        # what a session gets injected
python3 bin/graph-status                   # which graphs exist here
echo '{"source":"startup"}' | python3 hooks/inject_l0.py | python3 -m json.tool
```

## Conventions

- Cut a branch from main, land through a PR. Commit and push only when asked.
- Review is per file: `bin/review-pending` lists agent edits since the session opened,
  `bin/review-mark` marks them at their current content. There is no IDE panel.
- Memory CLIs take `--root` or `ALEXS_RIG_MEMORY`. Never hand-edit `docs/memory/snapshots/L0.md`;
  run `bin/l0-regen`.
- Query understand-anything or codemap-py before a blind grep of architecture. Never dump
  `knowledge-graph.json` into L0 or chat.
- Keep always-on text small. Detail belongs in `skills/alex-*` and `docs/`.
- No new dependencies. Hooks are fail-open and print nothing but their JSON payload; the
  shape they must emit is in [docs/hooks.md](docs/hooks.md).
- Prose: no em dashes in body text, short sentences, features before rationale.
