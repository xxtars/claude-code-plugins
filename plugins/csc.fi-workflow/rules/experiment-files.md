# Experiment File Management

Conventions for tracking ML experiment progress using structured markdown files.

## File responsibilities

| File | Purpose | Update frequency |
|------|---------|-----------------|
| `experiments/PLAN.md` | Research direction, pipeline design, experiment planning | When strategy changes |
| `experiments/LOG.md` | Progress tracking: status table + milestone results + weekly log index | After each milestone |
| `experiments/PITFALLS.md` | Lessons learned — reference when stuck, append when bitten | When discovering new pitfalls |
| `experiments/weekly/week-YYYY-MM-DD.md` | Detailed job records + verified results + notes for that week | During the week |

## LOG.md conventions
- Contains a **status table** (stage / status / brief notes) for at-a-glance progress
- Links to weekly logs for details
- Does NOT contain intermediate numbers (pass rates, partial metrics) — those go in weekly logs only, to prevent stale numbers from misleading future sessions

## Weekly log format (three-section separation)

### 1. Job History table (update immediately)
- When submitting: write job name, ID, submitted date, status=pending
- When completed: fill in started, finished, elapsed, final status
- Use `sacct` for accurate timestamps

### 2. Verified Results section (write only after verification)
- MUST read actual output files before writing any number
- Tag with data source and verification date: `"verified from <path>, <date>"`
- When not all jobs are done, do not write summary — mark completed parts as "partial"

### 3. Notes section
- Observations, decisions, analysis
- No raw numbers that may become stale

## SLURM job queries
- Use `sacct` to backfill accurate start/end times
- A cluster may run jobs from multiple projects — filter to only the current project's jobs when querying `squeue`/`sacct`
