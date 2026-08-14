# Design — Correction learning from your turns

**Status:** implemented as a two-stage system (see `docs/mining.md` for the operational reference).
**Feeds:** Alex's Rig `PRINCIPLES.jsonl` / L0 via `principle-upsert` — approval-gated.
**Beside:** Borda AI-Rig (how to build) — this learns *your* correction patterns.

---

## Two-stage design (what shipped)

The original sketch (below) proposed an LLM scan that proposes principles. What shipped splits that
into a **cheap capture** and an **on-demand LLM flush**, so the expensive step runs only when you
ask and never writes L0 without approval:

1. **Capture (Stage 1, zero-LLM).** `hooks/capture_correction.py` (UserPromptSubmit, beside
   `prompt_l0_miss.py`) scores each prompt with a small transparent weighted heuristic and appends
   raw rows to `docs/memory/mining/corrections-inbox.jsonl`. Silent, fail-open.
   - **Detector grounding:** corrections overwhelmingly open with "no," (also
     `nope`/`wait,`/`actually,`/`hmm,`); strongest cheap signal = short "no," opener + a
     negation/rule-verb. Weighted signals: strong opener (+3), soft opener (+2), negation (+1),
     rule verb `should/must/always/never` (+1), preference `i want/instead/just/no need` (+1),
     pending unreviewed edits (+1); threshold 3. No `again` keyword (means "re-run" here).
   - `bin/mine-corrections` is the optional bulk importer: same detector over Cursor
     `agent-transcripts`, appends to the same inbox. No templates, no auto-upsert.
2. **Flush (Stage 2, LLM, approval-gated).** `/alex-mine-corrections` reads the inbox, clusters it,
   synthesizes a few **general** principles with evidence, and — only on approval — `principle-upsert`s
   them, then `bin/corrections flush` + `bin/l0-regen`.

`bin/corrections list|flush` manages the inbox; generalization lives only in the flush skill.

---

## Original sketch (retained for context)

## Goal

Launch an agent that:

1. **Reads** your Cursor conversation history (local).
2. **Lists** corrections you made (pushback, “no, do X”, reverts of agent approach, style fixes).
3. **Clusters** common patterns — what you intend agents to do, and what you look for in code.
4. **Proposes** principle candidates for **you** to accept → `principle-upsert` (never silent L0 write).

---

## Data sources (local)

| Source | Path pattern (macOS) | Notes |
| --- | --- | --- |
| Per-workspace transcripts | `~/.cursor/projects/<workspace-id>/agent-transcripts/**/*.jsonl` | One JSON object per line; user/assistant messages; subagents under `subagents/` |
| Many workspaces | `~/.cursor/projects/*/agent-transcripts/` | Correction mining should scan **all** (or allow `--workspace` filter) |
| Search index | Cursor `SearchConversations` tool (agent-side) | Fast titles/snippets; not full transcript — use for discovery, then read JSONL for depth |

**Privacy (locked):** local-only by default; no upload; redact secrets (`.env`, keys, tokens) before any written artifact; artifacts live under project `docs/memory/` or `.alexs-rig/` (gitignored if sensitive).

---

## Pipeline

```text
1. DISCOVER
   list workspaces / conversation IDs (SearchConversations or find jsonl)
2. EXTRACT corrections
   heuristics + LLM pass on user turns that look like corrections
3. NORMALIZE
   one row per correction: {id, quote, context, repo?, date, tags[]}
4. CLUSTER
   group into patterns: intent / code-review lens / anti-patterns
5. PROPOSE principles
   5–15 one-liners max → human accept/edit/reject
6. UPSERT
   principle-upsert for accepted only → regen L0
```

### What counts as a “correction”

Include when user message (or follow-up) signals:

- Explicit fix: “no”, “don’t”, “instead”, “wrong”, “revert”, “stop doing X”
- Preference: “I prefer”, “always”, “never”, “in my projects…”
- Review lens: “check for…”, “I look for…”, “make sure…”
- Process: “ask before commit”, “use Plan”, “don’t stop on every edit”

Exclude: pure task statements with no pushback; huge pasted logs; secrets.

### Outputs (files)

```text
docs/memory/mining/
  corrections.jsonl     # extracted rows (id-addressable)
  patterns.md           # clustered themes (human-readable)
  principle-candidates.md   # proposed one-liners + evidence links
```

Human reviews `principle-candidates.md` → accepted lines become `PRINCIPLES.jsonl`.

---

## Agent / skill shape (later build)

| Piece | Role |
| --- | --- |
| `/alex-mine-corrections` (skill) | Orchestrates discover → extract → cluster → propose |
| Optional subagent | Long scan across many jsonl files (bounded batch) |
| CLI `mine-corrections` | Non-LLM listing of candidate user turns (grep heuristics) for speed |
| Gate | Auto-upsert named clusters; skip `other`; `--no-apply` for candidates-only |

### UX

```text
You: /alex-mine-corrections --last 30d
Agent: Found 47 correction-like turns across 12 chats.
       Wrote docs/memory/mining/corrections.jsonl
       Top patterns:
         1. Prefer batch review over per-edit stops (12)
         2. Plain-file standing state (8)
         …
       Proposed 9 principles → open principle-candidates.md
You: accept 1,2,5,7 → principle-upsert …
```

---

## Risks & mitigations

| Risk | Mitigation |
| --- | --- |
| Too much noise | Heuristic prefilter + cap candidates; human accept |
| Privacy / secrets | Redact; gitignore mining/ if needed; local-only |
| Stale patterns | Re-run; upsert supersedes old principle ids |
| Token blowup | Batch by workspace/date; summarize clusters, don’t dump all chats into L0 |
| Wrong “corrections” | Evidence quote + conversation id in candidates file |

---

## Spike before build (correction mining)

- [ ] Confirm you can list ≥3 past chats via transcripts or SearchConversations
- [ ] Manually open one jsonl; spot 2–3 real corrections by eye
- [ ] Decide scope v1: **all workspaces** vs **current project only**
- [ ] Decide: mining runs in **Cursor** (has transcript access) vs **Claude Desktop** (may need export/copy path)

**v1 recommendation:** run mining **from Cursor** (transcripts live there); write principles into the shared `docs/memory/` the Desktop harness also reads.

---

## Relation to MVP

| MVP now | This feature |
|---------|----------------|
| Empty/manual PRINCIPLES + upsert skill | Fills principles from history |
| L0 injection | Consumes accepted principles |

Ship memory upserts first; mining can be **v1.1** right after, or parallel once spikes clear — your call at architecture freeze.
