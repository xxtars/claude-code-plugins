---
name: update-log
description: Update experiment logs with job results from the cluster. Use when user says "update log", "record results", "更新log", or after checking job status reveals completed jobs.
---

# Update Experiment Log

Record job results into `experiments/LOG.md` and the current weekly log.

## Prerequisites

Read the project's `CLAUDE.md` for:
- **ssh_host**: from the Cluster section
- **slurm_user**: from the Cluster section

If not found, suggest running `/csc.fi-workflow:configure`.

## File structure

The experiment log uses a three-file system (see `rules/experiment-files.md` for details):
- `experiments/LOG.md` — High-level status table + milestone results
- `experiments/weekly/week-YYYY-MM-DD.md` — Detailed job records per week
- `experiments/PITFALLS.md` — Lessons learned

## Steps

1. **Identify current weekly log**: Find or create `experiments/weekly/week-YYYY-MM-DD.md` for the current week (Monday date).

2. **Check what's new**: Compare known jobs in the weekly log against actual cluster state:
   ```bash
   ssh <ssh_host> "sacct -u <slurm_user> --starttime=<week_start> --format=JobID,JobName%30,State,Start,End,Elapsed -n"
   ```

3. **Update Job History table** in the weekly log:
   - New jobs: add row with name/ID/submitted/status
   - Completed jobs: fill in started/finished/status/elapsed
   - Use `sacct` timestamps for accuracy

4. **Update Verified Results** (only when explicitly asked or when verifying output):
   - MUST read actual output files on the cluster before writing any numbers
   - Tag with source and date: `"verified from <path>, <date>"`
   - If not all jobs are done, mark partial results as "partial"
   - NEVER guess or copy numbers from memory

5. **Update LOG.md** status table:
   - Change stage status (pending → running → done)
   - Add brief summary in the notes column
   - Do NOT put intermediate numbers in LOG.md — those go in weekly logs only

6. **Update Notes section** in the weekly log:
   - Observations, decisions, analysis
   - No raw numbers that might become stale

## Notes
- The weekly log week boundary is Monday. If today is Wednesday Apr 9, the file is `week-2026-04-07.md`
- Always verify numbers from actual cluster output before writing to Verified Results
- If a job failed, check the error log and add to PITFALLS.md if it's a new lesson
