---
name: watch
description: Poll SLURM jobs at a fixed interval (default 1 h) and surface state/reason transitions to the local log and (optionally) Telegram. Use when the user says "watch", "盯着", "tell me when done", "监控 job", or wants to be notified about queue progress.
---

# Watch SLURM Jobs

Poll `squeue` every `<interval>` for jobs belonging to the **current project**, scoped by a job-name prefix. On any change in `JobID|Name|State|Reason|Elapsed|Timeleft`, log it locally and (if configured) push a formatted Telegram message that highlights *what changed* plus the current grouped snapshot. The loop exits when no matching jobs remain in the queue, then emits a final `sacct` summary.

One mode. State changes — queued→running, running→done, reason-flip, node-failed — all use the same loop.

## Prerequisites

From the project's `CLAUDE.md` Cluster section:
- **ssh_host**
- **slurm_user**
- **job_name_prefix** — e.g. `ep-` for EmotionProbe. The watcher only reports jobs whose `JobName` starts with this prefix.

If any of the three are missing, suggest `/csc.fi-workflow:configure` — that skill owns writing the Cluster section in CLAUDE.md, including the prefix. Don't add the prefix line inline from `watch`; it belongs with the rest of the cluster config so future re-runs of `configure` don't fight with it.

As a one-off escape hatch (cross-project monitoring, or a project with no naming convention), the user can pass `JOBIDS="<id,id,...>"` directly; the prefix is then ignored.

Optional, for Telegram pushes:
- `~/.claude/channels/telegram/.env` with `TELEGRAM_BOT_TOKEN=...`
- `~/.claude/channels/telegram/access.json` with the chat ID in `allowFrom[0]`

If Telegram isn't configured, the watcher silently no-ops the push and keeps the local log as the ground truth.

## Scope

- **Target jobs are discovered each tick** by filtering `squeue -u <slurm_user>` client-side on `JobName ~ ^<prefix>`. Jobs submitted *during* the watch are picked up automatically — no restart needed.
- **One watcher per project per CC session.** Different projects use different prefixes; launch a separate watcher for each. Multi-CC is safe because every watcher talks to Telegram via stateless `curl` (no `getUpdates` long-poll contention).
- **Explicit-IDs fallback**: if the user passes `JOBIDS="<id,id,...>"` instead of `JOB_NAME_PREFIX`, the watcher uses that fixed list and ignores the prefix. Useful for one-off cross-project monitoring.

## The watcher

Launch with `Bash run_in_background: true`. The harness emits a `<task-notification>` when the loop exits.

