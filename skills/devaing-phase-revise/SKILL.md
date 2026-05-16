---
name: devaing-phase-revise
description: Adjust the current phase or add a net-new feature area. Covers scope changes (issues wrong, missing, or excess), prototype revisions, business logic corrections, and adding functionality not in the original plan. Invoked with /devaing-phase-revise.
---

Read `.devaing/skills/phase-revise.md` from the current project root and execute it step by step.

If that file does not exist (project initialized before devaing v2), fall back to `body.md`
in the same directory as this SKILL.md file. Read that file and execute it.

This two-tier lookup means project-specific customizations win, and no re-initialization is needed when upgrading devaing.
