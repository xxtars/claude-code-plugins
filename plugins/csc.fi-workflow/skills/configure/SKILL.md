---
name: configure
description: Configure SLURM cluster connection for this project. Use when user first installs the plugin, says "configure slurm", or needs to update cluster settings.
---

# Configure SLURM Workflow

Set up the Cluster section in the project's `CLAUDE.md` so that other skills (`/sync`, `/check-jobs`, `/update-log`) can read the connection info.

## Steps

### Phase 1: Required (must collect)

1. Check if `CLAUDE.md` already has a `## Cluster` section. If so, show current settings and ask if the user wants to update or skip.

2. Collect:
   - **ssh_host**: SSH host alias or hostname (e.g., `mahti.csc.fi` or an alias from `~/.ssh/config`)
   - **slurm_user**: SLURM username (for `squeue -u`)
   - **slurm_account**: SLURM account/project (for `#SBATCH --account`)
   - **remote_path**: Project path on the cluster (e.g., `/scratch/project_xxx/username/project-name`)

3. Validate SSH connection: `ssh <ssh_host> "whoami && hostname"`. If it fails, help debug.

4. Write the `## Cluster` section in `CLAUDE.md`:
   ```markdown
   ## Cluster
   - Remote path: `<remote_path>`
   - Usage: `ssh <ssh_host> "cd <remote_path> && <command>"`
   - SLURM user: `<slurm_user>`
   - SLURM account: `<slurm_account>`
   - All commands run from project root
   ```

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
- SIF 容器目录: `<container_dir>`
- SIF 构建模板: `<build_template>`
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
- Deploy script convention
- Health check endpoint

If yes, append:
```markdown
## vLLM (CSC)
- deploy 脚本在容器内启动 vLLM server，run 脚本等待就绪后调用
- 健康检查用 `curl -s http://localhost:8000/v1/models`
```

**Overleaf** — ask if there's an Overleaf paper:
- Overleaf project path
- Target venue

If yes, append:
```markdown
## Overleaf
- Path: `overleaf/<project_id>/`
- Venue: <venue>
```

### Phase 3: Finish

5. Show the final CLAUDE.md Cluster section for confirmation.
6. Suggest running `/csc.fi-workflow:init` to scaffold experiment files if `experiments/` doesn't exist.

## Notes
- Do NOT create separate config files — CLAUDE.md IS the config
- If CLAUDE.md already has sections, update rather than duplicate
- Skip optional phases if the user declines — they can always re-run `/configure` later
- Collect all info by asking questions BEFORE writing, then write once
