---
name: init
description: Initialize experiment management structure for a new project. Use when user says "init experiments", "set up project", or starts a new ML research project.
---

# Initialize Experiment Structure

Scaffold the experiment management files for a new project.

## Prerequisites

Read the project's `CLAUDE.md` for the Cluster section (ssh_host, remote_path). If not found, run `/csc.fi-workflow:configure` first.

## Steps

1. Create the experiment directory structure:
   ```
   experiments/
     PLAN.md       ← Research direction, pipeline design, experiment planning
     LOG.md        ← Progress tracking (status table + milestone results)
     PITFALLS.md   ← Lessons learned (reference when stuck, append when bitten)
     weekly/       ← Detailed weekly job records + intermediate results
   ```

2. Copy templates from the plugin's `templates/` directory. Adapt as needed:
   - `experiments/PLAN.md` — empty scaffold with section headers
   - `experiments/LOG.md` — status table + weekly log index
   - `experiments/PITFALLS.md` — empty with format example
   - `experiments/weekly/` — empty, will be populated by `/csc.fi-workflow:update-log`

3. If `CLAUDE.md` doesn't have a Cluster section yet, ask the user for the remote path and add it.

## Notes
- Do NOT overwrite existing files — ask before replacing
- If `CLAUDE.md` already has a Cluster section, do not duplicate
- The weekly log format is defined in the plugin's `rules/experiment-files.md`
