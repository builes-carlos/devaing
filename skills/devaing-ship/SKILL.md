---
name: devaing-ship
description: Ship to production. Run after completing a phase, after phase-revise additions, or after a hotfix tested in dev. Detects what changed since the last deploy, checks migrations and seeds, validates env vars, deploys, and tags the release. Works for first deploys (new prod or adopt existing prod) and incremental deploys.
---

# devaing-ship

Ship what's ready in dev to production, safely and in order.

## Opening

```
╔══════════════════════════════════════════════════════════════╗
║  devaing-ship                                               ║
╚══════════════════════════════════════════════════════════════╝
```

## Step 0 — Read project context

Read `CONTEXT.md` and `.devaing.md`. Extract:
- Stack (framework, ORM, deploy target) from `## Architecture`
- Project name from `## Project`
- Current phase from `## Phases`
- `prod_url:` line from `.devaing.md` if present → store as `<prod-url>`
- `prod_db_url:` line from `.devaing.md` if present → store as `<prod-db-url>`

Store stack as `<stack>`, deploy target as `<deploy-target>` (infer from `## Architecture` in CONTEXT.md if not explicit).

## Step 1 — Determine last ship

```bash
git tag --list "ship/*" | sort -V | tail -1
```

If no tag found: **first deploy flow** — go to Step 2a.
If tag found: store as `<last-ship-tag>` and go to Step 2b.

## Step 2a — First deploy

Ask:

```
Is prod already running (the app is live and users exist)?

  1. No  — provision prod from scratch
  2. Yes — adopt existing prod (establish baseline)
```

Wait for response.

**If 1 (provision from scratch):** go to Step 3 — Provision prod.
**If 2 (adopt existing):** go to Step 4 — Adopt existing prod.

## Step 2b — Incremental deploy (ship tag exists)

Detect what changed since `<last-ship-tag>`:

```bash
# Code changes
git log <last-ship-tag>..HEAD --oneline

# New migration files
git diff <last-ship-tag>..HEAD --name-only | grep -E "migrations?/" | grep -v "^$"

# New seed files
git diff <last-ship-tag>..HEAD --name-only | grep -E "seeds?/" | grep -v "^$"

# New env vars (.env.example changes)
git diff <last-ship-tag>..HEAD -- .env.example
```

Summarize scope:

```
Scope since last ship (<last-ship-tag>):

  Code:              <N> commits
  Schema migrations: <N new files / none>
  Seed migrations:   <N new files / none>
  New env vars:      <list from .env.example diff / none>
```

If only code changes (no migrations, no new env vars):

```
Quick deploy — only code changes detected.

  <N> commits since <last-ship-tag>

Deploy now? (y/n)
```

If yes: skip to the "Deploy code" sub-step within Step 6. Skip the DB snapshot, schema migrations, seed migrations, and env var sub-steps — they have nothing to execute.

Otherwise: proceed to Step 5 — Deploy checklist.

## Step 3 — Provision prod (first deploy, no existing prod)

Walk through each item. Do not proceed until each is confirmed.

```
Provisioning prod environment. Let's go through each item.
```

**DB:**

```
1. Provision the production database.

   Provision your production database and get the connection string.
   e.g. For Supabase: create a new project at supabase.com → Settings → Database → Connection string.

   Paste the prod DATABASE_URL when ready:
```

Wait. Store as `<prod-db-url>`.

**Deploy target:**

```
2. Set up the deploy target.

   For Railway: create a new project at railway.app and connect your repo.
   In Railway: Settings → Source → Branch → set to "prod".
   (The prod branch was created by devaing-init. devaing-work never pushes to it.)

   For other deploy targets: connect to a dedicated deploy branch, not to your
   working branch (main). devaing-work merges to main constantly.

   Paste the prod app URL when ready (e.g., https://myapp.up.railway.app):
```

Wait. Store as `<prod-url>`. Save to `.devaing.md`:

```bash
echo "prod_url: <prod-url>" >> .devaing.md
```

**Env vars:**

```
3. Set all environment variables in prod.

   Required vars from .env.example:
```

Read `.env.example` and list all vars. Ask the user to confirm each is set in the deploy target's env config.

```
   Confirm all vars are set in <deploy-target>? (y/n)
```

**Validate:**

```
4. Run a health check to confirm prod is up.
```

```bash
curl -f <prod-url>/health 2>/dev/null || curl -f <prod-url> 2>/dev/null
```

If the check fails: warn but do not stop — the app may not have a `/health` endpoint.

```
   Prod is up? (y/n)
```

Wait for confirmation. Then go to Step 5 — Deploy checklist.

## Step 4 — Adopt existing prod (first deploy, prod already running)

This is a prod that exists but was never managed by devaing-ship. We establish a baseline without touching anything.

```
Adopting existing prod. I'll establish a baseline without running any migrations.

Paste the prod DATABASE_URL (needed to mark seeds as already executed):
```

Wait. Store as `<prod-db-url>`. Save to `.devaing.md`:

```bash
echo "prod_db_url: <prod-db-url>" >> .devaing.md
```

