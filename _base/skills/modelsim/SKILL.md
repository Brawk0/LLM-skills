---
name: modelsim
description: Work efficiently in ModelSim (Intel FPGA Starter Edition 10.5b) for Verilog/SystemVerilog testbench simulation. Use for vsim, vlog, vlib, vmap, .do files, headless/batch simulation runs, wave/WLF workflows, dataset comparison, VCD export, modelsim.ini tuning, transcript/exit-code automation, DPI-C builds, SDF/gate-level timing runs, ModelSim error diagnosis (verror, _lock, bad magic number), and any "how do I do X in ModelSim" question.
---

# ModelSim Productivity

## Core Goal

Run simulation tasks in ModelSim fast and reproducibly: prefer scriptable headless flows over GUI clicking, exploit the environment features (batch mode, WLF datasets, wildcard logging, project modelsim.ini, restart) to shorten every edit-compile-debug iteration, and diagnose tool errors from documented codes instead of guessing.

## Local Environment

- Simulator: ModelSim - Intel FPGA Starter Edition (ASE) 10.5b from Quartus 18.1, Windows: `C:\intelFPGA\18.1\modelsim_ase\win32aloem\` (`vsim.exe`, `vlog.exe`, `vlib.exe`, `vmap.exe`). Always call these explicitly, never whatever is first in `PATH`.
- The ASE binary is 32-bit (`win32aloem`): any DPI-C objects/DLLs must be built 32-bit (the MinGW gcc bundled under `modelsim_ase`), not with a 64-bit toolchain.
- Starter Edition limits (manual features that do NOT work here): mixed VHDL+Verilog elaboration (single-language license — prefer Verilog versions of IP), code coverage, PSL/concurrent SVA assertions and covergroups, the C Debug GUI, full Dataflow causality tracing (one process/signal at a time). `bind` of plain procedural checker modules still works.
- The exact matching documentation is converted into the Obsidian vault: index note `ПО\Программирование\ПЛИС\ModelSim\ModelSim users manual 10_5b\ModelSim users manual 10_5b.md` (chapter notes with `source-page` anchors into the PDF). The distilled Russian digest is `ПО\Программирование\ПЛИС\ModelSim\Продуктивная работа в ModelSim.md`.
- Repo-specific ModelSim facts (Gowin primitive libraries, verified testbench commands, lock-file cleanup for `C:\workspace\verilog`) live in `C:\workspace\verilog\docs\modelsim.md` and the `fpga-dev` skill. This skill owns tool techniques; `fpga-dev` owns project specifics — do not duplicate them here.

## Default Headless Run Recipe

Use `assets/run_tb_template.do` as the starting skeleton for a per-testbench `.do`. The load-bearing rules:

1. Make the `.do` a self-contained mini-project: recreate `work`, compile, elaborate, run, quit (existing user convention).
2. Put `onerror {quit -code 1}`, `onElabError {quit -code 12}`, `onbreak {resume}` BEFORE any `run` — otherwise a mid-script error strands the batch session at an interactive prompt.
3. Prefer `vsim -batch` over `vsim -c` for automation: no interactive prompt, output to stdout/`-logfile`, best performance for `$display`-heavy benches. Keep `-c` for interactive console work.
4. Branch GUI-only commands (`add wave`, zoom, dividers) on `batch_mode`: `if {![batch_mode]} { do wave.do }` — one `.do` serves GUI and regression.
5. Check `$LASTEXITCODE` in PowerShell; ModelSim exit codes are documented (0 ok, 1 bad invocation, 2 prior errors, 4/19/42-45 licensing, 5/6 library/design-unit access, 12 load/elaboration, 202 SIGINT, 211 segfault). `quit -code <n>` propagates custom codes.
6. Parameterize instead of cloning scripts: DO-file arguments `$1..$9`/`$argc`, environment variables `$env(NAME)` set from PowerShell, and SystemVerilog `+plusargs` (`$test$plusargs`/`$value$plusargs`) for run variants without recompilation.

Invocation pattern:

```powershell
& 'C:\intelFPGA\18.1\modelsim_ase\win32aloem\vsim.exe' -batch -logfile logs\tb.log -do "do run_tb.do; quit -f"
if ($LASTEXITCODE -ne 0) { <fail path> }
```

## Task Map

Read `references/modelsim-productivity.md` for the full command inventory. Section guide:

- Compile faster: `vlog -incr`, precompiled resource libraries, `-mfcu`, `-timescale`.
- Log everything, decide later: `add log -r /*` + `WildcardFilter`/`WildcardSizeThreshold` (memories and big arrays are silently excluded by default — the top "missing signal" trap).
- Keep and compare runs: `vsim -wlf <name>.wlf`, `dataset open`, `vsim -view gold=...`, `-wlfslim/-wlftlim`, `wlfrecover`, `vcd2wlf` (bridge from iverilog VCD).
- Wave efficiency: `add wave -group`, virtual signals, radix control, `write format restart` + `ShutdownFile`, expanded time (delta/event view).
- Debug without rerunning: `examine`/`describe` (incl. `-delta`), `when {...} {stop}`, `bp -cond`, breakpoint command scripts, `restart` with `DefaultRestartOptions = -force`.
- Time correctness: `vsim -t`, `timescale` rounding traps (ps-level delays silently become 0), 64-bit Tcl time math (`gtTime` family — plain `>` breaks past ~2.1 ms at 1 ps), `IterationLimit`, `+autofindloop`.
- Message hygiene: `verror <num>`, `-suppress`/`-error` promotion, `+nowarn<CODE>`, `-msglimit`, `[msg_system]` in modelsim.ini.
- Project modelsim.ini: `-modelsimini`, lookup order, `where` diagnosis, `Startup`, `TranscriptFile = logs/transcript#.log`, env-var expansion inside ini values.
- DPI-C: C files directly on the `vlog` line (auto-compiled, auto-loaded), `vlog -dpiheader`, `mti_Cmd` import, 32-bit toolchain caveats.
- Gate-level/SDF: `-sdfmax /dut=file.sdf`, `+notimingchecks`/`+nospecify`/`+no_tchk_msg`, precision rounding of SDF values.
- Known traps: stale `_lock` files, `bad magic number` WLF (unclosed run — `wlfrecover`), Tcl quoting of 4-state values, `project compileall` redundancy.

## Vault Term Notes

When writing vault notes about ModelSim topics, link the canonical term notes (in `ПО\Программирование\ПЛИС\` and `...\ПЛИС\ModelSim\`): `[[Дельта-цикл (delta cycle, итерация симулятора)]]`, `[[WLF-файл (Wave Log Format, vsim.wlf)]]`, `[[Dataset (набор данных симуляции ModelSim)]]`, `[[Виртуальные объекты ModelSim (virtual signal, virtual function)]]`, `[[Разрешение симулятора (simulator resolution limit, vsim -t)]]`, `[[VCD (Value Change Dump)]]`, `[[SDF (Standard Delay Format)]]`, `[[Signal Spy (иерархический доступ ModelSim)]]`, `[[batch mode ModelSim (vsim -batch)]]`, `[[headless-режим ModelSim]]` and the others listed in the digest note.

## Self-Improvement And Publishing

When ModelSim work reveals a durable, reusable lesson (a verified command pattern, an ASE limitation, a failure mode with its fix), use the `skill-learning` policy: save compact rules in this shared-base skill or `references/modelsim-productivity.md`. Verified repo-specific facts go to `C:\workspace\verilog\docs\modelsim.md` / `fpga-dev` instead. Do not store secrets, credentials, copyrighted manual text beyond short command syntax, generated logs, or one-off project facts here.

Before materially editing this skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check: fetch `origin main`, compare local `HEAD` with `origin/main`, fast-forward if local is behind and the relevant working tree is clean, and inspect dirty/ahead/diverged states before continuing.

After materially updating this skill, validate the shared base and adapters when feasible, then commit and push the relevant skill changes to the owning repository by default unless the user explicitly says not to. Stage only relevant skill files and repository metadata. Split commits by semantic block when the update contains independent concerns; avoid vague rollups such as "skill update".

If publishing encounters remote changes or merge conflicts, resolve them autonomously when the intended final meaning can be determined from the files, commit history, nearby rules, and the user's instruction. Preserve compatible rules from both sides, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
