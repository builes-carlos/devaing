---
name: devaing-init
description: Initialize a new devaing project OR show current status if already initialized. Reads CONTEXT.md first to detect existing setup before doing anything else. Use when starting a new project or re-running setup. Invoked with /devaing-init <project-name> or /devaing-init (uses current folder name).
---

# devaing-init

**Execute these steps in order. Do not skip or reorder.**

**Step A.** Use the Read tool to read `CONTEXT.md` if it exists. Do not output any text yet.

**Step B — Content evaluation.** Determine the quality of CONTEXT.md:

CONTEXT.md is **populated** when ALL of these hold:
- `## Project` has a real sentence (not the placeholder `> One sentence describing...` or empty)
- `## Architecture` has non-placeholder content
- `## Domain glossary` has at least one table row with actual terms

CONTEXT.md is **template** if it exists but fails any of the above. CONTEXT.md is **absent** if it does not exist.

**Step B2 — Code detection.** Check whether the working directory already has source code:

```bash
git ls-files | grep -vE "^(CONTEXT|AGENTS|\.devaing|docs/|README|\.github|\.gitignore)" | wc -l
```

Code is **present** when the count is > 5 OR any of `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod` exist at the project root.

**Step B3 — .devaing.md validity check.** Run:

```bash
grep -q "^granularity:" .devaing.md 2>/dev/null && \
grep -q "^project:" .devaing.md 2>/dev/null && \
grep -q "^prototyper:" .devaing.md 2>/dev/null && echo "valid" || echo "invalid"
```

`.devaing.md` is **valid** when all three fields are present. **Invalid or absent** otherwise.

**State detection matrix:**

| `.devaing.md` valid | Phases table has rows | Code present | Action |
|---|---|---|---|
| Yes | Yes | — | **Step C** — already initialized |
| Yes | No | — | **Step C2** — init complete, no phases yet |
| Invalid/absent | — | Yes | **Step D-RE** — existing project (vibe-coded or first run) |
| Invalid/absent | — | No | **Step D** — greenfield |

CONTEXT.md quality is irrelevant when `.devaing.md` is absent — a vibe-coded project may have a populated CONTEXT.md that was created manually or by a prior AI session. The canonical devaing marker is `.devaing.md` with its three machine-readable fields.

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

**Step C2 — Init complete, no phases yet.** CONTEXT.md is populated, `.devaing.md` is valid, but no phases defined. Init completed normally in a prior session — phase definition was never run. Do not assume interruption.

Resolve the project name. Output, then stop:

```
╔══════════════════════════════════════════════════════════════╗
║  <name> — ready, no phases defined yet                      ║
╚══════════════════════════════════════════════════════════════╝

Project is initialized. What do you want to do next?

  /devaing-phase-def    Define Phase 1 (epics, prototype, tasks)
  /devaing-ship         Set up and deploy to prod
```


**Step D — Greenfield project.** Resolve the project name (argument or `basename "$PWD"`). Output the welcome message below, then continue to Step 0:

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-init: <name>                                       ║
╚══════════════════════════════════════════════════════════════╝

Let's set up your project so it's ready to build, step by step.

Here's what's going to happen:

  1. Set up the repo, CI, and project files
  2. Set up the dev environment
  3. Then: /devaing-phase-def to define Phase 1 (epics, prototype, tasks)

When we're done, your project is wired up and ready to define.
```

**Step D-RE — Existing project.** Resolve the project name (argument or `basename "$PWD"`). Output:

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-init: <name>                                       ║
╚══════════════════════════════════════════════════════════════╝

Existing project detected. I'll scan the codebase to build context,
then validate my findings with you before setting up the framework.

Here's what's going to happen:

  1. Scan the codebase and summarize what I find
  2. Validate with you — correct anything wrong or missing
  3. Deep interview — business context, decisions, constraints
  4. Validate dev environment
  5. Set up the repo and project files
  6. Define the first phase together

When we're done, your project is ready to continue building.
```

Set a flag `<re_flow> = true` to enable RE-specific sub-steps later.

Continue to Step 0 and Step 0b as normal, then run **Step RE-scan** before continuing to Step 2.

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

- If 2: change `<prototyper>` to `Claude`, continue to the next step.
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

## Step RE-scan — Codebase reverse engineering (D-RE flow only)

Skip this entire section if `<re_flow>` is not set.

### RE-scan-1: Read the codebase

Do all of the following silently — no output until RE-scan-2:

