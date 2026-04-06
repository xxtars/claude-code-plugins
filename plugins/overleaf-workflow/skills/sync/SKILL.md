---
name: sync
description: Sync Overleaf project. Use when user says "sync overleaf", "push to overleaf", "pull from overleaf", or after editing paper locally.
---

# Sync Overleaf

Push local changes to Overleaf or pull remote changes.

## Finding the Overleaf directory

Look for the Overleaf path in the project's `CLAUDE.md` (under "Overleaf" section). Typically `overleaf/<project_id>/`.

## Push (local → Overleaf)

```bash
cd overleaf/<project_id>
git add -A
git commit -m "<concise description of changes>"
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
