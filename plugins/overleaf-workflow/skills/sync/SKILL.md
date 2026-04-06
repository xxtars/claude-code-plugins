---
name: sync
description: Sync Overleaf project via git. Use when user says "sync overleaf", "push to overleaf", "pull from overleaf", "push paper", or after editing paper locally. Do NOT use for cluster code sync — that's /csc.fi-workflow:sync.
---

# Sync Overleaf

Push local changes to Overleaf or pull remote changes.

## Finding the Overleaf directory

Look for the Overleaf path in the project's `CLAUDE.md` (under "Overleaf" section). Typically `overleaf/<project_id>/`.

## Push (local → Overleaf)

1. `cd` into the overleaf subdirectory
2. Check `git status` to review what changed
3. Stage relevant files, commit with a concise message, push:
   ```bash
   cd overleaf/<project_id>
   git add <changed files>
   git commit -m "<concise description>"
   git push
   ```

## Pull (Overleaf → local)

```bash
cd overleaf/<project_id>
git pull
```

## Handling conflicts

If pull results in merge conflicts:
1. Show the conflicting files
2. Ask the user which version to keep
3. Resolve and commit

## Important
- ALWAYS `cd` into the overleaf subdirectory before any git operations — it is a separate repo from the main project
- After push, changes appear on Overleaf within seconds
- After pull, you can read the latest tex files to see collaborator edits
- Keep commit messages short and descriptive (e.g., "Update Table 1 baselines", "Add related work section")
