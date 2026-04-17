# Iteration Workflow

Research is a loop, not a pipeline: **Story → Design → Execution → (results force Story/Design updates) → repeat**. This rule defines how to run that loop cleanly.

## The loop

```
 ┌──────────────────────────────────┐
 │   L1 Story       ← abstract/intro
 │    ↓                             │
 │   L2 Design      ← experiments.tex
 │    ↓                             │
 │   L3 Execution   ← LOG / weekly
 │    ↓                             │
 │  Results force Story/Design change
 │    ↓                             │
 │   L4 Iteration log  ← audit trail
 └──────┬───────────────────────────┘
        │
        └─→ loop back to L1 or L2
```

## When an iteration happens

Any of these events should trigger adding an L4 entry (and possibly editing L1/L2):

- A verified result in a weekly log **contradicts** a claim in Story
- A baseline or ablation **outperforms** the proposed method (rethink Story's "why it matters")
- A planned experiment is **abandoned** (update Design's experiment matrix, move the reasoning into PITFALLS or L4)
- A **new experiment** is added in response to reviewer-like feedback or a surprising result
- The **metric** changes — Design must reflect the new metric everywhere, L4 records why
- A **scope shrink or expansion** (drop a dataset, add one, switch target)

## Principles

1. **Never edit L1 or L2 silently.** If Story or Design changes, an L4 entry is mandatory. The edit without the log is a debt.
2. **Link to evidence.** Every L4 Trigger field should point to a weekly log date, a PITFALLS entry, or a verified result location. "We felt like it" is not an acceptable trigger.
3. **Paper lags results, not the other way around.** Update PLAN.md first. Paper (abstract / experiments.tex) updates follow the next time you sync with Overleaf.
4. **Keep the loop short.** If a week's results don't feed back into PLAN.md, either the results are trivial (fine) or you're accumulating debt (not fine).
5. **Don't retcon Story.** If the old Story turned out to be wrong, don't rewrite it in place — keep the L4 record of the change. This matters when a reviewer asks "why did you claim X?"

## What to do when running `/research-workflow:iterate`

The skill reads LOG + latest weekly + PITFALLS, compares against current PLAN, and proposes L1/L2 edits + L4 entries. **It does not write without user approval.** See `skills/iterate/SKILL.md`.

## What L4 is NOT

- **Not a results log** — that's weekly/*.md
- **Not a decision log for operational choices** — those go in PITFALLS (if about bugs/config) or just in commit messages
- **Not a TODO list** — TODOs go in weekly Notes

L4 is specifically: "the research shape changed, and here's why".
