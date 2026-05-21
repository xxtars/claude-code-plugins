---
name: watch
description: Monitor a SLURM job until it reaches a terminal state, then optionally chain to `/csc.fi-workflow:update-log`. Use when the user says "watch this job", "盯着", "tell me when done", or asks for automatic action on job completion. Pairs with `/csc.fi-workflow:check-jobs` (one-shot query) — `watch` is the continuous variant.
---

# Watch SLURM Job(s)

Monitor SLURM jobs until they reach a terminal state, then optionally record results.

## Prerequisites

Read the project's `CLAUDE.md` for:
- **ssh_host**: from the Cluster section
- **slurm_user**: from the Cluster section
- **remote_path**: from the Cluster section

If not found, suggest running `/csc.fi-workflow:configure`.

## Watch modes

Pick one based on the decision tree below. Different modes have different reliability and latency tradeoffs.

### Mode A — Foreground wait

Blocks the current turn until the job finishes. Best for **<15 min** (gputest jobs).

```bash
until ssh <ssh_host> "sacct -j <jobid> -P -n --format=State 2>/dev/null | \
    head -1 | grep -qE '^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL)'"; do
    sleep 30
done
```

Issue this as a regular foreground `Bash` call.

### Mode B — Background polling (most common)

Run as `Bash run_in_background: true`. Claude resumes via a `<task-notification>` when the loop exits. Best for **15 min – 3 h**.

```bash
( until ssh <ssh_host> "sacct -j <jobid> -P -n --format=State 2>/dev/null | \
    head -1 | grep -qE '^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL)'"; do
    sleep <interval>
  done && \
  ssh <ssh_host> "sacct -j <jobid> --format=JobID,State,Elapsed,ExitCode -p | head -3 && \
                   echo --- log tail --- && \
                   tail -30 <remote_path>/logs/<jobname>-<jobid>.out 2>/dev/null" )
```

### ⚠️ CRITICAL: keep the loop local

The `until` / `sleep` MUST run on the local machine, **NOT inside the ssh quote**. Each iteration should open a fresh short SSH for the `sacct` query, then close it.

The wrong form looks like:

```bash
# ❌ DO NOT USE
ssh <ssh_host> "until sacct ...; do sleep 1800; done"
```

That puts the entire loop on the login node. Failure modes:
- SSH idle disconnect → the loop becomes an orphan process on the login node; local Bash sees connection drop and reports a *false* failure to Claude.
- Laptop sleep / network drop → SSH dies, local Bash exits, but Claude has no way to tell the difference between job failure and SSH failure.
- CSC login nodes are not for long-running scripts (etiquette + admin can reap idle sessions).

The correct form (above) is robust to transient network drops: a failed `ssh` returns non-zero, the `until` loop does not exit, the next `sleep` runs, and the loop retries on the next iteration. Laptop sleep pauses the local sleep and resumes cleanly. Login nodes only see brief connections.

### Mode C — SLURM dependency chain

Cluster-side automation. Best for **>3 h** jobs with a known follow-up step.

```bash
ssh <ssh_host> "cd <remote_path> && \
    sbatch --dependency=afterok:<jobid> slurm/<follow_up.sh>"
```

- SLURM auto-launches `<follow_up.sh>` only after `<jobid>` exits 0.
- Completely decoupled from local CC session — survives laptop shutdown, CC restart, anything.
- Claude finds out about completion by running `/csc.fi-workflow:check-jobs` next time it's active.
- The follow-up sbatch must exist before issuing the dependency.

### Mode D — CronCreate periodic

Re-invoke Claude at fixed intervals via the `CronCreate` tool. Best for **passive queue health checks** across many jobs.

```
CronCreate cron="7 */2 * * *"  prompt="run /csc.fi-workflow:check-jobs and flag any failures"
```

- Runs only while CC session is alive (default). Pass `durable=true` to persist across restarts.
- Each fire costs context cache (full prompt re-read), so don't use this for single-job watching.
- Auto-expires after 7 days for the recurring variant. Tell the user this.

### Mode E — State-change watch (verbose)

Like Mode B (background poll, loop stays local), but **prints every state transition** as it happens, not just the terminal result. Best for **PENDING-blocked jobs** (`ReqNodeNotAvail` / reservations / `Service_break` / `Dependency`) where the interesting event is the unblock → run → complete chain over hours-to-days, and the user wants to *see* it move.

```bash
( prev=""
  while :; do
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    cur=$(ssh <ssh_host> "squeue -j <jobids> -h -o '%i|%T|%R|%M|%L' 2>/dev/null")
    if [[ "$cur" != "$prev" ]]; then
      echo "===== [$ts] state change ====="
      [[ -z "$cur" ]] && echo "(all jobs left the queue)" || printf '%s\n' "$cur" | column -t -s '|'
      prev="$cur"
    fi
    [[ -z "$cur" ]] && break
    sleep <interval>
  done
  ssh <ssh_host> "sacct -j <jobids> --format=JobID,JobName%24,State,Elapsed,ExitCode -p | head -20" )
```

