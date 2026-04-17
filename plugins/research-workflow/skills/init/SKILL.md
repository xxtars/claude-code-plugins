---
name: init
description: Scaffold the four-layer research workflow files (PLAN.md with Story/Design/Execution/Iteration sections, LOG.md, PITFALLS.md, and the current weekly log) for an ML research project. Make sure to use this skill whenever the user starts a new research project, wants to set up experiment tracking, scaffold research files, create a PLAN.md, or says "init", "init research", "init experiments", "set up project", "scaffold research", "新项目", "搭实验框架", "experiment tracking setup", even if they don't explicitly name the files.
---

# Initialize research workflow

Scaffold the four-file research structure. See `rules/research-files.md` for the conventions these files implement.

## Steps

1. Ensure directory exists:
   ```bash
   mkdir -p experiments/weekly
   ```

2. Create `experiments/PLAN.md` from `templates/PLAN.md` (in this plugin). Four sections:
   - **L1 Story** (claim / why it matters / current stance)
   - **L2 Design** (pipeline / experiment matrix / metrics & baselines)
   - **L3 Execution Status** (pointer only, no numbers)
   - **L4 Iteration Log** (append-only audit trail of Story/Design changes)

3. Create `experiments/LOG.md` from `templates/LOG.md`:
   - Stage Progress table
   - Weekly Logs index

4. Create `experiments/PITFALLS.md` from `templates/PITFALLS.md` (structured entry format: symptom / root cause / fix / date).

5. Create the current week's `experiments/weekly/week-YYYY-MM-DD.md` from `templates/weekly/week-TEMPLATE.md`, with the Monday date in the filename. Three sections: Job History / Verified Results / Notes.

6. If the project uses a cluster (CLAUDE.md has a `Cluster` section), suggest running the relevant cluster-plugin configure step after init completes (e.g., `/csc.fi-workflow:configure`).

## Principles

**Don't overwrite existing files.** The user's in-progress research lives in these paths. If a file already exists, ask before replacing — a blind overwrite can wipe weeks of notes. A polite "`experiments/PLAN.md` already exists. Replace / skip / abort?" is the right default.

**Leave template placeholders alone.** The scaffold's job ends at structure. Story (L1) and Design (L2) content is the user's research thinking, not something to generate from nothing — fabricating it would either be wrong or lock the user into a framing they didn't choose.

**Start weekly and LOG empty.** No synthetic numbers anywhere. Fake data in these files creates the same hazard as a stale comment: looks authoritative, misleads silently.

## After init

Remind the user:
- Fill Story (L1) first — the one-paragraph claim is the most important anchor for everything else
- PLAN.md is the hub; numbers live in weekly/ and are mirrored to the paper only after verification
- Run `/research-workflow:iterate` when results force a Story or Design change
