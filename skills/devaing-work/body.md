## Sub-agent invocation

Steps that say "Spawn a sub-agent" or "invoke Agent":
- **Claude Code**: use the `Agent` tool (no `isolation` parameter — work in current directory).
- **Other environments (Codex, Aider, Cursor, etc.)**: read `subagent_cli:` from `.devaing.md`. Default: `claude -p --model claude-sonnet-4-6`. Build the prompt and pipe it: `IMPLEMENTATION_REPORT=$(echo "$PROMPT" | $SUBAGENT_CLI)`.

For adversarial review, Claude Code can additionally use `subagent_type=compound-engineering:ce-adversarial-reviewer`. Other environments use the inline adversarial prompt included in the Adversarial review section below.

# devaing-work

Implement GitHub issues on epic branches. One person per epic (lock by issue assignment). PRs created and auto-merged to main when the epic closes. devaing-ship deploys main to prod.

## Opening — Issue selection

Fetch open issues grouped by milestone:

```bash
gh issue list --state open --json number,title,milestone,assignees --jq 'sort_by(.number)'
```

Identify the active phase from `CONTEXT.md ## Phases` (the row with Status `In Progress`). All issues in milestones of that phase are READY.

For each milestone in the active phase, compute its owner — the assignee of any open or recently-closed issue in that milestone:

```bash
gh issue list --milestone "<milestone>" --state all --json assignees \
  --jq '[.[] | select(.assignees | length > 0) | .assignees[0].login] | unique'
```

Display grouped by epic, numeric order within each, with owner if any:

```
Open tasks — Phase "<phase-name>"

  Epic "Auth" — owned by @userA
    #3   Login form UI
    #4   JWT middleware
    #5   Session refresh

  Epic "Billing" — no owner yet
    #6   Pricing table
    #7   Checkout flow

How do you want to work?

  1. One     — pick a task
  2. All     — implement all your epic's tasks in sequence
  3. Cascade — implement, close epic, take next available epic, repeat
  4. Hotfix  — fix something outside the backlog
```

Wait for response.

