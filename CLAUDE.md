# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Two things in one:
1. **The devaing framework** — seven Claude Code skills for hyper-agile product development (`skills/`). Read `STRATEGY.md` for the full framework design.
2. **A skill development toolkit** — Python scripts for validating, packaging, and optimizing the trigger description of any Claude Code skill (`scripts/`).

## Commands

### Validate a skill
```
python -m scripts.quick_validate skills/<skill-name>
```
Checks SKILL.md frontmatter: required fields `name` and `description`, allowed fields `name description license allowed-tools metadata compatibility`, kebab-case name, max 64 chars name / 1024 chars description.

### Package a skill into a .skill file
```
python -m scripts.package_skill skills/<skill-name>
python -m scripts.package_skill skills/<skill-name> ./dist
```
Produces a zip archive named `<skill-name>.skill`. Excludes `evals/` at skill root, `__pycache__`, `*.pyc`, `.DS_Store`. Runs validation before packaging.

### Run a trigger eval
```
python -m scripts.run_eval --eval-set path/to/eval.json --skill-path skills/<skill-name> --verbose
```
Eval set format: `[{"query": "...", "should_trigger": true/false}, ...]`

### Run the optimize loop
```
python -m scripts.run_loop --eval-set path/to/eval.json --skill-path skills/<skill-name> --model claude-opus-4-7 --verbose
```
Key flags: `--max-iterations 5`, `--runs-per-query 3`, `--holdout 0.4`, `--results-dir ./results`. Opens a live HTML report in the browser.

### Aggregate benchmark results
```
python -m scripts.aggregate_benchmark <benchmark_dir>
```
Reads `grading.json` files from `eval-N/with_skill/run-N/` and `eval-N/without_skill/run-N/` subdirectories. Writes `benchmark.json` and `benchmark.md`.

## Architecture

### Skill format

Every skill is a folder under `skills/` with a `SKILL.md`:
```yaml
---
name: kebab-case-name       # what users type as /name
description: one sentence   # what Claude sees when deciding to invoke
---
# Body seen only after invocation
```
The description is the only thing Claude evaluates when deciding whether to trigger the skill. The body is read after the decision.

### Description optimization pipeline

The core loop in `run_loop.py`:
1. `run_eval.py` — for each query, creates a temporary `.claude/commands/<skill-name>-<uuid>.md`, runs `claude -p <query> --output-format stream-json`, detects whether Claude calls `Skill` or `Read` with that file name, then deletes it. Uses `ProcessPoolExecutor` for parallel queries.
2. `improve_description.py` — calls `claude -p` (subprocess) with failing/false-triggering queries and history; asks for a new description under 1024 chars; retries if over limit.
3. Loop runs until all train queries pass or `--max-iterations` reached. Best description is chosen by test-set score (not final iteration).

The `CLAUDECODE` env var is stripped before each subprocess call — this is intentional to allow nesting `claude -p` inside a running Claude Code session.

### Skills in this repo (the devaing framework)

| Skill | Responsibility |
|-------|----------------|
| `devaing-init` | Bootstrap: repo, GitHub Project, CI, AGENTS.md, CONTEXT.md, `.devaing/skills/` portable layer, Phase 1 via devaing-phase-def |
| `devaing-phase-def` | Full phase definition loop: discovery, epics, prototype, review, issue generation. Does not exit until issues are created. Blocks devaing-phase-revise while open. |
| `devaing-phase-revise` | Adjust scope, prototype, or business logic during implementation. Blocked until devaing-phase-def has generated issues. |
| `devaing-work` | Implement issues on epic branches via sub-agent. Self-verify (tests + AC) and optional adversarial review before closing. Auto-merge epic to main when milestone closes. |
| `devaing-ship` | Deploy main to prod: detect changes since last tag, run migrations/seeds, verify env vars, tag release, archive shipped phases to CONTEXT_ARCHIVE.md. |
| `devaing-bug` | Convert a bug description into a structured issue with diagnosis and regression test criteria |
| `devaing-status` | Dashboard: current phase state, per-epic progress, next command to run |

Phases are the scoping unit. Each phase runs a full discovery cycle before generating issues. Tracking is always GitHub Issues + GitHub Projects — no local file alternative.

### What lives where

- `STRATEGY.md` — framework design, decision rationale, flows. Authoritative source. `STRATEGY.html` is a periodic human-facing snapshot, never auto-generated.
- `skills/<name>/SKILL.md` — thin adapter (5-10 lines). Claude Code reads this and delegates to `.devaing/skills/<name>.md` in the project, or falls back to `skills/<name>/body.md`.
- `skills/<name>/body.md` — portable skill body. No frontmatter. `devaing-init` copies these to `.devaing/skills/` in each project so other LLMs (Codex, Aider, Cursor) can follow the same flow. Diverges from SKILL.md only in sub-agent invocation style.
- `scripts/` — eval/optimize tooling. All scripts are runnable as `python -m scripts.<name>` from repo root.
- `scripts/__init__.py` — empty, makes `scripts/` a package so cross-script imports work.
