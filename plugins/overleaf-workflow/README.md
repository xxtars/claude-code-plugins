# overleaf-workflow

A [Claude Code](https://claude.ai/code) plugin for researchers editing papers with Overleaf + local Claude Code.

Sync your Overleaf project via git, get academic writing conventions applied automatically, and manage references — all without leaving the terminal.

## Features

| Skill | Command | Description |
|-------|---------|-------------|
| Configure | `/overleaf-workflow:configure` | Connect an Overleaf project for local editing |
| Sync | `/overleaf-workflow:sync` | Push/pull changes between local and Overleaf |
| Add Ref | `/overleaf-workflow:add-ref` | Add a BibTeX citation to the paper |

Also includes **rules** (auto-loaded when editing `overleaf/**`):
- Academic writing style (sentence structure, word choice, numbers)
- Abstract and Introduction structure guidelines
- Reference quality conventions

## Install

```bash
claude plugin install xxtars/overleaf-workflow
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

## How it works

Overleaf supports git access. This plugin clones your Overleaf project into `overleaf/<project_id>/` as a separate git repo (independent from your main project). Edits are synced via `git push`/`git pull`.

```
overleaf/<project_id>/     ← separate git repo, synced with Overleaf
  sections/
    abstract.tex
    introduction.tex
    ...
  references.bib
```

The writing style rules activate automatically when you edit files under `overleaf/`, guiding Claude to follow ML/CV top-venue conventions.

## License

MIT
