---
name: devaing-ship
description: Ship to production. Run after completing a phase, after phase-revise additions, or after a hotfix tested in dev. Detects what changed since the last deploy, checks migrations and seeds, validates env vars, deploys, and tags the release. Works for first deploys (new prod or adopt existing prod) and incremental deploys.
---

Read `body.md` in the same directory as this SKILL.md file and execute it step by step.

The `.devaing/skills/ship.md` copy in your project is for non-Claude Code runtimes (Codex, Aider, Cursor).
Claude Code always reads the globally installed body so skill updates take effect immediately.
