---
name: sync
description: Sync local code to SLURM cluster. Use when user says "sync", "push to cluster", "push to CSC", or after code changes that need to run on the cluster.
---

# Sync to Cluster

Push local code to the SLURM cluster via GitHub.

## Config
!`cat ~/.config/csc.fi-workflow/config.json 2>/dev/null || echo '⚠️ Not configured. Run /csc.fi-workflow:configure first.'`

## Flow

```
local commit → git push → ssh pull on cluster
```

### Steps

1. **Check local state**: `git status` — warn if there are unstaged changes or untracked files that should be committed.

2. **Commit** (if needed): Stage relevant files and commit. Follow the project's commit conventions. NEVER use `git add -f` to force-add ignored files.

3. **Push**: `git push` to the remote.

4. **Pull on cluster**: Read the project's remote path from `CLAUDE.md` (look for "Remote path" under Cluster section), then:
   ```bash
   ssh <ssh_host> "cd <remote_path> && git pull"
   ```

5. **Confirm**: Report success and show the latest commit hash on both sides.

### Error handling
- If push fails (no remote, auth issue), help debug but don't force-push
- If pull fails on cluster (merge conflict, dirty state), report the error — don't run `git reset` without user approval
- If remote path is not found in CLAUDE.md, ask the user and suggest running `/csc.fi-workflow:init`

## Notes
- This skill only syncs code. It does NOT submit SLURM jobs — that's the user's choice after sync
- Respect `.gitignore` — never force-add ignored files
