---
name: watch
description: Poll SLURM jobs at a fixed interval (default 1 h) and surface state/reason transitions to the local log and (optionally) Telegram. Use when the user says "watch", "盯着", "tell me when done", "监控 job", or wants to be notified about queue progress.
---

# Watch SLURM Jobs

Poll `squeue` every `<interval>` (default **1 h**) for a fixed list of job IDs. On any change in `JobID|State|Reason|Elapsed|Timeleft`, log it locally and (if configured) push it to Telegram. The loop exits when all target jobs have left the queue, at which point a final `sacct` summary is emitted.

There is one mode. No decision tree. State changes are state changes — queued→running, running→done, blocker-lifted, node-failed all use the same loop.

## Prerequisites

From the project's `CLAUDE.md`:
- **ssh_host** (Cluster section)
- **slurm_user** (Cluster section)
- **remote_path** (Cluster section)

If missing, suggest `/csc.fi-workflow:configure`.

Optional, for Telegram pushes:
- `~/.claude/channels/telegram/.env` with `TELEGRAM_BOT_TOKEN=...`
- `~/.claude/channels/telegram/access.json` with the chat ID in `allowFrom[0]`

(Both produced by the `claude-plugins-official/telegram` configure flow. If the user hasn't set up Telegram, the watcher silently no-ops the push.)

## Scope

- **Target jobs are the explicit IDs passed at startup.** The watcher does not auto-discover. If the user submits new jobs mid-watch, restart the watcher with the extended list or launch a second watcher.
- **One watcher per CC session.** Different CC instances don't share state — each starts its own background loop with its own job list. This is intentional: it keeps multi-CC clean.

## The watcher

Launch with `Bash run_in_background: true`. The harness emits a `<task-notification>` when the loop exits.

```bash
# --- Telegram helper (no-op if not configured) ---
TG_ENV="$HOME/.claude/channels/telegram/.env"
TG_ACCESS="$HOME/.claude/channels/telegram/access.json"
[[ -f "$TG_ENV" ]] && { set -a; source "$TG_ENV"; set +a; }
TG_CHAT_ID="${TG_CHAT_ID:-$(grep -oE '\"[0-9]+\"' "$TG_ACCESS" 2>/dev/null | head -1 | tr -d '\"')}"
notify_telegram() {
  [[ -z "${TELEGRAM_BOT_TOKEN:-}" || -z "${TG_CHAT_ID:-}" ]] && return 0
  local msg="${1:0:3900}"
  curl -fsS --max-time 10 "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${TG_CHAT_ID}" \
    --data-urlencode "text=${msg}" >/dev/null 2>&1 || true
}

# --- Watcher loop ---
JOBIDS="<comma,separated,ids>"
INTERVAL=${INTERVAL:-3600}   # 1 h default
LOG=${LOG:-/tmp/slurm_watch.log}

notify_telegram "[watch] started — jobs=${JOBIDS} interval=${INTERVAL}s"

( prev=""
  while :; do
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    cur=$(ssh <ssh_host> "squeue -j ${JOBIDS} -h -o '%i|%T|%R|%M|%L' 2>/dev/null")
    if [[ "$cur" != "$prev" ]]; then
      header="===== [$ts] state change ====="
      body=$([[ -z "$cur" ]] && echo "(all jobs left the queue)" || printf '%s\n' "$cur" | column -t -s '|')
      printf '%s\n%s\n' "$header" "$body" | tee -a "$LOG"
      notify_telegram "[watch] $ts
$body"
      prev="$cur"
    fi
    [[ -z "$cur" ]] && break
    sleep "$INTERVAL"
  done
  summary=$(ssh <ssh_host> "sacct -j ${JOBIDS} --format=JobID,JobName%24,State,Elapsed,ExitCode -p | head -20")
  printf '%s\n' "$summary" | tee -a "$LOG"
  notify_telegram "[watch] DONE
$summary"
)
```

Behavior:
- First tick fires immediately, so the initial state is also surfaced (compared against empty `prev`).
- `squeue` shows the `Reason` column, which changes well before `State` does (e.g., `ReqNodeNotAvail` → `Priority` → empty → state flips to `RUNNING`). All such transitions get reported.
- An ssh failure returns non-zero from the command substitution but doesn't kill the loop — `cur` is just empty for that tick and the next iteration retries. Don't add `set -e`.
- Telegram failures are swallowed (`|| true`); the local log is always ground truth.

## ⚠️ Critical: keep the loop local

The `until`/`while`/`sleep` MUST run on the local machine. Each iteration opens a fresh short SSH for the `squeue` query and closes it.

```bash
# ❌ DO NOT USE — entire loop on the login node
ssh <ssh_host> "while :; do squeue ...; sleep 3600; done"
```

Failure modes of the wrong form:
- SSH idle disconnect → orphan process on the login node; local Bash sees the drop and reports a *false* failure to Claude.
- Laptop sleep / network drop → SSH dies, but Claude can't distinguish that from a job failure.
- CSC login-node etiquette — admin may reap idle long-running shells.

The correct form (above) is robust to transient drops: failed ssh returns non-zero, the next `sleep` runs, loop continues.

## Interval guidance

| job kind | interval |
|----------|----------|
| typical (queued or hours-long running) | 1 h (3600 s) |
| `gputest` or `<15 min` job | 60 s |

Default to 1 h unless the job is a short-burst (e.g., `gputest` partition with `--time=15:00`) — at 1 h cadence a short job runs and finishes between two polls and you see only "left queue" with no transition history. For research workloads (most jobs are 30 min – 24 h), 1 h is the right default: it catches `queued → running → done` cleanly and won't spam the login node.

Don't go below 60 s — the SSH connection setup cost dominates and the login node gets noisy.

## Steps

1. **Collect job IDs** — from user input, recent `sbatch` output, or `squeue -u <slurm_user>`.
2. **Pick interval** — default 1 h; drop to 60 s only for short-burst jobs.
3. **Launch** the snippet above as `Bash` with `run_in_background: true`. Save the returned task ID so the user can inspect intermediate state via `Read` on the task output file.
4. **On `<task-notification>` (loop exit)**:
   - Read the final `sacct` summary from the output.
   - If any job ended in `{FAILED, TIMEOUT, OUT_OF_MEMORY, NODE_FAIL}`, diagnose: `scontrol show job <jobid>` + stderr tail (same flow as `/csc.fi-workflow:check-jobs`).
   - If the user wants logging, chain to `/csc.fi-workflow:update-log`.

## Pitfalls

- ❌ Putting `while`/`sleep` inside the ssh quote — see "Critical: keep the loop local".
- ❌ Polling at 15 s for a 6 h job — wastes ~1400 SSH connections per job.
- ❌ Polling at 1 h for a 5 min `gputest` job — loop sleeps through the entire job lifecycle.
- ❌ Routing Telegram through the MCP plugin's `reply` tool — that path uses `getUpdates` long-polling which breaks under multi-CC ([feedback-telegram-multi-cc](../../../telegram/...)). Always use direct `curl` to `api.telegram.org/bot<token>/sendMessage` from the bash watcher — it's stateless HTTP and contention-free.
- ❌ Anchoring without `^` when grepping SLURM states — `COMPLETED` matches `COMPLETEDFOOBAR`. Always anchor.
- ❌ Auto-discovering jobs by name pattern inside the watcher — naming is a project convention, not a skill concern. Pass IDs explicitly.

## Notes

- Terminal SLURM states (for the diagnose step): `COMPLETED`, `FAILED`, `CANCELLED`, `TIMEOUT`, `OUT_OF_MEMORY`, `NODE_FAIL`, `PREEMPTED`, `BOOT_FAIL`.
- Job stdout/stderr live at `<remote_path>/logs/<jobname>-<jobid>.out` by default; confirm via `scontrol show job <jobid>` if unsure.
- For jobs blocked by reservations (`Service_break` etc.), the watcher will sit at 1 h cadence and surface the unblock as a state change — no special handling needed. If the user asks "why is it blocked", read `scontrol show reservation` or `scontrol show job <jobid>` separately.
- For long-running multi-day chains where laptop sleep / CC restart matters, the orthogonal answer is SLURM `--dependency=afterok:<jobid>` at *submit time* — that's part of `/csc.fi-workflow:submit`, not `watch`. The watcher will then see the chain progress naturally as state changes.
