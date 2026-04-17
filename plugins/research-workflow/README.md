# research-workflow

Research workflow scaffolding and feedback-loop management for ML research projects. Defines the file conventions (PLAN / LOG / weekly / PITFALLS) that other plugins (`csc.fi-workflow`, `overleaf-workflow`, `memory-workflow`) write into.

## Why

A research project isn't a pipeline, it's a loop: **Story → Design → Execution → (results force updates) → Story/Design**. Most experiment-tracking tools only cover Execution. This plugin makes the Story and Iteration layers explicit, with an audit trail.

## Skills

| Skill | Command | When |
|-------|---------|------|
| `init` | `/research-workflow:init` | Scaffold PLAN / LOG / PITFALLS / weekly on a new project |
| `iterate` | `/research-workflow:iterate` | After a weekly log shows new verified results, reconcile with PLAN's Story and Design |

## File structure

```
experiments/
├── PLAN.md            ← 4 layers: Story / Design / Execution pointer / Iteration Log
├── LOG.md             ← Stage status + weekly index
├── weekly/
│   └── week-YYYY-MM-DD.md   ← Job history + verified results + notes
└── PITFALLS.md        ← Operational lessons (symptom / root cause / fix / date)
```

See [`rules/research-files.md`](rules/research-files.md) for the full conventions and [`rules/iteration-workflow.md`](rules/iteration-workflow.md) for the feedback-loop protocol.

## The four PLAN.md layers

| # | Layer | Purpose | Paper alignment |
|---|-------|---------|-----------------|
| L1 | Story | Core claim, why it matters, current stance | abstract + introduction |
| L2 | Design | Pipeline, experiment matrix, metrics, baselines | experiments.tex + appendix |
| L3 | Execution Status | Pointer to LOG.md and weekly logs (no numbers here) | — |
| L4 | Iteration Log | Append-only audit trail of Story/Design changes | — |

## Relationship to other plugins

```
research-workflow  ← defines PLAN / LOG / weekly / PITFALLS conventions
      │
      ├── csc.fi-workflow      writes weekly via update-log
      ├── overleaf-workflow    paper sync (future: Story ↔ abstract sync)
      └── memory-workflow      /wrap writes into these files
```

These plugins are **parallel, not nested**. Install what you need. The dependency is conceptual (their rules reference `research-workflow`), not packaged.

## Install

Add to your Claude Code plugins, enable `research-workflow@xxtars-plugins`.