**If 4 (Hotfix):** skip to [Hotfix flow](#hotfix-flow).

**If 1 (One):** ask which number, then continue to Step 1.

**If 2 (All):** identify the epic for the chosen first issue. Collect all open issues in that milestone sorted by number. Run Step 1 through Step 3 for each in sequence. Then run Closing logic.

**If 3 (Cascade):** repeat until zero open issues remain in the phase:
1. Identify next available epic for the current user (epic with no assignee yet, OR epic where current user is already the owner). If no available epic: stop and report which epics are owned by other users.
2. Run Step 1 through Step 3 for each open issue in that milestone in numeric order.
3. When milestone closes, repeat from 1.

## Step 1 — Resolve and claim the issue

```bash
gh issue view <N> --comments
```

Read the full issue: what to build, acceptance criteria. Verify the milestone (epic).

**Epic ownership check:**

```bash
gh issue list --milestone "<milestone>" --state all --json assignees \
  --jq '[.[] | select(.assignees | length > 0) | .assignees[0].login] | unique'
```

If the list contains any user other than the current GitHub user (`gh api user --jq '.login'`):

```
⚠ Epic "<milestone>" is owned by @<userA>.
Pick a different epic, or coordinate with @<userA> first.

Available epics for you: <list of milestones in current phase with no other-owner assignment>.

Take this one anyway? (y/n)
```

If user says no: stop and let them re-run.

**Assign the issue and move card:**

```bash
gh issue edit <N> --add-assignee @me
```

Move to "In Progress" in the GitHub Project:

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

If `.devaing.md` has no `project:` line or the update fails: continue silently.

**Lazy branch creation/checkout:**

Derive a slug from the milestone name (lowercase, replace non-alphanumeric with `-`, collapse repeated dashes, strip leading/trailing dashes). Store as `<slug>`.

```bash
git fetch origin
LOCAL=$(git branch --list epic/<slug>)
REMOTE=$(git ls-remote --heads origin epic/<slug>)
```

- Both empty: create new branch from main.
  ```bash
  git checkout main && git pull
  git checkout -b epic/<slug>
  git push -u origin epic/<slug>
  ```
- Local exists: `git checkout epic/<slug>` (no rebase — one person per epic).
- Only remote: `git checkout -t origin/epic/<slug>`.

## Step 2 — Implement via sub-agent

Check for prototype and design system:

```bash
ls prototype/ 2>/dev/null || ls src/prototype/ 2>/dev/null
```

Read DESIGN.md if it exists at the project root.

Build a **filtered** CONTEXT for the sub-agent: include only `## Project`, `## Domain glossary`, `## Architecture`, `## Key constraints`. Exclude `## Phases`, `## Next phase backlog`, and any compressed milestone history (reduces tokens, focuses the agent).

Spawn an Agent (no `isolation` parameter — work in current directory on the active epic branch) with this prompt:

> You are implementing GitHub issue #<N> for the project "<name>".
>
> **Project context (filtered):**
> <filtered CONTEXT.md content>
>
> **Issue:**
> <full issue content including acceptance criteria>
>
> **Design system:** <DESIGN.md content if exists, otherwise "none — use existing project styles">
>
> **Prototype screen for this slice:** <relevant prototype file content if found, otherwise "none">
>
> **Instructions:**
> - You are on branch `epic/<slug>`. Commit your changes on this branch. Do NOT switch branches, do NOT merge, do NOT open a PR.
> - If a prototype screen exists for this issue, replace it with real implementation. Leave all other prototype screens as mocks.
> - Follow design tokens in DESIGN.md if present. Do not invent a design system.
> - **Tests** — write tests only when:
>   (a) the code has complex business logic with branching or combinatorics (pricing, state machines, validation rules, parsing),
>   (b) the issue is fixing a bug — add one regression test that reproduces the bug,
>   (c) the code is async or non-clickable (cron, webhook, background job),
>   (d) the issue's acceptance criteria explicitly requests a test.
>   Otherwise: don't.
>   When you do write tests: test behavior, not implementation. 1 happy path + 1 critical edge case. Same commit as the feature.
> - Run existing tests after implementing (`npm test`, `pytest`, etc.) to confirm nothing broke.
> - Stage and commit all changes: `git commit -m "feat: <short description> (closes #<N>)"`. Do not commit .env files or secrets.
> - Report back: what you built, any non-obvious decisions, anything knowingly left incomplete.

Wait for the sub-agent to complete. Capture its report as `<implementation-report>`.

## Step 3 — Post-implementation

**Self-verification:**

Detect the test command from the project root:

- Node: check if `package.json` has a `"test"` script → `npm test`
- Python: check for `pytest.ini` or `[tool.pytest.ini_options]` in `pyproject.toml` → `pytest`
- Rust: `cargo test`
- Other: skip silently

If a test command is detected, run it. If exit code ≠ 0:

```
⚠ Tests failing after sub-agent commit.
<last 30 lines of output>

Options:
  1. Fix now    — spawn sub-agent to fix the failures
  2. Document   — add to CONTEXT.md Known limitations and continue
  3. Revert     — git reset --hard HEAD~1 (discards the commit)
```

Wait for response.
- "Fix now": spawn a sub-agent (same structure as Step 2) with the test output as the task. Commit the fix, re-run tests. Repeat up to 2 times.
- "Document": continue — the failure will go into Known limitations below.
- "Revert": run `git reset --hard HEAD~1`. Stop and return to issue selection.

**AC validation:** read the issue body with `gh issue view <N>`. Extract all `- [ ]` lines from `## Acceptance criteria`. Ask in a single prompt:

```
Acceptance criteria check for #<N>:
  [ ] <AC 1>
  [ ] <AC 2>
  ...

All criteria met? (y/n/partial)
```

- `y`: continue.
- `n`: offer Fix now / Document / Revert (same flow as test failure above).
- `partial`: ask which criteria are unmet. Apply Document to those — they go to Known limitations.

**Adversarial review:**

Check whether this is the last open issue in the milestone:

```bash
OPEN_IN_MILESTONE=$(gh issue list --milestone "<milestone>" --state open \
  --json number --jq 'length')
```

Default `y` if `OPEN_IN_MILESTONE` = 0 (last issue — worth reviewing before auto-merge). Default `n` otherwise.

```
Run adversarial review on this commit? (y/n, default <y/n>)
```

If `y`: spawn Agent with `subagent_type=compound-engineering:ce-adversarial-reviewer`. Prompt:

> Review the diff of the commit closing GitHub issue #<N> ("<title>") on branch `epic/<slug>`.
> Issue acceptance criteria: <criteria>.
> Construct failure scenarios for each changed component. Report findings categorized as HIGH / MEDIUM / LOW severity with a one-line description and a concrete failure scenario for each.

Process findings:
- HIGH findings: for each one, ask:
  ```
  HIGH: <finding>
  Fix now / Document in Known limitations / Ignore? (f/d/i)
  ```
  "Fix now": spawn sub-agent, commit fix as `fix: address adversarial review finding (#<N>)`.
- MEDIUM/LOW findings: show as a table, ask once:
  ```
  MEDIUM/LOW findings:
  | Severity | Finding |
  |---|---|
  | MEDIUM | <...> |
  | LOW | <...> |

  Document all in Known limitations? (y/n)
  ```

**CONTEXT.md update:** if `<implementation-report>` mentions new domain terms, new architecture components, new integrations, or new constraints: update CONTEXT.md.

**Known limitations:** if the report mentions anything intentionally left incomplete or broken: add to `## Known limitations` in CONTEXT.md:

```
- **<what>**: <description>. Deferred because: <reason>. Triggered by: <condition>. For now: <guidance>.
```

If CONTEXT.md changed:

```bash
git add CONTEXT.md
git commit -m "docs: update CONTEXT.md after #<N>"
```

**Push epic branch:**

```bash
git push origin epic/<slug>
```

**Close the issue:**

```bash
git rev-parse --short HEAD | xargs -I{} gh issue close <N> --comment "Implemented in {}. CONTEXT.md updated."
```

**Move to Done:**

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

If any command fails: skip silently.

## Closing — Epic complete check

Check if the milestone has 0 open issues:

```bash
OPEN_IN_MILESTONE=$(gh issue list --milestone "<milestone>" --state open \
  --json number --jq 'length')
```

If `OPEN_IN_MILESTONE` > 0: skip to "Per-issue close" below.

If 0 (epic complete):

1. Create PR from `epic/<slug>` to main:
   ```bash
   CLOSED_ISSUES=$(gh issue list --milestone "<milestone>" --state closed \
     --json number --jq '[.[] | "#\(.number)"] | join(", ")')
   PR_URL=$(gh pr create --base main --head epic/<slug> \
     --title "Epic: <milestone>" \
     --body "Closes milestone '<milestone>'. Issues: $CLOSED_ISSUES")
   ```

2. Auto-merge the PR to main (one dev owns the epic, no peer review by default — real QA happens at phase end):
   ```bash
   PR_NUMBER=$(echo "$PR_URL" | grep -o '[0-9]*$')
   gh pr merge $PR_NUMBER --merge --delete-branch
   ```

3. Sync local main:
   ```bash
   git checkout main && git pull
   ```

## Closing — Phase complete check

After the epic close (or if epic still has open issues, after the per-issue close), check if ALL milestones in the active phase have 0 open issues:

```bash
OPEN_IN_PHASE=$(gh issue list --state open --json number,milestone \
  --jq '[.[] | select(.milestone != null)] | length')
```

If `OPEN_IN_PHASE` > 0:

```
✓ #<N> done.

  → Next: /devaing-work
```

If 0 (phase complete): update `CONTEXT.md ## Phases` — change current phase Status to `Complete`. Commit + push:

```bash
git add CONTEXT.md
git commit -m "docs: Phase <N> complete"
git push
```

Output:

```
╔══════════════════════════════════════════════════════════════╗
║  Phase "<phase-name>" complete.                              ║
╚══════════════════════════════════════════════════════════════╝

QA en main local antes de shipear. Todo el código de la fase ya está mergeado.

  → Findings: /devaing-bug "..." o /devaing-phase-revise
  → Cuando estés listo: /devaing-ship
```

## Hotfix flow

```
Describe what to fix:
```

Wait. Store as `<hotfix-description>`.

Hotfix flow does not use epic branches. It works directly on a hotfix branch from main:

```bash
git checkout main && git pull
SLUG=$(echo "<hotfix-description>" | tr '[:upper:]' '[:lower:]' \
  | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-\|-$//g' | cut -c1-50)
git checkout -b hotfix/$SLUG
```

Spawn a sub-agent (same structure as Step 2) but pass `<hotfix-description>` instead of an issue. Commit message: `fix: <short description>`.

After sub-agent completes: run Step 3 (CONTEXT.md update + push). Push hotfix branch:

```bash
git push origin hotfix/$SLUG
```

Create and auto-merge a PR to main:

```bash
PR_URL=$(gh pr create --base main --head hotfix/$SLUG \
  --title "Hotfix: <hotfix-description>" \
  --body "Hotfix applied directly. No issue tracked.")
PR_NUMBER=$(echo "$PR_URL" | grep -o '[0-9]*$')
gh pr merge $PR_NUMBER --merge --delete-branch
git checkout main && git pull
```

Then ask:

```
Create a retroactive issue for tracking? (y/n)
(Recommended — keeps the backlog searchable)
```

If yes:

```bash
RETROACTIVE_URL=$(gh issue create \
  --title "Hotfix: <hotfix-description>" \
  --label "needs-triage" \
  --body "$(cat <<'EOF'
## What was fixed

<hotfix-description>

## Resolution

Implemented as hotfix. No issue was created before the fix.
EOF
)")
RETROACTIVE_N=$(echo "$RETROACTIVE_URL" | grep -o '[0-9]*$')
gh issue close $RETROACTIVE_N --comment "Closed retroactively — fix merged to main."
```

Output:

```
✓ Hotfix done.

  → When ready to deploy to prod: /devaing-ship
```