1. **Stack detection**: read `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, or similar files at the root. Note language, framework, key dependencies.
2. **Structure**: run `git ls-files`. Identify main source directories, entry points (e.g., `src/index.ts`, `app/main.py`), model/schema files, route/controller files.
3. **Deep read**: read up to 5 key files in this priority order: data models/schemas first, then main router or app entry point, then any `README.md`. Skip test files, lock files, and generated files.

### RE-scan-2: Present findings and validate

```
Here's what I found in <name>:

**What it does**: <one-sentence description inferred from the code>
**Stack**: <framework + language + key dependencies>
**Main entities**: <entity1>, <entity2>, ...
**Key flows**: <flow1>, <flow2>
**Architecture**: <brief description of structure and how components connect>

Is this accurate? What's wrong, missing, or outdated?
```

Wait for response. Store as `<re-corrections>`.

For each correction where the user says something is wrong, deprecated, or no longer used: mark it as a `<contradiction>` (what the code shows vs. what the user reported).

Then ask:

```
A few things the code can't tell me:

1. Who are the primary users of this system?
2. What business rules are most important that aren't obvious from the code?
3. Any constraints I should know about (legal, performance, integrations, third-party limits)?
```

Wait for response. Store as `<re-validation>`.

Output immediately — do not skip, do not continue to the next step without doing this:

```
---
Technical scan complete.

Next: business context interview. This is a separate required step,
always runs, covers different ground (why this was built, decisions
made, what's deferred, where it's going). Not a continuation of above.
---
```

### RE-scan-2b: Business context — grill-me

Output and wait:

```
╔══════════════════════════════════════════════════════════════╗
║         MODEL UPGRADE RECOMMENDED                           ║
╠══════════════════════════════════════════════════════════════╣
║  The interview works better with a more capable model.      ║
╚══════════════════════════════════════════════════════════════╝

To switch: /model — then come back and answer below.

Did you switch to a more capable model?
  y — yes, switched
  n — no, continuing as-is
```

Wait for response. If `y`: set `<model_upgraded> = true`. If `n`: set `<model_upgraded> = false`.

Invoke `grill-me` with the RE scan as context:

> "I've analyzed the codebase for <name>. Here's what I found: <RE summary from RE-scan-2>. Now I need to understand the business side. Tell me everything — why this exists, who uses it, what decisions shaped it, what's broken or deferred, and where it's going. Dump everything."

Run until the user signals done. Store responses as `<re-business-context>`.

If `<model_upgraded>` is true, output and wait:

```
╔══════════════════════════════════════════════════════════════╗
║         MODEL DOWNGRADE SUGGESTED                           ║
╠══════════════════════════════════════════════════════════════╣
║  Interview complete. You can switch back to a lighter model. ║
╚══════════════════════════════════════════════════════════════╝

To switch: /model

Type 'continue' when ready.
```

Integrate into CONTEXT.md in RE-scan-3.

### RE-scan-3: Write CONTEXT.md

Write `CONTEXT.md` at the project root, combining RE findings, corrections, and validation answers:

```markdown
# Context

## Project

<description from RE findings + re-corrections>

## Domain glossary

| Term | Definition |
|------|------------|
| <entity> | <inferred definition, corrected if applicable> |

## Architecture

<stack + structure from RE + re-corrections>

## Key constraints

<constraints from RE scan + re-validation answers>

## Known limitations

> Problems we are aware of and consciously not fixing yet.
> Format: what the problem is | why it's deferred | what would trigger the fix | operational guidance for the current state.

## Phases

| Phase | Name | Status | Epics |
|-------|------|--------|-------|
| 1 | Pre-devaing | Complete | Existing codebase |

## Next phase backlog

> Epics identified but deferred to future phases.
> Format: Phase N — Epic name — one-line description
```

The Phase 1 "Pre-devaing / Complete" entry represents everything built before devaing was introduced. This leaves the project in a state where `/devaing-phase-def` can define the next phase, and `/devaing-ship` can deploy what exists.

Store `<contradictions>` for Step 4c.

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

### Detect current branch

```bash
git branch --show-current
```

Store as `<branch>`. Default to `master` if empty.

## Step 3 — AGENTS.md

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

**Guardrail:** If the user asks to implement a feature or fix without invoking `/devaing-work`, do not implement it directly. Instead, ask: "¿Querés crear un issue primero y trabajarlo con `/devaing-work`?" Only proceed without the workflow if the user explicitly confirms they want to skip it.

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

## Step 4c — Contradiction issues (D-RE flow only)

Skip if `<re_flow>` is not set or `<contradictions>` is empty.

For each contradiction, create a GitHub issue:

```bash
gh issue create \
  --title "<short description of the discrepancy>" \
  --label "needs-triage" \
  --body "$(cat <<'EOF'
