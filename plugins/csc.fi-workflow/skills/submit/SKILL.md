---
name: submit
description: Submit a SLURM job and auto-record it in the experiment log. Use when user says "submit job", "sbatch", "提交实验", or when you are about to run sbatch on the cluster. Do NOT use for non-SLURM commands.
---

# Submit Job & Auto-Record

Submit a SLURM job on the cluster and automatically record it in the weekly log and LOG.md.

## Prerequisites

Read the project's `CLAUDE.md` for:
- **ssh_host**: from the Cluster section
- **remote_path**: from the Cluster section

If not found, suggest running `/csc.fi-workflow:configure`.

## Steps

### 1. Submit the job

Run the sbatch command on the cluster:
```bash
ssh <ssh_host> "cd <remote_path> && sbatch [options] <script> [args]"
```

Capture the job ID from the output (format: `Submitted batch job <JOBID>`).

### 2. Get the current code commit

```bash
git rev-parse --short HEAD
```

### 3. Auto-record in weekly log

Find or create the current weekly log (`experiments/weekly/week-YYYY-MM-DD.md`, Monday date).
If the file doesn't exist, create it from `research-workflow/templates/weekly/week-TEMPLATE.md` (requires `research-workflow` plugin).

Add a row to the **Job History** table:

| Job Name | Job ID | Pipeline | Dataset | Partition | Submitted | Started | Finished | Status | Commit |
|----------|--------|----------|---------|-----------|-----------|---------|----------|--------|--------|
| `<job-name>` | `<job-id>` | `<pipeline>` | `<dataset>` | `<partition>` | `<today>` | | | PENDING | `<commit>` |

- **Job Name**: from `--job-name` flag or sbatch script `#SBATCH --job-name`
- **Pipeline**: infer from context (e.g., training stage, evaluation, baseline)
- **Dataset**: infer from context or args if available
- **Partition**: from sbatch script or `--partition` flag
- **Submitted**: today's date (YYYY-MM-DD)
- **Commit**: short git hash from step 2

### 4. Update LOG.md status table

If the submitted job corresponds to a stage in `experiments/LOG.md`:
- Update the status to `⏳ pending` (or `⏳ running` if it starts immediately)
- Add the job ID in the notes column

### 5. Report

Show a summary:
```
Submitted: <job-name> (ID: <jobid>)
Partition: <partition>, Time limit: <time-limit>
Recorded in: experiments/weekly/week-YYYY-MM-DD.md
```

## Notes
- If submitting multiple jobs (e.g., a loop), record ALL of them in one batch
- If the sbatch command fails, do NOT record anything — help debug the error first
- The weekly log and LOG.md updates happen locally — remember to commit if needed
- This skill wraps sbatch; all the usual SLURM rules apply (containers, script structure, etc.)
