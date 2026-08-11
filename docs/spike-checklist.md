# Spike checklist — Alex's Rig (R2 dogfood)

Fill this while trying. No product code — evidence only. When done, paste results back into chat or check boxes in this file.

**Goal:** decide what to bootstrap vs build for uncommitted review, and confirm Desktop + dual-host habits.

---

## E1 — Desktop session diffs

- [ ] Open **Claude Code Desktop** on a real repo
- [ ] Set mode: **Plan** once, then **Edit automatically** (`acceptEdits`)
- [ ] Ask Claude to edit ≥2 files
- [ ] Find and click **`+N -M`** (or **Cmd+Shift+D** / Views → diff)
- [ ] Open ≥1 file diff; optionally leave a line comment

| Question | Your note |
|----------|-----------|
| Did you find `+N -M` without hunting? | |
| Is the diff pane good enough for daily session review? | Y / N / almost |
| Missing anything (per-turn tabs, open real file, …)? | |

---

## E7 — Uncommitted in VS Code (must-have)

- [ ] Same dirty tree open in **VS Code / Cursor**
- [ ] **Source Control**: open a changed file → side-by-side diff
- [ ] Install **Git Tree Compare** (`letmaik.git-tree-compare`)
- [ ] Compare working tree vs `main` (or default branch) → Open Diff → Open File

| Question | Your note |
|----------|-----------|
| SCM alone enough for uncommitted? | Y / N |
| Git Tree Compare better? | Y / N / install |
| Still hard to “see what changed”? | |

**Pass rule:** you can review uncommitted changes in the IDE without a commit/PR.

---

## E8 — Claude session sidebar (integrate candidates)

After an agent turn that edits files (Desktop or CLI with repo open in VS Code):

- [ ] Install **Claude Diff & Edit** (`dfarkash.claude-edits-scm`) — needs Claude Code ext nearby
- [ ] Confirm a “Changed Files” / review UI appears
- [ ] Optional: try **DiffDeck** (`RodneyZhang.diffdeck`) or **Claude Code Diff Review**

| Extension | Keep for bootstrap? | Why |
|-----------|---------------------|-----|
| Claude Diff & Edit | Y / N / maybe | |
| DiffDeck | Y / N / skip | |
| Other | | |

**If all N:** we design a thin Rig session-review skill/view (E9).

---

## E6 — PR path (extension OK)

- [ ] Install **GitHub Pull Requests** if needed
- [ ] Open a PR → **Checkout** (or `gh pr checkout N`)
- [ ] Open Diff vs **Open File** on one changed file

| Question | Your note |
|----------|-----------|
| Extension usable after checkout? | Y / N |
| Prefer `gh pr checkout` + SCM instead? | |

---

## E2 — Multi-agent (quick)

- [ ] Second session via worktree or `claude agents`
- [ ] Can you tell which folder/branch is which?

| Need custom SESSIONS.md registry? | Y / N / later |

---

## Dual-host smoke (decision #1)

- [ ] Same skill or plugin loads in **Desktop**
- [ ] Same skill or plugin loads in **VS Code Claude** (even a trivial test skill)

| Compatible enough for “both”? | Y / N / unknown yet |

---

## Verdict (fill last)

```text
Uncommitted IDE:   SCM only | + Git Tree Compare | + Claude Diff & Edit | need build
Desktop pane:      enough | need IDE more
PR:                extension OK | checkout-first docs
Session registry:  defer | need
Ready to freeze?:  Y / N
```

**Time budget:** ~30–60 minutes total.