## What the code shows

<what the RE scan found>

## What was reported

<what the user corrected>

## Proposed action

<cleanup, removal, documentation update, or fix — to be confirmed by a human>
EOF
)"
```

After all contradiction issues are created, output:

```
⚠️  Found <N> discrepanc(ies) between the codebase and your corrections:

  #N — <title>
  ...

These are marked needs-triage. Review them during phase definition or address them with /devaing-bug.
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

Skip if any of the following:
- CONTEXT.md is already **populated** (as defined in Step B)
- `<re_flow>` is set (CONTEXT.md was already written in RE-scan-3)

Otherwise write the blank template:

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

Skip if `.devaing.md` already exists AND was valid (passed the B3 check). If it exists but was invalid, overwrite it.

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
3. For existing projects: scans the codebase, validates with you, and writes CONTEXT.md from reality.
4. For new projects: creates a blank CONTEXT.md structure for devaing-phase-def to populate.
5. Kicks off Phase 1 by calling /devaing-phase-def.

## devaing-phase-def — Kick off a phase

1. Verifies previous phase is closed (no open issues).
2. Asks phase name and granularity.
3. For Phase 1 with populated CONTEXT.md: brief validation only, no full discovery.
4. For Phase 1 greenfield (CONTEXT.md absent or template): full discovery interview.
5. For Phase 2+: incremental interview about what changed since the last phase.
6. Defines epics for this phase, annotates next-phase backlog.
7. Builds or extends the prototype (living skeleton — never deleted).
8. Generates all issues calibrated to granularity.

## devaing-phase-revise — Adjust the current phase

1. Verifies a phase is open.
2. Adjusts scope (add/remove/modify issues), prototype, or business logic.
3. Updates CONTEXT.md and commits.
```

## Step 7c — Dev environment validation

Skip this step if `<re_flow>` is false (greenfield — no code exists yet to validate; the user validates the dev environment after Phase 1 scaffolds the project).

**For `<re_flow>` projects** (existing codebase):

Infer the start command from the stack detected in RE-scan-1 (e.g., `npm run dev`, `uvicorn app.main:app`, `go run .`). Then output and wait:

```
Before continuing, let's confirm the dev environment runs.

Detected stack: <stack from RE scan>
Expected start command: <inferred command>

Please verify:
  1. Run the start command — it should start without errors
  2. DB connection works (dev DB is reachable)
  3. .env file is present and all required vars are set

Fix anything broken now. I'll wait.

Ready? (y/n)
```

Do not continue until the user confirms.


## Step 7d — Seeds infrastructure

Skip if `<re_flow>` is false (greenfield — stack not known until phase-def runs; seeds will be set up when the first epic with reference data is implemented).

Check if seeds infrastructure already exists:

```bash
ls prisma/seeds/ 2>/dev/null || ls db/seeds/ 2>/dev/null || ls scripts/seeds/ 2>/dev/null
```

If found: skip this step.

Otherwise, infer the seeds directory from the stack in CONTEXT.md `## Architecture`:
- Prisma (Node): `prisma/seeds/`
- Alembic (Python): `db/seeds/`
- Other ORM or raw SQL: `db/seeds/`

Create the seeds directory and a baseline runner:

**For Prisma projects**, add to `schema.prisma`:

```prisma
model SeedMigration {
  id        String   @id
  executedAt DateTime @default(now())
}
```

Create `prisma/seeds/runner.ts`:

```typescript
import { PrismaClient } from '@prisma/client'
import fs from 'fs'
import path from 'path'

const prisma = new PrismaClient()

async function runSeeds() {
  const seedsDir = path.join(__dirname)
  const files = fs.readdirSync(seedsDir)
    .filter(f => f.endsWith('.ts') && f !== 'runner.ts')
    .sort()

  for (const file of files) {
    const id = file.replace('.ts', '')
    const existing = await prisma.seedMigration.findUnique({ where: { id } })
    if (existing) continue

    console.log(`Running seed: ${file}`)
    const seed = await import(path.join(seedsDir, file))
    await seed.default(prisma)
    await prisma.seedMigration.create({ data: { id } })
    console.log(`  Done: ${file}`)
  }
}

runSeeds().finally(() => prisma.$disconnect())
```

Add to `package.json` scripts:
```json
"seed": "ts-node prisma/seeds/runner.ts"
```

Run the migration to create the tracking table in dev:

