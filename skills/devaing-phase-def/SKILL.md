---
name: devaing-phase-def
description: Define a new phase end-to-end: discovery, epics, prototype, review loop, and issue generation. Owns the full definition process — from first question to closed backlog. /devaing-phase-revise is only available after this command closes. Invoked with /devaing-phase-def (no argument needed).
---

# devaing-phase-def

Define a phase completely: discovery → epics → prototype → review loop → issues.

This command does not stop until the phase is fully defined (issues generated). Prototype revisions are handled inline — no need to jump to another command. Once issues are created, /devaing-phase-def blocks and /devaing-phase-revise becomes available.

## Opening — Welcome message

Output immediately, before reading any files:

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-phase-def                                          ║
╚══════════════════════════════════════════════════════════════╝

Here's what's going to happen:

  1. Check current phase state
  2. Discover what this phase covers
  3. Define and approve the epics
  4. Build the prototype
  5. Review loop — adjust until satisfied
  6. Generate tasks and close the definition

If you're re-running this command, it detects where you left off
and picks up from there automatically.
```

## Step 0 — Phase state check

Read CONTEXT.md `## Phases`.

- If `## Phases` does not exist or has no entries: **Phase 1**. Skip this check entirely.
- If any phase has status `In Progress`: determine the setup state before doing anything else.

**Setup state matrix:**

| `## UX conventions` in CONTEXT.md | Open issues exist | State | Action |
|---|---|---|---|
| No | No | Interrupted before prototype | Resume at Step 7 |
| Yes | No | Prototype built, in review | Resume review loop (Step 7b) |
| — | Yes | Definition closed — active phase | Block |

**Interrupted (no UX conventions, no issues):** Output, then skip to Step 7:

```
⚠️  Phase "<name>" setup was interrupted before the prototype.

Epics already approved: <epic1>, <epic2>, ...

Resuming from prototype step. No re-discovery needed.
```

**Prototype built, review not finished (UX conventions exist, no issues):** Skip directly to Step 7b (review loop). Do not re-generate the prototype.

**Active phase (issues exist):** Output, then stop:

```
⛔ Phase "<name>" is already defined — <N> open tasks.

/devaing-phase-def is blocked while tasks are open.

Available now:
  /devaing-work #N          Implement an open task.
  /devaing-phase-revise     Adjust scope, prototype, or business logic.
  /devaing-bug              Report something broken.
  /devaing-phase-revise     Add something not in the current plan (New area).
```

Stop. Do not proceed.

## Step 1 — Phase name and granularity

If invoked from `/devaing-init`: use the phase name provided there. Skip this step.

Read `CONTEXT.md ## Phases`. Count closed phases. The new phase number is N = (closed count + 1).

If there are closed phases, list them for context. Then ask:

```
Closed phases: Phase 1 "MVP" — Complete

What should we call Phase <N>? (e.g., "Beta", "V2", "Pro")
```

If no closed phases yet:

```
What should we call Phase 1? (e.g., "MVP", "Beta", "V2")
```

Wait for response. Store as `<phase-name>`.

Then check `.devaing.md` for a `granularity:` line. If found, use that value and skip the question. Only ask if not found:

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

4. Create one milestone per epic:

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

Read `.devaing.md` for `prototyper:`. Default to `Claude` if not set. Store as `<prototyper>`.

---

### If `<prototyper>` is Claude

**Phase 1:** for each epic with UI, ask:

```
Epic "<name>" has UI. Prototype the interaction before generating issues? (y/n)
```

If yes: invoke `prototype` for that epic. After validation, document agreed UX decisions in `CONTEXT.md ## UX conventions`. Keep the prototype as a **living skeleton** — mock screens are replaced progressively by `/devaing-work` slices. Do not delete unimplemented screens.

Prototype screens must be stateless and presentational: no local state, no API calls, no hardcoded data beyond display fixtures.

**Phase 2+:** the prototype skeleton already exists. For each epic with UI in this phase, add the new screens as mocks to the existing skeleton. Do not touch screens already implemented in previous phases.

---

### If `<prototyper>` is Stitch

Before generating screens, verify the Stitch MCP is available by checking if any `mcp__stitch__*` tools are accessible.

If Stitch MCP is NOT available, output and wait:

```
⚠️  Stitch MCP is not connected.

How would you like to proceed?

  1. Build with Claude   — prototype skill builds stateless mock screens now.
  2. Skip prototype      — go straight to task generation. Add UX later with /devaing-phase-revise.
  3. Connect Stitch first — instructions below.
```

- If 1: proceed as Claude prototyper (invoke `prototype` skill).
- If 2: skip to Step 9 (no UX conventions written).
- If 3: output the following, then stop:

```
Steps to connect Stitch:

  1. Create a free account: stitch.withgoogle.com
  2. Generate an API key: Settings → API Keys → New key
  3. Save the key so Claude Code can read it:

     If you use the Claude Code desktop app (Windows):
       Add an "env" block to ~/.claude/settings.json:
         "env": { "STITCH_API_KEY": "<your-key>" }
       Then restart the app.

     If you launch Claude Code from a terminal (claude CLI):
       Windows:  setx STITCH_API_KEY "<your-key>"
       Mac/Linux: echo 'export STITCH_API_KEY="<your-key>"' >> ~/.zshrc
       Then close the terminal, open a new one, and relaunch.

     Note: setx does NOT work for the desktop app — the app does not
     inherit terminal environment variables.

~/.claude/.mcp.json must have the Stitch entry. Run /devaing-init
if you haven't already — it writes it automatically.

Re-run /devaing-phase-def when you're back.
```

