# devaing-phase-def

Define a phase completely: context validation → epics → prototype → review loop → issues.

This command does not stop until the phase is fully defined (issues generated). Prototype revisions are handled inline — no need to jump to another command. Once issues are created, /devaing-phase-def blocks and /devaing-phase-revise becomes available.

## Opening — Welcome message

Output immediately, before reading any files:

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-phase-def                                          ║
╚══════════════════════════════════════════════════════════════╝

Here's what's going to happen:

  1. Check current phase state
  2. Validate or build context for this phase
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

## Step 3 — Context validation or discovery

