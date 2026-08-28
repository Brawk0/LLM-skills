---
name: fpga-dev
description: FPGA development workflow for Verilog/SystemVerilog and soft-MCU firmware projects. Use when working on HDL, constraints, Gowin/Vivado/Quartus projects, FPGA simulation, synthesis, implementation, bitstream generation, timing/resource reports, programming files, DSView or logic-analyzer screenshots/captures, Gowin Analyzer Oscilloscope/GAO captures, local lidar FPGA firmware such as C:\workspace\verilog and LDR_20K, or soft-MCU/LwIP Ethernet work such as C:\workspace\dark_risc.
---

# FPGA Development

Entry point: read `workflow.md` in this folder and follow it fully. It carries the
whole procedure — project discovery, HDL naming and layout rules, the
simulate-before-hardware rule, progressive verification, the hardware session
log, and commit handling.

## Load References

- `workflow.md` — the workflow itself; always read it first.
- `local-gowin-lidar.md` — the local lidar Gowin workspace: paths, LDR_20K build,
  ModelSim checks, programming, MSOP TCP stream debugging, verified hardware facts.
- `mcu-fpga-command-spi.md` — command channel MCU -> FPGA over SSPI: frame layout,
  register addresses, the SPI-mode trap that silently shifts the whole frame.
- `soft-mcu-dark-risc-lwip.md` — DarkRISCV soft-MCU, LwIP profile, memory map, DDR3 MMIO.
- `gowin-analyzer-cli.md` — Gowin Analyzer Oscilloscope / GAO captures from the CLI.
- `ltdc-x3.md` — LTDC-X3 measurement chip: QSPI access, config, combine mode, bring-up.
- `w5500.md` — W5500 Ethernet over SPI.
- `agent-tooling.md` — measured cost of the direct-query tooling on this project,
  the compatibility flags this RTL needs, and static findings in it. Tool usage
  itself lives in the separate `rtl-agent-tools` skill.
- `scripts/parse_diptrace_asc.py` — parse DipTrace `.asc` schematics to trace board nets.

## Origin And Sync

The canonical copy of this skill lives in the FPGA project repository at
`C:\workspace\verilog\docs\skills\fpga-dev\`, where it is shared by Codex and
Claude Code through thin adapters in `.agents/skills/` and `.claude/skills/`.

This Google Drive copy exists so the skill is reachable from other workspaces.
When a new verified fact appears during FPGA work, write it into the project copy
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
