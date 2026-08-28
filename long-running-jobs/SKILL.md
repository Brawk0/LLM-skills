---
name: long-running-jobs
description: Discipline for work that takes minutes to hours — simulations, synthesis and place-and-route, long builds, batch conversions, hardware sweeps. Use when a command will not return promptly, when several such jobs run at once, when a job seems finished but produced no verdict, when stray processes hold files or burn CPU, or when deciding whether to wait, poll, or kill. Covers bounding every run, checking the artifact instead of the notification, cleaning orphans before starting, and reporting honestly whether work is actually in progress.
---

# Long-Running Jobs (Codex adapter)

Shared base skill: ../_base/skills/long-running-jobs/SKILL.md.

When this skill triggers, read that base SKILL.md completely and follow it together with any references/, scripts/, and assets/ next to the base file. Resolve relative resource paths from the shared base skill directory.

Keep this file as a Codex-specific thin adapter: frontmatter, trigger wording, and Codex-only metadata belong here; durable domain rules, reusable workflows, scripts, references, and lessons belong in the shared base skill.

Codex-specific notes:
- Update the shared base first for behavior changes, then adjust Codex/Claude adapters only when their platform-specific pointers or trigger descriptions need to change.
- Related skills: `modelsim` и `verilator` (запуск конкретных симуляторов), `fpga-dev` (сборка и PnR — самые долгие задачи проекта).