If Stitch MCP IS available, use the Stitch MCP tools to generate screens for each epic with UI.

For each epic with UI, call the available `mcp__stitch__*` tools to:
1. Create a Stitch project (or reuse the existing one for this project)
2. Generate screens covering the main user flows for this epic, passing:
   - Epic name and description
   - Relevant constraints and UX context from `CONTEXT.md`
3. Collect the returned screen URLs

After all epics are done:
- Export `DESIGN.md` from the Stitch project (use the available export tool)
- Save it to the project root as `DESIGN.md`
- Extract the design system (colors, typography, spacing, component patterns) from `DESIGN.md`
- Document as `CONTEXT.md ## UX conventions`

Share the screen URLs with the user so they can review.

**Phase 2+:** add new screens to the existing Stitch project. Do not regenerate screens from previous phases.

---

### If `<prototyper>` is Other MCP

For each epic with UI, call `<prototyper_tool>` following `<prototyper_instructions>`. Document results in `CONTEXT.md ## UX conventions`.

---

Commit:

```bash
git add CONTEXT.md DESIGN.md
git commit -m "docs: UX conventions from prototype — Phase <N>"
git push
```

Then proceed immediately to Step 7b.

## Step 7b — Review loop

This loop runs until the user closes the definition. Do not exit until they confirm.

Output:

```
╔══════════════════════════════════════════════════════════════╗
║  Prototype ready. Review and adjust before generating tasks. ║
╚══════════════════════════════════════════════════════════════╝

Epics: <epic1>, <epic2>, ...
<If Stitch: show screen URLs>
<If Claude: "Prototype is running — review the screens in the browser">

Anything to adjust?

  1. A screen or flow is wrong
  2. An epic is missing, wrong, or should be cut
  3. Business logic needs a correction
  4. Looks good — generate tasks
```

Wait for response.

**If 1 (screen or flow):** Ask which epic/screen. Then:
- Claude prototyper: invoke `prototype` for that epic only, passing the specific feedback. Update `CONTEXT.md ## UX conventions` with any changed patterns. Commit.
- Stitch: call the relevant `mcp__stitch__*` tool to regenerate the affected screens. Update `DESIGN.md` and `CONTEXT.md ## UX conventions`. Commit.

After adjustment, show the review loop output again.

**If 2 (epic change):** Ask what to add, remove, or modify. Apply changes:
- Update `CONTEXT.md ## Phases` epic list.
- Add or delete the GitHub milestone accordingly.
- If an epic was removed, note which prototype screens (if any) are now orphaned.
- Commit.

After adjustment, show the review loop output again.

**If 3 (business logic):** Ask what changed. Update `CONTEXT.md` (glossary, architecture, or constraints). Commit. Show the review loop output again.

**If 4 (looks good):** Proceed to Step 8.

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

Read `project:` from `.devaing.md`. Store as `<project-number>`.

Publish issues in dependency order. For each issue:

```bash
# Create issue and capture URL and node ID
ISSUE_URL=$(gh issue create \
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
)")

# Add to GitHub Project
gh project item-add <project-number> --owner <owner> --url "$ISSUE_URL"

# Get node ID for dependency API
ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -o '[0-9]*$')
ISSUE_NODE_ID=$(gh issue view $ISSUE_NUMBER --json id --jq '.id')
```

After all issues are created, register GitHub-native dependencies via REST API. First fetch the internal integer IDs for all issues (distinct from the display numbers):

```bash
gh api "repos/<owner>/<repo>/issues?state=all&per_page=100" \
  --jq '.[] | "\(.number) \(.id)"'
```

Then for each "B blocked by A" pair:

```bash
# -F sends issue_id as integer (required — -f sends a string and will fail with 422)
# Use the internal ID from the fetch above, NOT the display number
gh api -X POST "repos/<owner>/<repo>/issues/<B-number>/dependencies/blocked_by" \
  -F "issue_id=<A-internal-id>"
```

To remove a dependency later: `DELETE /repos/<owner>/<repo>/issues/<B>/dependencies/blocked_by/<A-internal-id>` (path-based, not body).

Repeat for every blocked/blocker pair. If a call fails, continue — the `## Blocked by` text in the body remains as readable fallback for agents.

Commit + push after all issues are created:

```bash
git add CONTEXT.md
git commit -m "docs: generate Phase <N> issues (<granularity>)"
git push
```

## Closing

```
╔══════════════════════════════════════════════════════════════╗
║  Phase <N> "<phase-name>" — backlog ready, implementation    ║
║  starts now.                                                 ║
╚══════════════════════════════════════════════════════════════╝

<N> tasks generated across <epic-count> epics. Nothing is built yet.
Start with the first unblocked task:

  /devaing-work #N          Implement a task end-to-end

Other commands:

  /devaing-phase-revise     Adjust scope, prototype, or business logic
  /devaing-bug              Report something broken
  /devaing-phase-revise     Add something not in the current plan (New area)

Not available yet:

  /devaing-phase-def        Blocked — Phase <N> has open tasks.
                            Close all tasks first, then start the next phase.
```
