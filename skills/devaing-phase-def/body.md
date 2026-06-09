# devaing-phase-def

Define a phase completely: context validation → epics → prototype → review loop → issues.

This command does not stop until the phase is fully defined (issues generated). Prototype revisions are handled inline — no need to jump to another command. Once issues are created, /devaing-phase-def blocks and /devaing-phase-revise becomes available.

**Invariant — grill-me runs on every phase-def, always with model upgrade:**
Every phase (including Phase 1 right after init) runs a grill-me focused on the scope of that phase. Before the grill-me, always show the model upgrade prompt and wait for response. After issues are generated, always show the model downgrade prompt. Never skip either prompt.

## Opening — Welcome message

Output immediately, before reading any files:

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-phase-def                                          ║
╚══════════════════════════════════════════════════════════════╝

Here's what's going to happen:

  1. Check current phase state
  2. Validate context
  3. Phase discovery — understand what this phase should accomplish
  4. Define and approve the epics
  5. Build the prototype
  6. Review loop — adjust until satisfied
  7. Generate tasks and close the definition

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
| No | No | Interrupted before prototype | Resume at Step 6 |
| Yes | No | Prototype built, in review | Resume review loop (Step 6b) |
| — | Yes | Definition closed — active phase | Block |

**Interrupted (no UX conventions, no issues):** Output, then skip to Step 6 (Prototype):

```
⚠️  Phase "<name>" setup was interrupted before the prototype.

Epics already approved: <epic1>, <epic2>, ...

Resuming from prototype step. No re-discovery needed.
```

**Prototype built, review not finished (UX conventions exist, no issues):** Skip directly to Step 6b (review loop). Do not re-generate the prototype.

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

If invoked from `/devaing-init`: skip the granularity sub-question only (use the value passed by init). Still ask for the phase name using the "no closed phases" prompt below.

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

## Step 3 — Validate context

Show a brief summary and ask for corrections.

Output:

```
Before the phase discovery, here's a snapshot of the product baseline.
Correct anything outdated or missing — the grill-me will cover the rest.

**Product**: <one sentence from ## Project>
**Architecture**: <brief from ## Architecture>
**Key constraints**: <brief from ## Key constraints>

Anything to correct or add?
```

Wait for response. If corrections given, update the relevant sections of CONTEXT.md.

Continue to Step 4.

## Step 4 — Update CONTEXT.md

If any updates were made in Step 3, commit:

```bash
git add CONTEXT.md
git commit -m "docs: update context before Phase <N> scoping"
git push
```

## Step 4b — Model upgrade

Show this before any discovery work:

```
╔══════════════════════════════════════════════════════════════╗
║         MODEL UPGRADE RECOMMENDED                           ║
╠══════════════════════════════════════════════════════════════╣
║  Phase discovery works better with a more capable model.    ║
╚══════════════════════════════════════════════════════════════╝

To switch: /model — then come back and answer below.

Did you switch to a more capable model?
  y — yes, switched
  n — no, continuing as-is
```

Wait for response. If `y`: set `<model_upgraded> = true`. If `n`: set `<model_upgraded> = false`.

## Step 4c — Backlog cross-reference (Phase 2+ only)

Skip entirely if this is Phase 1 or `CONTEXT.md ## Next phase backlog` has no entries for Phase <N>.

For each backlog item, grep/read the relevant source files to assess current state: not started, partially built, or scaffolded. Present the analysis without asking a question yet:

```
Backlog items — cruzados con el código actual:

- **<name>** — <description>. Estado: <not started / partially built / scaffolded>. <one line: what already exists or what's missing>.
- **<name>** — ...
```

Continue to Step 4d.

## Step 4d — Backlog selection (Phase 2+ only)

Skip if Phase 1.

Ask:

```
Which of these go into Phase <N>? Which stay in the backlog?
```

Wait for response. Store selected items as `<backlog-selection>`.

## Step 4e — Phase intent

Ask one open question. Include sub-prompts so the user knows what kind of answer is useful:

```
¿Qué querés que tenga Phase <N>? Describí a alto nivel.

  — ¿Qué cambia para el usuario con esta fase?
  — ¿Qué problema específico resuelve esta fase?
```

Wait for response. Store as `<phase-intent>`. Even a vague answer is valid — the grill-me will deepen it.

## Step 4f — Phase discovery (grill-me)

Before invoking grill-me, read:
- `CONTEXT.md ## Known limitations` — problems consciously deferred
- `CONTEXT.md ## Architecture` — current system shape
- Closed issues from the previous phase (to know what was actually built, not just planned)

Invoke `grill-me` with a hypothesis-rich prompt that deepens the phase intent. Do NOT ask the user to describe the phase from scratch. If `<phase-intent>` was vague, lead with your own hypotheses.

Prompt:

