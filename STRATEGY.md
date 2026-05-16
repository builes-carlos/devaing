# Strategy: devaing-init (and the devaing framework)

## What devaing is

A hyper-agile framework for building products with AI. Targets solo builders, dev pairs, and early-stage startups who want product fast without heavy process. Not Pocock (designed for large teams). Not vibe coding (no structure). The middle path.

**Core insight:** GitHub Issues is not bureaucracy — it's a token rationalization system. Issues let the user work granularly (one issue per session), share work with friends (parallel token consumption), and give agents enough context to execute without re-explanation.

## The seven skills

| Skill | Purpose |
|-------|---------|
| `/devaing-init` | Bootstrap: repo, CI, CONTEXT.md, Phase 1 epics, prototype, issues. For existing projects: RE scan + grill-me + dev env validation + seeds scaffold. |
| `/devaing-phase-def` | Define a phase end-to-end: epics, prototype, review loop, issue generation. Generates seed migration issues for epics with reference data. |
| `/devaing-phase-revise` | Adjust scope, prototype, or business logic during implementation. Reads ship tags to mark new issues as post-ship additions. |
| `/devaing-work` | No arg → Structured (dependency-aware issue list) or Hotfix (describe + fix, no process). Updates .env.example when new env vars are added. |
| `/devaing-ship` | Ship to prod: first deploy (new or adopt existing), incremental deploys from git diff, ordered checklist, git tagging. |
| `/devaing-bug` | Bug in natural language → structured issue with diagnosis → CONTEXT.md |
| `/devaing-status` | Snapshot: current phase, per-epic progress, next unblocked task, and the exact command to run next. |

## Key design decisions

### No PRDs
to-prd eliminated entirely. PRDs are expensive intermediaries nobody reads. Issues with acceptance criteria are the spec. ADRs capture non-obvious decisions after implementation.

### init owns "what is this product", phase-def owns "what we build in this phase"
These two responsibilities are strictly separated. init is the only place that discovers or reverse-engineers the product. phase-def starts from CONTEXT.md as truth and only scopes the phase — it never re-asks what the project is.

For greenfield projects, init creates a blank CONTEXT.md and phase-def runs a full grill-me (the only time grill-me fires). For existing projects, init does a RE scan + validation questionnaire and writes CONTEXT.md from reality before setup even starts. phase-def then finds CONTEXT.md already populated and skips discovery entirely.

