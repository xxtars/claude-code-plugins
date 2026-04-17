# claude-code-plugins

Personal [Claude Code](https://claude.ai/code) plugin marketplace for ML research workflows.

## Plugins

| Plugin | Description |
|--------|-------------|
| [research-workflow](plugins/research-workflow/) | Four-layer PLAN (Story / Design / Execution / Iteration), LOG/weekly/PITFALLS conventions, iterate skill |
| [csc.fi-workflow](plugins/csc.fi-workflow/) | SLURM cluster workflow for CSC (Mahti/Puhti): sync code, submit jobs, check status, record results |
| [overleaf-workflow](plugins/overleaf-workflow/) | Overleaf paper writing: git sync, academic writing conventions, reference management |
| [memory-workflow](plugins/memory-workflow/) | Session wrap-up: categorize decisions/dead-ends/open-items and persist to project files, user-gated |

## Plugin relationships

`research-workflow` defines the file conventions (`experiments/PLAN.md`, `LOG.md`, `weekly/`, `PITFALLS.md`). The other three plugins write into those files:

```
research-workflow   (file conventions + iterate)
      │
      ├── csc.fi-workflow     (cluster ops: update-log writes to weekly/LOG)
      ├── overleaf-workflow   (paper sync)
      └── memory-workflow     (/wrap writes to weekly/PITFALLS/memory)
```

Parallel plugins — install what you need. The dependency is documentary, not packaged.

## License

MIT
