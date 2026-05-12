---
name: devaing-init
description: Initialize a new project with the devaing framework. Asks working style upfront (granularity + GitHub vs Local), runs domain discovery with grill-me, defines epics, and generates slices as GitHub issues or BACKLOG.md. Idempotent — safe to re-run. Invoked with /devaing-init <project-name> or /devaing-init (uses current folder name).
---

# devaing-init

Initialize a new project with the full devaing setup. Every step checks whether the artifact already exists before acting — safe to re-run on any project state.

## Language override

All output from this skill — questions, inline messages, report tables, generated file content, and code comments — MUST be in English. This overrides any global language setting (including "Respond in Spanish").

## Opening — Welcome message

Resolve the project name first (read argument or `basename "$PWD"`), then output this welcome before asking anything:

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-init: <name>                                       ║
╚══════════════════════════════════════════════════════════════╝

Let's set up your project so it's ready to build, step by step.

Here's what's going to happen:

  1. Two quick questions about how you want to work
  2. Set up the repo and project files
  3. Interview you about your project (what it does, who it's for)
  4. Define the main work areas together
  5. Generate the concrete tasks for each area

When we're done, your project is ready to build — one task at a time.
```

## Step 0 — Resolve name, working style, and working directory

### Name resolution

Already done in the Opening step above.

### Working style questions

```
Question 1 of 2 — How detailed should the tasks be?
(Technically: slice / user story granularity)

  1. Broad    — 2-4 tasks per area. Each task covers a lot of ground.
                Move fast. Great for MVPs and exploring new ideas.

  2. Balanced — 3-6 tasks per area. One task = one concrete thing
                a user can do. The natural middle ground.

  3. Detailed — 6-12 tasks per area. Every edge case has its own task.
                For projects where bugs have real consequences.
```

Wait for response. Store as `<granularity>` (Broad/Balanced/Detailed).

```
Question 2 of 2 — Where do you want to track the task list?

  1. Local file  — A BACKLOG.md file in your project. No external accounts.
                   Start immediately.

  2. GitHub      — Issues and milestones on GitHub. Visibility, collaboration,
                   CI integration.
```

Wait for response. Store as `<tracking>` (Local/GitHub).

### Auth check (GitHub only)

If `<tracking>` is **Local**: skip this section entirely.

If `<tracking>` is **GitHub**:

```bash
gh auth status 2>/dev/null
```

If not authenticated, stop: "Run `gh auth login` before continuing."

```bash
gh api user --jq '.login'
```

Store result as `<owner>`.

### State detection matrix (GitHub only)

If `<tracking>` is **Local**: ensure we are inside the project directory. If not, `cd <name>` or create the directory.

If `<tracking>` is **GitHub**:

```bash
test -d <name> && echo "local_exists"
basename "$PWD"
gh repo view <owner>/<name> --json name 2>/dev/null && echo "remote_exists"
```

| Local dir exists | Is current dir | Remote exists | Action |
|-----------------|----------------|---------------|--------|
| Yes | Yes | — | Work here, skip repo creation |
| Yes | No | — | `cd <name>`, skip repo creation |
| No | — | Yes | `gh repo clone <owner>/<name>`, then `cd <name>` |
| No | — | No | `gh repo create <name> --private --clone`, then `cd <name>` |

All subsequent steps run from inside `<name>/`.

## Step 1 — Detect current branch

If `<tracking>` is **Local**: skip. Set `<branch>` to empty.

If `<tracking>` is **GitHub**:

```bash
git branch --show-current
```

Store as `<branch>`. Default to `master` if empty.

## Step 2 — AGENTS.md

If `AGENTS.md` exists, check whether the devaing execution section is present:

```bash
grep -q "devaing-work\|\.devaing\.md" AGENTS.md && echo "devaing_present" || echo "devaing_missing"
```

If `devaing_missing`: append the devaing sections below. If absent entirely: create from scratch with the full content below.

```markdown
## Agent skills

### Issue tracker

Issues live in GitHub Issues for this repo. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical labels (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### Execution

Full workflow spec: `.devaing.md` (readable by any agent or runtime).

Each issue is implemented in an isolated worktree. Never implement multiple issues in the same working tree simultaneously.

Claude Code: `/devaing-work #N`

### Review

Before opening a PR, run a code review in a fresh context (not the implementation context).

Claude Code: `/ce-code-review` or `/ultrareview`

### QA

After each PR merges, human QA verifies product behavior. Findings become new GitHub issues.

Claude Code: `/devaing-phase-revise` (adjust phase), `/devaing-bug "description"`, `/devaing-feature "description"`

### CONTEXT.md

After each issue closes, evaluate whether domain knowledge, architecture, constraints, or glossary changed. Update `CONTEXT.md` accordingly and commit. It is the single source of truth — keep it alive.
```

When appending to an existing file, add only the sections from `### Execution` onward.

## Step 3 — docs/agents/ files

Check each file independently. Only write files that do not already exist.

**`docs/agents/issue-tracker.md`** (skip if exists):

```markdown
# Issue tracker: GitHub

Issues for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..." --milestone "..."`
- **Read an issue**: `gh issue view <number> --comments`
- **List issues**: `gh issue list --state open --json number,title,body,labels,milestone`
- **Comment**: `gh issue comment <number> --body "..."`
- **Labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

## When a skill says "publish to the issue tracker"

Create a GitHub issue assigned to the relevant milestone.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.
```

**`docs/agents/triage-labels.md`** (skip if exists):

```markdown
# Triage Labels

| Label | Meaning |
|-------|---------|
| `needs-triage` | Needs evaluation |
| `needs-info` | Waiting on reporter |
| `ready-for-agent` | Fully specified, agent can take it |
| `ready-for-human` | Requires human decision |
| `wontfix` | Will not be actioned |
```

**`docs/agents/domain.md`** (skip if exists):

```markdown
# Domain Docs

Before exploring the codebase, read:

- `CONTEXT.md` at the repo root
- `docs/adr/` — ADRs that touch the area you're working in

Use the vocabulary from `CONTEXT.md`. Flag any contradiction with existing ADRs instead of silently overriding.
```

## Step 4 — GitHub labels

If `<tracking>` is **Local**: skip entirely.

If `<tracking>` is **GitHub** — run unconditionally (`--force` makes each call idempotent):

```bash
gh label create "needs-triage"    --color "e4e669" --description "Needs evaluation" --force
gh label create "needs-info"      --color "0075ca" --description "Waiting on reporter" --force
gh label create "ready-for-agent" --color "d73a4a" --description "Agent can take this" --force
gh label create "ready-for-human" --color "008672" --description "Requires human decision" --force
gh label create "wontfix"         --color "ffffff" --description "Will not be actioned" --force
```

## Step 5 — Compound Engineering plugin

```bash
claude plugin list | grep "compound-engineering"
```

If already installed: skip.

Otherwise attempt in order:
1. `claude plugin install compound-engineering`
2. `claude plugin marketplace add EveryInc/compound-engineering-plugin && claude plugin install compound-engineering`
3. If still failing: note "manual requerido" in the final report and continue.

## Step 6 — CI workflow

If `<tracking>` is **Local**: skip entirely.

If `<tracking>` is **GitHub**: skip if `.github/workflows/ci.yml` already exists.

Otherwise, infer the stack from the project root (look for `package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, `go.mod`) and create the appropriate workflow replacing `<branch>`:

**Node.js / TypeScript** (`package.json` present):

```yaml
name: CI

on:
  push:
    branches: [<branch>]
  pull_request:
    branches: [<branch>]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run typecheck
      - run: npm run lint
      - run: npm test
```

**Python** (`requirements.txt` or `pyproject.toml` present, no `package.json`):

```yaml
name: CI

on:
  push:
    branches: [<branch>]
  pull_request:
    branches: [<branch>]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest
```

**Unknown stack** — skip CI creation, note "ci.yml pendiente (stack no detectado)" in the final report.

## Step 7 — CONTEXT.md

Skip if exists. Otherwise write:

```markdown
# Context

## Project

> One sentence describing what this project does and for whom.

## Domain glossary

| Term | Definition |
|------|------------|
|      |            |

## Architecture

> High-level description of the system: main components and how they interact.

## Key constraints

> Technical, legal, or business constraints that shape decisions here.

## Known limitations

> Problems we are aware of and consciously not fixing yet.
> Format: what the problem is | why it's deferred | what would trigger the fix | operational guidance for the current state.

## Phases

| Phase | Name | Status | Epics |
|-------|------|--------|-------|

## Next phase backlog

> Epics identified but deferred to future phases.
> Format: Phase N — Epic name — one-line description
```

## Step 7b — .devaing.md

Skip if `.devaing.md` already exists.

Otherwise write `.devaing.md` at the project root:

```markdown
# devaing workflow

Runtime-agnostic spec. For Claude Code, use the `/devaing-*` skills directly.

## devaing-work — Implement a slice

Takes a GitHub issue (`#N`) or milestone name and implements the next vertical slice end-to-end.

1. **Mid-flight check**: look for an existing branch matching this milestone with unmerged commits. If found, offer to resume instead of starting over.
2. **Resolve the issue**: read what to build, acceptance criteria, and blockers. If given a milestone name, determine the next slice from CONTEXT.md and closed issues, then create the issue.
3. **Context budget**: if this session has already processed prior slices, recommend a fresh session.
4. **Implement**: if UI issue, implement the visual layer first (replace the matching prototype screen if one exists, leave others as mocks). Then backend + tests.
5. **Update CONTEXT.md**: after merge, add new domain terms, architecture changes, known limitations.
6. **Close the issue** with a reference to the PR.

## devaing-feature — Add a feature

1. Understand the request in one sentence.
2. Identify which epic/milestone it belongs to.
3. Verify it does not duplicate an existing open issue.
4. Create the issue: what to build, acceptance criteria, blockers.
5. Assign to the correct milestone with label `ready-for-agent` or `ready-for-human`.

## devaing-bug — Report and fix a bug

1. Capture: what happened, what was expected, how to reproduce.
2. Create the issue with reproduction steps and expected behavior.
3. Assign to the milestone of the affected epic.
4. If the fix is straightforward, implement immediately in an isolated worktree and open a PR.
5. If the bug reveals an undocumented constraint, add it to `CONTEXT.md ## Known limitations`.

## devaing-init — Initialize a project (one-time setup)

1. Creates or clones the GitHub repo.
2. Sets up AGENTS.md, .devaing.md, docs/agents/, CI, triage labels.
3. Creates CONTEXT.md base structure.
4. Kicks off Phase 1 by calling /devaing-phase.

## devaing-phase — Kick off a phase

1. Verifies previous phase is closed (no open issues).
2. Asks phase name and granularity.
3. Runs discovery: full grill-me for Phase 1, incremental interview for Phase 2+.
4. Defines epics for this phase, annotates next-phase backlog.
5. Builds or extends the prototype (living skeleton — never deleted).
6. Generates all issues calibrated to granularity.

## devaing-phase-revise — Adjust the current phase

1. Verifies a phase is open.
2. Adjusts scope (add/remove/modify issues), prototype, or business logic.
3. Updates CONTEXT.md and commits.
```

## Step 8 — Commit and push

```bash
git status --porcelain
```

If empty: skip, note "no changes".

If `<tracking>` is **Local**: skip entirely.

If `<tracking>` is **GitHub**:

```bash
git add .
git commit -m "chore: devaing project setup

- AGENTS.md: devaing workflow, execution and review conventions
- .devaing.md: runtime-agnostic skill spec (portable to any agent)
- docs/agents/: issue-tracker, triage-labels, domain docs
- .github/workflows/ci.yml: CI pipeline
- CONTEXT.md: base structure"
git push -u origin <branch>
```

## Final report

| Step | Status |
|------|--------|
| Repo | created / cloned / already existed / local |
| AGENTS.md | created / updated / already existed |
| docs/agents/ | created / already existed |
| Labels | applied / N/A (local) |
| Compound Engineering | installed / already installed / manual required |
| ci.yml | created / already existed |
| CONTEXT.md | created / already existed |
| .devaing.md | created / already existed |
| Commit | N files / no changes |

Then output one line: `✓ <name> ready.`

## Step 8b — Phase state detection

Check if this is a re-run on a project that already has a phase started:

```bash
grep -q "In Progress" CONTEXT.md && echo "phase_open" || echo "no_open_phase"
```

| State | Action |
|-------|--------|
| `## Phases` absent or empty | Fresh project — call `/devaing-phase` for Phase 1 |
| Phase `In Progress`, 0 issues | Phase kicked off but nothing built — show available skills |
| Phase `In Progress`, N issues open | Active phase — show available skills, skip `/devaing-phase` call |
| All phases `Complete` | Show that `/devaing-phase` is available for a new phase |

If a phase is already `In Progress`, output one line noting state and skip to Closing.

## Step 8c — Kick off Phase 1

Show this message so the user learns the command for future phases:

```
Starting Phase 1 — calling /devaing-phase.

For future phases, you will run this yourself:
  /devaing-phase "<phase-name>"
```

Then invoke `/devaing-phase`. Pass `<granularity>` and `<tracking>` from Step 0 so devaing-phase skips its own Step 1. The closing message comes from devaing-phase.

## Closing (re-run only — active phase detected)

Only shown when Step 8b detects a phase already in progress:

```
╔══════════════════════════════════════════════════════════════╗
║  <name> — setup already complete.                           ║
╚══════════════════════════════════════════════════════════════╝

Phase "<phase-name>" is open.

Available now:

  /devaing-phase-revise     Adjust scope, prototype, or business logic
  /devaing-work #N          Implement a task
  /devaing-bug              Report something broken
  /devaing-feature          Add something not in the current plan

Not available yet:

  /devaing-phase            Blocked — current phase has open issues.
```
