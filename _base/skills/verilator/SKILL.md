---
name: verilator
description: Build and run Verilator simulations of this project's Verilog/SystemVerilog, and make their results agree with ModelSim. Use for verilator, verilator_bin, --timing, --binary, --trace, obj_dir, VERILATOR_ROOT, lint-only runs, BLKANDNBLK and other UNSUPPORTED diagnostics, two-state versus four-state differences, X-initialisation, differential tracing against an event simulator, and any "why does Verilator disagree with ModelSim" question.
---

# Verilator

## Core Goal

Use Verilator where it wins — long runs — without ever trusting a number it produced until the same testbench in ModelSim produced the same number. Speed is worthless on a run that computes the wrong thing, and this project has already been bitten by exactly that.

## Local Environment

Verified 26.08.2026 on this workstation.

- Binary: `C:\workspace\verilog\1k\oss-cad-suite\bin\verilator_bin.exe`, version **5.019**. A second, older bundle exists at `C:\workspace\oss-cad-suite` (5.017) — do not use it.
- **Do not call `verilator`** — the launcher is a Perl script and the bundle has no `Pod::Usage`, so it dies before doing anything. Call `verilator_bin.exe` directly.
- `VERILATOR_ROOT` must be exported as `C:/workspace/verilog/1k/oss-cad-suite/share/verilator`. Without it the binary looks for a hardcoded `/yosyshq/share/verilator` that does not exist on disk.
- OpenOCD ships in the same bundle (0.12.0+dev, drivers `remote_bitbang` and `jtag_vpi`) but needs `oss-cad-suite/lib` on `PATH` for `libusb-1.0.dll`.
- C++ toolchain: MSYS2 UCRT64 GCC 16.2 (`C:\msys64\ucrt64\bin`).

## Build Traps On This Workstation

Each one blocks the build outright. A working recipe with all of them handled is
`C:\workspace\verilog\soft_mcu\dark_risc\sim\verilator\build_verilator.sh`.

- **`-Os` breaks linking of any C++ program here.** At `-Os` GCC 16.2 enables `-fdeclone-ctor-dtor` and emits references to `C4`/`D4` unified constructors that the shipped `libstdc++` does not provide. Reproduced with a three-line `std::string` program, so it is not a Verilator problem. Verilator's generated makefile uses `-Os`, so always add `-fno-declone-ctor-dtor` (or build at `-O2`).
- **`python3` must exist on `PATH`.** Verilator's generated makefile calls it and MSYS has none. Copy `python.exe` to `python3.exe` in a shim directory.
- **`--build` hangs** when Verilator spawns `make` itself from PowerShell with redirected output: no output, no files, the process lives for hours. Translate and compile as two separate steps.
- **`TEMP=C:\Windows`** is inherited by native tools in an MSYS shell and the linker fails with `Cannot create temporary file`. Run the compile step through `cmd.exe` with `TEMP` set natively, or from PowerShell.
- Pass the harness `.cpp` by **absolute path**; a relative one lands in the generated makefile relative to `obj_dir` and is not found.
- Do not wipe `PATH` down to MSYS only: native tools need the system directories for their DLLs.
- Extra flags reach only user files through `-CFLAGS`. To apply a define to the generated model too, rebuild with `make ... CXXFLAGS="-Os -I. <flags>"`. Never pass `CPPFLAGS` on the make command line — it replaces the include paths and nothing compiles.
- A custom `main` that uses `VerilatedContext` needs `-DVL_TIME_CONTEXT` **for every translation unit**, not just the main; otherwise the link fails on `sc_time_stamp()`.
- **Do not use the generated makefile from Git Bash.** MSYS2's `make` launched from a Git Bash (MINGW64) shell loses `TEMP` and dies with `Cannot create temporary file in C:\Windows\: Permission denied` before the compiler is ever called; `TMPDIR`, `TMP` and `TEMP` have no effect, in POSIX or Windows form, because the two runtimes do not share an environment. Calling `g++` directly works and removes the `-Os` and `CPPFLAGS` traps at the same time. `run_trace.sh` in the encoder bench is the working recipe.
- **`__ALL.cpp` is not everything.** It aggregates most generated units but leaves interface classes as separate translation units; compiling only `__ALL.cpp` fails to link on their constructors. Compile every generated `.cpp` **except** `__ALL.cpp`.
- **Name the top module.** Without `--top-module`, every module that nothing instantiates becomes an extra top and gets elaborated. Dead code then breaks the build for reasons that have nothing to do with the design under test: `math_modules.sv` here contains an unused `moving_average_filter` whose unpacked-array summation Verilator rejects with `SEL unexpected in assignment to unpacked array`.
- **`+incdir+` lists belong in a `-f` file.** With a few hundred directories the ModelSim command line silently truncates. Generate one file and feed it to both simulators — separate lists mean the two are compiling different projects, which is a very expensive way to find a divergence that is not there.
- **Wipe the `--Mdir` before every translation.** Verilator does not delete generated files that a source change made obsolete, and a build that compiles everything in the directory then links a stale translation unit against its replacement: `multiple definition of ..._nba_sequent__...`.
- **Full hierarchical paths need `-fno-inline`.** Verilator inlines modules by default and a probe like `dut.o_multiplier.gen_serial.o_serial_multiplier.count` fails with `Can't find definition of 'gen_serial'`. Worth it for a tracing build; leave it off for the speed run.

