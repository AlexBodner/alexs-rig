# alex-mine-corrections

Stage-2 flush: read the corrections inbox (captured cheaply from your turns), cluster it, and
propose GENERAL reusable principles. Nothing reaches L0 without your explicit approval.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/bin/corrections list
```

Then follow `skills/alex-mine-corrections/SKILL.md`: cluster → propose with evidence → on approval
`principle-upsert` the accepted ones → `bin/corrections flush` + `bin/l0-regen`. Optionally seed the
inbox with history first: `python3 ${CLAUDE_PLUGIN_ROOT}/bin/mine-corrections $ARGUMENTS`.
