---
name: devaing-work
description: Take a GitHub issue or milestone name and implement the next vertical slice end-to-end. Detects mid-flight sessions and resumes instead of starting over. Wraps /ce-work with mandatory CONTEXT.md update after merge. Invoked with /devaing-work #N or /devaing-work <milestone>. When invoked with no argument, presents a Structured/Hotfix choice.
---

Read `.devaing/skills/work.md` from the current project root and execute it step by step.

If that file does not exist (project initialized before devaing v2), fall back to `body.md`
in the same directory as this SKILL.md file. Read that file and execute it.

This two-tier lookup means project-specific customizations win, and no re-initialization is needed when upgrading devaing.
