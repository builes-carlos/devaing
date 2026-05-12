---
name: devaing-phase-revise
description: Adjust the current phase before or during implementation. Covers scope changes (issues wrong, missing, or excess), prototype revisions, and business logic corrections discovered after grill-me. Invoked with /devaing-phase-revise.
---

# devaing-phase-revise

Adjust the current phase — scope, prototype, or business logic — before writing more code.

## Language override

All output from this skill — questions, inline messages, report tables, generated file content, and code comments — MUST be in English. This overrides any global language setting (including "Respond in Spanish").

## Opening — Welcome message

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-phase-revise                                       ║
╚══════════════════════════════════════════════════════════════╝

Let's adjust the phase before building.

Here's what's going to happen:

  1. Verify a phase is currently open
  2. Understand what needs adjusting
  3. Make the changes
  4. Confirm what changed
```

## Step 0 — Verify phase is open

Read CONTEXT.md `## Phases`. Find the phase with status `In Progress`.

If none:

```
No open phase to revise.

  → To start a new phase: /devaing-phase "<name>"
```

Stop.

Check how many issues are already closed in the current phase:

```bash
gh issue list --milestone "<epic-name>" --state closed --json number,title \
  --jq 'length'
```

If any issues are already closed (implementation started), warn:

```
⚠ Implementation has already started — <N> issues are closed.
  Revising scope may conflict with work already done.
  Continue? (y/n)
```

## Step 1 — Read current state

Read `CONTEXT.md` completely. Read all open and closed issues for the current phase milestones. Load the prototype if it exists.

## Step 2 — Understand what needs adjusting

Ask:

```
What needs adjusting?

  1. Scope     — epics or issues that are wrong, missing, or should be cut
  2. Prototype — screens that don't make sense or need redesign
  3. Business  — something that changed the plan since discovery
  4. Multiple  — describe everything
```

Wait for response. Ask follow-up questions until the full scope of the adjustment is clear.

## Step 3 — Make adjustments

**Scope changes:**

- Add issue:
```bash
gh issue create --title "<title>" --milestone "<epic>" --label "ready-for-agent" \
  --body "$(cat <<'EOF'
## What to build
<behavior>

## Acceptance criteria
- [ ] <criterion>

## Blocked by
<#N or "None">
EOF
)"
```

- Remove issue (not yet started):
```bash
gh issue close <N> --comment "Removed from phase during revision: <reason>"
```

- Modify issue:
```bash
gh issue edit <N> --title "<new title>"
gh issue comment <N> --body "Scope updated: <what changed and why>"
```

Update `CONTEXT.md ## Epics` if an epic was added or removed from this phase.

**Prototype changes:**

Invoke `prototype` for the affected screens only. Do not touch screens from previous phases or unrelated screens. After validation, update `CONTEXT.md ## UX conventions` if interaction patterns changed.

**Business logic changes:**

Update the relevant sections of `CONTEXT.md` (glossary, architecture, constraints). If the change affects existing open issues, update those issues with a comment explaining what changed.

## Step 4 — Confirm changes

Show a summary:

```
Changes made:

  Issues added:    #N <title>
  Issues removed:  #N <title>
  Issues modified: #N <title>
  Prototype:       <screen> revised
  CONTEXT.md:      <section> updated
```

Commit:

```bash
git add CONTEXT.md
git commit -m "docs: phase revision — <one-line summary>"
git push
```

## Closing

```
╔══════════════════════════════════════════════════════════════╗
║  Phase revised. Ready to build.                             ║
╚══════════════════════════════════════════════════════════════╝

Available now:

  /devaing-phase-revise     Revise again if needed
  /devaing-work #N          Implement a task
  /devaing-bug              Report something broken
  /devaing-feature          Add something not in the current plan

Not available yet:

  /devaing-phase            Blocked — current phase has open issues.
```
