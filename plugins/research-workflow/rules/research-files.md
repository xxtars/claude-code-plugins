# Research File Conventions

A research project has four layers that feed each other in a loop. These files make the loop explicit.

```
experiments/
├── PLAN.md            ← Story, Design, Execution pointer, Iteration log
├── LOG.md             ← Execution state: stage status + weekly index
├── weekly/
│   └── week-YYYY-MM-DD.md   ← Execution detail: jobs, results, notes
└── PITFALLS.md        ← Operational lessons sedimented from execution
```

## The four layers (PLAN.md)

| # | Layer | What it holds | Aligned with |
|---|-------|---------------|--------------|
| L1 | **Story** | Core claim, why it matters, current stance on what's settled vs debatable | Paper abstract + introduction |
| L2 | **Design** | Pipeline, experiment matrix, metrics, baselines, ablations | Paper experiments + appendix tables |
| L3 | **Execution Status** | Pointer to LOG.md and latest weekly — **no duplicated numbers** | LOG.md |
| L4 | **Iteration Log** | Every time results force a Story/Design change, append one entry with Trigger / Change / Evidence | — |

**Key rule**: PLAN.md is the hub, but it holds claims not data. Numbers live in weekly logs (source of truth) and are mirrored into the paper once verified.

## Layer responsibilities

### L1 Story
One paragraph for each of:
- **Core claim** — what you're asserting
- **Why it matters** — the gap this closes
- **Current stance** — what's settled, what's open

Changes to Story should trigger an L4 entry and (usually) a paper abstract/intro update.

### L2 Design
- **Pipeline** — data → training → evaluation
- **Experiment matrix** — which combinations matter, which ablations
- **Metrics & baselines** — what you report, what you compare against

Changes to Design should trigger an L4 entry and (usually) a paper experiments.tex / appendix update.

### L3 Execution Status (pointer only)
A short block like:

```markdown
## 3. Execution Status
See [LOG.md](LOG.md) for stage progress. Latest weekly: [weekly/week-YYYY-MM-DD.md](weekly/week-YYYY-MM-DD.md).
```

Do **not** copy numbers from weekly logs into PLAN.md — they rot.

### L4 Iteration Log
Append-only, reverse-chronological or chronological (pick one, be consistent). Each entry:

```markdown
### YYYY-MM-DD — Short title
- **Trigger**: <what result caused the update>
- **Change**: <what moved in Story (L1) or Design (L2)>
- **Evidence**: <pointer to weekly log section, verified numbers, or PITFALLS entry>
```

This is the audit trail of why the research shape changed. Without L4, "why did we stop pursuing X?" becomes unanswerable a month later.

## LOG.md conventions

- **Stage table**: stage / status / brief notes. Status ∈ {pending, running, done, blocked}
- **Weekly index**: one row per weekly log with a one-line summary
- **No intermediate numbers** in LOG.md. Only milestone results. Numbers here go stale and mislead future sessions.

## Weekly log format (three sections)

### 1. Job History (update immediately)
Table of every run: name, id, submission info, status, commit hash.

### 2. Verified Results (write only after reading actual output)
- MUST read the actual output file/logs before writing any number
- Tag with source and date: `"verified from <path>, <date>"`
- For in-flight jobs: mark "partial"

### 3. Notes
Observations, decisions, analysis. **No raw numbers** (those go in section 2).

## PITFALLS.md

One entry per pitfall, using this structure:

```markdown
## Descriptive title
- **Symptom**: what you observed
- **Root cause**: why it happened
- **Fix**: how you resolved it
- **Date**: YYYY-MM-DD
```

When a pitfall also invalidates an assumption baked into Story or Design, add an L4 Iteration Log entry in PLAN.md pointing to the pitfall.
