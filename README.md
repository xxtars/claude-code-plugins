# claude-code-plugins

Personal [Claude Code](https://claude.ai/code) plugin marketplace for ML research workflows.

## Plugins

| Plugin | Description |
|--------|-------------|
| [research-workflow](plugins/research-workflow/) | Four-layer PLAN (Story / Design / Execution / Iteration), LOG/weekly/PITFALLS conventions, iterate skill |
| [csc.fi-workflow](plugins/csc.fi-workflow/) | SLURM cluster workflow for CSC (Mahti/Puhti): sync code, submit jobs, check status, record results |
| [overleaf-workflow](plugins/overleaf-workflow/) | Overleaf paper writing: git sync, academic writing conventions, reference management |
| [memory-workflow](plugins/memory-workflow/) | Session wrap-up: categorize decisions/dead-ends/open-items and persist to project files, user-gated |
| [web-paper-to-pdf](plugins/web-paper-to-pdf/) | Convert Distill-style web papers (transformer-circuits.pub, distill.pub) into clean LaTeX-typeset PDFs using the public NeurIPS 2024 template. Output is labelled as **unofficial archival rendering**. |

## Plugin relationships

`research-workflow` defines the file conventions (`experiments/PLAN.md`, `LOG.md`, `weekly/`, `PITFALLS.md`). Three of the workflow plugins write into those files:

```
research-workflow   (file conventions + iterate)
      │
      ├── csc.fi-workflow     (cluster ops: update-log writes to weekly/LOG)
      ├── overleaf-workflow   (paper sync)
      └── memory-workflow     (/wrap writes to weekly/PITFALLS/memory)
```

`web-paper-to-pdf` is independent — it has no dependency on the research-workflow file conventions.

Parallel plugins — install what you need. The dependency is documentary, not packaged.

## Disclaimer (web-paper-to-pdf)

PDFs produced by `web-paper-to-pdf` are **unofficial archival renderings**. They carry a footnote on the first page stating they are not produced or endorsed by the original authors, and they include the render date. Intended for personal reading / archival only — respect the copyright and license of the source pages. Not affiliated with Anthropic or any other organisation whose papers can be rendered.

## License

MIT for plugin code in this repo. Third-party files (e.g. `neurips_2024.sty`, the public NeurIPS template by Roman Garnett and contributors) carry their own terms.
