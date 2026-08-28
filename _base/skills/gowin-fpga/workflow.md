# Gowin FPGA

Use this skill to make Gowin builds reproducible and to preserve tool-specific quirks that are easy to forget.

## Quick Route

1. For `gw_sh.exe`, Tcl build scripts, `.gprj` mirroring, reports, and common CLI options, read `cli-build.md`.
2. For local Windows paths and the `C:\workspace\verilog` Gowin setup, read `local-windows.md`.
3. For Tang Primer 20K DDR3 and dual-purpose pin gotchas, read `tang-primer-20k-ddr3.md`.

## Working Rules

- Inspect the existing `.tcl`, `.gprj`, `.cst`, and `.sdc` files before inventing a build flow.
- If a project only has `.gprj`, mirror the XML `Device` and `FileList` into a small Tcl script instead of relying on undocumented CLI project commands.
- Treat synthesis, PnR, timing, bitstream generation, and hardware programming as separate milestones.
- Do not run Gowin Programmer or write FPGA SRAM/Flash unless the user explicitly asks for hardware programming.
- When a pin is not constrained, read the generated pin report before trusting a bitstream. Gowin may auto-place unconstrained top-level ports onto electrically wrong pins.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
