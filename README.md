# devaing

Vibe coding fails the second time you sit down.

Not because the AI got worse. Because the context window filled up, you lost the thread, and now you're re-explaining the same architecture decisions from two sessions ago. The AI builds confidently — toward something slightly wrong.

devaing is a discipline for building products with AI. Eight Claude Code skills that enforce one rule: **every piece of work is a self-contained GitHub issue with enough context for any agent to execute without re-explanation**. You validate what matters — the problem, the prototype, scope changes. The agent handles the rest.

Targets solo builders, dev pairs, and early-stage startups. Not Pocock (designed for large teams). Not vibe coding (no structure). The middle path.

---

## The core insight

GitHub Issues is not bureaucracy. It is a **token rationalization system**.

Each issue is a miniature spec that is always current because it is the thing you are working on right now. It contains the full context for one vertical slice: what to build, acceptance criteria, which epic it belongs to. The agent reads the issue, implements, reports back. No memory of previous sessions required.

Three things prevent context rot:

**1. Fresh sub-agent per issue.** Every issue is implemented by a sub-agent spawned with a clean context window. It receives a filtered CONTEXT.md (architecture, domain glossary, key constraints — not phase history) plus the full issue. Sub-agents run at 0-30% context fill — peak quality — on every issue, regardless of how long the phase has been running.

**2. CONTEXT.md as the living truth.** One file at the project root, updated after every issue closes. Domain glossary, architecture decisions, key constraints, known limitations. Any session can pick up any issue without a briefing.

**3. Human validation at the right moments only.** Discovery interview at the start of each phase. Prototype review before issues are generated. Scope changes through a structured question set. Everything else the agent executes without asking.

---

## The eight skills

| Skill | When to run | What it does |
|-------|-------------|--------------|
| `/devaing-director` | Every session | Project state + health audit + next step recommendation. Type `y` to execute the recommended skill. Full workflow navigable from a single command. |
| `/devaing-init` | Once per project | Creates repo, CI, GitHub Project, AGENTS.md, CONTEXT.md, CHECKPOINTS.md, seeds infrastructure. Kicks off Phase 1 via discovery interview. |
| `/devaing-phase-def` | Start of each phase | Discovery, epics, prototype, review loop, issue generation. Does not close until issues are created. |
| `/devaing-work` | Every build session | Claim an epic branch, implement via fresh sub-agent, self-verify AC + tests, optional adversarial review. Auto-merges epic to main on last issue. |
| `/devaing-phase-revise` | During implementation | Adjust scope, prototype, or business logic. Add a net-new feature area mid-phase. |
| `/devaing-ship` | Phase complete or hotfix ready | Deploy to prod: diff from last tag, ordered checklist (snapshot → migrations → seeds → code), git tag, archive shipped phases. |
| `/devaing-bug "..."` | When something breaks | Bug description → structured GitHub issue with diagnosis and regression test criteria. |
| `/devaing-help` | When disoriented | Framework reference: all 8 skills, typical flow, where to learn more. |

---

## Worked example

### Init (once per project)

```
/devaing-init cta-autos
```

Asks two questions: granularity (Broad / Balanced / Detailed) and prototyper (Claude / Stitch / MCP). Then runs a product discovery session — optional brainstorm followed by a structured interview. Writes CONTEXT.md from the answers.

Creates: GitHub repo, GitHub Project, triage labels, CI workflow, AGENTS.md, CHECKPOINTS.md, seeds infrastructure (`_seed_migrations` table + runner), and the portable `.devaing/skills/` layer.

Ends by calling `/devaing-phase-def` for Phase 1.

### Define a phase

```
/devaing-phase-def
```

Validates CONTEXT.md ("here's what I know — anything to correct?"), proposes epics for approval, builds prototype screens, enters a review loop. Adjust screens, epics, or business logic as many times as needed. On "looks good" → generates all issues in natural implementation order, creates GitHub milestones, adds issues to the Project board.

Does not close until issues are created.

### Build loop

```
/devaing-work #12
```

Per issue:

1. Checks for an orphaned branch from a prior session (offers to resume instead of starting over)
2. Reads `DESIGN.md` for design system tokens if it exists (Stitch output)
3. Spawns a **fresh sub-agent** with filtered CONTEXT.md + full issue + relevant prototype screen
4. Sub-agent commits to `epic/<slug>`, reports back
5. Self-verification: runs test suite, checks each acceptance criterion (y/n/partial)
6. If the diff touches migrations or seeds: `ce-data-integrity-guardian` reviews first
7. Adversarial review: enabled by default on the last issue in an epic — reviews the full epic diff, constructs failure scenarios
8. Updates CONTEXT.md, closes issue, moves Project card to Done
9. If last issue in epic: auto-merges `epic/<slug>` to main, deletes branch
10. If last issue in phase: compresses phase notes in CONTEXT.md

