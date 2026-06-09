# devaing-director

Show project state, run health checks, and offer to execute the next step.

## Opening

Read the following files silently before outputting anything:
1. `CONTEXT.md` — project name, phases table, UX conventions section
2. `.devaing.md` — granularity, prototyper

Do not output any text until the state is fully determined.

## Step 1 — Determine state

From what you read, determine:

- `<project-name>`: first sentence from `CONTEXT.md ## Project`
- `<prototyper>`: from `.devaing.md`. Default: Claude
- `<active-phase>`: the row in `## Phases` with status `In Progress`, if any
- `<has-ux-conventions>`: does `CONTEXT.md` contain `## UX conventions`?

Run:
```bash
gh issue list --state all --json number,title,state,milestone,body \
  --jq '.[] | {number, title, state, milestone: .milestone.title, body}'
```

Classify into one of these states:

| State ID | Condition |
|----------|-----------|
| `not-initialized` | CONTEXT.md missing or `## Phases` has no data rows |
| `no-active-phase` | All phases are Complete or no phases exist |
| `setup-interrupted` | Phase In Progress + no UX conventions + no open issues |
| `prototype-pending` | Phase In Progress + UX conventions exist + no open issues |
| `implementing` | Phase In Progress + open issues exist |
| `phase-complete` | Phase In Progress + all issues closed |

## Step 2 — Health audit

Run these checks silently. Collect failures in two buckets:
- `<health-issues>`: C1–C5 — coherence and setup integrity
- `<quality-issues>`: C6–C8 — fixable setup quality gaps

**C1 — Setup integrity**
```bash
test -f CONTEXT.md || \
  echo "C1: CONTEXT.md missing → run /devaing-init"
test -f .devaing.md && grep -q "^granularity:" .devaing.md && \
  grep -q "^prototyper:" .devaing.md || \
  echo "C1: .devaing.md missing or incomplete → run /devaing-init"
grep -q "devaing-work" AGENTS.md 2>/dev/null || \
  echo "C1: AGENTS.md missing devaing section → run /devaing-init"
test -d .devaing/skills && ls .devaing/skills/*.md >/dev/null 2>&1 || \
  echo "C1: .devaing/skills/ missing or empty → run /devaing-init (Step C will copy missing skills)"
```

**C2 — Phase coherence**
```bash
count=$(grep -c "In Progress" CONTEXT.md 2>/dev/null || echo 0)
[ "$count" -gt 1 ] && \
  echo "C2: $count phases marked In Progress → edit CONTEXT.md ## Phases, mark all but one as Complete"
```

```bash
gh milestone list --state closed --json title --jq '.[].title' 2>/dev/null | while read m; do
  open=$(gh issue list --milestone "$m" --state open --json number --jq 'length' 2>/dev/null)
  [ "${open:-0}" -gt 0 ] && \
    echo "C2: Milestone '$m' is closed but has $open open issue(s) → close or reassign them"
done
```

**C3 — Epic coherence**
```bash
orphans=$(gh issue list --state open --json number,milestone \
  --jq '[.[] | select(.milestone == null) | .number] | join(", ")' 2>/dev/null)
[ -n "$orphans" ] && \
  echo "C3: open issue(s) with no milestone: #$orphans → assign with: gh issue edit #N --milestone \"epic-name\""
```

**C4 — Branch coherence**
```bash
git rev-parse --verify prod >/dev/null 2>&1 || \
  echo "C4: prod branch missing → run /devaing-init (creates and pushes the prod branch)"
```

**C5 — Documentation coherence**
```bash
if grep -q "In Progress" CONTEXT.md 2>/dev/null; then
  open_milestones=$(gh milestone list --state open --json title --jq 'length' 2>/dev/null || echo 0)
  [ "${open_milestones:-0}" -eq 0 ] && \
    echo "C5: phase is In Progress but no open milestones found → run /devaing-phase-def or check CONTEXT.md ## Phases"
fi
```

**C6 — CONTEXT.md size**
```bash
lines=$(wc -l < CONTEXT.md 2>/dev/null || echo 0)
[ "$lines" -gt 200 ] && \
  echo "C6: CONTEXT.md is $lines lines (limit: 200) → split feature details to docs/features/<slug>.md, keep one-liner + pointer [manual]"
```

**C7 — CLAUDE.md quality**
```bash
if [ -f CLAUDE.md ]; then
  grep -q "## Critical Patterns" CLAUDE.md || \
    echo "C7: CLAUDE.md missing '## Critical Patterns' [auto-fix]"
  grep -q "## Tactical anti-patterns" CLAUDE.md || \
    echo "C7: CLAUDE.md missing '## Tactical anti-patterns' [auto-fix]"
fi
```

**C8 — Operational skills**
```bash
skill_count=$(find .claude/skills -maxdepth 2 -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
[ "${skill_count:-0}" -eq 0 ] && \
  echo "C8: no operational skills in .claude/skills/ [fixable with input]"
```

## Step 3 — Output dashboard

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-director: <project-name>                           ║
╚══════════════════════════════════════════════════════════════╝
```

**Health block:** if both `<health-issues>` and `<quality-issues>` are empty, output one line:
```
Health: ✓ all checks OK
```
If `<health-issues>` is non-empty, list each as a warning with its fix inline:
```
Health:
  ⚠ C1: .devaing/skills/ missing or empty → run /devaing-init (Step C will copy missing skills)
  ⚠ C4: prod branch missing → run /devaing-init (creates and pushes the prod branch)
