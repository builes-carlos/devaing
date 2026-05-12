---
name: devaing-work
description: Take a GitHub issue or milestone name and implement the next vertical slice end-to-end. Detects mid-flight sessions and resumes instead of starting over. Wraps /ce-work with mandatory CONTEXT.md update after merge. Invoked with /devaing-work #N or /devaing-work <milestone>.
---

# devaing-work

Implement a vertical slice end-to-end and keep CONTEXT.md alive.

## Language override

All output from this skill — questions, inline messages, report tables, generated file content, and code comments — MUST be in English. This overrides any global language setting (including "Respond in Spanish").

## Opening — Welcome message

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-work: <#N or area-name>                            ║
╚══════════════════════════════════════════════════════════════╝

I'm going to implement the next task end-to-end.

Here's what's going to happen:

  1. Check for any in-progress work that wasn't finished
  2. Read the task: what to build and how to verify it works
  3. Implement everything: UI + logic + tests
  4. Update the project map with what was learned
  5. Close the task and let you know when the PR is ready
```

## Step 1 — Detect mid-flight session

Before creating or fetching anything, check if a previous session for this milestone died mid-flight.

**GitHub mode** — look for an open issue with an existing branch:

```bash
gh issue list --milestone "<milestone>" --state open --json number,title,labels \
  --jq '.[] | select(.labels[].name == "ready-for-agent") | {number, title}'

# For each open issue found, check if a branch exists:
git branch --list | grep "<issue-slug>"
git worktree list
```

**No-GitHub mode** — look for an orphaned branch with unmerged commits:

```bash
# Find branches matching the milestone slug that have commits ahead of main
git branch --list | grep "<milestone-slug>"
git log main..<branch> --oneline 2>/dev/null
git worktree list
```

**If a mid-flight session is found** (open issue + existing branch, OR unmerged branch for the milestone):

```
⚠ Found in-progress work for "<milestone>":
  Branch: <branch-name>
  Commits ahead of main: N
  Resume from here? (y/n)
```

If yes: pass the existing branch and issue context to ce-work to resume. Skip issue creation.
If no: ask whether to abandon the branch before starting fresh.

## Step 2 — Resolve the issue

If invoked with an issue number (`/devaing-work #N`):

```bash
gh issue view <N> --comments
```

Read the full issue: what to build, acceptance criteria, blocked by. Verify all blockers are closed. If a blocker is still open, stop and tell the user which to complete first.

If invoked with a milestone name (`/devaing-work <milestone>`) and no mid-flight session detected:

**GitHub mode** — read closed issues and CONTEXT.md to determine the next slice, then create the issue:

```bash
gh issue list --milestone "<milestone>" --state closed --json number,title | head -20
```

```bash
gh issue create \
  --title "<title>" \
  --milestone "<milestone>" \
  --label "ready-for-agent" \
  --body "$(cat <<'EOF'
## What to build

<end-to-end behavior derived from CONTEXT.md and prior slices>

## Acceptance criteria

- [ ] <criterion>

## Blocked by

<#N or "None - can start immediately">
EOF
)"
```

**No-GitHub mode** — read git log and CONTEXT.md to determine the next slice. No issue created. Branch name must include the milestone slug: `feat/<milestone-slug>-<slice-slug>`.

Store the issue number (or branch name in no-GitHub mode) and proceed.

## Step 3 — Context budget check

Before dispatching to ce-work, assess the current session's context load. Context quality degrades predictably: at 50%+ the model rushes, at 70%+ it hallucinates and drops requirements.

If this is not the first slice in the current session (i.e., prior devaing-work output exists in this conversation):

```
⚠ Context warning: this session has already processed prior work.
  Starting ce-work now means the implementation runs in a loaded context.
  Recommendation: open a fresh Claude Code session and run /devaing-work again.
  Continue anyway? (y/n)
```

If the user confirms: proceed. If no: stop and let them restart clean.

## Step 4 — Route by issue type

