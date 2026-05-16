---
name: devaing-status
description: Show the current state of a devaing project and what to do next. Use when the user wants to know where they stand in the workflow, how many tasks are done, which epic is next, or what command to run. Also useful for getting oriented after returning to a project.
---

Read `.devaing/skills/status.md` from the current project root and execute it step by step.

If that file does not exist (project initialized before devaing v2), fall back to `body.md`
in the same directory as this SKILL.md file. Read that file and execute it.

This two-tier lookup means project-specific customizations win, and no re-initialization is needed when upgrading devaing.
