---
name: devaing-phase-def
description: Define a new phase end-to-end: epics, prototype, review loop, and issue generation. Starts from populated CONTEXT.md — discovery happens in /devaing-init. Owns the full definition process from epics to closed backlog. /devaing-phase-revise is only available after this command closes. Invoked with /devaing-phase-def (no argument needed).
---

Read `.devaing/skills/phase-def.md` from the current project root and execute it step by step.

If that file does not exist (project initialized before devaing v2), fall back to `body.md`
in the same directory as this SKILL.md file. Read that file and execute it.

This two-tier lookup means project-specific customizations win, and no re-initialization is needed when upgrading devaing.
