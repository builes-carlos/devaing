---
name: devaing-feature
description: Add a new feature area to an existing devaing project. Creates a GitHub milestone, generates vertical slice issues, and updates CONTEXT.md. Use when the user wants to add functionality not covered in the initial discovery. Invoked with /devaing-feature "description".
---

# devaing-feature

Add a new feature area to an existing devaing project.

## Language override

All output from this skill — questions, inline messages, report tables, generated file content, and code comments — MUST be in English. This overrides any global language setting (including "Respond in Spanish").

## Opening — Welcome message

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-feature: adding new functionality                  ║
╚══════════════════════════════════════════════════════════════╝

I'm going to break your idea into concrete tasks ready to build.

Here's what's going to happen:

  1. Read the current state of the project
  2. Ask a few questions to understand what you want
  3. Determine if it fits an existing area or needs a new one
  4. Generate the work tasks
  5. Update the project map
```

## Step 1 — Read context

Read `CONTEXT.md` completely. Understand the existing domain, architecture, constraints, and epics.

## Step 1b — Scope discovery

Ask these four questions before proceeding. Wait for all answers:

```
Before generating issues, I need to understand the scope:

1. What problem does this feature solve for the user?
2. Who uses it and in what situation?
3. What is explicitly out of scope?
4. Are there any technical or business constraints to respect?
```

Use the answers to inform issue generation. If any answer contradicts something in CONTEXT.md, flag it before continuing.

## Step 2 — Evaluate scope

Determine if the feature fits an existing milestone or requires a new one:

```bash
gh api repos/{owner}/{repo}/milestones --jq '[.[] | {number, title}]'
```

- **Fits existing milestone:** add issues to that milestone, skip milestone creation.
- **New area:** create a new milestone.

If unclear, ask the user one question: "Is this an extension of '<existing milestone>' or a new area?"

## Step 3 — Create milestone if needed

```bash
gh api repos/{owner}/{repo}/milestones --method POST \
  --field title="<feature-name>" \
  --field description="<feature-description>"
```

## Step 4 — Generate issues

Derive vertical slices from the feature description and CONTEXT.md context. No quiz, no PRD. Publish directly.

For each slice:

```bash
gh issue create \
  --title "<title>" \
  --milestone "<milestone>" \
  --label "ready-for-agent" \
  --body "$(cat <<'EOF'
## What to build

<end-to-end behavior description>

## Acceptance criteria

- [ ] <criterion>

## Blocked by

<#N or "None - can start immediately">
EOF
)"
```

Publish in dependency order.

## Step 5 — Update CONTEXT.md

If the feature introduces new domain terms, architectural components, or constraints not already in CONTEXT.md, update the relevant sections and commit:

```bash
git add CONTEXT.md
git commit -m "docs: update CONTEXT.md for <feature-name>"
git push
```

If nothing new emerged, skip.

## Closing

Show a table of issues created with their numbers, titles, and blockers. Then:

```
✓ <N> tasks created in "<name>".

What's next?

  → To implement the first task:
    /devaing-work "<name>"
```
