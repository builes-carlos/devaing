---
name: devaing-phase
description: Kick off a new phase in a devaing project. Verifies the previous phase is closed, runs incremental discovery, defines epics for this phase, generates issues, and extends the prototype. Called internally by /devaing-init for Phase 1. Invoked with /devaing-phase "phase-name" for subsequent phases.
---

# devaing-phase

Kick off a phase: discovery, epics, prototype, issues.

## Language override

All output from this skill — questions, inline messages, report tables, generated file content, and code comments — MUST be in English. This overrides any global language setting (including "Respond in Spanish").

## Opening — Welcome message

Resolve the phase number first (read `## Phases` in CONTEXT.md — count existing entries + 1), then output:

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-phase: Phase <N> — "<phase-name>"                  ║
╚══════════════════════════════════════════════════════════════╝

Here's what's going to happen:

  1. Verify the previous phase is fully closed
  2. Discover what this phase covers
  3. Define and approve the epics
  4. Build or extend the prototype
  5. Generate the tasks
```

## Step 0 — Phase state check

Read CONTEXT.md `## Phases`.

- If `## Phases` does not exist or has no entries: **Phase 1**. Skip this check entirely.
- If any phase has status `In Progress`:

```
⛔ Phase "<name>" is still open.

Close all open issues before starting a new phase.

  Open issues:
    #N <title> — <milestone>
    ...

Available now:
  /devaing-work #N          Implement an open task.
  /devaing-phase-revise     Adjust scope, prototype, or business logic.
  /devaing-bug              Report something broken.
  /devaing-feature          Add something not in the current plan.
```

Stop. Do not proceed.

## Step 1 — Phase name and granularity

If invoked from `/devaing-init`: use the phase name provided there. Skip this step.

Otherwise ask:

```
Phase name? (e.g., "MVP", "Beta", "V2")
```

Then ask granularity:

```
How detailed should the tasks be for this phase?

  1. Broad    — 2-4 tasks per area. Move fast.
  2. Balanced — 3-6 tasks per area. One task = one user action.
  3. Detailed — 6-12 tasks per area. Every edge case covered.
```

Store as `<granularity>`.

## Step 2 — Read existing context

Read `CONTEXT.md` completely. Read `docs/adr/` for recent decisions. If Phase 2+, read closed issues from the previous phase to understand what was already built.

## Step 3 — Model gate (upgrade)

```
╔══════════════════════════════════════════════════════════════╗
║         MODEL UPGRADE RECOMMENDED                           ║
╠══════════════════════════════════════════════════════════════╣
║  Next step (discovery) defines this entire phase.           ║
║  Consider switching to a more capable model first.          ║
╚══════════════════════════════════════════════════════════════╝

To switch models: /model

Type 'continue' when ready.
```

## Step 4 — Discovery

**Phase 1:** invoke `grill-me` with:

> "Dump everything you have about <name>. Notes, screenshots, mockups, competitor references, prior work, half-baked ideas — paste text directly here, or if you have files on disk (images, PDFs, docs), add them to the project files first so I can read them. Then tell me everything. I'll read it all and start asking questions."

Do NOT suggest a format. Do NOT ask a specific question yet. Let the user dump everything first, then ask targeted follow-ups.

**Phase 2+:** do NOT run a full grill-me. Ask directly:

> "Phase <N-1> is done. Here's what we built: [brief summary from CONTEXT.md and closed issues]. What's new in this phase? What changed? What did we defer that's now in scope? Any new constraints or business decisions since then?"

Run until the user signals done.

## Step 5 — Update CONTEXT.md

Update glossary, architecture, and constraints with what was learned. Commit:

```bash
git add CONTEXT.md
git commit -m "docs: populate CONTEXT.md from Phase <N> discovery"
git push
```

## Step 6 — Define epics for this phase

Synthesize the epic list from discovery + the annotated `## Next phase backlog` in CONTEXT.md. Do NOT re-interview.

Present and wait for approval:

```
Based on the discovery, I propose these epics for "<phase-name>":

1. **<name>** — <one sentence>
2. **<name>** — <one sentence>
...

Anything missing, wrong, or out of scope for this phase?
```

