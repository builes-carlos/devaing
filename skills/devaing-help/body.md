# devaing-help

Output the following reference verbatim. Do not read any project files.

---

```
╔══════════════════════════════════════════════════════════════╗
║  devaing — hyper-agile product development with AI          ║
╚══════════════════════════════════════════════════════════════╝
```

devaing is a framework for solo builders and small teams who want
to ship product fast without losing structure. It uses GitHub Issues
as the source of truth, generates UI prototypes before committing to
tasks, and delegates implementation to AI sub-agents.

The middle path between vibe coding (no structure) and Jira-driven
process (too slow for early-stage). Built for Claude Code.

## Core concepts

  Phases       The scoping unit. Define what you build in this cycle.
  Epics        Groups of issues inside a phase (= GitHub milestones).
  Issues       One vertical slice each. The atomic unit of work.
  Prototype    Built before issues are generated. Survives as a
               navigation skeleton — each work slice replaces one
               mock with real implementation.
  CONTEXT.md   Single source of truth for the project. Always current.
  CHECKPOINTS  Objective health criteria. devaing-director audits them.

## Skills

  COMMAND                 WHAT IT DOES                          WHEN TO USE

  /devaing-init           One-time project setup. Creates repo,  New project or
                          GitHub Project, CI, AGENTS.md,         adopting existing
                          CONTEXT.md, and the portable           codebase.
                          .devaing/skills/ layer.

  /devaing-phase-def      Define a phase end-to-end: epics,      Start of each
                          prototype, review loop, issue           build cycle.
                          generation. Does not exit until
                          issues are created.

  /devaing-phase-revise   Adjust scope, prototype, or business   During active
                          logic during implementation. Add a      implementation,
                          new area not in the current plan.       when plans change.

  /devaing-work           Implement the next GitHub issue via     After phase-def
                          sub-agent. Self-verifies AC, optional   generates issues.
                          adversarial review, auto-merges epic    One call per issue
                          when milestone closes.                  (or Cascade mode).

  /devaing-ship           Deploy to prod: detect changes since   When a phase or
                          last tag, run migrations/seeds,         hotfix is ready
                          verify env vars, tag release,           to go live.
                          archive shipped phases.

  /devaing-bug "..."      Bug description → structured GitHub    Any time something
                          issue with diagnosis and regression     is broken.
                          test criteria.

  /devaing-director       Read project state, run health         Any time. Replaces
                          checks, show next step. Offers to       checking manually.
                          execute the next skill on y/n           Useful as default
                          confirmation.                           entry point.

  /devaing-help           This screen.                           When lost.

## Typical flow

  /devaing-init              ← once per project
       ↓
  /devaing-phase-def         ← once per phase
       ↓
  /devaing-work #N  (×N)     ← one per issue until epic done
       ↓
  /devaing-ship              ← when phase is complete
       ↓
  /devaing-phase-def         ← start next phase

  At any point:
    /devaing-director         see where you are + what's next
    /devaing-phase-revise     change scope or add a new area
    /devaing-bug "..."        report something broken

## Where to learn more

  STRATEGY.md              Full framework design and rationale
  .devaing/skills/*.md     Portable skill bodies (readable by any LLM)
  .devaing.md              Project config (granularity, prototyper, subagent_cli)
```
