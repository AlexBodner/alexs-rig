---
name: alex-session-review
description: Review uncommitted session files and the current PR in one Source Control list. Viewed checkbox; agent re-edits un-view them. Not a DiffEditor.
---

# Alex review (session + PR, one list)

Architecture lock: Desktop **`+N -M`** is the session map. IDE marking is one **Review** view, not the GitHub Pull Requests extension.

## In Cursor / VS Code

1. Open **Source Control → Review**.
2. Toolbar **session** = files since session open. Toolbar **pull request** = files vs the PR base (committed PR + local edits). On a PR branch this starts on PR.
3. Click a file → native diff. Check **Viewed**. Content change unchecks.

Same checkboxes for both compares. You do not mark Viewed in two extensions.

Requires `./scripts/install_review_extension.sh`. Reload Window once.

## Desktop

Click **`+N -M`** / Cmd+Shift+D for the live map, then mark Viewed in Review.

## GitHub comments / merge

Optional: GitHub website, or GitHub Pull Requests extension. Not required for Viewed.

## Fallback CLI (headless / tests)

```bash
python3 bin/review-pending --name-only
python3 bin/review-mark path/to/file.py
python3 bin/review-mark --all
```

## Not this skill

- Building a custom DiffEditor → **forbidden**
- Silent auto-PR → **forbidden**