```
If `<quality-issues>` is non-empty, show them after health (or alone if health is clear):
```
Health: ✓ coherence OK
Quality:
  ⚡ C7: CLAUDE.md missing '## Critical Patterns' [auto-fix]
  ⚡ C8: no operational skills in .claude/skills/ [fixable with input]
```

Then show the relevant state block:

---

### not-initialized

```
Status: Not initialized

No devaing setup found.

Next step:

  /devaing-init
```

---

### no-active-phase

List closed phases (from CONTEXT.md), then:

```
Closed phases:
  Phase 1 "MVP" — Complete
  ...

Status: No active phase.

Next step:

  /devaing-phase-def         Start Phase <N> — new features, epics, prototype
  /devaing-ship              Deploy current code to prod

Also available:

  /devaing-bug "..."         Something is broken
  /devaing-work              Small addition without a new phase (choose Hotfix when prompted)
```

---

### setup-interrupted

```
Phase <N>: "<phase-name>" — In Progress
Epics: <epic1>, <epic2>, ...

Status: Phase setup was interrupted before the prototype was built.

Next step:

  /devaing-phase-def         Resume — will pick up at prototype step
```

---

### prototype-pending

```
Phase <N>: "<phase-name>" — In Progress
Epics: <epic1>, <epic2>, ...
Prototyper: <prototyper>

Status: Prototype is ready. Waiting for your review before generating tasks.
        Adjust epics, screens, or business logic inside the review loop.

Next step:

  /devaing-phase-def         Resume — approve or adjust prototype, then generate issues
```

If prototyper is Stitch: add `Review screens at the URLs in CONTEXT.md ## UX conventions.`

---

### implementing

Group issues by milestone. For each epic: total, closed, open. Show first unblocked pending task.

A task is unblocked if its body has no `Blocked by: #N` referencing an open issue.

```
Phase <N>: "<phase-name>" — In Progress

Progress:
  <epic-name>     ✓ <closed>/<total>   (<open> remaining)
  <epic-name>     ○ <closed>/<total>   (<open> remaining)
  ...
  Total: <done>/<total> tasks complete (<pct>%)

Next task:

  [ ] #<N> — <one-line description>
      Epic: <epic-name>
      Blocked by: <None or #N>

Recommended:

  /devaing-work #<N>

Also available:

  /devaing-phase-revise      Adjust scope, prototype, or add a new area
  /devaing-bug "..."         Report something broken
```

---

### phase-complete

```
Phase <N>: "<phase-name>" — All tasks complete ✓

  <done> tasks implemented across <N> epics.

Recommended:

  /devaing-ship              Deploy to prod
  /devaing-phase-def         Start Phase <N+1>

Also available:

  /devaing-bug "..."         Report something found during QA
```

---

## Step 4 — Offer execution

After the state block, ask:

```
─────────────────────────────────────────────────────────────────
Execute recommended step now? [y/n]
```

Wait for response.

- **y**: invoke the recommended skill using the `Skill` tool.
  - `implementing` → `Skill(skill="devaing-work", args="#<N>")` where `#<N>` is the first unblocked task.
  - `setup-interrupted` or `prototype-pending` → `Skill(skill="devaing-phase-def")`
  - `phase-complete` → `Skill(skill="devaing-ship")`
  - `no-active-phase` → `Skill(skill="devaing-phase-def")`
  - `not-initialized` → `Skill(skill="devaing-init")`

  **If not running in Claude Code** (no Skill tool available): read `.devaing/skills/<target>.md`
  and execute it step by step in the current conversation.

- **n**: output the command reference and stop.

## Step 4b — Fix quality gaps (conditional)

Skip if `<quality-issues>` is empty.

Output:

```
─────────────────────────────────────────────────────────────────
Quality gaps detected. Fix now? [y/n]
```

Wait for response.

**y**: Fix each gap in sequence:

- **C6 (CONTEXT.md > 200 lines)**: Explain the docs/features/ pattern. Feature details (state machines, file paths, SQL specifics, edge cases) move to `docs/features/<slug>.md`; CONTEXT.md keeps one line + pointer per feature. Ask which section to start with, then do the split.

- **C7 (missing `## Critical Patterns`)**: Append to CLAUDE.md:
  ```markdown
  ## Critical Patterns

  <!-- Code-level API-misuse patterns: Wrong: `<bad call>`. Correct: `<good call>`. -->
  ```

- **C7 (missing `## Tactical anti-patterns`)**: Append to CLAUDE.md:
  ```markdown
  ## Tactical anti-patterns

  <!-- Wrong patterns that caused bugs: **<name>**: <wrong> → <correct>. [Why: <reason>] -->
  ```

- **C8 (no operational skills)**: Ask which workflows to scaffold (push/deploy, migration, feature scaffold, debug, review). For each selected: create `.claude/skills/<name>/SKILL.md` as a skeleton pre-filled with project name, deploy mechanism, and migration path from CONTEXT.md.

**n**: skip.

## Step 5 — Command reference (always shown on n, or if state is not-initialized)

```
─────────────────────────────────────────────────────────────────

Commands

  HELP     /devaing-help            Framework overview and command reference
  SETUP    /devaing-init            One-time project setup
  PHASE    /devaing-phase-def       Discovery → epics → prototype → issues
  BUILD    /devaing-work            Implement next task
  ADJUST   /devaing-phase-revise    Fix scope, add new area, revise prototype
  DEPLOY   /devaing-ship            Deploy to prod
  REPORT   /devaing-bug "..."       Report something broken
  STATUS   /devaing-director        This screen
```
