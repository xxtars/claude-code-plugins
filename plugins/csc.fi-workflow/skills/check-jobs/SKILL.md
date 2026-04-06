---
name: check-jobs
description: Check SLURM job status on the cluster. Use when user asks about job status, queue, experiment progress, or says "check jobs", "看看排队情况".
---

# Check SLURM Jobs

Query the SLURM scheduler for current and recent job status.

## Prerequisites

Read the project's `CLAUDE.md` for:
- **ssh_host**: from the Cluster section
- **slurm_user**: from the Cluster section

If not found, suggest running `/csc.fi-workflow:configure`.

## Steps

1. **Show queue and recent jobs** in a single SSH call:
   ```bash
   ssh <ssh_host> "squeue -u <slurm_user> -o '%.10i %.30j %.10T %.10M %.6D %.20R %.10l' 2>/dev/null; echo '---'; sacct -u <slurm_user> --starttime=\$(date -d '3 days ago' +%Y-%m-%d) --format=JobID,JobName%30,State,Start,End,Elapsed -n 2>/dev/null"
   ```
   Filter out `.batch` and `.extern` sub-jobs from sacct output.

2. **Present results**: Show a clean summary with two sections — currently queued jobs and recently completed jobs.

3. **Diagnose failed jobs**: For any job with state FAILED, TIMEOUT, or OUT_OF_MEMORY, automatically fetch details:
   ```bash
   ssh <ssh_host> "scontrol show job <jobid> 2>/dev/null | grep -E 'StdErr|ExitCode|Reason'"
   ```
   Then read the last 30 lines of the stderr file to show the error:
   ```bash
   ssh <ssh_host> "tail -30 <stderr_path>"
   ```
   Summarize the failure reason for the user. If it's a new type of failure, suggest adding to `experiments/PITFALLS.md`.

4. **Focus on current project**: The cluster may run jobs from multiple projects. To filter:
   - Read the current weekly log (`experiments/weekly/week-*.md`) and `experiments/LOG.md` for known job names
   - From `squeue` and `sacct` output, highlight jobs whose name matches known project jobs
   - Jobs not matching any known name: show in a separate "Other projects" section (collapsed/dimmed)
   - If no weekly log exists, fall back to showing all jobs for the user

## Notes
- NEVER use `squeue` with the `-uall` flag (can cause memory issues on large clusters)
- Always run `date` inside the SSH command (on the cluster), not locally — macOS and Linux `date` syntax differs
- If the user asks about a specific job, use `sacct -j <jobid>` or `scontrol show job <jobid>` for details
- For job output logs, read from the SLURM output path (typically in `logs/` or `slurm-*.out`)
