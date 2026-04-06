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

1. **Show queue**: Run on the cluster:
   ```bash
   ssh <ssh_host> "squeue -u <slurm_user> -o '%.10i %.30j %.10T %.10M %.6D %.20R %.10l'"
   ```

2. **Present results**: Show a clean summary table with job ID, name, state, elapsed time, and reason (if pending).

3. **Check recently completed** (if requested or if queue is empty): Use `sacct` for recent jobs. Run the date calculation on the cluster (Linux) to avoid macOS `date` incompatibility:
   ```bash
   ssh <ssh_host> "sacct -u <slurm_user> --starttime=\$(date -d '3 days ago' +%Y-%m-%d) --format=JobID,JobName%30,State,Start,End,Elapsed -n"
   ```
   Filter out `.batch` and `.extern` sub-jobs for cleaner output.

4. **Focus on current project**: The cluster may run jobs from multiple projects. If the project has a weekly log or LOG.md with known job names/IDs, cross-reference to highlight relevant jobs.

## Notes
- NEVER use `squeue` with the `-uall` flag (can cause memory issues on large clusters)
- Always run `date` inside the SSH command (on the cluster), not locally — macOS and Linux `date` syntax differs
- If the user asks about a specific job, use `sacct -j <jobid>` or `scontrol show job <jobid>` for details
- For job output logs, read from the SLURM output path (typically in `logs/` or `slurm-*.out`)
