# overleaf-workflow

A [Claude Code](https://claude.ai/code) plugin for researchers editing papers with Overleaf + local Claude Code.

Sync your Overleaf project via git, get academic writing conventions applied automatically, and manage references — all without leaving the terminal.

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Configure | `/overleaf-workflow:configure` | Connect an Overleaf project for local editing |
| Sync | `/overleaf-workflow:sync` | Push/pull changes between local and Overleaf |
| Add Ref | `/overleaf-workflow:add-ref` | Add a BibTeX citation to the paper |

## Rules (auto-loaded for `overleaf/**`)

When you edit any file under `overleaf/`, the writing style rules are automatically loaded. They guide Claude to follow ML/CV top-venue conventions:

- **Sentence structure**: One idea per sentence, active voice, short and direct
- **Word choice**: No subjective modifiers ("significantly") — use numbers; no hedging
- **Numbers**: Unverified numbers use `--` placeholder; always include metric name with number
- **References**: Google Scholar BibTeX preferred; venue version over arXiv; protect capitalization with braces
- **Abstract**: 4-8 sentences, single paragraph. Background -> gap -> approach -> results
- **Introduction**: Funnel structure, 5-6 paragraphs. Prior work by ascending limitation
- **Method**: 3-5 subsections. Define notation before use; equations earn their place; figure-text alignment
- **Experiments**: Setup -> main results -> ablations -> analysis. Every table/figure needs a takeaway sentence; ablations isolate one variable at a time; include failure cases
- **Page limits**: Venue-aware reminders (NeurIPS 10pp, ICML 9pp, CVPR/ICCV/ECCV 8pp, etc.) — flags when approaching the limit

## Install

```bash
claude plugin install xxtars/claude-code-plugins/overleaf-workflow
```

## Quick Start

```bash
# 1. Connect your Overleaf project
/overleaf-workflow:configure

# 2. Edit paper locally, then sync
/overleaf-workflow:sync

# 3. Add a citation
/overleaf-workflow:add-ref
```

## How It Works

Overleaf supports [git access](https://www.overleaf.com/learn/how-to/Git_integration). This plugin clones your Overleaf project into `overleaf/<project_id>/` as a **separate** git repo (independent from your main project). Edits are synced via `git push`/`git pull`.

```
your-project/
  CLAUDE.md              <- records Overleaf path + venue
  .gitignore             <- contains "overleaf/" to isolate it
  overleaf/
    69ba72b885b50d.../   <- separate git repo, synced with Overleaf
      main.tex
      sections/
        abstract.tex
        introduction.tex
        method.tex
        experiments.tex
        ...
      references.bib
```

## Skill Details

### `/overleaf-workflow:configure`

One-time setup per Overleaf project.

**What it does:**
1. Asks for the Overleaf git URL and target venue (NeurIPS, ICML, CVPR, etc.)
2. **Validates the URL format**: Must match `https://git.overleaf.com/<24-char hex ID>`. If you paste a regular Overleaf URL (`https://www.overleaf.com/project/...`), it auto-extracts the project ID and converts it
3. Asks you to clone manually (Overleaf requires interactive auth — Claude can't do this step)
4. Adds `overleaf/` to `.gitignore` to keep it separate from your main project git
5. Records path and venue in CLAUDE.md
6. Verifies by listing the tex files in the cloned directory

**Note:** Overleaf git auth requires a token. Get it from https://www.overleaf.com/user/settings -> Git Integration.

### `/overleaf-workflow:sync`

Bidirectional sync between local edits and Overleaf.

**Push (local -> Overleaf):**
1. **Pulls first** to pick up any collaborator edits (avoids conflicts)
2. Shows `git status` for review
3. Stages only the files you changed (never `git add -A`)
4. Commits with a descriptive message and pushes
5. Changes appear on Overleaf within seconds

**Pull (Overleaf -> local):**
1. **Stashes uncommitted local changes** before pulling (prevents losing work if there are conflicts)
2. Pulls latest from Overleaf
3. Pops the stash; if conflicts arise, shows them for you to resolve

**Conflict resolution:**
- Shows which files conflict and the conflict markers (both versions)
- Asks you to choose which version to keep or how to merge
- Resolves, stages, and commits

**Important:** Always `cd` into the overleaf subdirectory before git operations — it's a separate repo.

### `/overleaf-workflow:add-ref`

Adds a BibTeX entry to the paper's `.bib` file.

**Input options:**
- Paper title -> searches Google Scholar for the BibTeX
- URL (arXiv, DOI page) -> extracts citation info from the page
- Raw BibTeX -> uses it directly

**Safety checks:**
- **Duplicate detection**: Checks by title, author+year, and DOI to avoid adding the same paper twice
- **Citation key collision**: If the generated key (e.g., `smith2025imagenet`) already exists, warns and suggests an alternative (e.g., `smith2025imagenetb`) — never silently overwrites
- **BibTeX syntax validation**: Before appending, verifies balanced braces, required fields (author, title, year, venue), and no stray characters that would break LaTeX compilation
- **Quality checklist**: Complete author names (no "et al."), title capitalization protected with braces, standard venue abbreviations, venue version preferred over arXiv preprints

**Output:** Shows the citation key so you can immediately use `\cite{key}` in your tex file.

## Writing Style Rules (Detail)

The rules in `rules/writing-style.md` are auto-loaded whenever you edit files under `overleaf/`. Here's what they enforce:

### General Conventions
| Rule | Good | Bad |
|------|------|-----|
| One idea per sentence | "We propose X. It addresses Y." | "We propose X, which addresses Y while also being Z." |
| Active voice | "We propose X" | "X is proposed" |
| No subjective modifiers | "improves by 3.2%" | "significantly improves" |
| No hedging | "achieves 85.2%" | "achieves a relatively good 85.2%" |
| Numbers need metrics | "85.2% accuracy" | "85.2%" |
| Unverified = placeholder | "achieves --% on X" | "achieves [TODO]% on X" |

### Section Structure Templates

**Abstract** (4-8 sentences, single paragraph):
Background -> Problem/Gap -> Key insight (optional) -> Our approach -> Results with benchmarks -> Significance (optional)

**Introduction** (5-6 paragraphs, funnel):
Background (broad->specific) -> Prior work (mainstream approaches) -> Gap/Limitation -> Our approach (method + novelty) -> Contributions (2-4 itemized) -> Paper outline (optional)

**Method** (3-5 subsections):
Overview/Problem formulation (with pipeline figure) -> Component subsections (motivation -> formulation -> explanation each) -> Training/Inference procedure. No implementation details here.

**Experiments** (4-6 subsections):
Setup (datasets, metrics, baselines, implementation) -> Main results (Table 1, bold best) -> Ablations (one variable at a time) -> Analysis (qualitative, failure cases) -> Additional experiments (optional)

### Page Limits by Venue

| Venue | Main body | Appendix |
|-------|-----------|----------|
| NeurIPS | 10 pages | unlimited |
| ICML | 9 pages | unlimited |
| CVPR/ICCV/ECCV | 8 pages (incl. refs) | limited supplementary |
| ACL/EMNLP | 8 pages (long) / 4 (short) | unlimited |
| AAAI | 8 pages (incl. refs) | - |

## License

MIT
