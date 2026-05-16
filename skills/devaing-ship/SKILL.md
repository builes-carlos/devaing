---
name: devaing-ship
description: Ship to production. Run after completing a phase, after phase-revise additions, or after a hotfix tested in dev. Detects what changed since the last deploy, checks migrations and seeds, validates env vars, deploys, and tags the release. Works for first deploys (new prod or adopt existing prod) and incremental deploys.
---

Read `.devaing/skills/ship.md` from the current project root and execute it step by step.

If that file does not exist (project initialized before devaing v2), fall back to `body.md`
in the same directory as this SKILL.md file. Read that file and execute it.

This two-tier lookup means project-specific customizations win, and no re-initialization is needed when upgrading devaing.
