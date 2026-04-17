---
name: iterate
description: Close the research feedback loop by reading the latest weekly results, LOG, and PITFALLS, then proposing user-approved edits to PLAN.md's Story (L1) or Design (L2) plus an audit entry in the Iteration Log (L4). Make sure to use this skill whenever the user wants to reconcile the research plan with recent results, update PLAN based on new findings, close the feedback loop between execution and story/design, or says "iterate", "/iterate", "update plan", "feedback loop", "reconcile results", "reconcile plan", "基于结果更新 plan", "结果对 plan 的影响", especially after a batch of experiments finishes and the user is thinking about what it means for direction.
---

# Iterate PLAN based on recent results

Research is a loop: execution results feed back into Story (L1) and Design (L2). This skill surfaces that feedback explicitly and records it in PLAN.md's Iteration Log (L4), so direction changes have an audit trail instead of silently happening in the user's head.

See `rules/iteration-workflow.md` for when iterations should happen and what counts as evidence.

## Prerequisites

- Project has `experiments/PLAN.md` with the four-layer structure (run `/research-workflow:init` if not)
- Project has at least one weekly log with Verified Results

## Steps

### 1. Read current state

- `experiments/PLAN.md` — current Story (L1), Design (L2), and existing L4 entries
- `experiments/LOG.md` — stage status
- Most recent 1–2 weekly logs under `experiments/weekly/` — focus on **Verified Results** and **Notes** sections
- `experiments/PITFALLS.md` — recent entries

### 2. Identify triggers

Walk through the evidence and look for any of the following (see `rules/iteration-workflow.md` for the full list):

- A verified result **contradicts** a claim in Story
- A baseline or ablation **outperforms** the proposed method
- A planned experiment was **abandoned** without explanation in L4
- A **new experiment** was added that isn't in L2 Design
- The **metric** effectively changed
- A PITFALLS entry invalidates an assumption baked into Story or Design

If a trigger already has a matching L4 entry, don't propose a duplicate.

### 3. Propose candidate entries

Present a numbered table with columns: `#`, `Type`, `Target`, `Proposal`.

- **Type**: `L1 edit` / `L2 edit` / `L4 entry`
- **Target**: specific PLAN.md section (or other file, if the proposal crosses into LOG/PITFALLS)
- **Proposal**: concrete text to be written — not "update the metric row", but the actual one- or two-line edit

Every proposal must cite **evidence** in its text: a specific weekly log section, a verified result path, or a PITFALLS entry. "Recent results suggest..." without a pointer isn't evidence — it's vibes.

### 4. Ask the user to approve

Accept any of:
- `all` → apply every proposal
- `N, M, ...` → approve the listed numbers
- `edit N: <text>` → replace proposal N before applying
- `skip N` → drop proposal N
- `quit` → apply nothing

If the user approves an L1 or L2 edit without a matching L4 entry, warn them and offer to generate the L4 entry. Story or Design changes without an audit trail become invisible debt — months later, "why did we drop X?" has no answer, and the user has to reconstruct reasoning from git blame.

### 5. Write approved changes

- **L4 entries**: append to `## 4. Iteration Log` in PLAN.md. Use the standard format (Trigger / Change / Evidence).
- **L1/L2 edits**: in-place edit of the relevant PLAN.md section. Preserve surrounding structure.
- **Stay in PLAN.md**: don't write to weekly logs, LOG.md, or PITFALLS.md from this skill — those are execution/operational layers, not plan layer. Mixing layers here erodes the distinction this plugin exists to maintain.

### 6. Report

List what was written to PLAN.md. Suggest:
- `git diff experiments/PLAN.md` for review
- Paper alignment check: Story edits likely need Overleaf abstract/intro update, Design edits likely need experiments.tex update (not done by this skill)

## Principles

**Every write gated by user approval.** This skill touches the research hub, not a dumping ground — a bad L4 entry or a misread L1 edit misleads the user and readers of the eventual paper. Better to propose something that gets rejected than to write something that gets regretted.

**Every proposal cites evidence.** Triggers without pointers are opinions, and opinions don't belong in L4 — the value of L4 is that a future reader can verify *why* the plan changed. "Metric inconsistency spotted last week" with no file reference is a dead entry.

**Stay in the plan layer.** The execution layer (weekly/LOG/PITFALLS) has its own curators — the cluster plugin, the user, PITFALLS triage. Editing those from iterate would make two skills fight over the same files.

**No duplicate L4 entries.** If the trigger already landed in L4, propose nothing new for it. Duplicate entries rot the audit trail and make "what actually changed?" harder to answer.

**If nothing triggers, exit quietly.** Forcing an L4 entry every run trains the user to ignore L4. A clean "no changes needed — latest results are consistent with current Story/Design" is a better signal than a manufactured update.

## What this skill does not do

- Run experiments (that's the cluster plugin)
- Verify numbers from output files (that's `update-log` in the cluster plugin)
- Sync paper with PLAN (that's for overleaf-workflow, future `sync-narrative` skill)
- Capture session-level memory (that's memory-workflow's `/wrap`)
