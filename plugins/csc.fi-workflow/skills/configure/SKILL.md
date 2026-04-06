---
name: configure
description: Configure SLURM cluster connection for this project. Use when user first installs the plugin, says "configure slurm", or needs to update cluster settings.
---

# Configure SLURM Workflow

Set up the Cluster section in the project's `CLAUDE.md` so that other skills (`/sync`, `/check-jobs`, `/update-log`) can read the connection info.

## Steps

1. Check if `CLAUDE.md` already has a `## Cluster` section. If so, show current settings and ask if the user wants to update.

2. Collect the following from the user:

   - **ssh_host**: SSH host alias or hostname (e.g., `mahti.csc.fi` or an alias from `~/.ssh/config`)
   - **slurm_user**: SLURM username (for `squeue -u`)
   - **slurm_account**: SLURM account/project (for `#SBATCH --account`)
   - **remote_path**: Project path on the cluster (e.g., `/scratch/project_xxx/username/project-name`)
   - **scratch_base**: Base scratch directory (optional, e.g., `/scratch/project_xxx/username`)
   - **container_dir**: Where SIF/Singularity containers are stored (optional)
   - **hf_cache**: HuggingFace cache path on the cluster (optional)

3. Validate SSH connection: `ssh <ssh_host> "whoami && hostname"`. If it fails, help debug.

4. Write or update the `## Cluster` section in `CLAUDE.md`:
   ```markdown
   ## Cluster
   - Remote path: `<remote_path>`
   - Usage: `ssh <ssh_host> "cd <remote_path> && <command>"`
   - SLURM user: `<slurm_user>`
   - SLURM account: `<slurm_account>`
   - All commands run from project root
   ```
   Add optional fields only if provided (scratch_base, container_dir, hf_cache).

5. Confirm success and suggest running `/csc.fi-workflow:init` to scaffold experiment files.

## Notes
- If the user already has a working SSH alias, use that directly
- Only ask for optional fields if the user's workflow involves containers or HuggingFace
- Do NOT create a separate config file — CLAUDE.md IS the config