**Create _seed_migrations table if absent:**

Using the project's ORM or raw SQL, create the table in prod:

```sql
CREATE TABLE IF NOT EXISTS "_seed_migrations" (
  "id" TEXT PRIMARY KEY,
  "executedAt" TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Mark all current seed files as already executed:**

```bash
ls prisma/seeds/*.ts 2>/dev/null || ls db/seeds/*.py 2>/dev/null || ls db/seeds/*.sql 2>/dev/null
```

For each seed file found, insert a record into `_seed_migrations` in prod (without running the seed):

```sql
INSERT INTO "_seed_migrations" ("id") VALUES ('<filename-without-extension>')
ON CONFLICT DO NOTHING;
```

This tells the seed runner that these seeds already ran.

**Prod URL:**

```
Paste the prod app URL (needed for health checks on future deploys):
```

Wait. Store as `<prod-url>`. Save to `.devaing.md`:

```bash
echo "prod_url: <prod-url>" >> .devaing.md
```

**Tag the baseline:**

```bash
git tag ship/baseline
git push origin ship/baseline
```

Store `<last-ship-tag>` = `ship/baseline`.

```
✓ Baseline established. Prod is now tracked.

From here, only new seeds (added after today) will run on the next ship.

Continue to deploy any pending code changes? (y/n)
```

If yes: go to Step 2b (detect changes from baseline). If no: skip to Closing — the ship/baseline tag was already created above.

## Step 5 — Deploy checklist

Build and display ordered checklist.

For seed migrations count:
- If `<last-ship-tag>` is set: show count of new seed files from the git diff.
- If `<last-ship-tag>` is none (first deploy from scratch): show "ALL — first deploy, none previously executed."

```
Deploy checklist:

  [ ] 1. DB snapshot — safety net before any changes
  [ ] 2. Schema migrations — <N pending / none>
  [ ] 3. Seed migrations — <N new / ALL (first deploy) / none>
  [ ] 4. New env vars — <list / none>
  [ ] 5. Deploy code
  [ ] 6. Verify prod

Execute in order? (y/n)
```

Wait for confirmation.

## Step 6 — Execute deploy

Run each step in order. Check each off as it completes.

**DB snapshot:**

```
1. DB snapshot — take a manual snapshot in your DB provider's dashboard before continuing.

Snapshot taken? (y/n)
```

**Schema migrations:**

If pending migrations exist, run against prod DB using the project's ORM:
- Prisma: `DATABASE_URL=<prod-db-url> npx prisma migrate deploy`
- Alembic: `DATABASE_URL=<prod-db-url> alembic upgrade head`
- Other: run equivalent command inferred from `<stack>`

```bash
<migration-command>
```

If command fails: stop and report the error. Do not proceed.

**Seed migrations:**

If new seed files exist (or this is a first deploy — all seeds will run since `_seed_migrations` is empty), run the seed runner against prod:
- Node: `DATABASE_URL=<prod-db-url> npm run seed`
- Python: `DATABASE_URL=<prod-db-url> python db/seeds/runner.py`

```bash
<seed-command>
```

If command fails: stop and report the error. Do not proceed.

**New env vars:**

For each new var detected in `.env.example` diff:

```
Set <VAR_NAME> in <deploy-target> env config.

Done? (y/n)
```

Wait for each.

**Deploy code:**

For Railway (prod branch strategy — set up in Step 3):

```
Push main to the prod deploy branch. Railway auto-deploys from prod.

  git push origin main:prod

Deploy triggered? (y/n)
```

For other deploy targets: push to whatever branch your deploy target monitors,
or trigger a manual deploy. Adapt based on `<deploy-target>` from `.devaing.md`.

Wait for confirmation that deploy completed.

**Verify:**

```bash
curl -f <prod-url>/health 2>/dev/null && echo "Health check passed" || echo "WARNING: health check failed or no /health endpoint"
```

```
Prod is working as expected? (y/n)
```

If no: stop and ask the user to investigate before tagging.

## Step 7 — Tag the release

Determine tag name based on context:

- Phase complete deploy: `ship/phase-<N>`
- Phase-revise additions: `ship/phase-<N>-additions-<YYYYMMDD>`
- Hotfix: `ship/hotfix-<YYYYMMDD>`
- Baseline adoption: already tagged in Step 4

Ask if unsure which applies:

```
What triggered this deploy?

  1. Phase complete
  2. Phase-revise additions
  3. Hotfix
```

```bash
git tag <tag-name>
git push origin <tag-name>
```

If this was a phase-complete deploy, update `CONTEXT.md ## Phases` — change current phase status to `Complete`. Commit + push.

## Closing

```
╔══════════════════════════════════════════════════════════════╗
║  Shipped: <tag-name>                                        ║
╚══════════════════════════════════════════════════════════════╝

What was shipped:
  Commits:           <N>
  Schema migrations: <N applied / none>
  Seed migrations:   <N applied / none>
  Env vars added:    <list / none>

Tag: <tag-name>
Prod: <prod-url>
```