For existing projects, init also runs grill-me after the RE scan to capture business context (why it was built, decisions made, where it's going) — not just what the code shows.

This means the only human validations in the full flow are: RE findings confirmation + grill-me (existing projects) or grill-me (greenfield), epic list approval, and the prototype review loop.

### Milestones = epics
GitHub milestones group issues by epic. Human navigates by milestone, not flat list.

### CONTEXT.md is the single source of truth
Updated after every operation: devaing-work, devaing-bug, devaing-phase-revise. Never stale because it grows with the product.

To prevent context rot from accumulated slice-by-slice notes, CONTEXT.md is compressed at milestone close: verbose operational detail is replaced with a 3-line summary block (what was built, decisions made, known limitations introduced). ADRs and Known limitations entries are never removed — only deduplicated into their canonical sections.

### Known limitations section in CONTEXT.md (from HBX/senior-dev practice)
Distinct from ADRs (decisions made) and key constraints (non-negotiable limits). Captures problems we are aware of and consciously not fixing yet: what the problem is, why it's deferred, what would trigger the fix, and operational guidance for the current state. devaing-work prompts for this at close alongside the ADR question.

### Working mode choice
After discovery, the user picks how issues are created: Progressive (devaing-work creates slices as it goes, no GitHub issues at init time), Backlog (first unblocked slice per epic), or Complete (all issues for the current phase upfront). Scope is always bounded by the current phase — future phases are defined when their phase starts. The framework adapts to session style.

### Prototype as living skeleton
UI prototypes are not deleted after UX validation. They survive as navigation skeletons. Each devaing-work slice replaces one mock screen with real implementation. The rest stays intact as scaffolding for future slices. UX decisions persist in CONTEXT.md under `## UX conventions`.

Prototype screens must be stateless and presentational — no local state, no API calls, no hardcoded data beyond display fixtures. This constraint keeps each screen independently replaceable without touching adjacent screens.

### Phase definition loop
devaing-phase-def owns the full definition process and does not exit until issues are generated. After the prototype is built, it enters a review loop: the user can adjust screens, epics, or business logic inline, then re-review, as many times as needed. When they confirm "looks good," issues are generated and the definition closes. There is no need to re-run the command or jump to another skill during definition.

/devaing-phase-revise is blocked while the phase is being defined (no issues exist yet). It only becomes available once devaing-phase-def has closed.

### Prototyper selection
The tool that generates the prototype is configured per-project in `.devaing.md` as `prototyper: Claude | Stitch | Other MCP`. Set at init time.

- **Claude**: invokes the built-in `prototype` skill. No external accounts.
- **Stitch**: uses the Stitch MCP server (`https://stitch.googleapis.com/mcp`, configured in `~/.claude/.mcp.json`). Generates higher-quality visual screens. Exports `DESIGN.md` to the project root. Requires `STITCH_API_KEY` env var.
- **Other MCP**: any MCP server already configured. User provides tool name and a brief description of what it expects and returns.

### DESIGN.md as design system bridge
When Stitch (or any external tool) generates the prototype, it exports a `DESIGN.md` file containing the design system: color palette, typography, spacing, and component patterns. devaing-work reads this file before implementing any UI slice and uses its tokens directly. This ensures the implemented code matches the approved visual design without inventing a parallel system.

### Phase state detection matrix
devaing-phase-def detects setup state at every invocation, enabling safe re-entry after interrupted sessions:

| UX conventions in CONTEXT.md | Issues exist | State | Action |
|---|---|---|---|
| No | No | Interrupted before prototype | Resume at prototype step |
| Yes | No | Prototype built, review in progress | Resume review loop |
| — | Yes | Definition closed — active phase | Block |

### Context rot awareness (from GSD)
Context quality degrades predictably: peak at 0-30%, rushes at 50%+, hallucinates at 70%+. devaing-work addresses this in two places: (1) warns before dispatching to ce-work if the session is already loaded, (2) suggests a fresh session after each closed slice.

### Mid-flight session recovery (from gstack)
If a devaing-work session dies mid-slice (context full, crash, closed window), the next invocation detects the orphaned work and offers to resume. Finds open issue with existing branch matching the milestone slug.

### GitHub Projects integration
Every devaing project gets a linked GitHub Project (created by devaing-init). Issues are added to the Project automatically when created. devaing-work moves cards to "In Progress" when work starts and "Done" when the issue closes. Issue dependencies are registered via the GitHub GraphQL API (GA August 2025) so blockers are visible natively in the issue sidebar and the Project board. The `## Blocked by` text in the issue body remains as a readable fallback.

### Production deployment strategy

Two DB environments: local dev + prod. No staging. No test users in prod.

Reference data (predefined messages, catalogs, configs) lives as versioned seed migrations with upsert. The `_seed_migrations` table tracks what ran, identical to how Prisma handles schema migrations. The seed runner compares files in repo vs. executed rows in the table.

**devaing-ship** is the single ship command regardless of trigger (phase complete, revise additions, hotfix). It derives everything it needs from git state and DB state — no other skill needs to feed it data, with one exception: devaing-work must keep `.env.example` updated when new env vars are added.

Ship tags (`ship/*`) are the deploy markers. The diff from the last ship tag tells devaing-ship exactly what changed. First deploys have no tag and branch into two cases: provision fresh prod, or adopt an existing prod (establish baseline without re-running anything already live).

The ceremony scales to scope: only code changed = one confirmation. Schema migrations or seeds involved = ordered checklist with DB snapshot first.

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

### Initial setup

**Greenfield (no prior code):**
```
/devaing-init
  → model upgrade suggestion (discovery is expensive)
  → working style questions (granularity, prototyper)
  → auth check + repo create/clone
  → GitHub Project created and linked to repo
  → triage labels, CI workflow, AGENTS.md, CONTEXT.md (blank template), .devaing.md
  → seeds infrastructure scaffold (_seed_migrations table, seeds runner)
  → dev env validation: confirm scaffolded env runs
  → model downgrade suggestion
  → /devaing-phase-def called for Phase 1 (runs full grill-me)
```

**Existing project (code already present, no devaing setup):**
```
/devaing-init
  → semantic check: CONTEXT.md absent or template + code present
  → model upgrade suggestion (discovery is expensive)
  → working style questions (granularity, prototyper)
  → RE scan: stack detection, structure, key files read
  → findings summary + validation questionnaire (users, business rules, constraints)
  → grill-me with RE context (business decisions, constraints, direction)
  → CONTEXT.md written from reality (not blank template)
  → contradictions (code vs. corrections) → needs-triage issues
  → auth check + repo create/clone
  → GitHub Project, triage labels, CI workflow, AGENTS.md, .devaing.md
  → dev env validation: confirm local env runs (start command, DB, .env)
  → seeds infrastructure scaffold (_seed_migrations table, seeds runner)
  → model downgrade suggestion
  → /devaing-phase-def called for Phase 1 (skips grill-me, CONTEXT.md already populated)
```

### Define a phase (new or resume)
```
/devaing-phase-def   (no argument — reads state from CONTEXT.md)
  → detect setup state (interrupted / review-in-progress / active / new)
  → if new: verify previous phase closed, ask phase name
  → discovery (conditional):
      Phase 1 + CONTEXT.md populated → brief "anything to correct?" only
      Phase 1 + CONTEXT.md absent/template → full grill-me
      Phase 2+ → incremental interview (what changed since last phase)
  → update CONTEXT.md with learnings
  → define and approve epic list              ← human validation
  → create GitHub milestones
  → generate prototype via <prototyper> (Claude / Stitch / Other MCP)
      if Stitch: export DESIGN.md to project root
  → review loop (inline):
      adjust screens / epics / business logic as many times as needed
      ← human validation (iterative)
  → "looks good" → generate issues → register dependencies via GitHub API
  → add all issues to GitHub Project
  → definition closed — /devaing-phase-revise now available
```

### Check project status
```
/devaing-status
  → read CONTEXT.md + .devaing.md + GitHub issues
  → output: phase, per-epic progress, next unblocked task
  → output: exact command to run next
```

### Build loop
```
human picks task (or uses /devaing-status to find it)
→ /devaing-work (no arg):
    → choice: Structured or Hotfix
    → Structured: fetch open issues, classify READY vs BLOCKED,
        show dependency table, user picks
    → Hotfix: describe what to fix → ce-work → optional retroactive issue
→ /devaing-work <milestone> or #N (Structured path)
    → detect mid-flight session (resume if found)
    → context budget check (warn if session already loaded)
    → read DESIGN.md if exists (Stitch design system tokens)
    → if UI: ce-frontend-design (with prototype screen + DESIGN.md) + ce-work
    → if not UI: ce-work directly
    → merge → CONTEXT.md update + .env.example if new vars added
    → ADR if non-obvious decision
    → suggest fresh session for next slice
    → if last issue in milestone: compress milestone in CONTEXT.md
    → if last issue in phase: QA prompt + /improve-codebase-architecture
```

### Ship to prod
```
/devaing-ship
  → read CONTEXT.md + .devaing.md for stack and deploy target
  → check last ship tag (git tag --list "ship/*")
  → if no tag (first deploy):
      → prod doesn't exist: provision DB + deploy target + env vars, validate
      → prod exists: adopt baseline (create _seed_migrations, mark existing
          seeds as executed, tag ship/baseline)
  → if tag exists (incremental):
      → diff from last tag: commits, schema migrations, seed files, .env.example
      → if only code: quick deploy
      → if migrations/seeds/env vars: full ordered checklist
  → execute: DB snapshot → schema migrations → seed migrations → env vars → deploy code → verify
  → tag release (ship/phase-N, ship/hotfix-YYYYMMDD, etc.)
  → update CONTEXT.md ## Phases if phase-complete deploy
```

### Add feature area
```
/devaing-phase-revise → "New area"
  → reads ship tags (what's already in prod)
  → 4 scope questions (problem, user, out-of-scope, constraints)
  → evaluate milestone (existing or new)
  → generate issues marked as post-ship additions
  → CONTEXT.md update
  → closing: reminder to /devaing-ship when implemented in dev
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
