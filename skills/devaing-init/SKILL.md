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

1. Silently upgrade `.devaing/skills/` for any skill body that is missing (forward-compatible with projects initialized before a skill was added):

```bash
SKILL_DIR="$HOME/.claude/skills"
for skill in work phase-def phase-revise ship bug help director; do
  [ -f ".devaing/skills/$skill.md" ] || \
    cp "$SKILL_DIR/devaing-$skill/body.md" ".devaing/skills/$skill.md" 2>/dev/null || true
done
```

2. Run `gh issue list --state open --json number,title,milestone --jq '.[] | "#\(.number) [\(.milestone.title)] \(.title)"'` to get open issues grouped by milestone.
3. Output the message below. Do not continue past this point.

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

  /devaing-director         Project state, health audit, and next step
  /devaing-phase-revise     Adjust scope, prototype, or business logic
  /devaing-bug "..."        Report something broken
  /devaing-help             Framework overview and command reference
```

**Step C2 — Init complete, no phases yet.** CONTEXT.md is populated, `.devaing.md` is valid, but no phases defined. Init completed normally in a prior session — phase definition was never run. Do not assume interruption.

Resolve the project name. Output, then stop:

```
╔══════════════════════════════════════════════════════════════╗
║  <name> — ready, no phases defined yet                      ║
╚══════════════════════════════════════════════════════════════╝

Project is initialized. What do you want to do next?

  /devaing-phase-def      Define Phase 1 (epics, prototype, tasks)
  /devaing-ship           Set up and deploy to prod
  /devaing-director       Project state and health audit
```


**Step D — Greenfield project.** Resolve the project name (argument or `basename "$PWD"`). Output the welcome message below, then continue to Step 0:

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-init: <name>                                       ║
╚══════════════════════════════════════════════════════════════╝

Let's set up your project so it's ready to build, step by step.

Here's what's going to happen:

  1. Capture what you're building (problem + vision)
  2. Set up the repo, CI, and project files
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

## Step 1b — Product discovery (greenfield only)

Skip entirely if `<re_flow>` is true (RE scan will capture context in RE-scan-2b).

**Scope:** this discovery captures the product — what it is, who it's for, what problem it solves. It does NOT define Phase 1. Phase 1 scope is defined later in `/devaing-phase-def`, which runs its own grill-me focused on what to build first.

First, check GitHub auth before the discovery session starts:

```bash
gh auth status 2>/dev/null
```

If not authenticated, stop: "Run `gh auth login` before continuing. Then re-run `/devaing-init`."

Ask the seed question:

```
¿Qué hace esta app a alto nivel?
```

Wait for response. Store as `<seed>`. If the answer is vague (one word, or no mention of who the users are or what problem it solves), ask up to 2 follow-up questions — one at a time, stop as soon as enough context is gathered:

1. "¿Para quién es?"
2. "¿Qué problema específico resuelve?"

Append any follow-up answers to `<seed>`.

Now show the model upgrade prompt before the interview:

```
╔══════════════════════════════════════════════════════════════╗
║         MODEL UPGRADE RECOMMENDED                           ║
╠══════════════════════════════════════════════════════════════╣
║  Discovery works better with a more capable model.          ║
╚══════════════════════════════════════════════════════════════╝

To switch: /model — then come back and answer below.

Did you switch to a more capable model?
  y — yes, switched
  n — no, continuing as-is
```

Wait for response. If `y`: set `<model_upgraded> = true`. If `n`: set `<model_upgraded> = false`.

Invoke `grill-me` with:

> "I'm setting up a new project called <name>. Here's what I know so far: <seed>.
>
> Granularity: <granularity>. Calibrate question depth: Broad = 3-5 focused questions covering problem, user, and core scope. Balanced = 6-10 questions adding constraints and key flows. Detailed = go deep on every persona, edge case, and technical constraint.
>
> Now capture it properly: what is this, who is it for, what problem does it solve, what are the key constraints, what's out of scope? Ask targeted questions based on what you already know — do not repeat what I already answered."

Run until the user signals done. Store all context as `<discovery-context>`.

Write CONTEXT.md immediately from discovery (do not leave it blank):

```markdown
# Context

## Project

<one sentence describing what this project does and for whom, from discovery>

## Domain glossary

| Term | Definition |
|------|------------|
| <term from discovery> | <definition> |

## Architecture

> To be defined during Phase 1. Stack TBD.

## Key constraints

<constraints from discovery — legal, technical, business>

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

Store flag `<context_written> = true` so Step 7 skips rewriting CONTEXT.md.

If `<model_upgraded>` is true, show the downgrade prompt before continuing:

```
╔══════════════════════════════════════════════════════════════╗
║         MODEL DOWNGRADE SUGGESTED                           ║
╠══════════════════════════════════════════════════════════════╣
║  Discovery complete. You can switch back to a lighter model. ║
╚══════════════════════════════════════════════════════════════╝

To switch: /model

Type 'continue' when ready.
```

## Step RE-scan — Codebase reverse engineering (D-RE flow only)

