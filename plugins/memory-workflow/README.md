# memory-workflow

Session-level memory management for Claude Code. One on-demand skill that asks you what to keep before writing anything.

## Why

Stop-hook-based auto-compressors (e.g. `claude-mem`) block every turn and burn LLM calls on noise. In dense tool-heavy workflows (cluster jobs, file ops) the signal-to-noise ratio is bad.

This plugin takes the opposite approach: **manual trigger, full conversation context, user-gated writes**. Run it when you're closing out a session that actually produced something worth remembering.

## What

| Skill | Command | When |
|-------|---------|------|
| `wrap` | `/memory-workflow:wrap` | End of a session that produced decisions, dead ends, or open items worth keeping |

## Categories

8 information categories, 5 of which are worth saving. See [`rules/categories.md`](rules/categories.md) for the full mapping.

## File layout it assumes

The `wrap` skill writes to files defined by the `research-workflow` plugin:

- `experiments/LOG.md` — major decisions (milestones)
- `experiments/PLAN.md` L4 Iteration Log — Story/Design changes (via `/research-workflow:iterate`, not this skill)
- `experiments/weekly/week-YYYY-MM-DD.md` — dead ends, open items, session notes
- `experiments/PITFALLS.md` — operational assumption corrections, version gotchas
- `~/.claude/projects/<proj>/memory/` — general facts, cross-session user preferences

If your project doesn't use this layout, run `/research-workflow:init` first, or the skill will ask where to put each category before proceeding.

## Install

Add this marketplace to `~/.claude/settings.json` and enable `memory-workflow@xxtars-plugins`.
