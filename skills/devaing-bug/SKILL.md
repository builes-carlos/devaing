---
name: devaing-bug
description: Report a bug in a devaing project. Converts a natural language description into a structured GitHub issue with diagnosis, assigns it to the relevant milestone, and marks it ready-for-agent. Invoked with /devaing-bug "description".
---

Read `body.md` in the same directory as this SKILL.md file and execute it step by step.

The `.devaing/skills/bug.md` copy in your project is for non-Claude Code runtimes (Codex, Aider, Cursor).
Claude Code always reads the globally installed body so skill updates take effect immediately.
