---
name: sync
description: Sync local code to SLURM cluster via git. Use when user says "sync", "sync code", "push to cluster", "push to CSC", or after code changes that need to run on the cluster. Do NOT use for Overleaf sync — that's /overleaf-workflow:sync.
---

# Sync Code to Cluster

Push local code to the SLURM cluster via GitHub.

## Prerequisites

Read the project's `CLAUDE.md` for:
- **ssh_host**: from the `Usage: ssh <host> ...` line in the Cluster section
- **remote_path**: from the `Remote path` line in the Cluster section

If not found, suggest running `/csc.fi-workflow:configure`.

## Flow

```
local commit → git push → ssh pull on cluster
```

### Steps

1. **Check local state**: `git status` — warn if there are unstaged changes or untracked files that should be committed.

2. **Commit** (if needed): Stage relevant files and commit. Follow the project's commit conventions. NEVER use `git add -f` to force-add ignored files.

3. **Push**: `git push` to the remote.

4. **Verify remote path exists**:
   ```bash
   ssh <ssh_host> "test -d <remote_path> && echo 'OK' || echo 'MISSING'"
   ```
   If MISSING, report the error and suggest checking the path in CLAUDE.md. Do NOT proceed.

5. **Pull on cluster**:
   ```bash
   ssh <ssh_host> "cd <remote_path> && git pull"
   ```

6. **Confirm**: Report success and show the latest commit hash on both sides.

### Error handling
- If push fails (no remote, auth issue), help debug but don't force-push
- If pull fails on cluster (merge conflict, dirty state), report the error — don't run `git reset` without user approval

## Notes
- This skill only syncs code. It does NOT submit SLURM jobs — that's the user's choice after sync
- Respect `.gitignore` — never force-add ignored files