```bash
# --- Config (replace placeholders before launching) ---
SSH_HOST="<ssh_host>"
SLURM_USER="<slurm_user>"
JOB_NAME_PREFIX="<prefix>"            # e.g. "ep-"; leave empty if using JOBIDS
JOBIDS=""                             # comma-separated; overrides prefix when set
PROJECT_NAME="<project name>"         # used in Telegram header (e.g. "EmotionProbe")
INTERVAL="${INTERVAL:-3600}"          # 1 h default; 1800 for >1 h gpu jobs; 60 for gputest
LOG="${LOG:-$(pwd)/logs/slurm_watch.log}"
mkdir -p "$(dirname "$LOG")"

# --- Telegram (HTML monospace) ---
TG_ENV="$HOME/.claude/channels/telegram/.env"
TG_ACCESS="$HOME/.claude/channels/telegram/access.json"
[[ -f "$TG_ENV" ]] && { set -a; . "$TG_ENV"; set +a; }
TG_CHAT_ID="${TG_CHAT_ID:-$(grep -oE '"[0-9]+"' "$TG_ACCESS" 2>/dev/null | head -1 | tr -d '"')}"
html_escape() { sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'; }
notify_telegram() {
  [[ -z "${TELEGRAM_BOT_TOKEN:-}" || -z "${TG_CHAT_ID:-}" ]] && return 0
  local msg="${1:0:3900}"
  curl -fsS --max-time 10 "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${TG_CHAT_ID}" \
    --data-urlencode "parse_mode=HTML" \
    --data-urlencode "text=${msg}" >/dev/null 2>&1 || true
}

# --- Snapshot fetch (prefix or explicit IDs) ---
fetch_snapshot() {
  if [[ -n "$JOBIDS" ]]; then
    ssh "$SSH_HOST" "squeue -j $JOBIDS -h -o '%i|%j|%T|%R|%M|%L' 2>/dev/null"
  else
    ssh "$SSH_HOST" "squeue -u $SLURM_USER -h -o '%i|%j|%T|%R|%M|%L' 2>/dev/null" \
      | awk -F'|' -v p="^$JOB_NAME_PREFIX" 'NF>=2 && $2 ~ p'
  fi
}

# --- Format current state: grouped table, plain text ---
format_table() {
  local raw="$1"
  [[ -z "$raw" ]] && { echo "(no matching jobs in queue)"; return; }
  local running pending other rc pc oc out=""
  running=$(awk -F'|' '$3=="RUNNING"' <<<"$raw")
  pending=$(awk -F'|' '$3=="PENDING"' <<<"$raw")
  other=$(awk -F'|' '$3!="RUNNING" && $3!="PENDING" && NF>=3' <<<"$raw")
  rc=$(printf '%s' "$running" | grep -c .)
  pc=$(printf '%s' "$pending" | grep -c .)
  oc=$(printf '%s' "$other" | grep -c .)
  if (( rc > 0 )); then
    out+="RUNNING ($rc)"$'\n'
    out+=$(awk -F'|' '{printf "  %-8s %-22s %s / %s\n", $1, substr($2,1,22), $5, $6}' <<<"$running")
    out+=$'\n'
  fi
  if (( pc > 0 )); then
    (( rc > 0 )) && out+=$'\n'
    out+="PENDING ($pc)"$'\n'
    out+=$(awk -F'|' '{printf "  %-8s %-22s %s\n", $1, substr($2,1,22), $4}' <<<"$pending" | head -10)
    out+=$'\n'
    (( pc > 10 )) && out+="  ... $((pc-10)) more"$'\n'
  fi
  if (( oc > 0 )); then
    (( rc + pc > 0 )) && out+=$'\n'
    out+="OTHER ($oc)"$'\n'
    out+=$(awk -F'|' '{printf "  %-8s %-22s %-12s %s\n", $1, substr($2,1,22), $3, $4}' <<<"$other")
    out+=$'\n'
  fi
  printf '%s' "$out"
}

# --- Diff prev vs cur: what changed since last poll, plain text ---
format_diff() {
  local prev="$1" cur="$2"
  local tp tc out=""
  tp=$(mktemp); tc=$(mktemp)
  printf '%s\n' "$prev" | awk -F'|' 'NF>=4 {print $1"\t"$3"\t"$2"\t"$4}' > "$tp"
  printf '%s\n' "$cur"  | awk -F'|' 'NF>=4 {print $1"\t"$3"\t"$2"\t"$4}' > "$tc"

  local finished started newly reasoned
  finished=$(awk -F'\t' 'NR==FNR{ids[$1]=1; next} !($1 in ids){printf "  %s %s\n", $1, $3}' "$tc" "$tp")
  newly=$(awk -F'\t' 'NR==FNR{ids[$1]=1; next} !($1 in ids){printf "  %s %s (%s)\n", $1, $3, $2}' "$tp" "$tc")
  started=$(awk -F'\t' '
    NR==FNR { pstate[$1]=$2; next }
    ($1 in pstate) && pstate[$1] != "RUNNING" && $2 == "RUNNING" { printf "  %s %s\n", $1, $3 }
  ' "$tp" "$tc")
  reasoned=$(awk -F'\t' '
    NR==FNR { pstate[$1]=$2; preason[$1]=$4; next }
    ($1 in pstate) && pstate[$1] == $2 && preason[$1] != $4 {
      printf "  %s %s: %s -> %s\n", $1, $3, preason[$1], $4
    }
  ' "$tp" "$tc")

  [[ -n "$started"  ]] && out+="▶ Started running:"$'\n'"$started"$'\n'
  [[ -n "$finished" ]] && out+="✓ Finished:"$'\n'"$finished"$'\n'
  [[ -n "$newly"    ]] && out+="+ Newly queued:"$'\n'"$newly"$'\n'
  [[ -n "$reasoned" ]] && out+="~ Reason changed:"$'\n'"$reasoned"$'\n'
  [[ -z "$out" ]] && out="(initial snapshot)"$'\n'

  rm -f "$tp" "$tc"
  printf '%s' "$out"
}

# --- Build & send a Telegram message (diff block + current snapshot block) ---
send_update() {
  local ts="$1" diff_plain="$2" table_plain="$3"
  local diff_html table_html
  diff_html=$(printf '%s' "$diff_plain"  | html_escape)
  table_html=$(printf '%s' "$table_plain" | html_escape)
  notify_telegram "<b>[watch] ${PROJECT_NAME} @ ${ts}</b>
<pre>${diff_html}</pre>
<pre>${table_html}</pre>"
}

# --- Initial ping ---
scope_label="prefix=${JOB_NAME_PREFIX}*"
[[ -n "$JOBIDS" ]] && scope_label="ids=${JOBIDS}"
notify_telegram "<b>[watch] ${PROJECT_NAME} started</b>
${scope_label}, interval=${INTERVAL}s"

# --- Watcher loop ---
prev=""
while :; do
  ts=$(date '+%Y-%m-%d %H:%M:%S')
  cur=$(fetch_snapshot)
  if [[ "$cur" != "$prev" ]]; then
    diff_txt=$(format_diff  "$prev" "$cur")
    snap_txt=$(format_table "$cur")
    {
      echo "===== [$ts] $PROJECT_NAME ====="
      echo "$cur"
      echo "--- changes ---"
      echo "$diff_txt"
    } >> "$LOG"
    send_update "$ts" "$diff_txt" "$snap_txt"
    prev="$cur"
  fi
  [[ -z "$cur" ]] && break
  sleep "$INTERVAL"
done

# --- Final sacct summary ---
job_ids=$(printf '%s\n' "$prev" | awk -F'|' '{print $1}' | grep -E '^[0-9]+$' | paste -sd, -)
if [[ -n "$job_ids" ]]; then
  summary=$(ssh "$SSH_HOST" "sacct -j $job_ids --format=JobID,JobName%24,State,Elapsed,ExitCode -p | head -40")
  printf '%s\n' "$summary" >> "$LOG"
  esc_summary=$(printf '%s' "$summary" | html_escape)
  notify_telegram "<b>[watch] ${PROJECT_NAME} DONE</b>
<pre>${esc_summary}</pre>"
fi
```