```bash
npx prisma migrate dev --name add_seed_migrations
```

Wait for confirmation the migration ran successfully before continuing.

**For Python/Alembic projects**, create `db/seeds/runner.py` with equivalent logic using the project's ORM.

**For other stacks**, create `db/seeds/runner.<ext>` following the same pattern: read executed seeds from `_seed_migrations` table, run pending files in order, mark each executed.

Create a migration to add the `_seed_migrations` table if not using Prisma (where it's managed via `schema.prisma`).

## Step 8 — Commit and push

```bash
git status --porcelain
```

If empty: skip, note "no changes".

Stage only devaing setup files — never use `git add .` as it would include the user's uncommitted work-in-progress code:

```bash
git add CONTEXT.md .devaing.md AGENTS.md \
  docs/agents/issue-tracker.md docs/agents/triage-labels.md docs/agents/domain.md \
  .github/workflows/ci.yml 2>/dev/null || true
# Add seeds files if they were created in Step 7d
git add prisma/seeds/ db/seeds/ scripts/seeds/ 2>/dev/null || true
git diff --cached --quiet && echo "nothing to commit" || \
git commit -m "chore: devaing project setup

- AGENTS.md: devaing workflow, execution and review conventions
- .devaing.md: runtime-agnostic skill spec (portable to any agent)
- docs/agents/: issue-tracker, triage-labels, domain docs
- .github/workflows/ci.yml: CI pipeline
- CONTEXT.md: populated from codebase scan"
git push -u origin <branch>
```

Create the production deploy branch:

```bash
git checkout -b prod
git push -u origin prod
git checkout <branch>
```

This branch is only ever updated by `devaing-ship`. `devaing-work` merges to `<branch>` and never touches `prod`.

## Step 8b-pre — Model downgrade

Skip if `<re_flow>` is true — model downgrade was already suggested after the grill-me interview.

Output and wait:

```
╔══════════════════════════════════════════════════════════════╗
║         SETUP COMPLETE                                      ║
╠══════════════════════════════════════════════════════════════╣
║  Project is ready. You can switch to a lighter model        ║
║  for the next steps.                                        ║
╚══════════════════════════════════════════════════════════════╝

To switch models: /model

Type 'continue' when ready.
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
| CONTEXT.md | created from RE scan / created blank / already existed |
| .devaing.md | created / already existed |
| Contradictions | N issues created / none |
| Commit | N files / no changes |

Then output one line: `✓ <name> ready.`

## Step 8b — Phase state detection

Check if this is a re-run on a project that already has a phase started:

```bash
grep -q "In Progress" CONTEXT.md && echo "phase_open" || echo "no_open_phase"
```

| State | `<re_flow>` | Action |
|-------|------------|--------|
| `## Phases` absent or empty | false | Fresh project — call `/devaing-phase-def` for Phase 1 (Step 8c) |
| Phase 1 "Pre-devaing / Complete" only | true | Existing project setup complete — Step 8c (show options, stop) |
| Phase `In Progress`, 0 issues | — | Phase kicked off but nothing built — show available skills |
| Phase `In Progress`, N issues open | — | Active phase — show available skills, skip `/devaing-phase-def` call |
| All phases `Complete` (Phase 2+) | — | Show that `/devaing-phase-def` is available for a new phase |

If a phase is already `In Progress`, output one line noting state and skip to Closing.

## Step 8c — Kick off Phase 1

**If `<re_flow>` is true** (existing project): CONTEXT.md already has Phase 1 "Pre-devaing / Complete". The code is already built. Do NOT call `/devaing-phase-def`. Output and stop:

```
╔══════════════════════════════════════════════════════════════╗
║  <name> — ready                                             ║
╚══════════════════════════════════════════════════════════════╝

Existing codebase is set up. What do you want to do next?

  /devaing-ship         First deployment to production
  /devaing-phase-def    Plan new features (Phase 2)
```

**If `<re_flow>` is false** (greenfield): show this message, then invoke `/devaing-phase-def`:

```
Starting Phase 1 — calling /devaing-phase-def.

For future phases, you will run this yourself:
  /devaing-phase-def
```

Pass `<granularity>` from Step 0 so devaing-phase-def skips the granularity sub-question in Step 1. The phase name question still runs in phase-def. The closing message comes from devaing-phase-def.

## Closing (re-run with incomplete setup)

Only reached from Step 8b when `.devaing.md` is missing but CONTEXT.md already has a phase in progress (setup was interrupted mid-run). Output the same re-run message from the Opening section, then stop.
