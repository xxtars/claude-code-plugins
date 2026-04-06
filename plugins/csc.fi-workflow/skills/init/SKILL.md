---
name: init
description: Initialize experiment management structure for a new project. Use when user says "init experiments", "set up project", or starts a new ML research project.
---

# Initialize Experiment Structure

Scaffold the experiment management files for a new project.

## Prerequisites

Read the project's `CLAUDE.md` for the Cluster section (ssh_host, remote_path). If not found, run `/csc.fi-workflow:configure` first.

## Steps

1. Create the experiment directory:
   ```bash
   mkdir -p experiments/weekly
   ```

2. Create `experiments/PLAN.md`:
   ```markdown
   # Experiment Plan

   ## Research Goal
   <!-- What are you trying to achieve? -->

   ## Pipeline Overview
   <!-- High-level description of your data → training → evaluation pipeline -->

   ## Experiment Design
   <!-- What experiments will you run? What are the key variables? -->

   ## Evaluation
   <!-- How will you measure success? Metrics, baselines, benchmarks -->
   ```

3. Create `experiments/LOG.md`:
   ```markdown
   # Experiment Log

   Progress tracking. Research plan in [PLAN.md](PLAN.md), detailed records in weekly logs, lessons in [PITFALLS.md](PITFALLS.md).

   ---

   ## Stage Progress

   | Stage | Status | Notes |
   |-------|--------|-------|
   | | | |

   ---

   ## Weekly Logs

   | Week | File | Summary |
   |------|------|---------|
   | | | |

   > Last updated: YYYY-MM-DD
   ```

4. Create `experiments/PITFALLS.md`:
   ```markdown
   # Pitfalls & Lessons Learned

   Reference this file when debugging. Append new entries when you discover a pitfall.

   ---

   <!-- Example entry:
   ## Descriptive title of the pitfall
   - **Symptom**: What you observed (error message, unexpected behavior)
   - **Root cause**: Why it happened
   - **Fix**: How you resolved it
   - **Date**: YYYY-MM-DD
   -->
   ```

5. If `CLAUDE.md` doesn't have a Cluster section yet, suggest running `/csc.fi-workflow:configure`.

## Notes
- Do NOT overwrite existing files — ask before replacing
- If `CLAUDE.md` already has a Cluster section, do not duplicate
- The weekly log format is defined in the plugin's `rules/experiment-files.md`