Skip this entire section if `<re_flow>` is not set.

Before starting, show the model upgrade prompt — the RE scan and grill-me that follow both benefit from a more capable model:

```
╔══════════════════════════════════════════════════════════════╗
║         MODEL UPGRADE RECOMMENDED                           ║
╠══════════════════════════════════════════════════════════════╣
║  Discovery works better with a more capable model.          ║
╚══════════════════════════════════════════════════════════════╝

To switch: /model — then come back and answer below.

Did you switch to a more capable model?
  y — yes, switched
  n — no, continuing as-is
```

Wait for response. If `y`: set `<model_upgraded> = true`. If `n`: set `<model_upgraded> = false`.

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
4. What bugs or mistakes have you already seen repeated in this codebase?
   (patterns that looked plausible but were wrong — for CLAUDE.md Tactical anti-patterns)
```

Wait for response. Store as `<re-validation>`. Store Q4 answers separately as `<re-antipatterns>`.

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

Invoke `grill-me` with the RE scan as context:

> "I've analyzed the codebase for <name>. Here's what I found: <RE summary from RE-scan-2>.
>
> Granularity: <granularity>. Calibrate question depth: Broad = 3-5 focused questions. Balanced = 6-10 questions. Detailed = go deep on every decision, constraint, and deferred work.
>
> Now I need to understand the business side: why this exists, who uses it, what decisions shaped it, what's broken or deferred, and where it's going. Ask targeted questions based on what the codebase already reveals."

Run until the user signals done. Store responses as `<re-business-context>`.

If `<model_upgraded>` is true, show the downgrade prompt before continuing:

```
╔══════════════════════════════════════════════════════════════╗
║         MODEL DOWNGRADE SUGGESTED                           ║
╠══════════════════════════════════════════════════════════════╣
║  Discovery complete. You can switch back to a lighter model. ║
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

After writing CONTEXT.md, also update `CLAUDE.md` if it exists:

```bash
test -f CLAUDE.md && echo "exists" || echo "missing"
```

**If it exists:**

- If `## Critical Patterns` section is absent: append it:
  ```markdown
  ## Critical Patterns

  > Not prose — for each pattern easy to misuse, show the wrong snippet and the correct one.
  ```
- If `<re-antipatterns>` is non-empty: append entries to `## Tactical anti-patterns` (create the section if absent):
  ```markdown
  ## Tactical anti-patterns

  - **<name>**: <wrong pattern> → <correct pattern>. [Why: <reason>]
  ```

