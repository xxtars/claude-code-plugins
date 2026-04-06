---
name: configure
description: Configure SLURM cluster connection. Use when user first installs the plugin, says "configure slurm", or needs to update cluster settings.
---

# Configure SLURM Workflow

Set up the connection to the user's SLURM cluster. The config file lives at `~/.config/csc.fi-workflow/config.json`.

## Steps

1. Check if config already exists:
   !`cat ~/.config/csc.fi-workflow/config.json 2>/dev/null || echo "NO_CONFIG"`

2. If config exists, show current settings and ask if the user wants to update. If not, collect the following:

   - **ssh_host**: SSH host alias or hostname (e.g., `mahti.csc.fi` or an alias from `~/.ssh/config`)
   - **slurm_user**: SLURM username (for `squeue -u`)
   - **slurm_account**: SLURM account/project (for `#SBATCH --account`)
   - **scratch_base**: Base scratch directory (e.g., `/scratch/project_xxx/username`)
   - **container_dir**: Where SIF/Singularity containers are stored (optional)
   - **hf_cache**: HuggingFace cache path on the cluster (optional)
   - **github_host**: GitHub SSH host on the cluster (default: `github.com`)

3. Validate SSH connection: `ssh <ssh_host> "whoami && hostname"`. If it fails, help debug.

4. Write config to `~/.config/csc.fi-workflow/config.json`:
   ```json
   {
     "ssh_host": "...",
     "slurm_user": "...",
     "slurm_account": "...",
     "scratch_base": "...",
     "container_dir": "...",
     "hf_cache": "...",
     "github_host": "github.com"
   }
   ```

5. Confirm success and suggest running `/csc.fi-workflow:init` if this is a new project.

## Notes
- `mkdir -p ~/.config/csc.fi-workflow` before writing
- Only ask for optional fields if the user's workflow involves containers or HuggingFace
- If the user already has a working SSH alias, use that directly
