---
name: devaing-bug
description: Report a bug in a devaing project. Converts a natural language description into a structured GitHub issue with diagnosis, assigns it to the relevant milestone, and marks it ready-for-agent. Invoked with /devaing-bug "description".
---

# devaing-bug

Convert a bug report into a structured, actionable GitHub issue ready for an agent to take.

## Opening — Welcome message

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-bug: logging a problem                             ║
╚══════════════════════════════════════════════════════════════╝

I'm going to turn your report into a structured task ready to fix.

Here's what's going to happen:

  1. Investigate the code to understand what's failing
  2. Propose the likely cause and how to verify the fix
  3. Log the problem formally
  4. Assign it to the right area of the project
```

## Step 1 — Read context

Read `CONTEXT.md` and the relevant code area related to the bug description.

## Step 2 — Investigate

Before creating the issue, investigate the codebase to find the probable cause:

- Locate the code path related to the reported behavior
- Identify the likely root cause
- Determine what a correct fix would look like
- Identify how to verify the fix works

If the root cause is not obvious after reading the code (ambiguous stack trace, intermittent behavior, multiple possible causes), invoke `diagnose` before proceeding. Let diagnose run its full loop: reproduce → minimise → hypothesise → instrument → fix. Use its findings to populate the issue.

## Step 3 — Assign milestone

Determine which epic/milestone this bug belongs to by comparing the affected area against the milestones:

```bash
gh api repos/{owner}/{repo}/milestones --jq '[.[] | {number, title}]'
```

If ambiguous, ask the user one question: "Is this in the '<option A>' or '<option B>' area?"

## Step 4 — Create issue

```bash
gh issue create \
  --title "Bug: <concise title>" \
  --milestone "<milestone>" \
  --label "ready-for-agent" \
  --body "$(cat <<'EOF'
## Observed behavior

<what the user described>

## Expected behavior

<what should happen instead>

## Steps to reproduce

1. <step>
2. <step>

## Root cause

<probable root cause from the investigation, including relevant code area>

## Proposed fix

<what to change and how to verify it works>

## Acceptance criteria

- [ ] <how to verify the bug is fixed>
- [ ] No regression in related functionality
EOF
)"
```

## Step 5 — Update CONTEXT.md

If the bug reveals a constraint, edge case, or architectural behavior not documented in CONTEXT.md, update the relevant section and commit:

```bash
git add CONTEXT.md
git commit -m "docs: update CONTEXT.md — constraint surfaced by bug #N"
git push
```

If nothing new emerged, skip.

## Closing

```
✓ Problem #<N> logged in area "<name>".

What's next?

  → To have an agent fix it now:
    /devaing-work #<N>
  → Or if urgent, ask me to implement the fix in this session.
```
