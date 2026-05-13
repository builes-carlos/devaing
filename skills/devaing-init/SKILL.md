---
name: devaing-init
description: Initialize a new devaing project OR show current status if already initialized. Reads CONTEXT.md first to detect existing setup before doing anything else. Use when starting a new project or re-running setup. Invoked with /devaing-init <project-name> or /devaing-init (uses current folder name).
---

# devaing-init

**Execute these steps in order. Do not skip or reorder.**

**Step A.** Use the Read tool to read `CONTEXT.md`. Do not output any text yet.

**Step B.** Look at the `## Phases` table in what you just read.
- If the table has at least one data row (a row with a phase name): go to **Step C**.
- If the file does not exist or the table has no data rows: go to **Step D**.

**Step C — Already initialized.** Do the following, then stop:

1. Run `gh issue list --state open --json number,title,milestone --jq '.[] | "#\(.number) [\(.milestone.title)] \(.title)"'` to get open issues grouped by milestone.
2. Output the message below. Do not continue past this point.

```
╔══════════════════════════════════════════════════════════════╗
║  <name> — Phase "<phase-name>" in progress                  ║
╚══════════════════════════════════════════════════════════════╝

Open tasks:

  #N  [<milestone>] <title>
  #N  [<milestone>] <title>
  ...

To implement the next task:

  /devaing-work #N

To see dependencies between tasks:

  gh issue list --state open --json number,title,body,milestone

Other commands:

  /devaing-phase-revise     Adjust scope, prototype, or business logic
  /devaing-bug "..."        Report something broken
  /devaing-phase-revise     Add something not in the current plan (New area)
```

**Step D — Fresh project.** Resolve the project name (argument or `basename "$PWD"`). Output the welcome message below, then continue to Step 0:

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-init: <name>                                       ║
╚══════════════════════════════════════════════════════════════╝

Let's set up your project so it's ready to build, step by step.

