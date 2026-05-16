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