Behavior:
- First tick fires immediately, surfaces the initial snapshot, and labels the diff block as `(initial snapshot)`.
- Subsequent ticks only message when `JobID|Name|State|Reason|Elapsed|Timeleft` actually changes — quiet between transitions, loud when something flips.
- Telegram messages use `parse_mode=HTML` with `<pre>` blocks so monospace alignment holds on mobile. HTML-special characters in job names/reasons are escaped.
- SSH failure: the command substitution returns empty for that tick, the loop sleeps, next iteration retries. Don't add `set -e`.
- Telegram failure: swallowed (`|| true`); the local log at `$LOG` is always authoritative.

## ⚠️ Critical: keep the loop local

The `while`/`sleep` MUST run on the local machine. Each iteration opens a fresh short SSH for the `squeue` query and closes it.

```bash
# ❌ DO NOT USE — entire loop on the login node
ssh <ssh_host> "while :; do squeue ...; sleep 3600; done"
```

Failure modes of the wrong form:
- SSH idle disconnect → orphan process on the login node; local Bash sees the drop and reports a false failure to Claude.
- Laptop sleep / network drop → SSH dies, and Claude can't distinguish that from job failure.
- CSC login-node etiquette — admin may reap idle long-running shells.

The correct form (above) is robust to transient drops: a failed ssh returns non-zero, the next `sleep` runs, loop continues.

