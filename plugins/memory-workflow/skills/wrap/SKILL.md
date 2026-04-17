---
name: wrap
description: Wrap up the current session by categorizing its content into research-layer entries (decisions, dead ends, assumption corrections, open items, version gotchas), general-memory entries (user preferences, feedback, cross-session facts, external references), and session-notes, then persist user-approved entries to the right project files. Make sure to use this skill whenever the user is winding down a substantive work session, says "wrap", "/wrap", "save session", "sync memory", "整理 session", "session done", "persist this session", or is about to close out a session that produced decisions or observations they'd otherwise lose.
---

# Wrap session

Extract high-value information from the conversation, ask the user which entries to keep, and write approved entries to the right files.

## Why this skill exists

Session-end auto-compressors (e.g., claude-mem's Stop hook) fire on every turn and compress via LLM indiscriminately — they block the main loop and drown signal in noise, especially in tool-heavy workflows. This skill is the opposite shape: **one manual invocation, full conversation context already loaded, user approves each entry**. The cost is one skill call per session; the benefit is writes you'd actually want to read later.

See `rules/categories.md` for the three tracks and target-file mapping — read that first.

## Prerequisites

1. Read the project's `CLAUDE.md` to learn the file layout and any information-placement policy (some projects restrict what can go into auto-memory vs. project files).
2. Read `rules/categories.md` (sibling of this skill) for the three tracks and target-file mapping.
3. Identify the current weekly log file, if the project uses one: Monday of this week → `experiments/weekly/week-YYYY-MM-DD.md`. If the project doesn't have a weekly structure, ask the user where to route Track A #5/#7 and Track C entries.

## Steps

### 1. Scan the conversation

Walk the full conversation (not just the last turn). For each track defined in `rules/categories.md`, extract candidate entries:

**Track A — Research layer**
- #1 Decision (tradeoff explicitly argued)
- #4 Number/config (non-obvious constants that took discussion)
- #5 Dead end (something attempted and abandoned with reasoning)
- #6 Assumption correction (prior belief overturned)
- #7 Open item (unresolved step for future session)
- #8 External dep version (behavior tied to a specific version)

**Track B — General memory (cross-session)**
- #9 user (role / goals / preferences stated or revised)
- #10 feedback (correction or validation of how to work)
- #11 project (cross-session project state — may be restricted by project policy)
- #12 reference (pointer to external system)

**Track C — Session-notes**
- #13 session-notes (important, but doesn't fit any of the above)

**Don't propose entries for**:
- Track A #2 (code/file changes) — git diff + commit is the authoritative record, duplicating here just rots
- Track A #3 (reasoning chain) — reasoning regenerates from the same evidence in a future session; only the evidence is worth keeping (and it lands in #1 or #6)
- Anything already recorded elsewhere in the project (grep-verify before proposing)
- Trivial sessions (status checks, lookups, no new state)

If nothing is worth recording, say so and exit — don't force entries to justify running the skill.

### 2. Propose a candidate table

Present the candidates as a numbered table with columns: `#`, `Track`, `Type`, `Target`, `Draft`.

- **Track**: `A` / `B` / `C`
- **Type**: category number + short name (e.g., `#1 decision`, `#10 feedback`)
- **Target**: specific file path (or `auto-memory` for Track B)
- **Draft**: concrete one-line text to be written

Few strong entries beat many weak ones. If Track C proposals exceed 2–3, reconsider — most should fit a specific category under Track A or B. When session-notes become a dumping ground the user stops reading them.

### 3. Ask the user to approve

Accept any of:
- `all` → write every entry as drafted
- `N, M, ...` → approve the listed numbers
- `edit N: <text>` → replace draft N before writing
- `move N to <file>` → change the target file for entry N
- `skip N` → drop entry N (or just list what to keep and the rest drops)
- `quit` → write nothing

Do not proceed past this step without an explicit user answer.

For Track B #11 (project type), check the project's `CLAUDE.md` information-placement policy first. If the policy scopes memory to user preferences only, offer to route to `experiments/LOG.md` instead of auto-memory before writing.

### 4. Write approved entries

- **Project markdown files** (`LOG.md`, weekly, `PITFALLS.md`): use Edit to append to the matching section. Match the existing format — tables for job history, bullets for notes, headings for topic blocks. Preserve surrounding structure.
- **Auto-memory** (`~/.claude/projects/<project>/memory/`): write using the two-step frontmatter convention (one file per entry + index line in `MEMORY.md`). Match the style of existing memory files in the same project.
- **Code comments**: don't auto-write. List the files/locations and suggest the user add the comment themselves (comments benefit from being written by the person who owns the code).
- **Session-notes** (#13): append to the Notes section of the current weekly log, prefixed with the session date.

Before writing each entry, grep the target file to confirm it isn't already there.

### 5. Report and stop

Summarize what was written: list each file + entry. Suggest `git status` so the user can review before committing. Don't run `git add` or `git commit` — that's the user's call and a good pause point before anything leaves the working tree.

## Principles

**User approval gates every write.** Memory pollution is harder to recover from than memory loss: a wrong entry misleads future sessions quietly for weeks. Spending seconds to approve each entry is cheaper than the grep-and-delete later.

**Append, don't rewrite.** Editing existing sections risks reshaping content the user didn't ask to touch. Appending gives a clean diff to review. If something genuinely needs to change in place, make that an explicit proposal in step 3, not a silent side effect.

**Save anchors, not inferences.** Reasoning chains regenerate from the same observation; the observation itself can't. Record the load-bearing evidence, and let the inference be re-derived next session.

**Respect project scope.** Different projects have different memory policies. Route Track B #11 according to the project's CLAUDE.md; don't assume one rule fits all.

**Skip trivial sessions.** A pure status-check session has nothing to wrap. Proposing zero entries is a valid outcome — "nothing to save" is more useful than a weak entry.

## Notes

This skill runs on demand, not via a hook. A SessionEnd hook would re-read the transcript from scratch in a headless LLM call, losing the conversation context that makes categorization accurate. Inline invocation keeps full understanding at analysis time.

For real-time capture (catching a decision as it happens rather than at session end), use a conversation convention — have Claude flag high-value moments inline with a "save this?" question. That's a dialogue pattern, not something this skill provides.
