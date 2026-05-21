# csc.fi-workflow

A [Claude Code](https://claude.ai/code) plugin for ML researchers working on [CSC](https://www.csc.fi/) (Finland's IT Center for Science) SLURM clusters (Mahti, Puhti).

Provides a structured workflow for syncing code, monitoring jobs, and recording experiment results on CSC clusters — so you can focus on research instead of cluster logistics.

## Companion plugins

File conventions for `experiments/PLAN.md`, `LOG.md`, `weekly/`, and `PITFALLS.md` are defined in **`research-workflow`** (same marketplace). This plugin writes into those files but doesn't own them.

- To scaffold a new project: `/research-workflow:init` first, then `/csc.fi-workflow:configure`
- To reconcile results with research plan: `/research-workflow:iterate`

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Configure | `/csc.fi-workflow:configure` | Set up cluster connection (SSH, account, paths) |
| Sync | `/csc.fi-workflow:sync` | Push code to cluster: `commit → push → ssh pull` |
| Check Jobs | `/csc.fi-workflow:check-jobs` | Query SLURM queue and recent job status (one-shot) |
| Watch | `/csc.fi-workflow:watch` | Monitor a SLURM job until completion (background polling, dependency chain, or periodic cron) |
| Submit | `/csc.fi-workflow:submit` | Submit SLURM job and auto-record in experiment log |
| Update Log | `/csc.fi-workflow:update-log` | Record job results into structured experiment logs |

## Rules (always-on)

Rules are automatically loaded into every conversation. They guide Claude's behavior when writing SLURM-related scripts.

- **SLURM Shell Conventions** (`slurm-shell.md`) — Never `set -e` in SLURM scripts; use Apptainer containers (not conda); three-layer script structure (`submit_*.sh` → `sbatch_*.sh` → `run/*.sh`); build SIF on compute nodes with `/dev/shm` as TMPDIR

For experiment file conventions (LOG, weekly, PITFALLS, PLAN), see `research-workflow/rules/research-files.md`.

## Install

```bash
claude plugin install xxtars/claude-code-plugins/csc.fi-workflow
```

## Quick Start

```bash
# 1. Scaffold research files (from research-workflow plugin)
/research-workflow:init

# 2. Configure your cluster connection
/csc.fi-workflow:configure

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
5. Writes everything to CLAUDE.md and suggests `/research-workflow:init` if experiment files don't exist yet

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

### `/csc.fi-workflow:watch`

Continuous variant of `check-jobs`: monitor one or more SLURM jobs until they reach a terminal state, then optionally chain to `update-log`.

**Four modes** with explicit selection rules:
- **A — Foreground wait** (<15 min): block the current Bash turn with a local `until` loop, short-poll `sacct` until done.
- **B — Background polling** (15 min – 3 h): same loop but `run_in_background: true`; Claude resumes via `<task-notification>` on exit.
- **C — SLURM dependency** (>3 h with known follow-up): `sbatch --dependency=afterok:<jobid> <follow_up>`. Cluster-side, survives laptop sleep / CC restart.
- **D — `CronCreate` periodic**: re-invoke Claude at fixed intervals across many jobs.

**Key correctness rule**: the polling loop must run *locally*, with each iteration opening a fresh short SSH for `sacct`. The wrong form (`ssh host "until ...; do sleep N; done"`) puts the loop on the login node, where SSH drops become false-positive failures and the loop becomes an orphan process. The skill documents this pitfall.

The skill picks the poll interval from a small table that scales with `--time` (15 s for <15 min, up to 30 min for >12 h).

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

## Experiment File Conventions

File responsibilities (PLAN / LOG / weekly / PITFALLS) and the weekly log three-section format (Job History / Verified Results / Notes) are defined by `research-workflow`. See [`research-workflow/rules/research-files.md`](../research-workflow/rules/research-files.md).

The `Commit` column in the weekly Job History table records the git commit hash that was running, so any result is reproducible later.

## SLURM Script Structure

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