## Interval guidance

| job kind | interval |
|----------|----------|
| typical multi-hour (queued or hours-long running) | 1 h (3600 s) |
| long gpu* job > 1 h, want quicker transition signal | 30 min (1800 s) |
| `gputest` or `<15 min` job | 60 s |

Default to 1 h. Drop to 1800 s when you want faster signal on a queue that's about to clear (gpu* with reservations lifting). Drop to 60 s only for `gputest` partition short bursts — at 1 h cadence those run and exit between two polls.

Don't go below 60 s — the SSH connection setup cost dominates and the login node gets noisy.

## Steps

1. **Read project config from `CLAUDE.md`**: `ssh_host`, `slurm_user`, `job_name_prefix`, project name (derive from `Remote path` basename if not stated).
2. **Pick interval** per table above.
3. **Launch** the snippet as `Bash` with `run_in_background: true`. Replace placeholders (`SSH_HOST`, `SLURM_USER`, `JOB_NAME_PREFIX`, `PROJECT_NAME`, `INTERVAL`) with the project values. Note the returned task ID — the user can `Read` the task output file or `tail -f` the log for intermediate state.
4. **On `<task-notification>` (loop exit)**:
   - Read the final `sacct` summary from the output.
   - If any job ended in `{FAILED, TIMEOUT, OUT_OF_MEMORY, NODE_FAIL}`, diagnose: `scontrol show job <jobid>` + stderr tail (same flow as `/csc.fi-workflow:check-jobs`).
   - If the user wants logging, chain to `/csc.fi-workflow:update-log`.

## Pitfalls

- ❌ Putting `while`/`sleep` inside the ssh quote — see "Critical: keep the loop local".
- ❌ Polling at 15 s for a 6 h job — wastes ~1400 SSH connections per job.
- ❌ Polling at 1 h for a 5 min `gputest` job — loop sleeps through the entire job lifecycle.
- ❌ Routing Telegram through the MCP plugin's `reply` tool — that path uses `getUpdates` long-polling which breaks under multi-CC. Always use direct `curl` to `api.telegram.org/bot<token>/sendMessage` from the bash watcher — it's stateless HTTP and contention-free.
- ❌ Forgetting `parse_mode=HTML` + `<pre>` — without monospace, the column-aligned table wraps unreadably on mobile.
- ❌ Forgetting to HTML-escape job names or reasons before wrapping in `<pre>` — a `&` or `<` will silently truncate the message.
- ❌ Filtering by name prefix on the cluster side with `squeue --name=NAME` — that's exact-match only, no glob. Always fetch all-user output then filter client-side with `awk`.
- ❌ Mixing prefix and explicit IDs in the same watcher — pick one. If `JOBIDS` is non-empty, the prefix is ignored.
- ❌ Relying on `JOBIDS=` to track a moving target — submit a new job mid-watch and the explicit-IDs form will miss it. Use the prefix mode unless the project has no naming convention.

## Notes

- Terminal SLURM states (for the diagnose step): `COMPLETED`, `FAILED`, `CANCELLED`, `TIMEOUT`, `OUT_OF_MEMORY`, `NODE_FAIL`, `PREEMPTED`, `BOOT_FAIL`.
- Job stdout/stderr live at `<remote_path>/logs/<jobname>-<jobid>.out` by default; confirm via `scontrol show job <jobid>` if unsure.
- For jobs blocked by reservations (`Service_break` etc.), the watcher will sit at its interval and surface the unblock as a reason→state change — no special handling needed. If the user asks "why is it blocked", read `scontrol show reservation` or `scontrol show job <jobid>` separately.
- For long-running multi-day chains where laptop sleep / CC restart matters, the orthogonal answer is SLURM `--dependency=afterok:<jobid>` at *submit time* — that's part of `/csc.fi-workflow:submit`, not `watch`. The watcher will then see the chain progress naturally as state changes.