### Deploy

```
/devaing-ship
```

Reads last ship tag (`git tag --list "ship/*"`). First deploy: provisions prod, runs migrations + seeds, sets env vars. Incremental: diffs from last tag — code only = quick deploy; migrations or seeds or env var changes = full ordered checklist with DB snapshot first.

Tags the release (`ship/phase-1`), archives the phase to CONTEXT_ARCHIVE.md.

### Navigate without remembering commands

```
/devaing-director
```

Shows: project state, health audit (C1-C5 CHECKPOINTS), next unblocked task, recommended command. Type `y` to execute immediately. Someone who has never used devaing can navigate an entire phase from this one command.

---

## Phase lifecycle

Three skills move phase state. The other five operate within it.

| State | Triggered by | `/devaing-phase-def` | `/devaing-phase-revise` |
|-------|-------------|----------------------|-------------------------|
| No active phase | `devaing-init` (first time) or `devaing-ship` (phase archived) | ✓ starts new phase | ✗ no active phase |
| setup-interrupted | `devaing-phase-def` interrupted before prototype | ✓ resumes at prototype step | ✗ no issues yet |
| prototype-pending | `devaing-phase-def` complete, prototype awaiting approval | ✓ resumes review loop | ✗ no issues yet |
| implementing | `devaing-phase-def` generates issues and closes | ✗ definition closed | ✓ opens |
| phase-complete | `devaing-work` closes last issue in phase | ✗ | ✓ add something before ship |

`/devaing-phase-def` is available while no issues exist. The moment it generates issues, it closes — and `/devaing-phase-revise` opens. They never overlap.

---

## How it works

### Epic branches + ownership lock

Each GitHub milestone maps to a `epic/<slug>` branch. The first developer to claim an issue in the milestone becomes the owner — enforced via GitHub issue assignment. One person per epic eliminates merge conflicts within the epic while parallel work happens across epics (Dev A on `epic/auth`, Dev B on `epic/billing`).

Branch lifecycle: created lazily on first issue claim. Auto-merged to main when the last issue closes. Deleted after merge.

### Self-verification + adversarial review

After each sub-agent commit, devaing-work:

1. Detects and runs the project's test suite (`npm test` / `pytest` / `cargo test`)
2. Reads each `- [ ]` acceptance criterion from the issue, asks for y/n/partial confirmation
3. On the last issue in an epic: runs `ce-adversarial-reviewer` on the full epic diff — it constructs failure scenarios rather than pattern-matching against known issues. On failure: fix now (new sub-agent), document in Known limitations, or revert.

For diffs touching migration or seed files: `ce-data-integrity-guardian` runs before adversarial review — checks migration safety, data constraints, transaction boundaries.

### Health audit via CHECKPOINTS

`CHECKPOINTS.md` is committed to the project root by `devaing-init`. Five categories evaluated mechanically by `/devaing-director` on every run:

- **C1 — Setup integrity:** CONTEXT.md, .devaing.md, AGENTS.md, .devaing/skills/ all present
- **C2 — Phase coherence:** at most one phase In Progress; no closed milestone with open issues
- **C3 — Epic coherence:** no orphan issues (open issues without a milestone)
- **C4 — Branch coherence:** prod branch exists; no rogue work commits on main
- **C5 — Documentation coherence:** active phase has at least one open milestone

All clear = one line. Violations = `⚠` warnings before the status report.

### Prototype as living skeleton

The prototype built in phase-def is not deleted after review. Each devaing-work slice replaces one mock screen with real implementation; all other screens stay intact as scaffolding. Screens must be stateless and presentational — no local state, no API calls — so each is independently replaceable without touching adjacent screens.

When Stitch is used as the prototyper, it exports `DESIGN.md` (colors, typography, spacing, component patterns). devaing-work reads this before implementing any UI slice.

### Production-grade deployment

devaing-ship is the only path to prod. It derives everything from git state:

- **Ship tags** (`ship/*`) mark every deploy. The diff from the last tag tells ship exactly what changed.
- **Seed migrations** use a `_seed_migrations` table (same pattern as schema migrations) to track which reference data files have run. Never re-run, never manual.
- **First deploy** has two paths: provision fresh prod, or adopt an existing one (establish baseline without re-running anything already live).

### Multi-LLM portability

devaing-init copies all skill execution bodies to `.devaing/skills/` in your project and writes `.devaing/AGENTS.md` with a routing table:

```
.devaing/skills/work.md
.devaing/skills/phase-def.md
.devaing/skills/ship.md
.devaing/skills/director.md
...
```

