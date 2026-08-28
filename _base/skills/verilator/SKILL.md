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
- **Nested interface members are not reachable.** Reading `if_outer.if_inner.field` — an interface instance passed into another interface — fails with `Can't find varpin scope of '<field>' in dotted signal`, followed by `Internal Error: ../V3Const.cpp: Not linked`. ModelSim and GowinSynthesis both accept it. The lidar encoder path does exactly this (`if_enc_v4.if_ref_enc.ch_A` in `ref_encoder_v4.sv`), and the only way through is to carry the signal as an ordinary port instead of through the nested interface. That is also where this project was already heading: the same file on `research/verilator-encoder-bench` takes `in_raw_encoder` as a plain port.
- **Every source directory has to be an `+incdir+`.** The repository convention is to include from the `src` root, but legacy files still include relative to themselves, and Verilator resolves neither relative to the including file. Generating one `-f` file with every directory that holds sources is the only thing that works; a missing one shows up as `Cannot find include file`.
- **A comment whose first word is `Verilator` is read as a directive.** Verilator scans comments for its own metacommands, so `// Verilator не принимает эту конструкцию` becomes `Unknown verilator comment` and stops translation. It does not matter that the rest is prose, or that the language is not English — only the first word after the slashes. Write the tool's name anywhere but first.
- **Cyrillic in `$display` reaches the generated C++ raw** and GCC warns `unknown escape sequence: '\c'` for byte sequences that happen to look like escapes. Output is still correct; the warnings are noise.
- Sources here include `"../rtl/config.vh"` — a path relative to the **current directory**. Run both the translation and the built binary from the directory that makes such paths resolve.
- **`$readmemh` DROPS THE LAST VALUE when the file does not end with a newline.** ModelSim reads it. This is silent data loss in calibration tables, not a build error, and it is the most dangerous divergence found so far. Measured 27.08.2026 on `width_list_20x20.hex`: ModelSim reported `min: 4239 max: 30434` over twenty entries, Verilator `min: 0 max: 29037` over nineteen with the twentieth left at zero. Reduced to a three-value file, the last value is missing in one copy and present in an otherwise identical copy that ends in a newline. Ten fixture and calibration files in this repository ended without one, `compensation_table.hex` among them. **Check every memory-init file for a trailing newline**, and prefer `tail -c 1 file | od -c` over eyeballing it. GowinSynthesis was checked the same day and reads the last value either way: two syntheses of one design differing only in the trailing newline gave byte-identical netlists, and the value from the unterminated last line was present in both (probe `probe/hexnl`). So the silicon was never affected — but every Verilator run of the last year was reading tables one entry short.
- **Indexing the result of an array method inline is a syntax error.** `exmpl_tbl.min()[0]` — the parser stops at the bracket, `unexpected '['`. ModelSim accepts it. Assign the method result to a queue first, then index the queue.
- **A fixed-size unpacked array cannot be passed to a `[]` formal.** A function declared `input uint24_t arr[]` takes a dynamic array; Verilator maps that to `VlQueue` and the generated C++ will not compile when the caller passes `logic [23:0] tbl [0:19]` (`no known conversion from 'VlUnpacked<…,20>'`). ModelSim converts silently. Copy into a real dynamic array at the call site.
- **A `real` variable connected to a non-real output port is refused** — `Unsupported: Output port connection 'x' connects real to non-real`. On inputs it is only a `REALCVT` warning. **Verilator is right here and ModelSim's silent conversion hides a defect**: the testbench was rounding module outputs through floating point. Declare port-connected signals with the port's own type and keep `real` for reference values.
- **Replication inside a dynamic-array assignment pattern is unsupported.** `logic [W-1:0] edges [] = '{ …, {W{1'b1}}, … }` gives `Non-1 replication to form 'logic[W-1:0][]' data type`. ModelSim accepts it. Declare the array with a fixed size and fill it by assignment.
- **A signal used in a port connection before it is declared collides with its own declaration in ModelSim.** Connecting `.in_phi_grid(phi_grid)` above the line that declares `logic [PHI_W-1:0] phi_grid` makes ModelSim create an implicit net at the connection and then reject the real declaration — `'phi_grid' already declared in this scope`. Verilator accepts the same file without a word. Declare before you connect; the error surfaces only in the slower simulator, usually long after the edit.
- **`fork ... join_none` around a `ref` argument is refused, and it is the single biggest blocker in this repository.** `general_tester.make_ndl(ref logic x)` spawned a process that outlives the task's argument — `%Error-LIFETIME: Process might outlive variable`. A sweep of all 213 testbenches on 28.08.2026 found this one shared file blocking **20** of the 129 that would not build. The hazard is real, not a tool quirk. Intra-assignment repeat control (`x <= repeat(1) @(posedge clk) 1'b1;`) would express the same waveform without a process, but Verilator refuses that too — `Unsupported: repeat event control`. What works in both is the plain blocking form: the task holds its caller for the two edges instead of returning at once. That changes testbench timing, so accept it only after checking the affected testbenches in both simulators — here none of the 27 users had a verdict to lose.
- **A testbench without `$finish` never ends.** ModelSim leaves you at a prompt; Verilator's `--main` loops until the wall-clock timeout, and the runner then reports a build or run failure for a testbench that actually worked. `run_verilator.sh` warns when `$finish` is missing — heed it, and put the `$finish` after the verdict, in the stimulus process, not in a block that fires on the first strobe. The cost is not only patience: a bisect over four builds of `shot_scheduler_tb` would have burned forty minutes in timeouts after every run had already printed its verdict. **Before running one testbench many times, check it has a `$finish`.**

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

- **ModelSim loses `signed` on a net declared through a type parameter — Verilator keeps it.** `wire local_t_signed x = y >>> N;` where `local_t_signed` is `logic signed [W-1:0]` looks signed and is signed in Verilator, but ModelSim treats the net as unsigned and turns `>>>` into a logical shift. Measured 27.08.2026 in `dpll_nco`: with `lcl_err = -1`, `lcl_err >>> 3` gave **2 097 151** in ModelSim (that is `0xFFFFFF` shifted in zeros) against `-1` in Verilator. The period correction came out at two million, the PLL never locked, and the two simulators reported 3 shots versus 22 on identical RTL. Declare the net `wire signed [W-1:0]` and wrap the operand in `$signed()`; then both read it the same way. **This is the one divergence so far where ModelSim, not Verilator, is the odd one out** — worth remembering while the project still treats ModelSim as the reference.
- **`repeat` inside `fork ... join_none` is refused.** `%Error-LIFETIME: Process might outlive variable '__Vrepeat…'`. ModelSim accepts it. Restructure the spawned process without a `repeat`, or keep the loop in the main thread.
- **A variable driven from both an `initial` block and an `always_ff` behaves differently.** Verilator runs it as written; ModelSim produced a constant zero for the whole test. Found in a testbench of mine, not in the RTL, and it cost a wrong diagnosis: the arithmetic under test was fine, the harness was not. Same family as `BLKANDNBLK` — one variable, one driver.

- **`<=` inside an `initial` block is executed as `=`.** Verilator says so plainly — `%Warning-INITIALDLY ... This will be executed as a blocking assignment '='!` — and then does it. ModelSim schedules it in the NBA region as written. So a stimulus generator "made race-free" by switching to non-blocking is race-free in one simulator and unchanged in the other. Found 27.08.2026 in `raw_encoder_from_file`, where exactly that fix had been applied the day before. What actually saved it was the other half of the same fix: counting the ticks on `@(negedge clk)`, which puts the assignment half a cycle away from the sampling edge and makes the blocking/non-blocking question irrelevant. **Do not rely on `<=` in an `initial` block for ordering — put the assignment in the opposite clock phase instead.**

- **A rewrite that LATCHES an undefined value diverges where the original did not.** The old NCO read `ref_period` only through wires: while it was undefined the comparison produced `x`, the branch was not taken, and everything recovered by itself once the period appeared. The rewritten one *loads* the period into a down-counter, and an `x` that lands there stays forever — the sign bit is `x`, the edge never comes, the module is dead. Measured 27.08.2026 on the same RTL and the same testbench: ModelSim gave 9 shots and `FAILED`, Verilator gave 1513 and `ALL PASS`, because two-state simulation has no `x` to latch. The lesson is not about the tools: **when you replace combinational reads with registered state, you also remove the design's ability to recover from an undefined input**, and the four-state simulator is the only one that will tell you.

### The rule that follows from them

**The trust was earned, not assumed.** After the six fixes above, the same testbench over 80 ms of model time gives `full_view_fires=11357 sector_fires=7326 total=18683 errors=0 ALL PASS` in **both** simulators, down to the nanosecond timestamps of the angle-step warnings, and a 1.2 ms differential trace matches on all 506 375 recorded rows. Verilator took 21.9 s where ModelSim took 43 min 48 s — but the number only became worth having once it was the same number.

**Before comparing two simulators, make sure they are being fed the same stimulus.** A testbench that drives inputs on the edge the design samples is not a valid reference for either tool, and the first divergence you find will be in the input, not the design. Drive stimulus in the opposite phase.


**A four-state simulator cannot be matched by adding X to Verilator — Verilator has no X.** The only convergence is to remove the undefined value, and in a design without a reset that means every register carries an initial value. That is not a concession to the tool: on Gowin the flip-flops load their initial values from the bitstream, so the X-propagating run is the one that does *not* describe the hardware. Where the two simulators disagree at time zero, the design is relying on something the silicon does not provide.

## Run Both Simulators On Every Testbench

Project decision, 27.08.2026: every simulation is run in **both** ModelSim and
Verilator, and the two verdicts are compared. The runner is `run_both.sh` on the
`feat/clk-300mhz` branch; it takes one testbench, runs it through both, and
prints whether the verdicts agree.

The reason is that each simulator is blind in a different way. ModelSim carries
four states and accepts constructs Verilator refuses outright; Verilator is two
orders of magnitude faster and catches what ModelSim passes over in silence. A
verdict from one of them is a claim; a matching verdict from both is a check.

**A matching verdict is not always a check.** Two runs that both die before
printing anything agree perfectly. The runner used to call that state `RUN_OK`
on one side and nothing on the other and report «вердикты совпали»; it now names
it `НЕТ_ВЕРДИКТА` on both sides and says plainly that nothing was verified.
Whenever a comparison comes back green, confirm that at least one of the two
logs actually contains the words PASS or FAIL.

**Give the runner a testbench name, not only a path.** `./run_both.sh dpll_nco_tb`
now resolves the name under `src/` and `probe/`. Before that, a bare name became
a path that did not exist, and the runner reported «нет .do / сборка не прошла» —
a fabricated divergence caused by the call, not the design.

**At 300 MHz ModelSim stopped being practical for the full-path testbench.**
`encoder_processing_tb` plays a real encoder recording, so raising the system
clock from 50 to 300 MHz multiplies the simulated cycles by six. ModelSim took
43 minutes at 50 MHz; at 300 it was still running after two hours of CPU and had
to be killed, while Verilator finished the same run in minutes. From this point
the full-path test is a Verilator test, and ModelSim keeps the module-level ones
where its four states still earn their keep. That is not a preference — it is the
first place where the two-simulator rule costs more than it returns.

**Making a testbench self-checking is a PAIR of changes, not one.** The `$finish`
goes in the testbench; the `.do` must switch from a fixed `run 2400` to `run -all`
at the same time. Otherwise ModelSim stops mid-run and prints no verdict while
Verilator prints one — a divergence manufactured by the harness, not the design.
155 of the 204 `.do` files in this repository still carry a fixed `run N`, so
expect to hit this on nearly every testbench you rewrite. The reverse order is
also wrong: `run -all` on a testbench with no `$finish` hangs ModelSim forever.

**Measure the distance, do not estimate it.** `sweep_verilator.sh` on the
`feat/clk-300mhz` branch runs every `*_tb.sv` through Verilator and sorts the
outcome into five buckets — builds and passes, builds and fails, builds without a
verdict, times out, does not build — and for the last bucket it names the cause
from the log. First run, 28.08.2026, 213 testbenches: 84 built, 27 gave a PASS.
The cause histogram is what makes the number useful:

    20  fork around a ref argument, all from one shared file
    23  rotten include paths — the file moved or was deleted
     6  default value on a module input
     5  module name differs from the file name
    ~75 long tail

Fixing the first cause alone moved thirteen testbenches out of «does not build»,
and fixing the top-module lookup in the runner covered five more. **Attack the
histogram, not individual testbenches.**

The measurement also settles what the real obstacle is. It is not Verilator:
fifty-two testbenches build and run but never end, because they were written to
be watched as waveforms and have no `$finish` and no self-check at all. Until
those become self-checking, dropping ModelSim gains nothing on them — there is no
verdict to compare in either simulator. That is the work, and it is countable.

**The direction of travel is away from ModelSim.** It is the reference today
only because the design was written against it. Every divergence found is
recorded here with the measurement that settled it, and when the list stops
growing, Verilator becomes the reference and ModelSim the second opinion. Do not
treat "ModelSim says so" as authority — treat it as one of two readings.

Write down every divergence, including the ones that turn out to be our defect.
Those are the majority, and they are what makes the list finite.

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
