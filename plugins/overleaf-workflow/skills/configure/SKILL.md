---
name: configure
description: Configure Overleaf project for local editing. Use when user says "set up overleaf", "connect overleaf", or starts working with an Overleaf project.
---

# Configure Overleaf Project

Set up an Overleaf project for local git-based editing.

## Steps

1. Ask the user for:
   - **Overleaf git URL**: `https://git.overleaf.com/<project_id>` (found in Overleaf → Menu → Git)
   - **Target venue** (optional): e.g., NeurIPS, ICML, CVPR — affects page limits and style guidance

2. Clone the Overleaf repo into `overleaf/<project_id>/`:
   ```bash
   git clone https://git.overleaf.com/<project_id> overleaf/<project_id>
   ```
   Overleaf will prompt for email + password (or token).

3. Add `overleaf/` to the main project's `.gitignore` if not already there — the overleaf repo is independent from the main project git.

4. Record the configuration in the project's `CLAUDE.md`:
   ```markdown
   ## Overleaf
   - Path: `overleaf/<project_id>/`
   - Venue: <venue>
   ```

5. Verify by listing the tex files:
   ```bash
   ls overleaf/<project_id>/*.tex overleaf/<project_id>/sections/*.tex
   ```

## Notes
- The overleaf directory is a **separate git repo** — never mix its git operations with the main project
- Overleaf git auth may require a token: https://www.overleaf.com/user/settings → Git Integration
