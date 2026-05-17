# Strategy: devaing-init (and the devaing framework)

## What devaing is

A hyper-agile framework for building products with AI. Targets solo builders, dev pairs, and early-stage startups who want product fast without heavy process. Not Pocock (designed for large teams). Not vibe coding (no structure). The middle path.

**Core insight:** GitHub Issues is not bureaucracy — it's a token rationalization system. Issues let the user work granularly (one issue per session), share work with friends (parallel token consumption), and give agents enough context to execute without re-explanation.

## The seven skills

| Skill | Purpose |
|-------|---------|
| `/devaing-init` | Bootstrap: repo, CI, CONTEXT.md, `.devaing/skills/` portable layer, Phase 1 via phase-def. For existing projects: RE scan + grill-me + dev env validation + seeds scaffold. |
| `/devaing-phase-def` | Define a phase end-to-end: epics, prototype, review loop, issue generation. Generates seed migration issues for epics with reference data. |
| `/devaing-phase-revise` | Adjust scope, prototype, or business logic during implementation. Reads ship tags to mark new issues as post-ship additions. |
| `/devaing-work` | Implement GitHub issues on epic branches via sub-agent. Self-verify (tests + AC), optional adversarial review, auto-merge epic to main at close. Hotfix flow included. |
| `/devaing-ship` | Ship to prod: first deploy (new or adopt existing), incremental deploys from git diff, ordered checklist, git tagging, archive shipped phases to CONTEXT_ARCHIVE.md. |
| `/devaing-bug` | Bug in natural language → structured issue with diagnosis + regression test criteria → CONTEXT.md |
| `/devaing-status` | Snapshot: current phase, per-epic progress, next task, exact command to run next. |

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

### Epic branches + ownership lock
One branch per milestone (`epic/<slug>`). One person per epic — the first developer to claim an issue in the milestone becomes the owner. Lock is implemented via GitHub issue assignment: devaing-work assigns the issue at claim time and checks existing assignees before starting. If another user owns the epic, the developer is redirected to an available epic.

Parallelism happens between epics, not within them: Dev A on `epic/auth`, Dev B on `epic/billing`. This eliminates merge conflicts within the epic — only one person commits to the branch.

Branch lifecycle: created lazily when the first issue of the epic is claimed. Auto-merged to main when the last issue closes. Branch deleted after merge.

### Working mode choice
After the opening issue list, the user picks: One (single issue), All (all issues in the epic), Cascade (implement all epics in sequence), or Hotfix (off-backlog fix). Cascade repeats until zero open issues remain in the phase. Hotfix uses a separate `hotfix/<slug>` branch and auto-merges without issue tracking (retroactive issue optional).

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

### Sub-agent with fresh context (from GSD)
Each issue is implemented by a sub-agent spawned with a clean context. The parent skill passes a filtered CONTEXT.md (only `## Project`, `## Domain glossary`, `## Architecture`, `## Key constraints` — not Phases history) plus the full issue content. The sub-agent commits and reports back. This isolates context rot to the sub-agent, not the orchestrating session.

### Self-verification before closing
After the sub-agent commits, devaing-work runs the project's test suite (auto-detected: `npm test` / `pytest` / `cargo test`). If tests fail, the user chooses: fix now (spawn another sub-agent with the failure output), document in Known limitations, or revert the commit. Then it reads each `- [ ]` acceptance criterion from the issue and asks for a single y/n/partial confirmation before closing.

### Adversarial review (from HBX practice)
HBX pattern: after each implementation commit, a review pass constructs failure scenarios (not pattern-matching against known issues). devaing-work integrates this as an optional step: default `y` when closing the last issue in a milestone (before auto-merge to main), default `n` for intermediate issues. Uses `ce-adversarial-reviewer` on Claude Code; other environments use an inline adversarial prompt.

### GitHub Projects integration
Every devaing project gets a linked GitHub Project (created by devaing-init). Issues are added to the Project automatically when created. devaing-work moves cards to "In Progress" when work starts and "Done" when the issue closes. No `## Blocked by` entries — order within an epic is captured by issue number (phase-def creates issues in natural implementation order).

### CONTEXT_ARCHIVE.md for shipped phases
devaing-ship moves completed phase rows from `CONTEXT.md ## Phases` to `CONTEXT_ARCHIVE.md` after tagging a release. `## Architecture`, `## Domain glossary`, `## Key constraints`, and `## Known limitations` never move — they accumulate. This keeps the active CONTEXT.md lean across many phases while preserving history.

### Portability: thin adapter + body.md
Each skill is split into two files:
- `SKILL.md` — thin adapter (5-10 lines): reads `.devaing/skills/<name>.md` from the project, falls back to `body.md` in the same directory.
- `body.md` — portable body: full flow, no frontmatter, sub-agent invocation described tool-agnostically.