Codex, Aider, Cursor, or any agent that can read files can drive the full devaing workflow. The `subagent_cli:` field in `.devaing.md` (default: `claude -p --model claude-sonnet-4-6`) controls the sub-agent invocation command.

---

## What lands in your repo

| File/Dir | Purpose |
|----------|---------|
| `CONTEXT.md` | Living truth: domain glossary, architecture, constraints, known limitations, phase state |
| `CHECKPOINTS.md` | Objective health criteria. Director audits them on every run. Human-readable for manual audits. |
| `.devaing.md` | Per-project config: granularity, prototyper, GitHub Project number, subagent_cli |
| `AGENTS.md` | Agent execution conventions: issue tracker, triage labels, domain docs, workflow spec, guardrails |
| `DESIGN.md` | Design system from Stitch: colors, typography, spacing, components (if using Stitch) |
| `.devaing/skills/` | Portable skill bodies for Codex/Aider/Cursor and other LLM runtimes |
| `.devaing/AGENTS.md` | Routing table for non-Claude Code runtimes |
| `docs/adr/` | Architecture Decision Records, created by devaing-work for non-obvious decisions |
| `docs/agents/` | Supporting agent docs: issue-tracker.md, triage-labels.md, domain.md |
| `prisma/seeds/` (or `db/seeds/`) | Seed migration runner + `_seed_migrations` tracking table |
| `.github/workflows/ci.yml` | CI pipeline created by init based on detected stack |
| `CONTEXT_ARCHIVE.md` | Shipped phases moved here by devaing-ship (keeps CONTEXT.md lean across many phases) |

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

# Linux — see cli.github.com/manual/installation
```

Authenticate:

```bash
gh auth login
```

**3. Compound Engineering plugin** (optional but recommended)

Provides `ce-adversarial-reviewer` and `ce-data-integrity-guardian`, used by devaing-work for review passes. devaing-work runs without it — review falls back to an inline adversarial prompt.

```bash
claude plugin install compound-engineering
```

If that fails:

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

Restart Claude Code. The eight `/devaing-*` skills load immediately.

**What the script does:** copies each `skills/devaing-*/` folder (SKILL.md + body.md) into `~/.claude/skills/`. SKILL.md is the thin adapter Claude Code reads at session start. body.md is the portable execution body — used as fallback when a project's `.devaing/skills/` does not have a local override.

---

## Design decisions

**No PRDs.** PRDs are expensive intermediaries nobody reads. Issues with acceptance criteria are the spec. ADRs capture non-obvious decisions after implementation, when the actual tradeoffs are known — not before, when they are speculation.

**Milestones are epics.** GitHub milestones group issues by epic. You navigate by milestone, not by flat issue list. Flat lists do not scale past 20 issues.

**Phases scope what gets built.** Each phase runs a full discovery cycle before generating issues. Future phases are defined when their phase starts, not upfront. Speculative backlogs rot before they are worked.

**Human validation at the right moments only.** Three gates in the full flow: the discovery interview, the epic list approval, and the prototype review. Everything else the agent executes without asking.

**Adversarial review, not pattern-matching.** The code reviewer constructs failure scenarios — what would break this, what edge case was missed — rather than checking against a known list of anti-patterns. It reviews the full epic diff at close, not just the last commit.

**Known limitations are first-class.** CONTEXT.md has a `## Known limitations` section — distinct from ADRs and constraints. Problems we know about and are not fixing yet: what the problem is, why it is deferred, what would trigger the fix. devaing-work prompts for this at every issue close.

---

## What devaing is NOT

- Not a replacement for Pocock or Compound Engineering in large teams
- Not a way to skip thinking (the discovery interview is mandatory and expensive — that is the investment)
- Not Jira (Jira is for human communication, outside the framework)
- Not vibe coding with structure added on top (the structure is intentional and non-negotiable)

---

## Development toolkit

The `scripts/` directory contains tools for validating and optimizing the trigger descriptions of any Claude Code skill. Useful when modifying devaing skills or building your own.

### Validate a skill

Checks frontmatter: required fields, allowed fields, kebab-case name, max 64-char name, max 1024-char description.

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

Iteratively improves the skill's trigger description to maximize invocation accuracy on a held-out query set. Opens a live HTML report in the browser.

```bash
python -m scripts.run_loop \
  --eval-set path/to/eval.json \
  --skill-path skills/<skill-name> \
  --model claude-opus-4-7 \
  --verbose
```

Key flags: `--max-iterations 5`, `--runs-per-query 3`, `--holdout 0.4`, `--results-dir ./results`

### Aggregate benchmark results

Reads `grading.json` files from run_eval output and writes `benchmark.json` and `benchmark.md`.

```bash
python -m scripts.aggregate_benchmark <benchmark_dir>
```
