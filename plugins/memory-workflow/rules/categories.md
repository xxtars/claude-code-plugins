# Memory categories

Session content sits on **two tracks**: research-layer entries (tied to experiments) and general-memory entries (cross-session facts). Plus one catch-all for important session-specific notes that don't fit either.

> File layout (PLAN / LOG / weekly / PITFALLS) is defined by `research-workflow`. See `research-workflow/rules/research-files.md`. Auto-memory lives at `~/.claude/projects/<project>/memory/` and is a Claude Code built-in.

---

## Track A — Research layer (tied to experiments)

| # | Category | Signal | Save? | Target |
|---|----------|--------|-------|--------|
| 1 | **Decision** | "选 X 不选 Y 因为 Z" / "we picked A over B because..." | ✅ | `experiments/LOG.md` (milestone) or current weekly Notes (minor). Major research-direction changes → `/research-workflow:iterate` routes to PLAN.md L4 instead. |
| 2 | **Code/file change** | diff-level edits | ❌ | git diff + commit message already covers this |
| 3 | **Reasoning chain** | how we thought step-by-step | ❌ (only keep conclusion + evidence) | folds into #1 or #6 |
| 4 | **Number / config** | ports, file paths, API format | ⚠️ | code comment (primary) or `CLAUDE.md` |
| 5 | **Dead end** | "tried X, doesn't work because Y" | ✅ | current weekly log Notes → "Abandoned:" section |
| 6 | **Assumption correction** | "原来不是..." / "actually it's..." | ✅ | auto-memory (if general fact) or `experiments/PITFALLS.md` (if operational) |
| 7 | **Open item / breakpoint** | "等 Y 完成后..." / TODO | ✅ | current weekly log Notes |
| 8 | **External dep version** | behavior tied to a specific version of an external tool | ✅ | `experiments/PITFALLS.md` or code comment at call site |

---

## Track B — General memory (cross-session)

Matches Claude Code's built-in auto-memory types. Targets `~/.claude/projects/<project>/memory/<file>.md` + index update in `MEMORY.md`.

| # | Type | Signal | Save? |
|---|------|--------|-------|
| 9  | **user** | User's role, goals, knowledge, preferences | ✅ |
| 10 | **feedback** | Correction or validation of how to work (both "don't do X" and "keep doing X") | ✅ |
| 11 | **project** | Cross-session project state not in code/git | ⚠️ (check project's memory-scope policy in CLAUDE.md — some projects restrict memory to user preferences only, routing project state to `experiments/LOG.md` instead) |
| 12 | **reference** | Pointer to external system (issue tracker, dashboard, doc) | ✅ |

---

## Track C — Session-notes (catch-all, last resort)

| # | Category | Signal | Save? | Target |
|---|----------|--------|-------|--------|
| 13 | **Session notes** | Important observation from this session that **doesn't fit any of #1–12** | ⚠️ use sparingly | current weekly log Notes section, prefixed with date |

When to use:
- A surprising empirical pattern you're not sure what to do with yet
- Context for a decision that hasn't crystallized (proto-decision)
- A half-finished thought worth revisiting
- A cross-cutting observation that isn't a dead end, decision, or correction

When NOT to use:
- As a dumping ground when the content actually fits another category → be honest, pick the real category
- For ephemeral status (that's what conversation context is for)
- For trivia

**Anti-pattern**: Session-notes grows into a junk drawer. If `/wrap` proposes 3+ session-notes entries in one session, stop and re-examine — most should probably be #1/#5/#6/#7.

---

## Guiding principles

- **Signal over volume**: A session may have zero entries worth saving. Trivial status-check sessions produce nothing.
- **Evidence over narrative**: Record the load-bearing observation, not the reasoning chain.
- **User-gated writes**: Never write without explicit user approval. Pollution is harder to fix than omission.
- **No duplication**: Check whether the fact is already in another file before writing.
- **Category choice is honest**: if something fits #1 decision, don't call it #13 session-notes because you're lazy.

## Target-file cheat sheet

- **Research-structure change** → `/research-workflow:iterate` → PLAN.md L4 (not this skill)
- **Execution milestone** → `experiments/LOG.md`
- **Operational lesson, version gotcha** → `experiments/PITFALLS.md`
- **Weekly detail, dead end, open item, session-note** → current `experiments/weekly/week-*.md` Notes
- **Code-level values** → code comment (flag to user, don't auto-write)
- **Cross-session user/feedback/reference facts** → `~/.claude/projects/<proj>/memory/`
- **Cross-session project facts** → ask user (`LOG.md` vs memory depends on project policy)
