# devaing

A hyper-agile framework for building products with AI. Six Claude Code skills that take a project from blank repo to shipped features, one vertical slice at a time.

Targets solo builders, dev pairs, and early-stage startups who want product fast without heavy process. Not Pocock (designed for large teams). Not vibe coding (no structure). The middle path.

---

## Core insight

GitHub Issues is not bureaucracy — it is a token rationalization system. Each issue is a self-contained unit of work with enough context for an agent to execute without re-explanation. This lets you:

- Work granularly: one issue per session, fresh context every time
- Share work: multiple agents consume issues in parallel
- Maintain quality: acceptance criteria live where the work is tracked

---

## The framework at a glance

| Command | When to run | What it does |
|---------|-------------|--------------|
| `/devaing-init` | Once per project | Creates repo, CI, GitHub Project, AGENTS.md, CONTEXT.md. Kicks off Phase 1. |
| `/devaing-status` | Anytime | Current phase, per-epic progress, next unblocked task, exact command to run. |
| `/devaing-phase-def` | Start of each phase | Full definition loop: discovery, epics, prototype, review, issue generation. |
| `/devaing-phase-revise` | During implementation | Adjust scope, prototype, or business logic. Add a net-new feature area. |
| `/devaing-work` | Every build session | Implement the next task end-to-end. Shows dependency list if run with no argument. |
| `/devaing-bug "..."` | When something breaks | Converts a plain-language description into a structured GitHub issue with diagnosis. |

---

## Prerequisites

**1. Claude Code**