**Check for prototype:**

```bash
ls prototype/ 2>/dev/null || ls src/prototype/ 2>/dev/null
```

If a prototype exists and the issue involves UI: identify the prototype screen that corresponds to this slice. The implementation should replace that mock screen with real behavior. Leave all other prototype screens intact.

**If the issue involves UI (screens, components, visual design):**

1. Invoke `ce-frontend-design` first, passing the issue content and the corresponding prototype screen if one exists. Let it implement the UI with design quality, verify via screenshots, and iterate until it matches the expected behavior.
2. Then invoke `ce-work` for any remaining non-UI logic (backend, tests, integration).

**Otherwise:**

Invoke `ce-work` passing the issue content as the work document. Let ce-work run its full flow: worktree, TDD, review, PR, CI, merge.

## Step 5 — Update CONTEXT.md and ADRs

After the PR merges, evaluate whether anything changed in:

- **Domain glossary**: new terms introduced during implementation
- **Architecture**: new components, patterns, or integrations added
- **Key constraints**: limits or behaviors discovered that weren't documented

If anything changed, update `CONTEXT.md` and commit:

```bash
git add CONTEXT.md
git commit -m "docs: update CONTEXT.md after closing #<N>"
git push
```

Ask two questions:

**1. Non-obvious decisions:** "Was there a non-obvious decision during implementation? (library choice, design pattern, workaround, technical trade-off)"

If yes: create an ADR in `docs/adr/NNNN-<slug>.md` documenting: context, decision, alternatives considered, and consequences. Commit:

```bash
git add docs/adr/
git commit -m "docs: ADR for decision made in #<N>"
git push
```

**2. Known limitations:** "Did anything surface that we knowingly left broken or incomplete? (race condition, best-effort operation, scaling gap, deferred fix)"

If yes: add an entry to `CONTEXT.md` under `## Known limitations`:

```
- **<what>**: <description of the problem>. Deferred because: <reason>. Triggered by: <what condition would require fixing this>. For now: <operational guidance>.
```

Commit:

```bash
git add CONTEXT.md
git commit -m "docs: known limitation from #<N>"
git push
```

## Step 6 — Close the issue

```bash
gh issue close <N> --comment "Implemented in PR #<PR>. CONTEXT.md updated."
```

## Closing

Check if this was the last open issue in its milestone:

```bash
gh issue list --state open --json number,milestone \
  --jq '[.[] | select(.milestone.title == "<milestone>")]  | length'
```

If 0 remaining in this milestone, check if ALL milestones in the current phase are now complete:

```bash
# Get all milestones belonging to current phase from CONTEXT.md ## Phases
# Check open issue count per milestone
gh issue list --state open --json number,milestone \
  --jq '[.[] | select(.milestone != null)] | length'
```

If open issues still exist in other phase milestones:
```
✓ Milestone "<name>" complete.

  → Next task: /devaing-work <next-milestone>
```

If ALL phase milestones are at 0 open issues — **phase complete**:
```
╔══════════════════════════════════════════════════════════════╗
║  Phase "<phase-name>" complete.                             ║
╚══════════════════════════════════════════════════════════════╝

Before closing:

  QA — verify real behavior in device/browser.
  Tests can't catch: confusing flows, missing pieces, things that feel off.
  Findings → /devaing-bug "what happened"

  Architecture review (every 2-3 phases):
  /improve-codebase-architecture

When ready for the next phase:

  /devaing-phase "<next-phase-name>"
```

Update CONTEXT.md `## Phases` — change current phase status from `In Progress` to `Complete`:

```bash
git add CONTEXT.md
git commit -m "docs: Phase <N> complete"
git push
```

Otherwise:

```
✓ Task #<N> closed — PR #<PR> ready to review.

What's next?

  → Review the PR and merge if everything looks good.
  → For the next task, open a fresh session and run:
    /devaing-work <area-name>

  Fresh session = clean context = better implementation quality.
```
