---
name: configure
description: Configure SLURM cluster connection for this project. Use when user first installs the plugin, says "configure cluster", "configure slurm", or needs to update cluster settings. Do NOT use for Overleaf — that's /overleaf-workflow:configure.
---

# Configure SLURM Workflow

Set up the Cluster section in the project's `CLAUDE.md` so that other skills (`/csc.fi-workflow:sync`, `/csc.fi-workflow:check-jobs`, `/csc.fi-workflow:update-log`) can read the connection info.

## Steps

### Phase 1: Required (must collect)

1. Check if `CLAUDE.md` already has a `## Cluster` section. If so, show current settings and ask if the user wants to update or skip.

2. Collect:
   - **ssh_host**: SSH host alias or hostname (e.g., `mahti.csc.fi` or an alias from `~/.ssh/config`)
   - **slurm_user**: SLURM username (for `squeue -u`)
   - **slurm_account**: SLURM account/project (for `#SBATCH --account`)
   - **remote_path**: Project path on the cluster (e.g., `/scratch/project_xxx/username/project-name`)
   - **job_name_prefix**: Job name prefix used by this project's sbatch scripts (e.g., `ep-` for EmotionProbe, `nlgrpo-` for an RL run). Used by `/csc.fi-workflow:watch` to scope queue polling to this project when multiple projects share the same `slurm_user`. Suggest a default derived from the project directory basename (lowercase, short — `EmotionProbe` → `ep-`); confirm or override with the user. If the project genuinely has no naming convention, leave empty — `/csc.fi-workflow:watch` will then require an explicit `JOBIDS=` list.

3. Validate SSH connection: `ssh <ssh_host> "whoami && hostname"`. If it fails, help debug.

4. Validate remote path is accessible and writable:
   ```bash
   ssh <ssh_host> "test -d <remote_path> && test -w <remote_path> && echo 'OK' || echo 'ERROR: path missing or not writable'"
   ```
   If it fails, help the user correct the path before proceeding.

5. Write the `## Cluster` section in `CLAUDE.md`:
   ```markdown
   ## Cluster
   - Remote path: `<remote_path>`
   - Usage: `ssh <ssh_host> "cd <remote_path> && <command>"`
   - SLURM user: `<slurm_user>`
   - SLURM account: `<slurm_account>`
   - Job name prefix: `<job_name_prefix>` (used by `/csc.fi-workflow:watch` to scope queue polling to this project)
   - All commands run from project root
   ```
   Omit the `Job name prefix` line entirely if the user left it empty.

### Phase 2: Optional (ask "Do you want to configure X?")

**CSC Paths** — ask if the user works with containers or HuggingFace models:
- Scratch base (e.g., `/scratch/project_xxx/username/`)
- Datasets path
- SIF container directory
- SIF build template path
- HuggingFace cache path
- APPTAINER_TMPDIR

If yes, append under Cluster:
```markdown
### CSC Paths
- Scratch: `<scratch_base>`
- Datasets: `<datasets_path>`
- SIF container directory: `<container_dir>`
- SIF build template: `<build_template>`
- HF cache: `<hf_cache>`
- APPTAINER_TMPDIR: `<tmpdir>`
```

**GitHub SSH** — ask if local and cluster use different GitHub SSH configs:
- Local SSH host alias (e.g., `github-xxtars`)
- Cluster SSH host (default: `github.com`)

If yes, append:
```markdown
### GitHub SSH
- Local: host alias `<local_alias>` → `git@<local_alias>:username/<repo>.git`
- CSC: `<cluster_host>` → `git@<cluster_host>:username/<repo>.git`
```

**vLLM** — ask if the project uses vLLM on the cluster:

If yes, append:
```markdown
## vLLM (CSC)
- deploy script starts vLLM server inside container; run scripts wait for readiness then call API
- Health check: `curl -s http://localhost:8000/v1/models`
```

### Phase 3: Finish

6. Show the final CLAUDE.md for confirmation.
7. Suggest running `/csc.fi-workflow:init` to scaffold experiment files if `experiments/` doesn't exist.

## Notes
- Do NOT create separate config files — CLAUDE.md IS the config
- If CLAUDE.md already has sections, update rather than duplicate
- Skip optional phases if the user declines — they can always re-run `/csc.fi-workflow:configure` later
- Collect all info by asking questions BEFORE writing, then write once
- Do NOT configure Overleaf here — use `/overleaf-workflow:configure` for that