Download from [claude.ai/code](https://claude.ai/code). Requires a Pro or Team subscription.

**2. GitHub CLI**

```bash
# Mac
brew install gh

# Windows
winget install GitHub.cli
```

Then authenticate:

```bash
gh auth login
```

**3. Compound Engineering plugin**

Provides `ce-work` (implementation engine) and `ce-frontend-design` (UI quality layer), which devaing-work delegates to.

```bash
claude plugin install compound-engineering
```

If that fails (plugin marketplace not yet configured):

```bash
claude plugin marketplace add EveryInc/compound-engineering-plugin
claude plugin install compound-engineering
```

---

## Installation

```bash
git clone https://github.com/builes-carlos/devaing.git
cd devaing
bash install.sh
```

Then restart Claude Code. The six `/devaing-*` commands will be available immediately.

### What the script does

Copies each `skills/devaing-*/SKILL.md` into `~/.claude/skills/`. Claude Code loads skill files from that directory at session start. No build step, no dependencies.

---

## Typical session flow

### Starting a new project

```
/devaing-init my-project
```

This runs once. It creates or clones the repo, sets up AGENTS.md and CONTEXT.md, creates a GitHub Project, installs CI, and immediately calls `/devaing-phase-def` to kick off Phase 1.

### Defining a phase

```
/devaing-phase-def
```

Runs a full discovery session (deep interview for Phase 1, targeted questions for Phase 2+), proposes epics for approval, builds a prototype, and enters a review loop. The review loop runs as many times as needed — adjust screens, epics, or business logic inline. When you confirm "looks good," it generates all issues and registers dependencies in GitHub. The command does not close until issues are created.

### Checking where you stand

```
/devaing-status
```

Reads CONTEXT.md and GitHub Issues and shows: current phase, progress per epic, the next unblocked task, and the exact command to run next. Use this after returning to a project or before starting a session.

### Building

```
/devaing-work
```

With no argument, fetches all open issues, classifies them as READY or BLOCKED based on `## Blocked by` in each issue body, and presents a grouped list. You choose how many to implement:

1. **One** — pick a specific issue number
2. **All ready now** — implement all currently unblocked issues in sequence
3. **Cascade** — implement READY issues, automatically re-evaluate what's now unblocked after each batch, repeat until the phase is empty or a batch makes no progress

For a single issue:

```
/devaing-work #12
```

For a milestone by name:

```
/devaing-work "User Auth"
```

What happens per issue:

1. Mid-flight check: looks for an existing branch with unmerged commits (session recovery)
2. Context budget check: warns if the current session is already loaded
3. Reads DESIGN.md for design tokens if it exists
4. Routes to `ce-frontend-design` first for UI issues (then `ce-work` for backend/tests), or directly to `ce-work` for non-UI issues
5. After merge: updates CONTEXT.md with new domain knowledge, asks about ADRs and known limitations
6. Closes the issue, moves the GitHub Project card to Done
7. If this was the last issue in a milestone: compresses that milestone's notes in CONTEXT.md
8. If this was the last issue in the phase: prompts for QA and architecture review

### Reporting a bug

```
/devaing-bug "the user list shows deleted accounts"
```

Reads CONTEXT.md, investigates the relevant code, identifies the probable cause, and creates a structured GitHub issue with observed behavior, expected behavior, root cause, proposed fix, and acceptance criteria. If the cause is not obvious, runs `/diagnose` first.

### Adjusting scope mid-phase

```
/devaing-phase-revise
```

Available once a phase has issues. Options: correct existing issues, adjust the prototype, update business logic, or add a net-new feature area (triggers a focused 4-question discovery session and generates new issues directly).

---

## CONTEXT.md: the living document

Every operation that changes what is built updates CONTEXT.md. It is the single source of truth that agents read before working and that you read to understand the current state of the product.

Sections:

| Section | Contents |
|---------|----------|
| `## Project` | One-sentence description |
| `## Domain glossary` | Terms with definitions, updated as new concepts emerge |
| `## Architecture` | Components and how they interact, updated as structure changes |
| `## Key constraints` | Non-negotiable limits (technical, legal, business) |
| `## Known limitations` | Problems consciously deferred: what, why, what would trigger the fix, operational guidance |
| `## UX conventions` | Design decisions from prototype review: layout patterns, interaction models, component rules |
| `## Phases` | Status table: phase number, name, status (In Progress / Complete), epics |
| `## Next phase backlog` | Epics identified but deferred to future phases |

### Context compression

When a milestone closes, its slice-by-slice notes are replaced with a 3-line summary block:
- What was built (interfaces exposed, components added)
- Decisions (links to ADRs, or one-line summary)
- Known limitations introduced (or "none")

This prevents context rot as the document grows across many milestones.

---

## Prototype as living skeleton

When a phase is defined, a prototype is built for each epic that has UI. The prototype is not deleted after the review loop. It survives as a navigation skeleton: mock screens are replaced progressively by `/devaing-work` slices. All other screens stay intact as scaffolding.

Prototype screens must be stateless and presentational: no local state, no API calls, no hardcoded data beyond display fixtures. This keeps each screen independently replaceable without touching adjacent screens.

### Prototyper options

Set in `.devaing.md` as `prototyper: Claude | Stitch | Other MCP`:

| Option | Description |
|--------|-------------|
| Claude | Uses the built-in `prototype` skill. No external accounts needed. |
| Stitch | Google Stitch via MCP (`https://stitch.googleapis.com/mcp`). Higher visual quality. Exports `DESIGN.md` to the project root. Requires `STITCH_API_KEY` in `~/.claude/settings.json`. |
| Other MCP | Any MCP tool already configured. Provide the tool name and a brief description of what it expects and returns. |

When Stitch is used, `DESIGN.md` contains the full design system (colors, typography, spacing, component patterns). `/devaing-work` reads this before implementing any UI slice to ensure the code matches the approved visual design.

---

## Issue format

Every issue has three required sections:

```markdown
## What to build

<end-to-end behavior, not layer-by-layer. No file paths.>

## Acceptance criteria

- [ ] <criterion>

## Blocked by

<#N or "None - can start immediately">
```

The `## Blocked by` section is what `/devaing-work` and `/devaing-status` use to classify issues as READY or BLOCKED. A task is READY when no referenced issue numbers are still open.

Dependencies are also registered via the GitHub Issues native dependency API so blockers are visible in the issue sidebar and the GitHub Project board.

---

## Phase state detection

`/devaing-phase-def` detects the current setup state at every invocation, enabling safe re-entry after interrupted sessions:

| UX conventions in CONTEXT.md | Open issues exist | State | Action |
|---|---|---|---|
| No | No | Interrupted before prototype | Resume at prototype step |
| Yes | No | Prototype built, review in progress | Resume review loop |
| — | Yes | Definition closed — active phase | Block, show available commands |

---

## Project file reference

| File | Purpose |
|------|---------|
| `CONTEXT.md` | Single source of truth for domain knowledge, architecture, constraints, and phase state |
| `.devaing.md` | Per-project config: tracking system, granularity, prototyper, GitHub Project number |
| `AGENTS.md` | Agent execution conventions for this repo (issue tracker, labels, domain docs, review rules) |
| `DESIGN.md` | Design system exported by Stitch (colors, typography, spacing, components). Read by devaing-work before UI implementation. |
| `docs/adr/` | Architecture Decision Records, created by devaing-work when non-obvious decisions are made |
| `docs/agents/` | Supporting docs for agents: issue-tracker.md, triage-labels.md, domain.md |
| `.github/workflows/ci.yml` | CI pipeline created by devaing-init based on detected stack |

---

## External skill dependencies

devaing integrates these third-party skills without modifying them:

| Skill | Source | Used by | Purpose |
|-------|--------|---------|---------|
| `ce-work` | Compound Engineering plugin | `devaing-work` | Full implementation engine: branch, TDD, commits, PR, code review, CI, merge |
| `ce-frontend-design` | Compound Engineering plugin | `devaing-work` | UI implementation with design quality: detects design system, visual thesis, screenshot verification |
| `grill-me` | Compound Engineering plugin | `devaing-phase-def` | Deep discovery interview for Phase 1 |
| `prototype` | Claude Code built-in | `devaing-phase-def` | Stateless mock screens for UX validation |
| `diagnose` | Claude Code built-in | `devaing-bug` | Root cause analysis for bugs where the cause is not obvious |
| `improve-codebase-architecture` | Claude Code built-in | `devaing-work` | Suggested at phase close (every 2-3 milestones) |

---

## Development toolkit

The `scripts/` directory contains tools for validating and improving the trigger descriptions of any Claude Code skill. These are useful when modifying the devaing skills or building new ones.

### Validate a skill

Checks frontmatter: required fields, allowed fields, kebab-case name, max 64 chars name, max 1024 chars description.

```bash
python -m scripts.quick_validate skills/<skill-name>
```

### Package a skill

Produces a zip archive named `<skill-name>.skill`. Excludes `evals/`, `__pycache__`, `*.pyc`, `.DS_Store`. Runs validation before packaging.

```bash
python -m scripts.package_skill skills/<skill-name>
python -m scripts.package_skill skills/<skill-name> ./dist
```

### Run a trigger eval

Tests whether Claude correctly decides to invoke (or not invoke) a skill for a set of queries.

```bash
python -m scripts.run_eval \
  --eval-set path/to/eval.json \
  --skill-path skills/<skill-name> \
  --verbose
```

Eval set format:

```json
[
  {"query": "I want to start implementing the next task", "should_trigger": true},
  {"query": "Can you explain what a phase is?", "should_trigger": false}
]
```

### Run the optimize loop

Iteratively improves the skill description to maximize trigger accuracy. Uses a train/holdout split. Opens a live HTML report in the browser.

```bash
python -m scripts.run_loop \
  --eval-set path/to/eval.json \
  --skill-path skills/<skill-name> \
  --model claude-opus-4-7 \
  --verbose
```

Key flags: `--max-iterations 5`, `--runs-per-query 3`, `--holdout 0.4`, `--results-dir ./results`

### Aggregate benchmark results

Reads `grading.json` files from `eval-N/with_skill/run-N/` and `eval-N/without_skill/run-N/` subdirectories. Writes `benchmark.json` and `benchmark.md`.

```bash
python -m scripts.aggregate_benchmark <benchmark_dir>
```

---

## Design decisions

**No PRDs.** PRDs are expensive intermediaries nobody reads. Issues with acceptance criteria are the spec. ADRs capture non-obvious decisions after implementation, when the actual tradeoffs are known.

**No quiz loops during execution.** Only two human validations in the setup flow: the discovery interview and the epic list approval. Everything else the agent executes without asking.

**Milestones are epics.** GitHub milestones group issues by epic. You navigate by milestone, not by flat issue list.

**Phases scope what gets built.** Each phase runs a full discovery cycle before generating issues. Future phases are defined when their phase starts, not upfront. This prevents speculative backlog that becomes stale before it's worked.

**Context budget is explicit.** Context quality degrades predictably: peak at 0-30%, the model rushes at 50%, hallucinates at 70%. devaing-work warns before dispatching to ce-work if the session is already loaded and suggests a fresh session after each closed slice.

**Session recovery.** If a devaing-work session dies mid-slice (context full, crash, closed window), the next invocation detects the orphaned branch and offers to resume instead of starting over.

---

## What devaing is NOT

- Not a replacement for Pocock or Compound Engineering in large teams
- Not a way to skip thinking (the discovery interview is mandatory and expensive — that is the investment)
- Not Jira (Jira is for human communication, outside the framework)
- Not vibe coding (structure is intentional, not optional)
