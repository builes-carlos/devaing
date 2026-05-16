---
name: devaing-phase-revise
description: Adjust the current phase or add a net-new feature area. Covers scope changes (issues wrong, missing, or excess), prototype revisions, business logic corrections, and adding functionality not in the original plan. Invoked with /devaing-phase-revise.
---

# devaing-phase-revise

Adjust scope, prototype, or business logic during implementation — or add a net-new feature area. Only available after /devaing-phase-def has generated issues.

## Opening — Welcome message

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-phase-revise                                       ║
╚══════════════════════════════════════════════════════════════╝

Adjust the current phase — scope, prototype, or business logic.

Use this command during implementation when something needs to change.
For pre-implementation adjustments, use /devaing-phase-def (which
handles prototype revisions inline before generating tasks).

Here's what's going to happen:

  1. Verify a phase is currently open
  2. Understand what needs adjusting
  3. Make the changes
  4. Confirm what changed

After revising, run /devaing-phase-def to generate the task backlog
(if tasks don't exist yet) or continue with /devaing-work.
```

## Step 0b — Read ship state

Before checking phase state, determine what's already in prod:

```bash
git tag --list "ship/*" | sort -V
```

If ship tags exist: store the most recent as `<last-ship-tag>`. This marks what's already in prod.
If no tags: prod has never been shipped to, or devaing-ship has not been run yet. Store `<last-ship-tag>` = none.

Output one line so the user knows the context:

```
Last shipped: <last-ship-tag> / not yet shipped to prod
```

## Step 0 — Verify phase is open and definition is closed

Read CONTEXT.md `## Phases`. Find the phase with status `In Progress`.

If none:

```
No open phase to revise.

  → To start a new phase: /devaing-phase-def
```

Stop.

Check whether any issues exist for this phase (open or closed):

```bash
gh issue list --state all --json number,milestone \
  --jq '[.[] | select(.milestone != null)] | length'
```

If 0 issues exist (definition not yet closed):

```
⛔ Phase "<name>" is still being defined — no tasks generated yet.

/devaing-phase-revise is only available after /devaing-phase-def closes.

Use /devaing-phase-def to adjust prototype, epics, or business logic
while the phase is being defined.
```

Stop.

Read the epic names from the `In Progress` row in `CONTEXT.md ## Phases`. For each epic milestone in the current phase, count closed issues:

```bash
gh issue list --milestone "<epic-name>" --state closed --json number --jq 'length'
```

Sum the counts across all current-phase epics. Use this total as the "already closed" count. Do not include issues from other phases.

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
  4. New area  — add functionality that wasn't in the original plan
  5. Multiple  — describe everything
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

**New area:**

Ask these four questions and wait for all answers:

```
Before generating issues:

1. What problem does this feature solve for the user?
2. Who uses it and in what situation?
3. What is explicitly out of scope?
4. Are there any technical or business constraints to respect?
```

If any answer contradicts something in `CONTEXT.md`, flag it before continuing.

Determine if the feature fits an existing milestone or requires a new one:

```bash
gh api repos/{owner}/{repo}/milestones --jq '[.[] | {number, title}]'
```

If unclear, ask: "Is this an extension of `<existing milestone>` or a new area?"

Create a milestone if needed:

```bash
gh api repos/{owner}/{repo}/milestones --method POST \
  --field title="<name>" \
  --field description="<description>"
```

Generate vertical slices in dependency order and publish each as a GitHub issue with `ready-for-agent` label, the same `## What / ## Acceptance criteria / ## Blocked by` body format used by other issues in this project. If `<last-ship-tag>` is set and is not 'none' (i.e., at least one actual ship tag exists), add a note at the top of each issue body: `> Post-ship addition — not in prod as of <last-ship-tag>.`

After all issues are created, register GitHub-native dependencies via REST API (same approach as in devaing-phase-def Step 9): fetch internal integer IDs, then POST to `/issues/<blocked>/dependencies/blocked_by` with `-F issue_id=<blocker-internal-id>`.

Update `CONTEXT.md` if the new area introduces domain terms, architectural components, or constraints not already documented.

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

Check whether the task backlog exists:
Check whether there are any open issues in the current phase milestones.

**If no tasks exist yet** — this state should not be reached (Step 0 blocks it). If somehow reached, redirect:

```
  → /devaing-phase-def to finish defining the phase.
```

**If tasks already exist (implementation is underway):**

```
╔══════════════════════════════════════════════════════════════╗
║  Phase revised. Ready to build.                             ║
╚══════════════════════════════════════════════════════════════╝

  /devaing-phase-revise     Revise again if needed
  /devaing-work #N          Implement a task
  /devaing-bug              Report something broken
  /devaing-phase-revise     Add something not in the current plan (New area)

When the new issues are implemented and tested in dev:

  /devaing-ship             Deploy additions to prod

Not available yet:

  /devaing-phase-def        Blocked — current phase has open issues.
```