## Language Traps In This RTL

Verilator refuses several constructs this project uses. Each refusal below was real, and in one case the refusal was correct and the code was wrong.

- **Port in an interface declaration** (`interface foo(logic ch_A);`) — `Unsupported: Ranges ignored in port-lists`. Move the signal into the interface body.
- **Default value on a module input** (`input reset = 0`) — unsupported. Guard the declaration with `` `ifdef VERILATOR ``; an unconnected input is zero in Verilator anyway.
- **Mixing blocking and non-blocking assignment to one variable** — `%Error-BLKANDNBLK`. **Never silence this with `-Wno-BLKANDNBLK`.** Verilator cannot represent a variable that is both, and the silenced build computes silently wrong results. Details and the fix pattern: vault note «Смешение блокирующего и неблокирующего присваивания одной переменной».
- The same rule extends to structures: the manual states that all members of a structure are scheduled together, so writing one member blocking and another non-blocking is unsupported.
- Includes are resolved only through `+incdir+`, never relative to the including file. This RTL includes relatively, so pass an `+incdir+` for every source directory.
- Sources here include `"../rtl/config.vh"` — a path relative to the **current directory**. Run both the translation and the built binary from the directory that makes such paths resolve.
- **`UNOPTFLAT` on an unpacked array is usually a false alarm.** A chain `assign sum[i] = sum[i-1] + in_arr[i]` is a ladder, not a loop, but Verilator tracks the array as one signal and reports circular combinational logic. Unlike `BLKANDNBLK`, suppressing this one costs nothing but scheduling: `-Wno-UNOPTFLAT`.

## Making Results Agree: Differential Tracing

Guessing which construct diverged has failed repeatedly on this project. Measure instead.

1. Write one testbench that both simulators run unchanged, and have it dump a CSV of the signals along the path under test — one line **per change**, not per clock, or the file is unusable.
2. Run it in ModelSim and in Verilator into separate files.
3. Compare with `diff_trace.py` (in the encoder bench): it aligns the two by simulated time, skips points where either side is `x`/`z`, and reports the **first** divergence plus, per column, when that column first diverged.
4. `$time` is returned in units of the simulator's **precision**, and the two differ: ModelSim launched with `-t 1ns` counts nanoseconds, Verilator with `--timescale 1ns/1ps` counts picoseconds. Normalise before comparing or the sets of time points do not intersect at all.
5. Expect `x` in ModelSim against `0` in Verilator at time zero: the event simulator is four-state, Verilator is two-state and `--x-initial fast` zeroes everything. That difference is a property of the models. It matters only where the design lets an undefined value reach arithmetic.

### Divergences found this way

Three, on one path, each hidden behind the previous one. All three were defects
of ours; none was a limitation of Verilator.

- **Division by zero before the first encoder rib.** `ref_encoder_calculator` divides by `rib_period` every clock, and that period is zero until the encoder produces a rib. The quotient is undefined; ModelSim held `absolute_position` at 0 while Verilator produced 148 574 at 263 ns, and from that point the scheduler state machines took different branches and never resynchronised. Fixed by gating the divider on a non-zero period.
- **A gate opened before the pipeline behind it was full.** `fxp_div_pipe` is free-running with a latency of `Q_WIDTH + 3`; the gate above let the quotient out the moment the period became non-zero, while the pipeline still held results computed with a zero divisor. One cycle of rubbish — ModelSim 0, Verilator 524 287 — was enough to send the scheduler down a different branch permanently. Fixed by delaying the gate through a shift register of the same length as the pipeline.
- **A register left without an initial value.** `encoder_pll.timer_current_period` had no `= 0` while the two registers written by the same `always` block did. Its X reached the divisor of the angle-lead divider, and there `b == 0` decides between a one-cycle divide-by-zero exit and a full 29-cycle division: ModelSim (four-state) took the long branch, Verilator (two-state, `--x-initial fast`) the short one, and the free-running divider kept a permanent phase offset. One `= 0` brought the traces to **2927 of 2927 identical points**.
- **Stimulus driven on the same clock edge the design samples.** `raw_encoder_from_file` played its recording with `repeat (ticks) @(posedge clk)` and assigned the new level right after. Both simulators resume the coroutine on the same edge — the `repeat` count is not in question — but Verilator lets an `always @(posedge clk)` block see that assignment on the *same* edge, while ModelSim shows it on the next. Every one of the 33 encoder edges in a 1.2 ms window landed one clock apart, so the two simulators were being fed different input. Non-blocking assignment does not help; the fix is to count the ticks on `@(negedge clk)`, which both simulators read identically. Measured with a four-line testbench; details in the vault note «Гонка стимула и схемы на одном фронте такта».
- **The stimulus counted an edge that only existed at time zero.** With the ticks moved to `@(negedge clk)`, the offset flipped sign instead of disappearing: `reg clk = 0` is an assignment *at* time 0, so the transition x → 0 is a negedge, and whether the stimulus process reached its first `@(negedge clk)` before or after the clock got its initial value is not defined. ModelSim counted that pseudo-edge, Verilator did not. Synchronise to a real edge first — `@(posedge clk); @(negedge clk);` — and never count edges straight from time zero.
- **A `generate` branch selected by a string parameter, silently taken by neither.** `multiplier` declared `parameter MODE = "SERIAL"` — untyped, so its type is the packed vector of its default — while `linear_interpolation` passed the mode down through `string MULT_MODE`. Comparing the two types, ModelSim picked the right branch and Verilator picked **none**: the module was generated empty, `done_stb` was never driven, and the interpolator FSM waited forever. Sixteen thousand missing shots, no warning, clean build. Declare such a parameter `parameter string MODE`, and always give the `generate` an `else` that fails loudly. Details: vault note «Строковый параметр в условии generate».

### The rule that follows from them

**The trust was earned, not assumed.** After the six fixes above, the same testbench over 80 ms of model time gives `full_view_fires=11357 sector_fires=7326 total=18683 errors=0 ALL PASS` in **both** simulators, down to the nanosecond timestamps of the angle-step warnings, and a 1.2 ms differential trace matches on all 506 375 recorded rows. Verilator took 21.9 s where ModelSim took 43 min 48 s — but the number only became worth having once it was the same number.

**Before comparing two simulators, make sure they are being fed the same stimulus.** A testbench that drives inputs on the edge the design samples is not a valid reference for either tool, and the first divergence you find will be in the input, not the design. Drive stimulus in the opposite phase.


**A four-state simulator cannot be matched by adding X to Verilator — Verilator has no X.** The only convergence is to remove the undefined value, and in a design without a reset that means every register carries an initial value. That is not a concession to the tool: on Gowin the flip-flops load their initial values from the bitstream, so the X-propagating run is the one that does *not* describe the hardware. Where the two simulators disagree at time zero, the design is relying on something the silicon does not provide.

## Verification Rule

A Verilator number is not a result until the same testbench in ModelSim produced the same number. When they disagree, the divergence is a finding either way: an RTL defect of ours, or a documented limit of the tool. Record which, with the measurement that settled it.

## Learning

When work reveals a durable, reusable lesson for this domain, use the `skill-learning` policy. Save the rule, the flag, the diagnostic message, or the divergence pattern here; keep project-specific measurements in the `fpga-dev` skill and transient task state in the Obsidian notes.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