`devaing-init` copies the body.md files from the plugin dir to `.devaing/skills/` in each project, and writes `.devaing/AGENTS.md` so Codex, Aider, and Cursor can follow the same workflow. The `subagent_cli:` field in `.devaing.md` (default: `claude -p --model claude-sonnet-4-6`) lets the user swap models or tools for sub-agent invocations without touching the skill files.

### Production deployment strategy

Two DB environments: local dev + prod. No staging. No test users in prod.

Reference data (predefined messages, catalogs, configs) lives as versioned seed migrations with upsert. The `_seed_migrations` table tracks what ran, identical to how Prisma handles schema migrations. The seed runner compares files in repo vs. executed rows in the table.

**devaing-ship** is the single ship command regardless of trigger (phase complete, revise additions, hotfix). It derives everything it needs from git state and DB state — no other skill needs to feed it data, with one exception: devaing-work must keep `.env.example` updated when new env vars are added.

Ship tags (`ship/*`) are the deploy markers. The diff from the last ship tag tells devaing-ship exactly what changed. First deploys have no tag and branch into two cases: provision fresh prod, or adopt an existing prod (establish baseline without re-running anything already live).

The ceremony scales to scope: only code changed = one confirmation. Schema migrations or seeds involved = ordered checklist with DB snapshot first.

## Skills integrated (third-party, not modified)

- `grill-me` → domain discovery inside devaing-phase-def and devaing-init RE scan
- `prototype` → UI validation before issue generation inside devaing-phase-def
- `compound-engineering:ce-adversarial-reviewer` → adversarial review in devaing-work Step 3 (Claude Code only; other environments use inline prompt)
- `diagnose` → hard bugs in devaing-bug when cause is not obvious

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
  → working style questions (granularity, prototyper)
  → auth check + repo create/clone
  → GitHub Project created and linked to repo
  → triage labels, CI workflow, AGENTS.md, CONTEXT.md (blank template), .devaing.md
  → .devaing/skills/ created + body.md files copied (portable layer)
  → .devaing/AGENTS.md written (Codex/Aider/Cursor instructions)
  → seeds infrastructure scaffold (_seed_migrations table, seeds runner)
  → /devaing-phase-def called for Phase 1 (runs full grill-me + model upgrade suggestion)
```

**Existing project (code already present, no devaing setup):**
```
/devaing-init
  → semantic check: CONTEXT.md absent or template + code present
  → working style questions (granularity, prototyper)
  → RE scan: stack detection, structure, key files read
  → findings summary + validation questionnaire (users, business rules, constraints)
  → grill-me with RE context (business decisions, constraints, direction)
  → CONTEXT.md written from reality (not blank template)
  → contradictions (code vs. corrections) → needs-triage issues
  → auth check + repo create/clone
  → GitHub Project, triage labels, CI workflow, AGENTS.md, .devaing.md
  → .devaing/skills/ created + body.md files copied (portable layer)
  → dev env validation: .env check, DB connection, typecheck
  → seeds infrastructure scaffold (_seed_migrations table, seeds runner)
  → output: ready for /devaing-phase-def (Phase 2) or /devaing-ship
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
  → "looks good" → generate issues
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
    → choice: One / All / Cascade / Hotfix
    → Hotfix: describe fix → sub-agent via subagent_cli → optional retroactive issue
→ /devaing-work <milestone> or #N (Structured path)
    Step 1 — Claim:
        fetch open issues for milestone, show READY vs BLOCKED table
        user picks (or Cascade picks next unblocked)
        assign issue to self (epic ownership lock via GitHub assignment)
        create epic/<slug> branch lazily if first issue in milestone
    Step 2 — Implement:
        read DESIGN.md if exists (Stitch design system tokens)
        spawn sub-agent via subagent_cli with filtered CONTEXT.md
            (only ## Project, ## Domain glossary, ## Architecture, ## Key constraints)
        sub-agent commits directly to epic branch
    Step 3 — Verify and close:
        self-verification: detect test command (npm test / pytest / cargo test),
            run it, validate each AC from issue (y/n/partial)
            on failure: Fix now (spawn sub-agent with failure output) / Document / Revert
        adversarial review: default y if last issue in epic, default n otherwise
            spawn ce-adversarial-reviewer (or inline prompt for other LLMs)
            triage HIGH per-finding, MEDIUM/LOW as table → document in Known limitations
        CONTEXT.md update + .env.example if new env vars added
        push epic branch, close issue, move Project card to Done
    Closing checks:
        if last issue in epic: auto-merge epic branch to main, delete branch
        if last issue in phase: compress phase in CONTEXT.md
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
  → if phase-complete deploy:
      → mark phase Status = Complete in CONTEXT.md ## Phases
      → move phase row to CONTEXT_ARCHIVE.md (create if absent)
      → commit both files
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
