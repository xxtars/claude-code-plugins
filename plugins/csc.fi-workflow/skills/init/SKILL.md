---
name: init
description: Initialize experiment management structure for a new project. Use when user says "init experiments", "set up project", or starts a new ML research project.
---

# Initialize Experiment Structure

Scaffold the experiment management files for a new project.

## Cluster config
!`cat ~/.config/csc.fi-workflow/config.json 2>/dev/null || echo '⚠️ No cluster config found. Run /csc.fi-workflow:configure first.'`

## Steps

1. Ask the user for the **remote project path** on the cluster (e.g., `/scratch/.../project-name`). This is project-specific and will be stored in the project's `CLAUDE.md`.

2. Create the experiment directory structure:
   ```
   experiments/
     PLAN.md       ← Research direction, pipeline design, experiment planning
     LOG.md        ← Progress tracking (status table + milestone results)
     PITFALLS.md   ← Lessons learned (reference when stuck, append when bitten)
     weekly/       ← Detailed weekly job records + intermediate results
   ```

3. Copy templates from the plugin's `templates/` directory. Adapt as needed:
   - `experiments/PLAN.md` — empty scaffold with section headers
   - `experiments/LOG.md` — status table + weekly log index
   - `experiments/PITFALLS.md` — empty with format example
   - `experiments/weekly/` — empty, will be populated by `/csc.fi-workflow:update-log`

4. Add to the project's `CLAUDE.md` (create if not exists):
   ```markdown
   ## Cluster
   - Remote path: `<user-provided path>`
   - Usage: `ssh <ssh_host> "cd <remote_path> && <command>"`
   - All commands run from project root
   ```

5. Suggest adding `experiments/` tracking to the project's workflow.

## Notes
- Do NOT overwrite existing files — ask before replacing
- If `CLAUDE.md` already has a Cluster section, update rather than duplicate
- The weekly log format is defined in the plugin's `rules/experiment-files.md`
