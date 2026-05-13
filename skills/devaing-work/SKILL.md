---
name: devaing-work
description: Take a GitHub issue or milestone name and implement the next vertical slice end-to-end. Detects mid-flight sessions and resumes instead of starting over. Wraps /ce-work with mandatory CONTEXT.md update after merge. Invoked with /devaing-work #N or /devaing-work <milestone>.
---

# devaing-work

Implement a vertical slice end-to-end and keep CONTEXT.md alive.

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
  5. Mark the task done
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

**If invoked with no argument:**

1. Fetch all open issues with their bodies:

```bash
gh issue list --state open --json number,title,milestone,body --jq 'sort_by(.number)'
```

2. Fetch the set of currently open issue numbers:

```bash
gh issue list --state open --json number --jq '[.[].number]'
```

3. For each issue, parse the `## Blocked by` section of its body and extract referenced numbers (lines matching `#N`). Classify:
   - **READY** — no blockers listed ("None"), or all referenced numbers are not in the open set
   - **BLOCKED** — at least one referenced number is still open

4. Display, grouping READY first sorted by number, then BLOCKED sorted by number. Show which open issue is blocking each blocked task:

```
Open tasks — <phase name>

  READY
  #N   [Milestone]   title

  BLOCKED
  #N   [Milestone]   title   ← #M
  ...

How many tasks do you want to implement?

  1. One     — pick from the list above
  2. All ready now — implement all currently READY tasks in sequence
  3. Cascade — implement READY tasks, unlock the next ones, repeat until the phase is empty
```

5. Wait for response.

**If 1 (one):** Ask which number. Use the confirmed or typed number as the target and continue to the `#N` path below.

**If 2 (all ready now):** Collect all READY issue numbers sorted by number. For each in order, spawn an Agent with `isolation: "worktree"` to implement the issue end-to-end. The agent must: read CONTEXT.md and DESIGN.md before starting; implement UI, data layer, API routes, and tests; create a branch, open a PR, run `compound-engineering:ce-correctness-reviewer` and `compound-engineering:ce-testing-reviewer` on the diff, address critical findings, wait for CI, and merge. After all complete, run the Step 5/6 post-merge updates for each. Then show the closing summary.

**If 3 (cascade):** Repeat until zero open issues remain in the phase:
1. Fetch open issues and note the current count. Compute READY set (same classification as above).
2. If READY is empty but open issues remain: all are blocked — stop and report which are waiting.
3. For each READY issue in number order, spawn an Agent with `isolation: "worktree"` to implement the issue end-to-end. Each agent must: read CONTEXT.md and DESIGN.md before starting; implement UI, data layer, API routes, and tests; create a branch, open a PR, run `compound-engineering:ce-correctness-reviewer` and `compound-engineering:ce-testing-reviewer` on the diff, address critical findings, wait for CI, and merge.
4. After all agents in the batch complete, re-fetch open issues. If the open count has not decreased (no issues were closed), stop and report which issues failed — do not loop.
5. Otherwise, recompute READY (newly unblocked issues may now be ready) and repeat from step 1.

Each subagent runs in its own isolated context — no context budget accumulation in the orchestrating session.

---

If invoked with an issue number (`/devaing-work #N`):

```bash
gh issue view <N> --comments
```

Read the full issue: what to build, acceptance criteria, blocked by. Verify all blockers are closed. If a blocker is still open, stop and tell the user which to complete first.

If invoked with a milestone name and no mid-flight session detected, read closed issues and CONTEXT.md to determine the next slice, then create the issue:

```bash
gh issue list --milestone "<milestone>" --state closed --json number,title | head -20
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

Move the issue to "In Progress" in the GitHub Project:

```bash
PROJECT_NUMBER=$(grep "^project:" .devaing.md | awk '{print $2}')
OWNER=$(gh api user --jq '.login')
ITEM_ID=$(gh project item-list $PROJECT_NUMBER --owner $OWNER --format json \
  --jq ".items[] | select(.content.number == <N>) | .id")
PROJECT_ID=$(gh project view $PROJECT_NUMBER --owner $OWNER --format json --jq '.id')
STATUS_FIELD=$(gh project field-list $PROJECT_NUMBER --owner $OWNER --format json \
  --jq '.fields[] | select(.name == "Status")')
FIELD_ID=$(echo $STATUS_FIELD | jq -r '.id')
IN_PROGRESS_ID=$(echo $STATUS_FIELD | jq -r '.options[] | select(.name == "In Progress") | .id')
gh project item-edit --id $ITEM_ID --field-id $FIELD_ID \
  --project-id $PROJECT_ID --single-select-option-id $IN_PROGRESS_ID
