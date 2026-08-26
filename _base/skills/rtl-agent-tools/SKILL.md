---
name: rtl-agent-tools
description: Direct-query tooling for RTL debug instead of indirect detours. Use when you would otherwise re-run a simulation just to add another $display, chain many greps to trace where a signal goes or who drives it, read a VCD/FST dump as text, or prove that a lint fix or refactor did not change behavior. Covers wavepeek waveform queries, vcd2fst conversion, slang elaboration/lint, slang-netlist connectivity graphs (drivers, fan-in/fan-out, path and combinational-loop queries), and yosys+eqy equivalence checking.
---

# RTL Agent Tools

Entry point: read `workflow.md` in this folder and follow it fully. It carries the
daily commands for each tool, the sampling rules that make the queries correct,
and the limits where each tool stops being useful.

## Load References

- `workflow.md` — the workflow itself; always read it first.
- `install.md` — download links, versions, and build steps. Read it ONLY when a
  needed binary is missing from the paths listed in `workflow.md`; otherwise it
  costs tokens for nothing.

Project-specific measurements, the compatibility flags the lidar RTL needs, and
static findings in it live in the `fpga-dev` skill next to this one, in
`agent-tooling.md`.

## Origin And Sync

The canonical copy of this skill lives in the FPGA project repository at
`C:\workspace\verilog\docs\skills\rtl-agent-tools\`, where it is shared by Codex
and Claude Code through thin adapters in `.agents/skills/` and `.claude/skills/`.

This Google Drive copy exists so the skill is reachable from other workspaces.
When a new verified fact appears during RTL work, write it into the project copy
first, then re-sync this folder from it. If the two ever disagree, the project
repository wins — it is the one edited during real hardware sessions.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
