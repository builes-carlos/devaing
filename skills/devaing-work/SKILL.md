---
name: devaing-work
description: Take a GitHub issue or milestone name and implement the next vertical slice end-to-end. Detects mid-flight sessions and resumes instead of starting over. Updates CONTEXT.md and closes the issue after merge. Invoked with /devaing-work #N or /devaing-work <milestone>. When invoked with no argument, presents a Structured/Hotfix choice.
---

Read `body.md` in the same directory as this SKILL.md file and execute it step by step.

The `.devaing/skills/work.md` copy in your project is for non-Claude Code runtimes (Codex, Aider, Cursor).
Claude Code always reads the globally installed body so skill updates take effect immediately.
