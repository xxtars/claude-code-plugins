# csc.fi-workflow

A [Claude Code](https://claude.ai/code) plugin for ML researchers working on [CSC](https://www.csc.fi/) (Finland's IT Center for Science) SLURM clusters (Mahti, Puhti).

Provides a structured workflow for syncing code, monitoring jobs, and tracking experiment progress via Apptainer containers — so you can focus on research instead of cluster logistics.

## Features

| Skill | Command | Description |
|-------|---------|-------------|
| Configure | `/csc.fi-workflow:configure` | Set up cluster connection (SSH, account, paths) |
| Init | `/csc.fi-workflow:init` | Scaffold experiment management files for a new project |
| Sync | `/csc.fi-workflow:sync` | Push code to cluster: `commit → push → ssh pull` |
| Check Jobs | `/csc.fi-workflow:check-jobs` | Query SLURM queue and recent job status |
| Update Log | `/csc.fi-workflow:update-log` | Record job results into structured experiment logs |

Also includes **rules** (always-on conventions) for:
- Shell script best practices on SLURM clusters
- Experiment file management (LOG / weekly logs / PITFALLS)

## Install

```bash
claude plugin install xxtars/csc.fi-workflow
```

## Quick Start

```bash
# 1. Configure your cluster connection
/csc.fi-workflow:configure

# 2. In a new project, scaffold experiment files
/csc.fi-workflow:init

# 3. Daily workflow
/sync                    # push code to cluster
/check-jobs              # see what's running
/update-log              # record results
```

## Requirements

- SSH access to a CSC cluster (Mahti or Puhti, with key-based auth recommended)
- Git repository for your project (synced via GitHub/GitLab)
- Apptainer (pre-installed on CSC clusters)

## Experiment Management

The plugin creates a structured experiment tracking system:

```
experiments/
  PLAN.md        ← What you're doing and why
  LOG.md         ← High-level progress (status table + milestones)
  PITFALLS.md    ← Lessons learned (so you don't repeat mistakes)
  weekly/
    week-2026-04-07.md  ← Detailed job records + verified results
```

**Key principle**: Numbers in weekly logs are *verified* — they must be read from actual cluster output, tagged with source and date. LOG.md only contains milestones, not intermediate numbers that go stale.

## Configuration

After install, run `/csc.fi-workflow:configure` in your project. It adds a `## Cluster` section to your project's `CLAUDE.md`:

```markdown
## Cluster
- Remote path: `/scratch/project_xxx/username/project-name`
- Usage: `ssh cluster.example.com "cd /scratch/.../project-name && <command>"`
- SLURM user: `username`
- SLURM account: `project_id`
- All commands run from project root
```

No separate config files — `CLAUDE.md` is the single source of truth. Each project has its own config, fully self-contained.

## License

MIT
