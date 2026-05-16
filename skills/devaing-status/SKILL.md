---
name: devaing-status
description: Show the current state of a devaing project and what to do next. Use when the user wants to know where they stand in the workflow, how many tasks are done, which epic is next, or what command to run. Also useful for getting oriented after returning to a project.
---

# devaing-status

Show project state and next step.

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
- `<has-issues>`: are there open or closed GitHub issues?

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

## Step 2 — Output status dashboard

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-status: <project-name>                             ║
╚══════════════════════════════════════════════════════════════╝
```

Then show the relevant block for the detected state:

---

### not-initialized

```
Status: Not initialized

No devaing setup found in this project.

Next step:

  /devaing-init
```

---

### no-active-phase

List closed phases, then:

```
Closed phases:
  Phase 1 "MVP" — Complete
  ...

Status: No active phase.

Next step:

  /devaing-phase-def         Start Phase <N>
  /devaing-ship              Deploy current code to prod
```

---

### setup-interrupted

```
Phase <N>: "<phase-name>" — In Progress
Epics: <epic1>, <epic2>, ...

Status: Phase setup was interrupted before the prototype was built.
        Discovery and epics are done. Prototype step never ran.

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

Next steps:

  /devaing-phase-def         Approved — generate the task backlog
  /devaing-phase-revise      Need to adjust something first
```

If prototyper is Stitch, add: `Review screens at the URLs in CONTEXT.md ## UX conventions.`

---

### implementing

Show per-epic progress, then next task:

```
Phase <N>: "<phase-name>" — In Progress

Progress:
  <epic-name>     ✓ <done>/<total>
  <epic-name>     ○ <done>/<total>
  ...
  Total: <done>/<total> tasks complete (<pct>%)

Next task:

  [ ] <task-slug> — <one-line description>
      Blocked by: <None or other task>

Next step:

  /devaing-work <task-slug-or-issue-number>
```

Derive progress from GitHub issues grouped by milestone.

Show the first unblocked pending task as "Next task". A task is unblocked if its "Blocked by" is None or all its blockers are checked/closed.

---

### phase-complete

```
Phase <N>: "<phase-name>" — All tasks complete ✓

  <done> tasks implemented across <N> epics.

Next step:

  /devaing-ship              Deploy to prod
  /devaing-phase-def         Start Phase <N+1>
```

---

## Closing

After the state block, always append a command reference. This is the same regardless of project state:

```
─────────────────────────────────────────────────────────────────

Commands

  SETUP    /devaing-init            One-time project setup
  PHASE    /devaing-phase-def       Discovery → epics → prototype → issues
  BUILD    /devaing-work            Implement next task (shows dependency list)
  ADJUST   /devaing-phase-revise    Fix scope, add new area, revise prototype
  REPORT   /devaing-bug "..."       Report something broken
  STATUS   /devaing-status          This screen
```