Notes:
- Uses `squeue` (not `sacct`) so the `Reason` column is visible — that's what changes when a blocker lifts (e.g., `ReqNodeNotAvail` → `Priority` → `(none)` → state flips to `RUNNING`).
- Exit condition is "all jobs gone from the queue" — same end as Mode B AND-watch; the only behavioral difference is intermediate logging.
- Default interval is **1 h** for blocked-PENDING (queue state changes slowly; faster polling spams the login node for no signal). Drop to a Mode B / table cadence once jobs are RUNNING if you want sharper terminal latency.
- For laptop-sleep durability over multi-day blocks, the same Mode C advice applies — switch to `--dependency=` if there's a follow-up sbatch.

## Decision tree

```
Q1: Is any target job currently PENDING with a queue-side blocker
    (ReqNodeNotAvail, reservation, Service_break, Dependency)?
    yes      → Mode E (state-change watch, 1 h interval)
    no       → continue to Q2

Q2: How long is the job's TIME_LIMIT?
    <15 min  → Mode A (foreground wait)
    15m–3h   → Mode B (background polling)
    >3 h     → continue to Q3

Q3: Is there a follow-up sbatch script that should run on success?
    yes      → Mode C (SLURM dependency)
    no       → Mode B with 30-min interval, plus suggest writing a follow-up sbatch and switching to Mode C

Q4: Are we monitoring queue health across many jobs over time?
    yes      → Mode D (CronCreate)
```

## Poll interval picker (matches the project's `feedback_slurm_poll_cadence` memory)

| TIME_LIMIT  | sleep interval |
|-------------|----------------|
| <15 min     | 15 s           |
| 15 min – 1 h | 60 s          |
| 1 h – 6 h   | 5 min (300 s)  |
| 6 h – 12 h  | 15 min (900 s) |
| >12 h       | 30 min (1800 s) |
| PENDING-blocked (Mode E) | 1 h (3600 s) |

Match cadence to job length: too-frequent polling spams the login node with SSH connections; too-sparse loses minutes of latency at completion. For Mode E (state-change watch) the cadence tracks how often the *queue* changes, not how long the job runs — 1 h is the default unless the user knows the blocker lifts on a known schedule.

## Steps

1. **Identify target job(s)**. From user input ("watch 6666265"), recent `sbatch` output, or by running `squeue` and asking which one.

2. **Get the TIME_LIMIT**:
   ```bash
   ssh <ssh_host> "squeue -j <jobid> --format='%l' -h"
   ```
   If the job has already left the queue (rare for new submissions but possible), read the sbatch script's `#SBATCH --time=` line.

3. **Pick the mode** via the decision tree.

4. **Pick the poll interval** from the table (only for Mode A/B).

5. **Issue the watch command**:
   - Mode A: foreground `Bash` call.
   - Mode B: `Bash` with `run_in_background: true`. Save the returned background task ID; the user may want to inspect output mid-run.
   - Mode C: `sbatch --dependency=...`; the next-step job is now queued.
   - Mode D: `CronCreate` with the appropriate cron expression.

6. **On completion** (Mode A/B):
   - Show final state + last 30 lines of stdout/stderr.
   - If state ∈ {FAILED, TIMEOUT, OUT_OF_MEMORY, NODE_FAIL}: diagnose using `scontrol show job` + stderr tail (same flow as `/csc.fi-workflow:check-jobs`).
   - If the user asked for automatic logging, chain to `/csc.fi-workflow:update-log`.

7. **For Mode C**: report the dependency chain and suggest a `check-jobs` invocation later to see the chain progress.

## Multi-job watch

For watching N jobs at once, two approaches:

- **OR-watch** (any-finishes): wrap the `sacct -j j1,j2,j3 -P -n --format=JobID,State | head -N | grep -qE '...'` so the loop exits as soon as any of them hits a terminal state.
- **AND-watch** (all-finish): use `! grep -qE 'PENDING|RUNNING'` so the loop exits only when none are still active.

State the choice to the user before launching.

## Common pitfalls

- ❌ `ssh host "until sacct ...; do sleep ...; done"` — see "CRITICAL: keep the loop local" above.
- ❌ Polling every 15 s for a 6 h job — wastes ~1440 SSH connections.
- ❌ Polling every 30 min for a 10 min job — completion latency dominates the job time.
- ❌ Using Mode B for jobs >3 h when the laptop is expected to sleep — switch to Mode C.
- ❌ Anchoring grep without `^` — `COMPLETED` may match the substring of `COMPLETED ` in other tools' output; always use `'^(COMPLETED|FAILED|...)'`.

## Notes

- Terminal SLURM states (always include in the grep): `COMPLETED`, `FAILED`, `CANCELLED`, `TIMEOUT`, `OUT_OF_MEMORY`, `NODE_FAIL`, `PREEMPTED`, `BOOT_FAIL`.
- `sacct` may need `--allusers` on some clusters; check what CSC's default behavior is for the project's account.
- Job logs follow the SBATCH `--output` / `--error` paths; default location is `<remote_path>/logs/<jobname>-<jobid>.out`. Verify by reading `scontrol show job <jobid>` if unsure.
- For jobs in `PENDING` state with a queue-side blocker (`ReqNodeNotAvail`, reservation, `Service_break`, `Dependency`), use **Mode E** at 1 h cadence — don't skip them. The whole point of watching is to catch the unblock → run → complete transitions, and `squeue`'s `Reason` column changes well before the state does. Also tell the user what the blocker is (read `scontrol show reservation` or check the maintenance schedule) so they can decide whether to keep waiting or resubmit elsewhere.
