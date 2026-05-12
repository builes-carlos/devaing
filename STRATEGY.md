# Strategy: devaing-init (and the devaing framework)

## What devaing is

A hyper-agile framework for building products with AI. Targets solo builders, dev pairs, and early-stage startups who want product fast without heavy process. Not Pocock (designed for large teams). Not vibe coding (no structure). The middle path.

**Core insight:** GitHub Issues is not bureaucracy — it's a token rationalization system. Issues let the user work granularly (one issue per session), share work with friends (parallel token consumption), and give agents enough context to execute without re-explanation.

## The six skills

| Skill | Purpose |
|-------|---------|
| `/devaing-init` | Bootstrap: repo, CI, discovery, Phase 1 epics, prototype, issues. |
| `/devaing-phase` | Start a new phase: verify previous phase closed, discovery, epics, prototype extension, issues. |
| `/devaing-phase-revise` | Adjust current phase scope, prototype, or business logic before or during implementation. |
| `/devaing-work` | Issue number or milestone name → mid-flight detection → context check → implement → CONTEXT.md → close. |
| `/devaing-feature` | New feature area → milestone → first slice → CONTEXT.md |
| `/devaing-bug` | Bug in natural language → structured issue with diagnosis → CONTEXT.md |

## Key design decisions

### No PRDs
to-prd eliminated entirely. PRDs are expensive intermediaries nobody reads. Issues with acceptance criteria are the spec. ADRs capture non-obvious decisions after implementation.

### No quiz loops
Only two human validations in devaing-init: grill-me (domain) and epic list approval. Everything else the agent executes without asking.

### Milestones = epics
GitHub milestones group issues by epic. Human navigates by milestone, not flat list.

### CONTEXT.md is the single source of truth
Updated after every operation: devaing-work, devaing-bug, devaing-feature. Never stale because it grows with the product.

### Known limitations section in CONTEXT.md (from HBX/senior-dev practice)
Distinct from ADRs (decisions made) and key constraints (non-negotiable limits). Captures problems we are aware of and consciously not fixing yet: what the problem is, why it's deferred, what would trigger the fix, and operational guidance for the current state. devaing-work prompts for this at close alongside the ADR question.

### Working mode choice
After discovery, the user picks how issues are created: Progressive (devaing-work creates slices as it goes, no GitHub issues at init time), Backlog (first unblocked slice per epic), or Complete (all issues for the current phase upfront). Scope is always bounded by the current phase — future phases are defined when their phase starts. The framework adapts to session style.

### Prototype as living skeleton
UI prototypes are not deleted after UX validation. They survive as navigation skeletons. Each devaing-work slice replaces one mock screen with real implementation. The rest stays intact as scaffolding for future slices. UX decisions persist in CONTEXT.md under `## UX conventions`.

### Context rot awareness (from GSD)
Context quality degrades predictably: peak at 0-30%, rushes at 50%+, hallucinates at 70%+. devaing-work addresses this in two places: (1) warns before dispatching to ce-work if the session is already loaded, (2) suggests a fresh session after each closed slice.

### Mid-flight session recovery (from gstack)
If a devaing-work session dies mid-slice (context full, crash, closed window), the next invocation detects the orphaned work and offers to resume. GitHub mode: finds open issue with existing branch. No-GitHub mode: finds unmerged branch matching the milestone slug.

## Skills integrated (third-party, not modified)

- `grill-me` → domain discovery (Step 9)
- `prototype` → UI validation before issue generation (Step 9d)
- `ce-work` → implementation engine inside devaing-work
- `ce-frontend-design` → UI issues routed here first in devaing-work
- `diagnose` → hard bugs in devaing-bug when cause is not obvious
- `improve-codebase-architecture` → suggested every 2-3 milestones at close

## Documentation format

SKILL.md and STRATEGY.md are the permanent source of truth — always up to date, agent-readable.

STRATEGY.html is a generated companion for human consumption. It is a periodic snapshot of STRATEGY.md, not a live document. Rules:
- Generate it only when explicitly requested, never proactively.
- When updating it, use surgical edits on the existing file, not a full rewrite.
- If it diverges from STRATEGY.md, STRATEGY.md wins.


## Sources

### Pocock
Structure: atomic issues, isolated worktrees, ADRs post-implementation, vertical slices, Compound Engineering as execution layer. Dropped: PRDs, quiz loops, one PRD per epic.

### gstack (Garry Tan / YC)
Feed-forward pipeline (each step writes artifacts the next consumes), role chaining via CE skills (designer → engineer → reviewer), prototype before committing to UI. Also: checkpoint/context-restore concept → adapted as mid-flight session recovery in devaing-work. Dropped: taste learning, multi-model validation, safety gates (out of scope for devaing's target).

### GSD (get-shit-done, gsd-build/TACHES)
Context rot model: 0-30% peak quality, 50%+ rushes, 70%+ hallucinates. Context isolation per task. Adapted as: Progressive working mode (no full backlog upfront), context budget warning in devaing-work before dispatching to ce-work, fresh session suggestion after each closed slice. Dropped: autonomous next-step detection, separate REQUIREMENTS/STATE/ROADMAP files (unified in CONTEXT.md).

## Flows

### Initial setup (new project)
```
/devaing-init
  → tech setup (repo, CI, AGENTS.md, CONTEXT.md, labels, plugin)
  → grill-me                          ← human validation 1
  → populate CONTEXT.md
  → propose epic list                 ← human validation 2
  → create GitHub milestones
  → prototype UI epics (living skeleton, not deleted)
  → working mode choice: Progressive / Backlog / Complete
  → Closing with /devaing-work instructions
```

### Start new phase
```
/devaing-phase "phase-name"
  → verify previous phase fully closed (all issues merged)
  → read CONTEXT.md + closed issues from previous phase
  → incremental discovery (abbreviated — no full grill-me for Phase 2+)
  → update CONTEXT.md with new learnings
  → define and approve epics for this phase       ← human validation
  → create milestones (GitHub mode)
  → extend prototype with new screens (living skeleton, prior screens untouched)
  → working mode choice: Progressive / Backlog / Complete (phase-scoped)
  → closing with /devaing-work instructions
```

### Build loop
```
human picks milestone
→ /devaing-work <milestone> or #N
    → detect mid-flight session (resume if found)
    → context budget check (warn if session already loaded)
    → if UI: ce-frontend-design (with prototype screen) + ce-work
    → if not UI: ce-work directly
    → merge → CONTEXT.md update → ADR if non-obvious decision
    → suggest fresh session for next slice
    → if last issue in milestone: QA prompt + /improve-codebase-architecture
```

### Add feature
```
/devaing-feature "description"
  → 4 scope questions (problem, user, out-of-scope, constraints)
  → evaluate milestone (existing or new)
  → generate issues directly
  → CONTEXT.md update
```

### Report bug
```
/devaing-bug "description"
  → read CONTEXT.md + investigate code
  → if cause obvious: structured issue with diagnosis
  → if cause not obvious: /diagnose first, then issue
  → assign milestone
  → CONTEXT.md update if new constraint found
```

## What devaing is NOT

- Not a replacement for Pocock in large teams
- Not a way to skip thinking (grill-me is mandatory and expensive — that's the investment)
- Not Jira (Jira is for human communication, outside the framework)
- Not a vibe coding wrapper (structure is intentional, not optional)