Here's what's going to happen:

  1. Set up the repo and project files
  2. Interview you about your project (what it does, who it's for)
  3. Define the main work areas together
  4. Generate the concrete tasks for each area

When we're done, your project is ready to build — one task at a time.
```

## Step 0 — Working style

```
Question 1 of 2 — How detailed should the tasks be?

  1. Broad    — 2-4 tasks per area. Move fast. Great for MVPs.
  2. Balanced — 3-6 tasks per area. One task = one concrete user action.
  3. Detailed — 6-12 tasks per area. Every edge case covered.
```

Wait for response. Store as `<granularity>`.

```
Question 2 of 2 — Who generates the prototype?

  1. Claude     — Built-in prototype skill. No setup needed.
  2. Stitch     — Google Stitch via MCP. Better visual quality.
                  Requires a free account at stitch.withgoogle.com.
  3. Other MCP  — Any design tool you have configured as an MCP server.
```

Wait for response. Store as `<prototyper>`.

If `<prototyper>` is **Other MCP**, ask:

```
MCP tool name? (e.g., mcp__figma__generate_screen)
```

Wait. Store as `<prototyper_tool>`.

```
Briefly describe what it expects and returns:
(e.g., "Call with epic_name and description. Returns a URL.")
```

Wait. Store as `<prototyper_instructions>`.

## Step 0b — Stitch MCP setup

Skip if `<prototyper>` is not `Stitch`.

The real availability test is whether any `mcp__stitch__*` tool is accessible in the current session. Do not check env vars or run `claude mcp list` — the env var may exist in the OS registry but not in this process if Claude Code was not restarted after `setx`.

If any `mcp__stitch__*` tool is accessible: skip to the next step.

Otherwise:

**Write `.mcp.json` if needed.** Read `~/.claude/.mcp.json`. If the file does not exist or has no `stitch` entry, write or merge:

```json
{
  "stitch": {
    "type": "http",
    "url": "https://stitch.googleapis.com/mcp",
    "headers": {
      "x-goog-api-key": "${STITCH_API_KEY}"
    }
  }
}
```

Then output and wait:

```
Stitch MCP is not connected. How would you like to proceed?

  1. Set up Stitch now (requires restart)
  2. Use Claude for prototyping instead
```

- If 2: change `<prototyper>` to `Claude`, continue to Step 2.
- If 1: output the following, then stop:

```
Steps to connect Stitch:

  1. Create a free account: stitch.withgoogle.com
  2. Generate an API key: Settings → API Keys → New key
  3. Save the key so Claude Code can read it:

     If you use the Claude Code desktop app (Windows):
       Add an "env" block to ~/.claude/settings.json:
         "env": { "STITCH_API_KEY": "<your-key>" }
       Then restart the app.

     If you launch Claude Code from a terminal (claude CLI):
       Windows:  setx STITCH_API_KEY "<your-key>"
       Mac/Linux: echo 'export STITCH_API_KEY="<your-key>"' >> ~/.zshrc
       Then close the terminal, open a new one, and relaunch.

     Note: setx does NOT work for the desktop app — the app does not
     inherit terminal environment variables.

~/.claude/.mcp.json is already configured for Stitch.

Re-run /devaing-init when you're back.
```

## Step 2 — Auth and working directory

### Auth check

```bash
gh auth status 2>/dev/null
```

If not authenticated, stop: "Run `gh auth login` before continuing."

```bash
gh api user --jq '.login'
```

Store result as `<owner>`.

### State detection matrix

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

Claude Code: `/devaing-phase-revise` (adjust phase or add new area), `/devaing-bug "description"`

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

Run unconditionally (`--force` makes each call idempotent):

```bash
gh label create "needs-triage"    --color "e4e669" --description "Needs evaluation" --force
gh label create "needs-info"      --color "0075ca" --description "Waiting on reporter" --force
gh label create "ready-for-agent" --color "d73a4a" --description "Agent can take this" --force
gh label create "ready-for-human" --color "008672" --description "Requires human decision" --force
gh label create "wontfix"         --color "ffffff" --description "Will not be actioned" --force
```

## Step 4b — GitHub Project

Check if a project named `<name>` already exists:

```bash
gh project list --owner <owner> --format json --jq '.projects[] | select(.title == "<name>") | .number'
```

If found, store as `<project-number>` and skip creation.

Otherwise create it:

```bash
gh project create --owner <owner> --title "<name>" --format json --jq '.number'
```

Store result as `<project-number>`.

Link the project to the repo so issues appear automatically:

```bash
gh project link <project-number> --owner <owner> --repo <owner>/<name>
```

Add `project: <project-number>` to `.devaing.md`.

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

Skip if `.github/workflows/ci.yml` already exists.

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

tracking: GitHub
granularity: <granularity>
prototyper: <prototyper>
project: <project-number>

Runtime-agnostic spec. For Claude Code, use the `/devaing-*` skills directly.

## devaing-work — Implement a slice

Takes a GitHub issue (`#N`) or milestone name and implements the next vertical slice end-to-end.

1. **Mid-flight check**: look for an existing branch matching this milestone with unmerged commits. If found, offer to resume instead of starting over.
2. **Resolve the issue**: read what to build, acceptance criteria, and blockers. If given a milestone name, determine the next slice from CONTEXT.md and closed issues, then create the issue.
3. **Context budget**: if this session has already processed prior slices, recommend a fresh session.
4. **Implement**: if UI issue, implement the visual layer first (replace the matching prototype screen if one exists, leave others as mocks). Then backend + tests.
5. **Update CONTEXT.md**: after merge, add new domain terms, architecture changes, known limitations.
6. **Close the issue** with a reference to the PR.

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
4. Kicks off Phase 1 by calling /devaing-phase-def.

## devaing-phase-def — Kick off a phase

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
| GitHub Project | created / already existed |
| Labels | applied / already existed |
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
| `## Phases` absent or empty | Fresh project — call `/devaing-phase-def` for Phase 1 |
| Phase `In Progress`, 0 issues | Phase kicked off but nothing built — show available skills |
| Phase `In Progress`, N issues open | Active phase — show available skills, skip `/devaing-phase-def` call |
| All phases `Complete` | Show that `/devaing-phase-def` is available for a new phase |

If a phase is already `In Progress`, output one line noting state and skip to Closing.

## Step 8c — Kick off Phase 1

Show this message so the user learns the command for future phases:

```
Starting Phase 1 — calling /devaing-phase-def.

For future phases, you will run this yourself:
  /devaing-phase-def
```

Then invoke `/devaing-phase-def`. Pass `<granularity>` from Step 0 so devaing-phase-def skips its own Step 1. The closing message comes from devaing-phase-def.

## Closing (re-run with incomplete setup)

Only reached from Step 8b when `.devaing.md` is missing but CONTEXT.md already has a phase in progress (setup was interrupted mid-run). Output the same re-run message from the Opening section, then stop.