After approval:

1. Update `CONTEXT.md ## Phases`:

```markdown
## Phases

| Phase | Name | Status | Epics |
|-------|------|--------|-------|
| <N> | <phase-name> | In Progress | <epic1>, <epic2>, ... |
```

2. If next-phase epics were identified during discovery, annotate in `CONTEXT.md ## Next phase backlog`:

```markdown
## Next phase backlog

- Phase <N+1> — <epic name> — <one-line description>
```

3. **Admin panel rule:** verify the epic list contains an admin panel epic. If not, add one automatically and tell the user:

```
Adding required epic: Admin Panel
All system configuration must live in the DB, not in code.
```

4. If `<tracking>` is **GitHub**: create one milestone per epic:

```bash
gh api repos/<owner>/<name>/milestones --method POST \
  --field title="<epic-name>" \
  --field description="<epic-description>"
```

5. Commit:

```bash
git add CONTEXT.md
git commit -m "docs: define Phase <N> epics"
git push
```

## Step 7 — Prototype

**Phase 1:** for each epic with UI, ask:

```
Epic "<name>" has UI. Prototype the interaction before generating issues? (y/n)
```

If yes: invoke `prototype` for that epic. After validation, document agreed UX decisions in `CONTEXT.md ## UX conventions`. Keep the prototype as a **living skeleton** — mock screens are replaced progressively by `/devaing-work` slices. Do not delete unimplemented screens.

**Phase 2+:** the prototype skeleton already exists. For each epic with UI in this phase, add the new screens as mocks to the existing skeleton. Do not touch screens already implemented in previous phases. Ask the user to review the updated prototype before proceeding.

Commit:

```bash
git add CONTEXT.md
git commit -m "docs: UX conventions from prototype — Phase <N>"
git push
```

## Step 8 — Model gate (downgrade)

```
╔══════════════════════════════════════════════════════════════╗
║         DISCOVERY COMPLETE                                  ║
╠══════════════════════════════════════════════════════════════╣
║  Next: task generation. You can switch to a lighter model.  ║
╚══════════════════════════════════════════════════════════════╝

To switch models: /model

Type 'continue' when ready.
```

## Step 9 — Generate issues

For each epic in order, generate all vertical slices calibrated to `<granularity>`:

- **Broad**: 2-4 slices per epic. 2-3 high-level acceptance criteria.
- **Balanced**: 3-6 slices per epic. 4-6 specific acceptance criteria.
- **Detailed**: 6-12 slices per epic. Full acceptance criteria including negative paths.

**If `<tracking>` is GitHub**: publish in dependency order.

```bash
gh issue create \
  --title "<title>" \
  --milestone "<epic-name>" \
  --label "ready-for-agent" \
  --body "$(cat <<'EOF'
## What to build

<end-to-end behavior, not layer-by-layer. No file paths.>

## Acceptance criteria

- [ ] <criterion>

## Blocked by

<#N or "None - can start immediately">
EOF
)"
```

**If `<tracking>` is Local**: append to `BACKLOG.md` under a new phase section:

```markdown
## Phase <N>: <phase-name>

### [Epic] <epic-name>
> <epic-description>

- [ ] **<slice-slug>** — <one-line description>
  - What: <end-to-end behavior>
  - Criteria: <criterion> / <criterion>
  - Blocked by: None / <slice-slug>
```

Commit:

```bash
git add BACKLOG.md
git commit -m "docs: generate Phase <N> slice backlog (<granularity>)"
git push
```

## Closing

```
╔══════════════════════════════════════════════════════════════╗
║  Phase <N> "<phase-name>" is ready.                         ║
╚══════════════════════════════════════════════════════════════╝

Before building, review the prototype.
If anything looks wrong — scope, flows, business logic — fix it now:

  /devaing-phase-revise

Available now:

  /devaing-phase-revise     Adjust scope, prototype, or business logic
  /devaing-work #N          Implement a task end-to-end
  /devaing-bug              Report something broken
  /devaing-feature          Add something not in the current plan

Not available yet:

  /devaing-phase            Blocked — Phase <N> has open issues.
                            Close all tasks first, then start the next phase.
```
