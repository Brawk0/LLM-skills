---
name: verilator
description: Build and run Verilator simulations of this project's Verilog/SystemVerilog, and make their results agree with ModelSim. Use for verilator, verilator_bin, --timing, --binary, --trace, obj_dir, VERILATOR_ROOT, lint-only runs, BLKANDNBLK and other UNSUPPORTED diagnostics, two-state versus four-state differences, X-initialisation, differential tracing against an event simulator, and any "why does Verilator disagree with ModelSim" question.
---

# Verilator (Codex adapter)

Shared base skill: ../_base/skills/verilator/SKILL.md.

When this skill triggers, read that base SKILL.md completely and follow it together with any references/, scripts/, and assets/ next to the base file. Resolve relative resource paths from the shared base skill directory.

Keep this file as a Codex-specific thin adapter: frontmatter, trigger wording, and Codex-only metadata belong here; durable domain rules, reusable workflows, scripts, references, and lessons belong in the shared base skill.

Codex-specific notes:
- Update the shared base first for behavior changes, then adjust Codex/Claude adapters only when their platform-specific pointers or trigger descriptions need to change.
- Related skills: `modelsim` (эталон, с которым сверяются результаты), `fpga-dev` (факты проекта), `rtl-agent-tools` (прямые запросы к волнам и связности).