> "We're defining Phase <N> '<phase-name>' for <project>.
>
> Product state: <one-line from ## Project>
> Built in Phase <N-1>: <brief summary of closed issues from previous phase>
> Known limitations not yet fixed: <list from ## Known limitations, or 'none documented' if empty>
> Taking from backlog: <backlog-selection, or 'nothing selected' if Phase 1 or empty>
> Phase intent from the user: <phase-intent>
>
> Based on this, my hypotheses for what Phase <N> should accomplish: <2-3 specific hypotheses derived from the phase intent and the gaps above>
>
> Granularity: <granularity>. Calibrate depth: Broad = 3-5 questions on scope boundary and key user value. Balanced = 6-10 questions. Detailed = go deep on every scenario and edge case.
>
> If the phase intent was vague, use your hypotheses as the starting point — do not ask the user to repeat what they just said. Ask targeted questions to confirm or correct these hypotheses, identify what else should be in scope, and pin down what's explicitly out of scope."

Run until the user signals done. Store as `<phase-discovery>`.

## Step 5 — Define epics for this phase

Synthesize the epic list from `<backlog-selection>` + `<phase-intent>` + `<phase-discovery>`. Do NOT re-interview.

Present and wait for approval:

```
Based on the discovery and selected backlog, I propose these epics for "<phase-name>":

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

2. If next-phase epics were identified, annotate in `CONTEXT.md ## Next phase backlog`:

```markdown
## Next phase backlog

- Phase <N+1> — <epic name> — <one-line description>
```

3. Create one milestone per epic:

```bash
gh api repos/<owner>/<name>/milestones --method POST \
  --field title="<epic-name>" \
  --field description="<epic-description>"
```

4. Commit:

```bash
git add CONTEXT.md
git commit -m "docs: define Phase <N> epics"
git push
```

5. Create the phase integration branch:

```bash
git checkout main && git pull
git checkout -b phase-<N>
git push -u origin phase-<N>
```

## Step 6 — Prototype

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
- If 2: skip to Step 7 (no UX conventions written).
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

Then proceed immediately to Step 6b.

## Step 6b — Review loop

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
- Other MCP: call `<prototyper_tool>` again with the epic name, the affected screen description, and the user's requested changes following `<prototyper_instructions>`. Update `CONTEXT.md ## UX conventions`. Commit.

After adjustment, output before showing the loop again:

```
Changes since last review:
- Screen "<name>" in epic "<epic>": <one sentence describing what changed>
```

Show the review loop output again.

**If 2 (epic change):** Ask what to add, remove, or modify. Apply changes:
- Update `CONTEXT.md ## Phases` epic list.
- Add or delete the GitHub milestone accordingly.
- If an epic was removed, note which prototype screens (if any) are now orphaned.
- Commit.

After adjustment, output before showing the loop again:

```
Changes since last review:
- Epic "<name>": <added / removed / renamed to "<new-name>" / scope changed: one sentence>
```

Show the review loop output again.

**If 3 (business logic):** Ask what changed. Update `CONTEXT.md` (glossary, architecture, or constraints). Commit.

Output before showing the loop again:

```
Changes since last review:
- Business logic: <one sentence describing what was corrected>
```

Show the review loop output again.

**If 4 (looks good):** Proceed to Step 7.

## Step 7 — Generate issues

For each epic in order, generate all vertical slices calibrated to `<granularity>`:

- **Broad**: 2-4 slices per epic. 2-3 high-level acceptance criteria.
- **Balanced**: 3-6 slices per epic. 4-6 specific acceptance criteria.
- **Detailed**: 6-12 slices per epic. Full acceptance criteria including negative paths.

Read `project:` from `.devaing.md`. Store as `<project-number>`.

Publish issues in dependency order. For each issue:

```bash
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

gh project item-add <project-number> --owner <owner> --url "$ISSUE_URL"
```

**Seed migration issues:** after generating all issues for an epic, check whether the epic introduces reference data (predefined messages, catalogs, templates, system configuration, or any content that must exist in the DB before the app functions). If yes, add one additional issue to that epic:

```bash
gh issue create \
  --title "Seed migrations: <epic-name>" \
  --milestone "<epic-name>" \
  --label "ready-for-agent" \
  --body "$(cat <<'EOF'
## What to build

Create versioned seed migrations for all reference data introduced in this epic.
Use upsert (INSERT ... ON CONFLICT DO UPDATE or ORM equivalent) so seeds are safe to run multiple times.
Register each executed seed in the `_seed_migrations` table via the seed runner.

## Acceptance criteria

- [ ] Seed files created for all reference data in this epic
- [ ] Each seed uses upsert — running twice produces no errors and no duplicates
- [ ] Seeds tracked in `_seed_migrations` table after first run
- [ ] Seed runner executes them on deploy (npm run seed or equivalent)

## Blocked by

<number of the last issue in this epic — seeds depend on schema being ready>
EOF
)"
```

Skip this issue if the epic has no reference data (pure UI, pure API endpoints with no predefined content).

Commit + push after all issues are created:

```bash
git add CONTEXT.md
git commit -m "docs: generate Phase <N> issues (<granularity>)"
git push
```

## Step 7b — Model downgrade

If `<model_upgraded>` is true:

```
╔══════════════════════════════════════════════════════════════╗
║         MODEL DOWNGRADE SUGGESTED                           ║
╠══════════════════════════════════════════════════════════════╣
║  Phase defined. You can switch back to a lighter model.     ║
╚══════════════════════════════════════════════════════════════╝

To switch: /model

Type 'continue' when ready.
```

Wait for response before showing the closing message.

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
