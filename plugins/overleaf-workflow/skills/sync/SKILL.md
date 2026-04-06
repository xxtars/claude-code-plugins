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
2. **Pull first** to avoid conflicts with collaborator edits:
   ```bash
   cd overleaf/<project_id>
   git pull
   ```
   If pull conflicts arise, resolve them (see Handling Conflicts below) before proceeding.
3. Check `git status` to review what changed
4. Stage changed files (use specific filenames from `git status`, not `git add -A`), commit, push:
   ```bash
   git add sections/experiments.tex references.bib   # example: only changed files
   git commit -m "<concise description>"
   git push
   ```

## Pull (Overleaf → local)

1. `cd` into the overleaf subdirectory
2. **Stash uncommitted changes** if any exist, to prevent losing local work:
   ```bash
   cd overleaf/<project_id>
   git stash --include-untracked   # only if git status shows changes
   git pull
   git stash pop                   # only if we stashed above
   ```
3. If `git stash pop` produces conflicts, see Handling Conflicts below.

## Handling conflicts

If pull or stash pop results in merge conflicts:
1. Show the conflicting files (`git diff --name-only --diff-filter=U`)
2. Show the conflict markers in each file so the user can see both versions
3. Ask the user which version to keep (or how to merge)
4. Resolve, stage, and commit

## Important
- ALWAYS `cd` into the overleaf subdirectory before any git operations — it is a separate repo from the main project
- After push, changes appear on Overleaf within seconds
- After pull, you can read the latest tex files to see collaborator edits
- Keep commit messages short and descriptive (e.g., "Update Table 1 baselines", "Add related work section")