**If CLAUDE.md doesn't exist:** note in the final report. These sections should be added when the developer creates CLAUDE.md.

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
- `<context_written>` is true (CONTEXT.md was written in Step 1b from discovery)

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
subagent_cli: claude -p --model claude-sonnet-4-6

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
3. Validates context — brief summary + "anything to correct?" No discovery (that's /devaing-init).
4. For Phase 2+: also asks "anything changed since last phase that affects scope?" One question only.
5. Defines epics for this phase, annotates next-phase backlog.
6. Builds or extends the prototype (living skeleton — never deleted).
7. Generates all issues calibrated to granularity.

## devaing-phase-revise — Adjust the current phase

1. Verifies a phase is open.
2. Adjusts scope (add/remove/modify issues), prototype, or business logic.
3. Updates CONTEXT.md and commits.
```

## Step 7b-portable — Portable skills layer

Create the `.devaing/skills/` directory and populate it with the skill bodies. This enables other LLMs (Codex, Aider, Cursor) to follow the same workflow by reading these files.

Skip if `.devaing/skills/` already exists with files (already set up in a prior run).

```bash
mkdir -p .devaing/skills
```

Copy body.md files from the installed skill location to the project:

```bash
SKILL_DIR="$HOME/.claude/skills"
for skill in work phase-def phase-revise ship bug help director; do
  src="$SKILL_DIR/devaing-$skill/body.md"
  if [ -f "$src" ]; then
    cp "$src" ".devaing/skills/$skill.md"
  fi
done
```

Create `.devaing/AGENTS.md` for non-Claude Code agents:

```bash
cat > .devaing/AGENTS.md << 'EOF'
# devaing project

This project uses the devaing workflow. When the user invokes a devaing command,
read and execute the corresponding file in `.devaing/skills/`.

| Command | File |
|---------|------|
| devaing-work / implement issue | `.devaing/skills/work.md` |
| devaing-ship / deploy | `.devaing/skills/ship.md` |
| devaing-phase-def / define phase | `.devaing/skills/phase-def.md` |
| devaing-phase-revise / adjust phase | `.devaing/skills/phase-revise.md` |
| devaing-bug / report bug | `.devaing/skills/bug.md` |
| devaing-director / project state + orchestrator | `.devaing/skills/director.md` |
| devaing-help / framework reference | `.devaing/skills/help.md` |

Each skill file is self-contained markdown with bash commands. Follow it literally.

Sub-agent CLI: see `.devaing.md` field `subagent_cli`. Default: `claude -p --model claude-sonnet-4-6`.
For Codex: `codex exec`, for Aider: `aider --message`.
EOF
```

If any `cp` above fails (skill not installed): note in the final report which skill files were missing. Do not stop.

## Step 7c — CHECKPOINTS.md

Skip if `CHECKPOINTS.md` already exists at the project root.

Otherwise write it:

```markdown
# Checkpoints — Health audit

> Objective criteria for project health. devaing-director audits these on every run.
> Run manually when returning to a project after a long break.

## C1 — Setup integrity
- [ ] CONTEXT.md exists at project root with populated ## Project section
- [ ] .devaing.md exists with fields: granularity, project, prototyper
- [ ] AGENTS.md contains devaing execution section (references devaing-work)
- [ ] .devaing/skills/ contains all skill body files

## C2 — Phase coherence
- [ ] At most one phase has status "In Progress" in CONTEXT.md ## Phases
- [ ] No closed GitHub milestone has open issues

## C3 — Epic coherence
- [ ] All open GitHub issues are assigned to a milestone (no orphans)

## C4 — Branch coherence
- [ ] prod branch exists (created by devaing-init, only updated by devaing-ship)
- [ ] No direct work commits on master outside merges from epic/* or hotfix/*

## C5 — Documentation coherence
- [ ] If a phase is In Progress, at least one GitHub milestone is open
- [ ] CONTEXT_ARCHIVE.md exists if any phase has been shipped

## C6 — Context size
- [ ] CONTEXT.md is under 200 lines
      (if not: move feature implementation details to docs/features/<slug>.md)
```

## Step 7d — Dev environment validation

Skip this step if `<re_flow>` is false (greenfield — no code exists yet to validate; the user validates the dev environment after Phase 1 scaffolds the project).

**For `<re_flow>` projects** (existing codebase): run these checks silently. Stop only if a check fails; continue without output if all pass.

**Check 1 — .env:**

```bash
test -f .env && echo "ok" || echo "missing"
```

If missing: stop with "`.env` is missing. Create it and fill in required vars, then re-run `/devaing-init`."

**Check 2 — DB connection:**

For Prisma projects:

```bash
npx prisma db pull 2>&1 | head -20
```

If output contains "error" (case-insensitive) or exit is non-zero: stop with the error output and "Check `DATABASE_URL` in `.env` and confirm the DB is reachable."

For Python/SQLAlchemy or other ORMs: run an equivalent quick connection test if inferable from the stack.

**Check 3 — Code compiles (Node/TypeScript only):**

```bash
npx tsc --noEmit 2>&1 | tail -20
```

If exit non-zero: stop with the error output and "Fix typecheck errors before continuing."

If all checks pass: continue to the next step without prompting the user.


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

If exit code is non-zero: stop and report the full output. Otherwise continue.

**For Python/Alembic projects**, create `db/seeds/runner.py` with equivalent logic using the project's ORM.

**For other stacks**, create `db/seeds/runner.<ext>` following the same pattern: read executed seeds from `_seed_migrations` table, run pending files in order, mark each executed.

Create a migration to add the `_seed_migrations` table if not using Prisma (where it's managed via `schema.prisma`).

## Step 7f — Operational skills

Ask:

```
Which project-specific operations will you repeat most? (select any, or skip)

  a) push / deploy flow — commit + push branches, trigger deploy
  b) database migrations — create, apply locally, run in production
  c) new feature scaffold — model + route + UI with project conventions
  d) debug errors — follow request→response flow for this stack
  e) code / component review — checklist for this project's patterns
  f) other: ___
```

For each selected: create `.claude/skills/<name>/SKILL.md` pre-filled with the project's stack and conventions from CONTEXT.md and CLAUDE.md. Use 3–5 steps maximum. Bake in project-specific details: branch names, DB connection pattern, deploy URL, anti-patterns from `## Tactical anti-patterns`.

```yaml
---
name: <kebab-name>
description: <one-line — what this does for <project-name>>
---

# <name>

## Step 1 — <first action>
...
```

If the user selects "skip" or no options: skip silently.

## Step 8 — Commit and push

```bash
git status --porcelain
```

If empty: skip, note "no changes".

Stage only devaing setup files — never use `git add .` as it would include the user's uncommitted work-in-progress code:

```bash
git add CONTEXT.md CHECKPOINTS.md .devaing.md .devaing/ AGENTS.md \
  docs/agents/issue-tracker.md docs/agents/triage-labels.md docs/agents/domain.md \
  .github/workflows/ci.yml 2>/dev/null || true
# Add seeds files if they were created in Step 7e
git add prisma/seeds/ db/seeds/ scripts/seeds/ 2>/dev/null || true
# Add operational skills if they were created in Step 7f
git add .claude/skills/ 2>/dev/null || true
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
| CHECKPOINTS.md | created / already existed |
| .devaing.md | created / already existed |
| Operational skills | N created / skipped |
| CLAUDE.md | Critical Patterns added / Tactical anti-patterns added / not found |
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
