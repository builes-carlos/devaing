---
name: devaing-bug
description: Report a bug in a devaing project. Converts a natural language description into a structured GitHub issue with diagnosis, assigns it to the relevant milestone, and marks it ready-for-agent. Invoked with /devaing-bug "description".
---

Read `.devaing/skills/bug.md` from the current project root and execute it step by step.

If that file does not exist (project initialized before devaing v2), fall back to `body.md`
in the same directory as this SKILL.md file. Read that file and execute it.

This two-tier lookup means project-specific customizations win, and no re-initialization is needed when upgrading devaing.