```

If `.devaing.md` has no `project:` line or the update fails, continue silently.

## Step 3 — Context budget check

Only applies to mode 1 (single issue). Modes 2 and 3 spawn each `ce-work` as a subagent with its own context — no budget concern.

For mode 1: before dispatching to ce-work, assess the current session's context load. Context quality degrades predictably: at 50%+ the model rushes, at 70%+ it hallucinates and drops requirements.

If this is not the first slice in the current session (i.e., prior devaing-work output exists in this conversation):

```
⚠ Context warning: this session has already processed prior work.
  Starting ce-work now means the implementation runs in a loaded context.
  Recommendation: open a fresh Claude Code session and run /devaing-work again.
  Continue anyway? (y/n)
```

If the user confirms: proceed. If no: stop and let them restart clean.

## Step 4 — Route by issue type

**Check for prototype and design system:**

```bash
ls prototype/ 2>/dev/null || ls src/prototype/ 2>/dev/null
```

If a prototype exists and the issue involves UI: identify the prototype screen that corresponds to this slice. The implementation should replace that mock screen with real behavior. Leave all other prototype screens intact.

If `DESIGN.md` exists at the project root: read it before implementing any UI. Use the design tokens (colors, typography, spacing, component patterns) defined there. Do not invent a design system — follow what Stitch or the external tool defined.

**Implementation protocol:**

1. Create a branch:
   ```bash
   git checkout -b issue-<N>-<slug>
   ```
2. Implement end-to-end: UI, data layer, API routes, and tests. Do not defer any layer.
3. For UI work: follow `DESIGN.md` design tokens if present. Otherwise follow prototype screens. After implementing, take a screenshot and verify it matches the intended design before proceeding.
4. Run the test suite. Fix all failures before proceeding.
5. Open a PR:
   ```bash
   gh pr create --title "<issue title>" --body "Closes #<N>"
   ```
6. Review the diff using compound-engineering reviewer agents via the Agent tool:
   - Always: `compound-engineering:ce-correctness-reviewer` and `compound-engineering:ce-testing-reviewer`
   - For large diffs or diffs touching auth, payments, or data mutations: also `compound-engineering:ce-adversarial-reviewer`
   - Address all critical findings before proceeding.
7. Wait for CI to pass. Fix any failures.

## Step 5 — Update CONTEXT.md and ADRs

After the PR merges, evaluate whether anything changed in:

- **Domain glossary**: new terms introduced during implementation
- **Architecture**: new components, patterns, or integrations added
- **Key constraints**: limits or behaviors discovered that weren't documented

If anything changed, update `CONTEXT.md` and commit + push:

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

Move to "Done" in the GitHub Project. If any command fails, skip silently:

```bash
PROJECT_NUMBER=$(grep "^project:" .devaing.md | awk '{print $2}')
OWNER=$(gh api user --jq '.login')
PROJECT_ID=$(gh project view $PROJECT_NUMBER --owner $OWNER --format json --jq '.id')
ITEM_ID=$(gh project item-list $PROJECT_NUMBER --owner $OWNER --format json \
  --jq ".items[] | select(.content.number == <N>) | .id")
STATUS_FIELD=$(gh project field-list $PROJECT_NUMBER --owner $OWNER --format json \
  --jq '.fields[] | select(.name == "Status")')
FIELD_ID=$(echo $STATUS_FIELD | jq -r '.id')
DONE_ID=$(echo $STATUS_FIELD | jq -r '.options[] | select(.name == "Done") | .id')
gh project item-edit --id $ITEM_ID --field-id $FIELD_ID \
  --project-id $PROJECT_ID --single-select-option-id $DONE_ID
```

## Closing

Check if this was the last open issue in its milestone:

```bash
gh issue list --state open --json number,milestone \
  --jq '[.[] | select(.milestone.title == "<milestone>")] | length'
```

If 0 remaining in this milestone, check if ALL milestones in the current phase are now complete:

```bash
gh issue list --state open --json number,milestone \
  --jq '[.[] | select(.milestone != null)] | length'
```

If open issues still exist in other phase milestones:

**Compress the closed milestone in CONTEXT.md.** Replace verbose slice-by-slice notes with a single summary block:

```markdown
### <milestone-name> (complete)
- Built: <what was built — interfaces exposed, components added>
- Decisions: <link to ADRs if any, or one-line summary>
- Known limitations: <reference to ## Known limitations entries if any, or "none">
```

Commit + push:

```bash
git add CONTEXT.md
git commit -m "docs: compress milestone <name> in CONTEXT.md"
git push
```

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

  /devaing-phase-def
```

Update CONTEXT.md `## Phases` — change current phase status to `Complete`. Commit + push:

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
