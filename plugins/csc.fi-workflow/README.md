# csc.fi-workflow

A [Claude Code](https://claude.ai/code) plugin for ML researchers working on [CSC](https://www.csc.fi/) (Finland's IT Center for Science) SLURM clusters (Mahti, Puhti).

Provides a structured workflow for syncing code, monitoring jobs, and tracking experiment progress via Apptainer containers — so you can focus on research instead of cluster logistics.

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Configure | `/csc.fi-workflow:configure` | Set up cluster connection (SSH, account, paths) |
| Init | `/csc.fi-workflow:init` | Scaffold experiment management files for a new project |
| Sync | `/csc.fi-workflow:sync` | Push code to cluster: `commit → push → ssh pull` |
| Check Jobs | `/csc.fi-workflow:check-jobs` | Query SLURM queue and recent job status |
| Submit | `/csc.fi-workflow:submit` | Submit SLURM job and auto-record in experiment log |
| Update Log | `/csc.fi-workflow:update-log` | Record job results into structured experiment logs |

## Rules (always-on)

Rules are automatically loaded into every conversation. They guide Claude's behavior when writing scripts or managing experiment files for this project.

- **SLURM Shell Conventions** (`slurm-shell.md`) — Never `set -e` in SLURM scripts; use Apptainer containers (not conda); three-layer script structure (`submit_*.sh` → `sbatch_*.sh` → `run/*.sh`); build SIF on compute nodes with `/dev/shm` as TMPDIR
- **Experiment File Management** (`experiment-files.md`) — Four-file system (PLAN / LOG / PITFALLS / weekly); LOG.md only holds milestones (no intermediate numbers); weekly log numbers must be verified from actual cluster output and tagged with source + date

## Install

```bash
claude plugin install xxtars/csc.fi-workflow
```

## Quick Start

```bash
# 1. Configure your cluster connection
/csc.fi-workflow:configure

# 2. In a new project, scaffold experiment files
/csc.fi-workflow:init

# 3. Daily workflow
/sync                    # push code to cluster
/check-jobs              # see what's running
/update-log              # record results
```

## Requirements

- SSH access to a CSC cluster (Mahti or Puhti, with key-based auth recommended — passphrase-free or via `ssh-agent`)
- Git repository for your project (synced via GitHub/GitLab)
- Apptainer (pre-installed on CSC clusters)

## Skill Details

### `/csc.fi-workflow:configure`

One-time setup per project. Collects SSH host, SLURM user/account, and remote project path, then writes a `## Cluster` section in CLAUDE.md. No separate config files — CLAUDE.md is the single source of truth.

**What it does:**
1. **Required**: Collects `ssh_host`, `slurm_user`, `slurm_account`, `remote_path`
2. **Validates SSH**: Runs `whoami && hostname` on the cluster to confirm connectivity
3. **Validates remote path**: Checks the path exists and is writable (`test -d && test -w`) — catches typos before they cause silent failures later
4. **Optional**: CSC-specific paths (scratch, datasets, SIF containers, HF cache, APPTAINER_TMPDIR), GitHub SSH aliases (if local and cluster use different configs), vLLM setup
5. Writes everything to CLAUDE.md and suggests `/init` if experiment files don't exist yet

### `/csc.fi-workflow:init`

Scaffolds the experiment management structure:

```
experiments/
  PLAN.md        <- What you're doing and why (research goal, pipeline, experiment design)
  LOG.md         <- High-level progress (status table + milestone summaries)
  PITFALLS.md    <- Lessons learned (symptom / root cause / fix / date)
  weekly/
    week-2026-04-07.md  <- Detailed job records + verified results
```

Does not overwrite existing files — asks before replacing.

### `/csc.fi-workflow:sync`

Pushes local code to the cluster via GitHub:

```
local commit -> git push -> ssh pull on cluster
```

**Safety checks:**
- Warns about unstaged/untracked files before committing
- **Verifies remote path exists** on the cluster before pulling — if the path is wrong, reports the error immediately instead of failing silently
- Never force-adds ignored files; never force-pushes
- Does NOT auto-submit SLURM jobs — that's your choice after sync

### `/csc.fi-workflow:check-jobs`

Queries `squeue` (active) and `sacct` (recent 3 days) in a single SSH call.

**Key features:**
- **Failed job diagnosis**: For FAILED/TIMEOUT/OUT_OF_MEMORY jobs, automatically runs `scontrol show job` to get the stderr path, then reads the last 30 lines of the error log. Summarizes the failure reason and suggests adding to PITFALLS.md if it's a new type of failure
- **Project-level filtering**: Reads job names from your weekly log and LOG.md to identify which jobs belong to the current project. Jobs from other projects are shown separately so you can focus on what matters
- Filters out `.batch` and `.extern` sub-jobs from sacct output
- All timestamps use the cluster's timezone (via remote `date` command, not local)

### `/csc.fi-workflow:submit`

Submits a SLURM job and **automatically records** it in the experiment log. Replaces the manual workflow of "sbatch → then remember to update the log".

**What it does:**
1. Runs `sbatch` on the cluster and captures the job ID
2. Gets the current git commit hash
3. Adds a row to the weekly log's Job History table (job name, ID, partition, submitted date, commit hash, status=PENDING)
4. Updates the corresponding stage in LOG.md if applicable
5. Reports a clean summary

Use this instead of raw `sbatch` whenever you want automatic tracking.

### `/csc.fi-workflow:update-log`

Records job results into the weekly log and LOG.md.

**Key features:**
- **Auto-creates weekly log**: Calculates the Monday of the current week and creates the file from the template if it doesn't exist. No more getting the date wrong
- **Smart diff**: Parses existing Job History in the weekly log, queries `sacct`, and shows a diff summary ("3 new jobs, 2 status updates, 1 newly failed") before writing — so you review before changes are made
- **Verified results only**: Never guesses or copies numbers from memory. Must read actual output files on the cluster, tagged with source path and date
- **Three-section weekly log**: Job History (table), Verified Results (numbers from cluster), Notes (observations/decisions, no raw numbers)
- LOG.md gets milestone status updates only — no intermediate numbers that go stale

## Experiment Management

### File Responsibilities

| File | Purpose | When to update |
|------|---------|----------------|
| `PLAN.md` | Research direction, pipeline design, experiment planning | When strategy changes |
| `LOG.md` | Status table + milestone summaries + weekly log index | After each milestone |
| `PITFALLS.md` | Lessons learned (symptom, root cause, fix) | When discovering new pitfalls |
| `weekly/week-*.md` | Detailed job records + verified results + notes | During the week |

### Weekly Log Format

Each weekly log has three sections:

**Job History** — a table tracking every SLURM job:

| Job Name | Job ID | Pipeline | Dataset | Partition | Submitted | Started | Finished | Status | Commit |
|----------|--------|----------|---------|-----------|-----------|---------|----------|--------|--------|

The `Commit` column records the git commit hash that was running, so you can reproduce any result later.

**Verified Results** — numbers read from actual cluster output, tagged with source and date. Nothing is written here until the output file is read.

**Notes** — observations, decisions, analysis. No raw numbers that might become stale.

### SLURM Script Structure

The plugin encourages a three-layer separation:

```
submit_experiment.sh     <- Loop/batch submission (optional)
  -> sbatch_experiment.sh   <- SLURM #SBATCH directives + apptainer exec
       -> run/experiment.sh    <- Business logic inside the container
```

This keeps resource config separate from execution logic.

## Configuration

After running `/configure`, your CLAUDE.md will contain:

```markdown
## Cluster
- Remote path: `/scratch/project_xxx/username/project-name`
- Usage: `ssh cluster.example.com "cd /scratch/.../project-name && <command>"`
- SLURM user: `username`
- SLURM account: `project_id`
- All commands run from project root

### CSC Paths
- Scratch: `/scratch/project_xxx/username/`
- Datasets: `/scratch/project_xxx/username/DATASET/`
- SIF container directory: `/scratch/.../containers/`
- HF cache: `/scratch/.../.cache/huggingface`
- APPTAINER_TMPDIR: `/scratch/.../.cache/apptainer_tmp`
```

## License

MIT
