# FPGA Development

Use this skill to make FPGA work reproducible: inspect the project first, identify the exact toolchain and target device, make narrow HDL/constraint edits, and verify with the lightest check that proves the change.

For long-running or high-stakes FPGA tasks, create an active goal when goal tools are available and write a compact plan/checkpoint before substantive work starts. Record the objective, target branch, files in scope, user constraints, planned simulations/builds, baseline observations, and next steps so context compaction cannot erase task state. After compaction, interruption, or a long gap, read the active goal/plan and the checkpoint before continuing.

## User Correction Loop

- Treat every explicit user request to redo or correct the work as durable
  feedback, not as a one-off chat instruction.
- Before finishing the task, distill the correction into a concise,
  testable rule in the most relevant project skill reference. Record both the
  reusable workflow lesson and any verified project-specific fact needed to
  prevent the same mistake.
- Do not paste conversation history into the skill. State the resulting
  guardrail, evidence requirement, branch/target distinction, command, or
  hardware fact directly.
- Validate the updated skill and mention the changed skill file in the task
  handoff.

## Workflow

1. Identify the active FPGA project before editing.
   - Look for `.gprj`, `.xpr`, `.qpf`, `.qsf`, `.cst`, `.xdc`, `.sdc`, `.tcl`, `.do`, `impl/`, `sim/`, and top modules.
   - Read existing build scripts before inventing commands.
   - Treat generated implementation outputs as artifacts unless the user asks to inspect them.

2. If the user says a project is incomplete after `git pull`, a clone is missing dependencies, or a previous commit/TODO asks to fix dependencies, resolve it autonomously.
   - Inspect the newest relevant commit first: commit message, TODOs, touched files, submodule pointer changes, and build-script changes.
   - Check `.gitmodules`, `git submodule status --recursive`, submodule remotes, and whether the exact pinned submodule commits exist on the configured non-local remote with `git ls-remote` or equivalent.
   - Replace local-only submodule URLs such as `C:/workspace/...` with the intended shareable remote when it is knowable from the submodule remotes. If the pinned commit only exists locally, do not silently leave the superproject pointing at an unreachable SHA; either move to a reachable commit only when that preserves the requested behavior, or record the exact unpublished submodule commits and state that pushing that submodule is required. Do not push unless the user explicitly asks.
   - Search project files, build scripts, TCL, `.gprj`, `.do`, docs, and active source for references to untracked `.v/.sv/.svh/.vh`, `.cst`, `.sdc`, `.ipc/.mod`, `.hex/.mem`, firmware, scripts, and vendor sources. Add missing source dependencies to version control when they are required to open/build/simulate the active project.
   - Keep generated outputs out of version control: `impl/`, `work/`, ModelSim `wlft*`, `vsim.wlf`, `.vcd`, PnR/synthesis reports, temporary PDFs, OS shortcuts, copied batch files, and local GUI/user files. Extend `.gitignore` when noisy generated files obscure the dependency audit.
   - Prefer making project paths relative and script-derived from the repository root. Avoid checked-in absolute paths to `C:\workspace\verilog` in active project files or build entrypoints unless the tool format truly requires them.
   - Document external tool dependencies that cannot be vendored, such as Gowin EDA, ModelSim, MSYS2 make, RISC-V GCC, `lconf`, Npcap/Scapy, and hardware/programmer requirements, including the exact wrapper command that proves the setup.
   - Verify the fix from a clean checkout shape when feasible: clone or worktree into a temporary directory, initialize submodules, run the lightest build/simulation check that covers the active target, and confirm no required file is present only because it was untracked in the original workspace.

3. Classify the task.
   - HDL edit: inspect the module, its interfaces, testbench, included packages, and call sites.
   - Constraint edit: inspect pin, clock, timing, and IO-standard constraints together with the board/top wrapper.
   - Build/debug: find the project script and latest logs/reports before changing code.
   - Simulation: prefer existing `.do` or documented ModelSim/Questa flow.
   - Programming/flash: require an explicit user request before invoking programmer tools or writing hardware.

4. Make scoped changes.
   - Prefer existing project modules, IP wrappers, helpers, and known-good implementations before writing new HDL. Add new modules only when no suitable reusable block exists or reuse would make the change riskier.
   - Before hand-writing a local edge detector, synchronizer, pulse generator,
     timer, counter, FIFO, CRC, serializer, or similar helper, search the
     repository with `rg` by both function and likely module names and inspect
     its existing call sites. A private implementation is not justified merely
     because it takes only a register and an `assign`: reuse the canonical
     module when its latency, reset, clock-domain, and synthesis semantics fit.
     If they do not fit, record the concrete mismatch and cover the new helper
     with a focused TB. When correcting this pattern, audit and replace the
     obvious duplicates in the same functional scope instead of fixing only
     the first quoted occurrence.
   - Before duplicating a non-trivial arithmetic converter for several values
     from one transaction, compare its worst-case latency with the required
     transaction interval. When one instance has sufficient throughput,
     time-multiplex it with latched transaction inputs, explicit result
     association state, and a bounded completion contract. Prove distinct
     per-value results, configuration snapshot semantics, and the real
     integration rate in TB; then compare PnR resources and timing against the
     parallel baseline. Keep parallel instances when throughput evidence
     requires them, not merely because the port mapping is shorter.
   - Use `edge_detector` as the canonical generic helper for sampled signal
     transitions. Its public event strobes are `out_edge_detected_stb`,
     `out_rising_edge_detected_stb`, and
     `out_falling_edge_detected_stb`. Do not introduce `front_detector`,
     `front_detected`, or `backfront_detected` in generic helper, port,
     instance, or directly connected local-signal names. Established
     domain-event names such as `start_transaction_stb` may remain when they
     describe the consumer's meaning rather than the detector implementation.
   - Rename a shared HDL helper as one repository-wide contract change: rename
     its directory, source file, module, include guard, focused TB and `.do`
     file, include/build/project references, instance names, related
     configuration fields, public ports, and directly connected implementation
     signals. Audit active and legacy consumers, scripts, and documentation
     with `rg`; do not stop after the current top compiles. List every public
     named port at every touched instance and write an intentionally unused
     output as `.out_name()` so elaboration does not report it as missing.
     Acceptance requires the focused self-checking TB, affected integration
     TBs, synthesis/PnR, and a zero-result stale-name audit before commit.
   - Define every FSM state set with a SystemVerilog enum such as
     `typedef enum { ... } state_t`, and declare both current- and next-state
     registers with that enum type. Do not specify an explicit base type or
     packed width such as `logic [N-1:0]` for an FSM enum; leave its
     representation to the compiler and synthesis tool. Do not model an FSM
     with state `localparam` values plus an untyped `logic [N-1:0]` register.
     Preserve explicit enumerator values when an encoding is externally
     observed, used for diagnostics, or must remain stable; otherwise allow
     the enum to assign sequential values. When correcting legacy code, audit
     the obvious FSM copies in the same functional scope and prove the typed
     version with the affected TB and synthesis/PnR flow.
   - For a configurable serial or protocol engine, derive phase-counter widths
     from the longest legal phase across its public parameters, not only from
     the largest current default. Its focused TB must check wire order,
     per-phase output-enable/turnaround, exact cycle count, completion-strobe
     width, reset during a transaction, and safe illegal-state recovery. The
     recovery path must release bus ownership (`busy`, chip-select, clock, and
     output-enable as applicable), not merely assign the idle enum value.
   - Do not describe QSPI as one universal transaction protocol. State the
     exact verified lane/edge contract in the module name and documentation,
     for example mode-0 `1-4-4 SDR`: command on one lane, address and data on
     four lanes. Opcode meaning, address width, dummy/turnaround selection,
     register layout, SDR/DDR choice, and device setup are separate contracts.
     Put the reusable wire transaction in a transport module and bind
     device-specific values at the integration boundary. Add a thin adapter
     only when it owns a meaningful reusable device contract, translation, or
     behavior. If a module only forwards the same ports and binds constants
     already known by its consumer, delete it and instantiate the transport
     directly.
   - Do not generalize a serial transport beyond its known consumers merely
     because a parameter can be added. Search current call sites first and
     implement the narrowest reusable contract that they actually require.
     Add runtime commands, additional address widths, lane modes, or DDR only
     with a real consumer and a focused protocol test for that variant.
     Parameterized indexed part-selects and shift serializers can infer more
     logic than a fixed proven path in Gowin, even when behavioral simulation
     is identical.
   - Accept a protocol-engine extraction only after the transport TB, any
     meaningful adapter TB, affected integration TBs, and synthesis/PnR all
     pass. Remove a pass-through wrapper and its wrapper-only TB; prove the
     fixed command/address/dummy binding in every affected integration TB.
     Compare registers, logic, Fmax, setup/hold, and bitstream freshness with a
     build of the exact pre-refactor commit. When a global PnR delta obscures
     the cause, compare primitive counts for the affected modules in the two
     synthesized netlists. A file-boundary refactor should not silently buy
     unused flexibility with LUTs.
   - Preserve existing module style, naming, reset polarity, clock-domain conventions, and package/interface structure.
   - Audit every active `` `include `` in each edited HDL source or testbench.
     Keep it only when it supplies a referenced macro, type, interface,
     package, module, or required compilation-order dependency. Remove unused,
     duplicate, legacy, and "just in case" includes together with declarations
     that existed only to justify them, then compile or elaborate the affected
     translation unit to prove that no hidden dependency was removed.
   - Each file must be SELF-SUFFICIENT: it includes everything it references
     itself, with the path written relative to ITS OWN location, and it never
     relies on a dependency arriving because some other file happened to be
     compiled first. This is the other half of the audit rule above — together
     they mean "include exactly what you use, no more and no less".
     - A file that waits for a transitive include compiles only in one
       particular file order. It then breaks when the `.do`/`.prj`/`add_file`
       order changes, when a focused TB compiles it alone, when synthesis
       builds the list from a different top, or when someone removes an
       "unused" include from an unrelated file. The failure surfaces far from
       the file that caused it.
     - Give every `.sv`/`.svh` an `` `ifndef `` include guard, so being
       explicit costs nothing: a repeated include is free, while a missing one
       is a latent order dependency. Without guards GowinSynthesis reports
       `ERROR (EX3794): Overwriting previous definition of module` where
       ModelSim stays silent.
     - Самодостаточность режет в ОБЕ стороны: включать надо СВОИ прямые
       зависимости и ТОЛЬКО их. Если файл включает `X.sv`, но сам ничего из `X`
       не инстанцирует и не использует, а `X` нужен лишь тому, кого этот файл
       тоже включает, — такой include лишний и должен быть удалён. Зависимости
       чужого модуля — забота чужого модуля.
     - У лишнего транзитного include есть измеримая цена, а не только
       эстетическая. Gowin склеивает относительные пути НЕ нормализуя их, и
       цепочка включений даёт строки вида
       `src/main/../TDC/lidar_measurement_pipeline/../encoder_processing/../..`.
       Измерено 12.08.2026: сборка того же дерева из каталога с длинным
       префиксом пути упала пачкой `ERROR (EX1985) Cannot open include file`
       именно на таких склейках, тогда как из `C:\workspace\verilog` собиралась.
       Каждый лишний ярус включения приближает проект к MAX_PATH и делает
       сборку зависящей от того, где лежит рабочая копия.
     - **Конвенция этого репозитория с 12.08.2026: include пишется ОТ КОРНЯ
       `src/`**, а не относительно своего каталога:
       `` `include "machines/machine_header.sv" `` вместо `"../../../machines/…"`.
       Корень объявлен обеим цепочкам: Gowin — `set_option -include_path
       <repo>/src` (уже стоял во всех 14 сборочных tcl), ModelSim — `+incdir+<src>`
       через обёртку `vlog` в `src/MS_common/modelsim_common.do`.

       Это НЕ «сторонний include»: за файл ничего не подключается, он
       по-прежнему перечисляет все свои зависимости сам. Меняется только точка
       отсчёта имени, зато файл перестаёт зависеть от собственного расположения.

       Замер на `R120M_BM2BF1X1`: до конверсии максимум 241 символ при лимите
       260, 42 пути длиннее 200, до 11 сегментов `..`; после — 140 символов, ни
       одного `..`, запас 120. Приёмка конверсии 929 include в 334 файлах:
       `.bin` побитово тот же, 4 сборочные цели собрались, 8 ТБ зелёные.

       Конверсия ВСКРЫВАЕТ несамодостаточные файлы, и это её польза.
       `ltdc_point_builder`, `tdc_processing`, `DST_calculator`, `BLDC_driver`,
       `strobe_delayer`, `R120_M_1_1_0_brd_ifm` инстанцировали модули, которых
       не включали: их заранее подключал `main.sv` коротким путём, чтобы
       сторожевые `ifndef` погасили длинные вложенные include. Вот ЭТО и есть
       настоящий сторонний include; убирать его надо вместе с переходом,
       добавив каждому файлу собственные зависимости.
     - `+incdir` is for locating a genuinely shared search root, NOT for
       repairing a wrong relative path. If a file compiles only because
       `+incdir` found its dependency by bare name, fix the path in the file.
     - Measured 2026-08-07 (ModelSim 10.5b): a relative `` `include `` resolves
       against the DIRECTORY OF THE INCLUDING FILE, not against the current
       working directory. Compiling from an unrelated directory with an
       absolute path to the TB and no `+incdir` at all resolved a two-hop
       chain with `Errors: 0`. `Cannot open \`include file` means the FILE
       MOVED relative to its dependency (a TB copied into a scratch dir keeps
       its old `../../../` prefix), not that the shell was in the wrong place.
   - Indent Verilog and SystemVerilog with four spaces per nesting level. Do not use literal tab characters or two-space indentation. Keep continuation indentation on four-space boundaries. When indentation is corrected in an HDL module already in task scope, include that cleanup in the same task and commit unless the user explicitly asks to split it; do not leave the verified formatting behind merely because it predates the latest semantic request. For an indentation-only change, confirm that the diff is whitespace-only and rerun the relevant testbench before committing.
   - Follow these HDL naming rules in new and edited module contracts:
     - Prefix ordinary input ports with `in_` and output ports with `out_`; `clk`, `rst`, and interface ports are exceptions.
     - Prefix every interface port and interface instance with `if_`; use `if_lcl_<name>` for a local interface.
     - End every one-cycle strobe name with `_stb`; do not use `_1t` as the public strobe suffix.
     - Mark internal interconnects that do not cross the current module boundary with the `lcl_` prefix (`lcl_<name>`), and do not give them `in_` or `out_` prefixes. `lcl` goes at the front of the name, never at the end: the trailing `_lcl` form found in older code (`crc_lcl`, `if_rmii_lcl`, `real_rib_detected_lcl_stb`) is legacy and must not be used in new or edited declarations; rename it when the surrounding lines are being reworked anyway, not as a standalone sweep.
     - For a local strobe, use `lcl_<name>_stb` so `lcl_` stays the prefix and `_stb` remains the final suffix.
     - Prefix every module instance name with `obj_`, normally `obj_<module_name>` (`ref_encoder_z_rib_detector #() obj_ref_encoder_z_rib_detector (...)`); add a distinguishing suffix when one module is instantiated several times. Short forms such as `o_<module_name>` are legacy and must not be used in new code. Interface instances keep the `if_` prefix instead.
     - Update every named port map and relevant testbench in the same change when renaming a port. Keep an intentionally unused port explicit with an empty named connection only when it remains a meaningful shared contract used or directly validated by another active call site; otherwise remove the port and its dead propagation end to end.
   - Declare parameters, ports, and variables in column form whenever the language allows one keyword/type to introduce several names: write the keyword (`parameter`, `input`, `output`, `logic[23:0]`, ...) once, then put each name on its own indented line, one comma-separated item per line. Do not repeat the type keyword on every line and do not pack a long list onto one line. Alternative values kept for bench work stay as commented-out lines inside the same block, next to the active one, and a trailing `//` comment belongs on the line of the name it describes. Two closely related names may share a line only when they are a pair (a value and its copy).

     ```systemverilog
     parameter
         INIT_VALUE = 100_000,
         // INIT_VALUE = 1500,
         FEEDBACK_COEFFICIENT = 4,
         INIT_VALUE_IIR = (INIT_VALUE * (FEEDBACK_COEFFICIENT - 1) / FEEDBACK_COEFFICIENT);

     logic[23:0]
         rib_period_rought,
         instant_period_cnt, instant_period_cnt_cpy = 0,
         rib_cnt,  // теперь генерируется из ref_enc_phase_counter
         max_rib_cnt = 0,
         avg_rib_period, // значение после двух фильтров баттерворта
         real_period = 0,
         virtual_rib_period,
         virtual_rib_precise_cnt;
     ```

     The bit width is part of the shared declaration head, so group variables by width: one `logic[23:0]` block for all 24-bit signals instead of a separate declaration per name. The same applies to the port list — one `input` / `output` keyword, then the ports in a column, with a nested type keyword only where the type actually changes. Reference implementation: `src/ref_encoder/ref_encoder_v4/ref_encoder_v4/ref_encoder_v4.sv`.
   - Prefer a SystemVerilog streaming concatenation over a generate loop for
     pure static packing, unpacking, or element reordering when it expresses
     the mapping directly. Specify both direction and slice size explicitly
     (for example, `{<<8{bytes}}`), document which element occupies the least-
     significant slice, and verify the order in a focused TB with distinct,
     non-symmetric element values. Compile and synthesize the expression with
     the target toolchain before adopting it; fall back to explicit indexed
     assignments when streaming support or the mapping is ambiguous.
   - Keep acquisition depth and exported result count as separate contracts.
     A parameter such as `HITS_PER_CHANNEL` describes the hit-buffer depth in
     each physical channel; it must not be interpreted as the number of
     logical echoes at the protocol output. Name the output count separately,
     document the channel/hit-to-output mapping, and verify it with distinct
     per-channel values at the final serialized interface. Checking only an
     internal array or configuration register is not sufficient.
   - Preserve every field of every exported logical result end to end. Reading
     a complete device result window is not sufficient: parse, latch, convert,
     qualify, and serialize the dedicated TOF and PW/intensity of each logical
     echo. Never reuse a protocol payload field, especially `intensity1` or
     `intensity2`, as hidden storage for mirror, channel, sector, or other
     association metadata; keep that metadata in dedicated state. Acceptance
     must use distinct, non-symmetric PW/intensity values for the echoes,
     change the association metadata independently, and check the final
     serialized payload bytes across a packet boundary.
   - Do not encode product, calibration, or conversion thresholds as elaboration-time parameters when they must change while the FPGA is running. Parameters are for immutable structural choices and, at most, reset/default values; the consuming datapath must receive a `logic` or interface field through ordinary ports. Put the field at the owning configuration boundary and thread it through every intermediate module to the consumer. Until the real write source is defined, keep the current value only as a documented startup default; do not invent a command address, runtime detector, or calibration algorithm ahead of that decision. Acceptance must change the field at least once in the same elaborated DUT and assert the changed functional result. A parameter override, default-only check, hierarchical constant, or `force` by itself does not prove a synthesizable runtime write source; when that source is deferred, distinguish verified RTL plumbing from live-hardware writability.
   - Поле интерфейса не знает, чем оно является для модуля. Роль задаёт имя
     ПОРТА потребителя, а не имя поля.

     Одно и то же `if_mcu_fpga.msop_tcp_echo_mode` для `MCU_FPGA` — то, что он
     только что ЗАПИСАЛ по команде, а для цепочки MSOP — псевдостатическая
     настройка, которую она ЧИТАЕТ и обязана защёлкнуть. Ярус (`_req`, `_lat`,
     `_act`), направление и признак настройки — свойства не величины, а её
     употребления в конкретном модуле.

     Отсюда разделение: имя поля интерфейса описывает СУЩНОСТЬ (что это за
     величина и чья она), имя порта — РОЛЬ в модуле. Ролевые квалификаторы
     (`in_`, `out_`, `cfg`, `_req`/`_act`/`_lat`, `_stb`) в имена полей
     интерфейса не тащить: поле, названное `in_cfg_...`, соврёт первому же
     модулю, который его пишет, а не читает.

     Практическое следствие: введение конвенции для портов НЕ требует
     переименования полей интерфейса, и разнобой между `msop_tcp_echo_mode` в
     интерфейсе и `in_cfg_echo_mode` на порту — не рассогласование, а разные
     уровни описания.
   - Псевдостатическое поле (runtime-настройка) именуется квалификатором `cfg`.

     Это значение, которое задаёт пользователь/МК и которое само по себе не
     меняется: формат пакета, разрешение сетки, пороги, смещения. По сути это
     `parameter`, который разрешено писать на работающей ПЛИС, поэтому его
     нельзя ни объявлять параметром (см. правило выше), ни путать с обычными
     данными и состоянием тракта.

     **Контракт `cfg`:** источник вправе изменить значение в ЛЮБОЙ такт, без
     синхронизации с кадром или транзакцией, и не ждёт подтверждения. Решение о
     том, КОГДА применить изменение, принадлежит модулю-потребителю: он
     выбирает свою точку применения (граница кадра, конец транзакции, флаш
     конвейера) и до неё обязан работать по защёлкнутому значению.

     | Роль | Имя | Природа |
     |---|---|---|
     | пришло снаружи | `in_cfg_<имя>` | порт; может уехать посреди кадра |
     | нормализовано (мусор → дефолт) | `lcl_cfg_<имя>_req` | провод, следует за входом |
     | действует в текущей транзакции | `lcl_cfg_<имя>_act` | регистр, меняется только в точке применения |
     | заявка ≠ действующего | `lcl_cfg_mismatch` | СОСТОЯНИЕ, живёт сколь угодно долго — суффикса `_stb` не несёт |
     | момент применения | `lcl_cfg_apply_stb` | строб, ровно один такт |

     Правила, которые это даёт:
     - `in_cfg_*` НЕ использовать напрямую в датапате запущенной транзакции —
       под ним значение может смениться на середине кадра. В датапат идёт
       только `_act`.
     - Нормализация обязана стоять ДО сравнения. Если сравнивать `_act` с сырым
       входом, разные нелегальные значения, дающие один и тот же легальный
       результат, поднимут ложное расхождение и приведут к сбросу конвейера на
       ровном месте.
     - Пока политика применения «немедленно», `mismatch` и `apply_stb`
       совпадают, и держать оба сигнала не нужно — оставить `lcl_cfg_apply_stb`
       и описать политику комментарием. Разделять их обязательно в тот момент,
       когда применение становится отложенным: тогда расхождение живёт много
       тактов, и имя с `_stb` станет ложью.
     - Модуль без собственной транзакции (чисто комбинационный форматтер)
       защёлкивать нечего: он принимает `in_cfg_*` и ничего не хранит.

     Эталон в этом репозитории — цепочка MSOP:
     `msop_tcp_pipeline` (владеет точкой применения — граница пакета) →
     `MSOP_TCP_SPI_sender` → `MSOP_TCP_sender` (своя точка применения — сброс
     конвейера) → `MSOP_TCP_body_builder` (комбинационный, только `in_cfg_*`).
   - Keep FPGA board firmware split into a strict file-layer hierarchy when creating or substantially changing a target:
     1. CST/XDC/QSF constraints are the first and lowest physical layer: package pins, IO standards, pullups, and raw package/connector names only.
     2. The board-interface wrapper translates constraint-level port names into meaningful hardware interfaces, `wire`, and `logic` signals; keep pin directions, tri-state behavior, straps, and board-role comments here.
     3. Helper-hardware files contain reusable plumbing such as PLLs, clock dividers, reset generators, serializers, FIFOs, CRC blocks, multipliers, counters, and pin-safe adapters.
     4. Main/application logic files contain the actual behavior and protocol modules, analogous to `main`. Do not hide package pins, CST naming, board straps, PLL/divider plumbing, or pin adapters inside the main logic layer.
   - For board-level dev-board firmware, inspect and reuse existing board wrappers and constraints such as `m20k_dev_brd_ifm.sv` / `m20k_dev_brd.cst` before creating a new top-level pin/interface layer.
   - For one-off dev-board checks, do not add new `m20k_dev_*` top, `.cst`, or `.sdc` files just to isolate a small test. Fold the test into an existing board wrapper/constraint flow, or explain why reusing the existing wrapper would be unsafe before adding files.
   - Do not create a new SystemVerilog interface or interface wrapper for every small bench task. Use plain ports for simple one-off firmware unless the surrounding design already expects an interface.
   - Do not wrap a single scalar pin in a SystemVerilog interface when it has no grouped protocol, shared timing or ownership semantics, or useful modport contract. Pass it through coordination layers as an ordinary `input` or `output`, remove the one-field interface instance and its unused include, and update every named connection end to end.
   - Before declaring a signal live, grep for where it is READ, not only where it is declared and port-mapped. A port can be wired through several levels and never consumed: `out_frame_started_stb` travelled `frame_detector` → `angle_sinc_frame` → `angle_calculator` → `encoder_processing` → `lidar_measurement_pipeline` and was never read there, while MSOP frames were actually cut by a different signal. A dead path costs nothing at runtime but sends every reader of the code down the wrong causal chain, and a testbench may even `force` it to hide the confusion.
   - Treat every empty named connection such as `.out_name()` as a contract-audit trigger. Trace all active call sites and real readers/writers: if nobody consumes an output or drives an input meaningfully, remove that public port, its transitive forwarding, declarations, test-only passthrough wiring, and now-unused includes. If a value is still needed only inside the module, keep it as an `lcl_*` signal instead of exporting it. A focused TB that directly validates behavior at the module defining the port can justify a reusable contract; a higher-level TB that merely observes or forces a pass-through signal cannot by itself justify propagating that port upward.
   - Remove one-hop local aliases that only connect a child-module output to the same module's public output. Connect the child directly to the public output and read that signal locally when the contract is identical and there is exactly one driver. Keep a local signal only when it owns real behavior such as registering, CDC isolation, width/type conversion, arbitration, or a deliberate fanout/timing boundary; do not preserve an otherwise functionless `lcl_*` declaration plus `assign`.
   - Treat temporary debug instrumentation as having an explicit end of life. Before finalizing a production refactor, search the active hierarchy, constraints, testbenches, and wave scripts for `dbg_`, `debug`, `для отладки`, temporary UART reporters, event counters, protocol sniffers, and functional signals mirrored onto service pins. Trace the readers of every hit: when it is diagnostic-only and the investigation is closed, remove its ports, interface fields, transitive propagation, state, counters, and stale TB references end-to-end instead of merely leaving the final output open. Preserve the functional guard, rejection branch, packet-format choice, or other product behavior that the diagnostic signal only observed. If a board/CST contract requires the physical port to remain, drive a defined safe idle value in the board wrapper and describe it as reserved/service in the constraint comments. Dedicated, explicitly named bring-up tops may retain isolated diagnostics. Prove the cleanup with focused behavioral TBs and, when it changes the synthesized hierarchy, with PnR resource, timing, bitstream-freshness, and pin-constraint checks.
   - Avoid broad rewrites of HDL that could perturb timing unless the user asked for refactoring.
   - When the user asks to refactor a touched HDL module, treat the refactor as part of the requested change rather than optional cleanup. Bring the module contract and touched declarations into the active branch's HDL conventions: remove unused legacy ports, interfaces, and transitive include dependencies; separate coordination from functional pipelines at natural boundaries; normalize touched naming, instances, and declaration layout; and update every call site and affected testbench hierarchy in the same change. Preserve behavior unless the user explicitly requests a functional change, keep unrelated modules out of scope, capture a simulation baseline before editing, rerun focused testbenches afterward, and run synthesis/PnR when the structural change can affect timing or resources.
   - Do not treat moving a large legacy block into another file as proof that the block belongs in the design. Before preserving or deleting it, trace each responsibility to a current consumer, board/protocol output, focused regression, or verified hardware behavior. Delete synthesis-dead state and inactive branch-specific code. If the behavior is active but obscures a coordination module, isolate it behind a named functional module and focused testbench; do not delete a proven product path merely because its implementation is difficult to read.
   - For CDC, async reset, generated clocks, PLLs, IO, and RAM/IP primitives, verify the intended vendor/tool behavior instead of assuming generic Verilog semantics.

5. ПРОВЕРЕНО 11.08.2026: ping в сети 192.168.2.x НЕ доказывает, что стенд жив.

   Измерено прямо: `ping 192.168.2.207` и `ping 192.168.2.199` — заведомо
   несуществующие адреса — отвечают 2 из 2 без потерь. В сети есть устройство,
   отвечающее за всех. При этом `arp -a` на тот же адрес показывает, что записи
   нет, то есть отвечает не хост по этому IP.

   Следствие: успешный ping нельзя приводить как доказательство работы тракта.
   Я пользовался им весь день как основной проверкой, и часть выводов вида
   «стенд восстановлен» на нём и держалась.

   Чем проверять на самом деле, в порядке надёжности:
   - счётчики прошивки, прочитанные из ОЗУ через SWD (адреса брать из
     `arm-none-eabi-nm firmware.elf`, читать `openocd ... mdw <адрес> <N>`) —
     работает даже когда консоль по USB отключена;
   - вывод в консоль USB CDC, если она подключена;
   - снимок анализатора.

   Ключевой признак живого приёма — счётчик принятых кадров РАСТЁТ. Ноль в нём
   при «проходящем» ping означает, что тракт мёртв, а отвечает кто-то другой.

5. Кадровый канал стенда 20K: незавершённое чтение УНИЧТОЖАЕТ кадр.

   Контракт `RMII_to_SPI_slave` — «одна транзакция равна одному пакету»: при
   подъёме CS с недочитанным пакетом остаток выбрасывается из очереди (drain до
   кода границы `10`). Значит опрос, прочитавший только два байта длины и
   отпустивший линию, теряет кадр целиком, и наружу это никак не считается.

   Воспроизведено в `m20k_dev_brd_eth_tb` 10.08.2026: первый опрос вернул длину
   60, второй сразу следом — ноль, прерывание упало. На железе тот же механизм
   выглядел как 2750 холостых опросов подряд с интервалом 30.5 мкс, каждый читал
   `00 00`, а линия прерывания оставалась поднятой.

   Следствие для прошивки МК: **прочитав ненулевую длину, обязан дочитать кадр
   до конца**. Любой ранний выход из чтения — потеря данных, а не безобидный
   пропуск. Это же ограничение делает опасным полнодуплексный обмен, где число
   тактов тела считается как максимум из двух длин: если своя длина больше
   чужой, чужой кадр дочитывается, а если меньше — теряется.

5. После неудачного опыта ПЛИС надо ПЕРЕЗАЛИТЬ, прежде чем судить о правке.

   Автоматы остаются в состоянии, в которое их загнал предыдущий опыт, и
   перепрошивка одного микроконтроллера его не снимает. Возврат исходного кода
   и заливка только МК дают картину «правка сломала», хотя код уже прежний.

   Измерено 10.08.2026 дважды подряд на стенде 20K: после отката кадрового
   канала ping не проходил и FLASH молчала, а после переконфигурации ПЛИС тем
   же самым образом всё заработало. Первый раз это стоило неверного вывода
   «регрессию вызвала защита от пустого кадра» — защита оказалась невиновна.

   Правило: цикл проверки — залить ПЛИС, залить МК, только потом мерить. Если
   результат отличается от ожидаемого, повторить заливку ПЛИС до того, как
   объяснять результат кодом.

5. Обвинение конкретному модулю — это гипотеза, а не вывод. Проверять ДО того,
   как назвать её пользователю.

   Разбор кода даёт правдоподобное объяснение почти всегда, и оно почти всегда
   звучит убедительно: «модуль реализует режим наполовину», «глубина буфера
   мала», «параметр не проброшен». Но пока гипотеза не воспроизведена фокусным
   тестом, она остаётся гипотезой, а сформулированная как факт — уводит и
   пользователя, и следующего агента в сторону и портит доверие к остальным
   выводам в том же ответе.

   Правило: прежде чем написать «модуль X написан неверно», собрать фокусный ТБ
   на этот модуль, который проверяет именно спорное свойство, и приложить его
   вердикт. Нет ТБ — формулировать как «подозрение, не проверено», явным словом.

   Урок 10.08.2026, стоил двух неверных диагнозов подряд. Перевод кадрового
   канала стенда в SPI mode 0 сломал приём на железе. Я дважды заявил, что
   виноват `SPI_Slave`: якобы выдача MISO осталась по спаду и первый бит не
   выставляется до первого фронта. Фокусный ТБ `SPI_Slave_modes_tb` показал
   PASS в обе стороны: модуль корректен, править нечего. Первый прогон того же
   ТБ, к слову, дал FAIL — но из-за дефекта в самом ТБ (два драйвера на
   `ndl_Byte_to_master`, из `initial` и из `always`, отсюда `X` на линии).
   То есть проверять надо и собственный тест: `X` на сигнале — это почти всегда
   ошибка стенда, а не находка.

5. Отладка неожиданного поведения железа: СНАЧАЛА воспроизвести в симуляции.

   Когда плата ведёт себя не так, как ожидалось, не начинать с перепрошивок и
   переносов индикации. Взять снятый анализатором/осциллографом стимул (байты,
   тайминги, частоты) и подать его в тестбенч на реальный топ платы, наблюдая
   внутренние сигналы. Один прогон занимает около минуты против пяти-шести на
   цикл «сборка + заливка», и показывает то, чего на пинах не видно.

   Урок 23.07.2026 (стоил десяти циклов сборки и прошивки железа): команды МК не
   доезжали до регистров ПЛИС. На плате менялись пины индикации, биты счётчиков,
   источники стробов — всё вслепую. Первый же тестбенч, подавший снятый кадр на
   командный SPI, сразу показал причину: адрес 0x438 читался как 0x870, то есть
   весь кадр сдвинут на бит из-за несовпадения режима SPI мастера и слейва.

   Признак, по которому надо сразу идти в симулятор: на шине сигнал есть и
   выглядит корректно, а внутренняя реакция отсутствует. Такое расхождение
   почти всегда про фазу/выравнивание, и на пинах его не увидеть.

   Индикацию на светодиод/пин добавлять ПОСЛЕ того, как гипотеза проверена в
   симуляции — чтобы на железе подтверждать уже понятое, а не искать вслепую.

6. Verify progressively.
   - First run syntax/compile checks when available.
   - Run relevant testbenches for behavioral changes.
   - ModelSim ASE DOES run several simulations concurrently — do not serialize testbenches on a licensing assumption. Measured 2026-07-28: two `vsim -c` runs launched together kept two live `vsimk` kernels for ~2 min of real overlap and both finished with exit 0, Errors: 0.
   - Treat `** Fatal: vish lost connection to vsim process` / `** Fatal: Exiting VSIM license process` / `Kernel lost connection to front end process` as "this run proved nothing", not as a design defect and not as a diagnosed cause. A run reported as "completed, exit code 0" whose output ends in those lines did NOT verify anything — rerun it and check the verdict line. Observed once (2026-07-28) when two heavy project testbenches ran in parallel and the longer one had been pushed off the foreground by a 600 s harness timeout; the actual cause was never established. Do not repeat the licensing explanation as fact: the concurrency measurement above refutes it for light designs, and memory pressure (`win32aloem` is a 32-bit binary, ~2 GB address space) or the timeout handling remain untested candidates for heavy ones.
   - CORRECTED 2026-08-07 by measurement: relative `` `include `` paths resolve against the DIRECTORY OF THE INCLUDING FILE, not against the current working directory. Compiling a TB from an unrelated directory works with no `+incdir` at all, provided every file's include paths are correct relative to itself. `Cannot open \`include file` therefore means the FILE moved away from its dependency — typically a TB copied into a scratch directory while keeping its original `../../../` prefix — so fix the path or compile the TB in place. Prefer the project `.do` files: they already `cd` to the script directory, which keeps copied paths honest.
   - Give long simulations a realistic time budget before treating silence as a hang: check that `vsimk` is actually burning CPU (`Get-Process vsimk | Select CPU`). Scale from a known run — one `encoder_processing` instance covers ~3 ms of model time per 1.5 min, so a 40 ms two-instance sweep such as `encoder_processing_sector_tb` needs ~40-45 min and prints its verdict only at the very end.
   - Match evidence to the claim being made. Simulation can prove packet bytes, state-machine behavior, CRC/FCS, timing of internal handshakes, or other logic-level properties; tool evidence can prove build, pin placement, timing, bitstream generation, and programmer operations; hardware evidence can be Ethernet capture, UART output, LEDs, link state, oscilloscope/logic-analyzer/GAO capture, or user-confirmed physical behavior. Require Ethernet capture only when the claim is that packets actually traversed the network.
   - Before programming hardware, prefer a ModelSim Intel FPGA Edition 10.5b simulation or at least a ModelSim compile/elaboration check for the firmware top.
   - ModelSim tool techniques (batch runs, robust .do error handling, WLF/dataset comparison, logging traps, error diagnosis) live in the shared `modelsim` skill (`.codex/skills/_base/skills/modelsim/` in the Obsidian vault; vault digest «Продуктивная работа в ModelSim»). Top wins for this repo: `vsim -batch -logfile` for regressions; `onerror {quit -code 1}` before `run` so PowerShell sees real exit codes; `add log -r /*` for post-mortem waves (memories are excluded from wildcards by default — WildcardFilter/WildcardSizeThreshold).
   - Before re-running a simulation just to add one more `$display`, or starting a long grep chain for "where does this signal go", use the direct-query tooling in the `rtl-agent-tools` skill (`docs/skills/rtl-agent-tools/workflow.md`): wavepeek over a VCD/FST dump, slang / slang-netlist connectivity queries, yosys+eqy equivalence proof after a lint fix. Project-specific numbers, the compatibility flags this RTL needs, and static findings in it are in `agent-tooling.md`.
   - Совпавший битовый образ ЗАКРЫВАЕТ вопрос проверки на железе. Это самое
     сильное доказательство, доступное для рефакторинга, и оно дешевле любого
     стенда.

     Правило: собрать образ из отрефакторенного дерева и сравнить SHA-256 с
     образом, уже проверенным на железе.
     - Совпал — рефакторинг доказанно ничего не изменил, конфигурационный поток
       тот же самый бит в бит. Проверять на железе НЕ нужно: это буквально та
       же прошивка, а её статус (`HWOK`) наследуется. Перепрошивка ничего не
       добавит к доказательству.
     - Не совпал — разница реальная, даже если правка выглядит косметической.
       Нужна проверка на железе; «должно быть эквивалентно» не аргумент.

     Сравнивать **`.bin`, а не `.fs`**. Измерено 12.08.2026 (Gowin V1.9.8.07,
     GW2A-LV18PG256C8/I7, пересборка того же дерева): `.bin` совпал по SHA-256
     полностью, а `.fs` отличался — ровно одной строкой заголовка
     `//Created Time`, при идентичных `//CheckSum` и `UserCode` и одинаковом
     числе строк. То есть несовпадение SHA у `.fs` само по себе НЕ означает
     разницы в дизайне; payload несёт `.bin`.

     Чего это НЕ доказывает: совпадение `UserCode`/`CheckSum` без SHA-256 —
     `CheckSum` 16-битная, коллизия возможна. И одинаковый `.bin` говорит
     только о конфигурации ПЛИС: прошивка МК, содержимое FLASH и рантайм-
     настройки в него не входят.

     **Ловушка сравнения: сверять `.bin` ТОЛЬКО после успешной сборки.** При
     падении сборки на диске остаётся `.bin` от прошлого удачного прогона, и
     сравнение радостно скажет «побитово тот же». Поймано 12.08.2026: сборка
     упала на `ERROR (EX3937) Instantiating unknown module`, а проверка дала
     «совпало». Порядок: удалить артефакт перед пересборкой, проверить код
     возврата и наличие `Bitstream generation completed`, и только потом
     сравнивать.
   - Порядок внесения изменений: **навык первым, код по месту, критерий —
     `.bin`.**
     - Правило или конвенция сначала записывается в навык, и уже из него
       применяется к коду. Навык — источник, состояние кода — следствие; иначе
       договорённость живёт только в переписке и теряется к следующей задаче.
     - Переносить изменение между ветками правкой ПО МЕСТУ, а не слиянием,
       когда слияние тащит лишнее. Ветки проекта несут разное (стенд, продукт,
       варианты платы), и merge ради одной конвенции затягивает в боевую линию
       чужую незрелую работу. Аккуратная точечная правка в целевой ветке
       честнее и проверяется тем же критерием.
     - Критерий валидности переноса — ПОБИТОВОЕ совпадение `.bin` с эталоном
       ТОЙ ЖЕ ветки. Совпал — правка внесена верно. Не совпал — она изменила
       дизайн, и разбираться надо до того, как двигаться дальше.
     - Отсюда порядок действий: снять эталонный `.bin` ДО правки, внести
       правку, удалить артефакт, пересобрать, сверить.
     - **`.bin` покрывает ТОЛЬКО синтез. Путь ModelSim он не проверяет вовсе.**
       У Gowin корень включений объявлен своим `-include_path`, у ModelSim —
       своим `+incdir`; сломанный `+incdir` даёт побитово совпавший `.bin` при
       полностью мёртвой симуляции. Измерено 12.08.2026 на `R120M.BF2_TDC7201`:
       `.bin` совпал с образом `HWOK`, а `vlog` падал на каждом корневом
       include. Поэтому после правок сборочной обвязки прогонять на КАЖДОЙ
       ветке хотя бы один ТБ, а не только сборку.
     - Снимать эталон НЕ только для `.bin`, но и для ТБ. Без базового прогона
       нельзя отличить свою регрессию от дефекта, который на ветке уже был. В
       том же заходе два ТБ упали вместе: базовый прогон на исходном коммите
       показал, что один падал и раньше (дефект ветки), а второй сломал я.
   - Скрипт, отчитавшийся об успехе, — не доказательство. Проверять РЕЗУЛЬТАТ.

     Массовая правка по якорю молча не срабатывает, если якорь не совпал: замена
     с `\n` в файле с CRLF ничего не находит, а скрипт печатает «готово».
     Поймано 12.08.2026 — обёртка `vlog` не встала, при этом соседняя вставка в
     тот же файл прошла, и `grep` по ней подтвердил ложный успех. Проверять
     надо то, что реально нужно (`assert 'rename vlog' in текст`), и сверять
     число заменённых мест с ожидаемым: два одинаковых блока с разным
     окружением дают одно совпадение вместо двух.
   - Падающий ТБ на боевой ветке — сперва проверить, не устарел ли ОН САМ.

     Когда фикс RTL портируется между ветками в одну сторону, ТБ под него может
     остаться старым, и падение выглядит как дефект продукта. Порядок: сравнить
     файл ТБ и файл модуля с соседней веткой (`git show <branch>:<path>`) и
     только потом лезть в RTL. Пример 12.08.2026:
     `msop_tcp_pipeline_echo_count_tb` падал на `R120M.BF2_TDC7201`
     (`distance_byte_count got=2 expected=3`), при этом `msop_tcp_pipeline.sv`
     побитово совпадал с `R120M.BF2`, где тот же ТБ проходил. Причина — ТБ ждал
     строб фиксированные два такта, а рукопожатие занятости сериализатора X17
     сделало строб отложенным; правка ТБ доехала только до `R120M.BF2`.
   - Run synthesis/implementation only when the change can affect hardware build, timing, pinout, or generated firmware.
   - If a GUI/CLI tool gives surprising or inconsistent hardware behavior, inspect the tool and firmware source that builds/parses the packet before changing HDL or firmware. Treat screenshots and GUI labels as symptoms; confirm the actual protocol bytes, offsets, ports, bind addresses, and parser expectations from source or packet capture.
   - For bench-board firmware tasks, do not stop at simulation and `.fs` generation. After a clean build, verify on the actual hardware unless the user explicitly asks for build-only work or the board/tool is unavailable.
   - Step zero of hardware bring-up: do NOT start debugging configuration or RTL for a stuck function until every required signal is confirmed physically present and correct on the wires. Probe/scope each stimulus, clock, trigger, the stimulus SOURCE, and the DUT response along the whole signal path, and confirm the bench top actually drives the pin a bench cable is wired to. An undriven pin, a top-level port the wrapper never declared/drove, an unconstrained pin, or a dead source masquerades as a config/logic bug and can burn an entire debug session. (Concrete: an LTDC-X3 bring-up returned only `no_hit` for a long time while config was repeatedly changed — the real cause was that the bench top never drove `FPGA_HF` (K12/K13), the pin the STOP cable was wired to, so the STOP source had no signal at all.)
   - For hardware verification, program volatile memory when possible, then capture real observable evidence such as UART terminal output, packet capture, LEDs, link state, logic-analyzer/DSView bytes, or user-confirmed physical behavior.
   - When the user confirms that an exact Git state works on hardware, record
     the result in a tracked project reference before committing it: date,
     full tested commit SHA, board/top and image fingerprint when known,
     evidence class, verified scope, and `PASS`. Do not invent missing capture
     or telemetry details; a bare "works" is a user-confirmed functional
     hardware smoke pass. Name the tested parent SHA explicitly because the
     documentation commit that records the result was not itself programmed.
     Follow an existing tag or release convention when one exists; otherwise
     do not invent a tag name or create an empty commit when the tracked
     verification record can make the hardware milestone visible in Git.
   - Treat DSView and other logic-analyzer screenshots or exported captures as hardware evidence. If an image or capture file is available, inspect it directly instead of asking the user to transcribe bytes. Record the probe-to-signal mapping, sample rate, decoder settings, and which lines are expected to be active for the selected protocol mode.
   - Summarize errors by root cause and cite the log/report file paths.

7. Проверить расстановку выводов ДО заливки. ОБЯЗАТЕЛЬНО, каждая сборка.
   - Открыть `impl/pnr/<имя>.pin.html` и сверить с файлом ограничений хотя бы
     цепи, без которых прибор немой: командный канал МК-ПЛИС, проброс к
     конфигурационной флеши, шину потока измерений.
   - Сосчитать в журнале сборки строки `Reading constraint file` и сверить с
     числом добавленных `.cst`. **Файл ограничений у Gowin ОДИН: `gw_sh` читает
     последний добавленный, а прежние отбрасывает МОЛЧА.** Разделение на
     «основной плюс вариантный» не складывается. Склеивать в один файл перед
     добавлением.
   - Зачем это отдельным пунктом: 21.08.2026 такой пропуск стоил ПОЛДНЯ. Вынос
     четырёх выводов SPI2 в отдельный `.cst` отбросил основной файл целиком,
     синтезатор расставил все прочие выводы сам — командный канал вместо
     C10/T10/M8/N9 встал на H5/T11/J6/N10, проброс к флеши вместо
     P10/R10/M9/L10 на K3/H4/R1/K6. Сборка прошла БЕЗ ЕДИНОГО ЗАМЕЧАНИЯ, образ
     залился и сошёлся при обратном чтении, а на приборе выглядел как «ПЛИС не
     поднялась»: обмен по SPI3 давал сплошные единицы, опознание 0x00FFFFFF.
     Разбор ушёл искать негодный битстрим, порчу флеши и цепочку многозагрузки.
   - Сопутствующее правило разбора: **признак «проброс мёртв» НЕ означает «образ
     не загрузился».** Проброс живёт ВНУТРИ образа и молчит в двух разных
     случаях: образа нет, и образ есть, но в нём сломан командный канал.
     Различать их до того, как строить объяснение.
   - Чтение отчёта занимает секунду. Цена пропуска — цикл заливки, отказ и
     разбор по ложному следу.

8. Report hardware outputs clearly.
   - Name generated files such as `.fs`, `.bin`, `.bit`, `.sof`, `.pof`, or reports.
   - Include target device, top module, build command, result path, and whether timing/build passed.
   - State when programming or hardware verification was not performed, and do not present a hardware-targeted task as complete if only simulation/build passed.
   - Create a local git commit after each meaningful intermediate milestone that passed verification. A milestone is commit-worthy when there is feedback from real hardware, a packet/UART/LED/capture observation, or correct simulator/tool output that proves the current stage. Treat the whole task as complete only after hardware observation, terminal/capture evidence, simulator evidence for simulation-only work, or user confirmation proves it worked. Do not push unless explicitly asked.

## Hardware Session Log

Log every hardware session, not only the ones that changed the design. The log
is what later answers an outside proposal ("switch TR_MODE", "run the HighRes
test", "verify the register map") and what a report is assembled from. An
undocumented measurement is a measurement that will be demanded again.

Log a session whenever the board was programmed and something was observed:
bring-up, a measurement sweep, a tuning run, a hardware regression, or a change
that was tried and rolled back.

Record, per session:

- date, the exact commit SHA that was built, the bitstream fingerprint (Gowin
  UserCode), board, and top module;
- the configuration that was actually loaded — device register values, HDL
  parameters, clock/divider settings, IO drive strengths — not only the fields
  that were edited this time;
- stimulus and physical conditions: target distance or cable delay, echo count,
  shot rate, pulse width/amplitude, probe points;
- the measured number with units and sample size (`σ = 83 ps over 20000 shots`),
  never a bare verdict such as "стало лучше";
- evidence class and where the artifact lives: oscilloscope/analyzer capture,
  UART dump, packet capture, `.fs` and report paths;
- **variants tried and rejected, together with the number that rejected them.**
  Rejected settings are the most reusable part of the log: they are what answers
  a later proposal to try exactly that setting again.

Log negative and null results with the same rigor as successes. "No effect" is a
result: proving that UART activity and shot rate do not move σ is what later
removes a whole branch of an outside checklist from consideration.

Keep the running journal in the project's Obsidian notes, and promote only
stable verified facts into the reference files next to this one
(`local-gowin-lidar.md`, `ltdc-x3.md`, and similar). A hardware result must not
exist only in chat history or only in a commit message.

## Commit Handling

At the end of each completed FPGA task, create a local commit with a concise Russian commit message. Use the conventional form when it fits.

Split commits by semantic block when the work contains independent concerns. Avoid vague rollups such as "skill update" or one commit mixing an RTL feature with an unrelated docs move; prefer separate concise commits, each describing one concrete change.

In the final response, also present the commit message as a fenced `text` code block containing only the commit message, with no bullet, prefix, or extra prose inside the block, so the user can copy it with one click.

```text
<тип>: <краткое описание>
```

Examples:

- `test: добавить проверки формата MSOP TCP`
- `fix: исправить ширину поля расстояния в tdc_processing`
- `docs: уточнить порядок сборки LDR_20K`

Create a new commit after a completed task or a verified intermediate milestone. Verification means real hardware feedback, packet/UART/LED/capture evidence, or correct simulator/tool output for software/simulation stages. Do not commit unverified guesses or half-built code. Do not amend commits and do not push unless explicitly requested.

Commit a verified slice immediately after its successful simulation or other acceptance check, before starting the next change or milestone; do not accumulate several already-green slices in one later commit. When several focused testbenches form one acceptance suite for the same edit, finish that suite and create one commit for the slice. Never create an empty commit when no tracked change exists, and never stage unrelated user changes merely to satisfy the checkpoint.

## Local Lidar Gowin Project

When the task mentions this lidar workspace, Gowin, LDR_20K, GW2A-18C, ModelSim, FPGA tables, firmware flash, or paths under `C:\workspace\verilog`, read `local-gowin-lidar.md`.

For Gowin Analyzer Oscilloscope, GAO, `.rao`, `.gao`, or internal hardware signal capture tasks, also read `gowin-analyzer-cli.md`.

For `lconf` tasks involving FPGA table uploads or FLASH blobs, also inspect:

- `C:\workspace\lidar\lconf\COMPENSATION_TABLES.md`
- `C:\workspace\lidar\lconf\FLASH_BIN_BLOB_RULES.md`

## Soft MCU And LwIP

For soft-MCU Ethernet work, treat firmware and HDL as one system.

- Do not commit local filesystem paths such as `C:\workspace\...` or
  `C:/workspace/...` into `.gitmodules`. Submodules must use a portable remote
  URL that another machine can fetch. If a local sibling checkout is useful on
  one workstation, keep it as a personal override in `.git/config` with
  `git submodule set-url` or `git config`, not in tracked project metadata.
- Before working on `dark_risc`, LwIP, soft-MCU firmware, memory maps, or FPGA/MCU Ethernet boundaries, read `soft-mcu-dark-risc-lwip.md`.
- Treat the soft-MCU reference as a self-learning project notebook: when a command, gotcha, register map, build constraint, toolchain quirk, memory-size limit, simulation result, or hardware observation becomes a reusable confirmed fact, update that reference in the same task. Keep transient task checklists in Obsidian and stable procedures in the skill reference.
- Local soft-MCU repo: `C:\workspace\dark_risc`; in the `verilog` repo it should be used as the `soft_mcu/dark_risc` submodule.
- Local STM32 F4 + LwIP reference: `C:\workspace\ToF-LIDAR-MCU-F401`, cloned from the corporate repo `github.com/ak-tech-electronics/ToF-LIDAR-MCU-F401` (bench firmware on branch `gpx`). It uses LwIP with `NO_SYS=1`, IPv4, ARP, UDP, raw API, and no sockets/netconn. The old path `C:\workspace\stm32_f401ccu6_platformio` was removed on 2026-08-10 — do not look for it.
- Repo LwIP source submodule: `C:\workspace\verilog\third_party\lwip`; `contrib\apps\udpecho_raw\udpecho_raw.c` is a minimal raw UDP callback example.
- Prefer moving L3/L4 parsing such as IP/UDP handling into soft-MCU firmware through LwIP. Keep HDL focused on RMII/MAC filtering, frame buffering, CRC/FCS handling, runtime config registers, and the frame transport boundary.
- For the LwIP netif boundary, pass full Ethernet frames without preamble/SFD/FCS into `ethernet_input`; implement TX through `netif->linkoutput` back to the FPGA Ethernet TX path.
- Track the soft-MCU UDP/LwIP integration checklist in `C:\Users\User\Мой диск\Obsidian\Проекты\FPGA soft MCU UDP LwIP.md`.

## 20K Dev Board Ethernet Checks

When testing Ethernet on the 20K dev board:

- Reuse the existing board files first: `src/main/m20k_dev_brd_ifm.sv`, `src/main/m20k_dev_brd.cst`, and `20k/LDR_20K/src/Eth_time_constraints.sdc`. Do not leave task-specific top/constraint/timing files in the repo unless the user explicitly wants a separate firmware target.
- Reuse existing RMII/UDP modules such as `static_udp_rmii` or `staticUDP_pack_former`; fix them in place when they are the intended reusable block instead of creating duplicates.
- For RMII transmit tests, validate packet bytes in wire order. Ethernet bytes are sent in packet order, while each byte's RMII dibits are sent least-significant bits first. A testbench that reconstructs data with the same indexing bug as the DUT is not a valid proof.
- For PHY bring-up, follow the existing board wrapper's reset behavior. On the 20K dev board, `m20k_dev_brd_ifm.sv` keeps `EthRST` deasserted high; if a NIC shows `Disconnected` or captures zero packets, check `EthRST`, link state, pinout, and clock before changing UDP payloads.
- For packet capture on Windows, prefer the adapter name with `tshark -i "Ethernet 5"` instead of a numeric interface id. Npcap interface numbers can change after the link comes up. Confirm with `Get-NetAdapter` and capture fields such as `eth.src`, `eth.dst`, `ip.src`, `ip.dst`, `udp.srcport`, `udp.dstport`, and payload.
- For RX destination-MAC filtering, validate the usual hardware classes explicitly: local unicast, broadcast, multicast, and a rejected unrelated unicast. When Windows cannot add static neighbor entries without elevation, Scapy/Npcap `sendp` to `Ethernet 5` can send raw Ethernet frames; accept/reject is proven by the FPGA UART output, not by local packet capture alone.
- For new Ethernet RX filtering and later protocol fields, prefer runtime configuration over hardcoded constants. MAC addresses, EtherType, IP addresses, UDP ports, multicast enables/groups, and similar fields should be driven by an existing control path or a small reusable register/config block; HDL parameters are acceptable only as reset defaults, testbench defaults, or temporary bring-up fallbacks.
- Кадр длиннее буфера моста молча не проходит. `rmii_tx_w_buf` и `eth_strm_frmr`
  имеют `FIFO_DEPTH = 10`, то есть 2^10 = 1024 байта на кадр, и до 10.08.2026
  глубина не была проброшена наружу из `SPI_RMII_bridge`. Симптом на железе
  крайне обманчив: `tcp_write` проходит, счётчик отправленных кадров растёт,
  ARP и ping работают, а клиент получает ноль байт и буфер TCP не освобождается
  — выглядит как «TCP молчит» или «клиент не читает». Отличать по размеру: 758
  байт шли, 1118 уже нет. Полноразмерный Ethernet-кадр 1518 байт требует
  `TX_FIFO_DEPTH` и `RX_FIFO_DEPTH` не меньше 11. Проверять размером кадра
  прежде, чем искать причину в стеке или в клиенте.
- The user's networks can contain real working lidars in addition to the FPGA dev board. Broadcast discovery is allowed, but treat it as a multi-device operation: prefer an explicit adapter, collect all responses, filter the FPGA board by MAC/model/IP, and never treat the first discovery response as the target. For reproducible bench tests, send `NET_CONFIG`/write commands directly to the intended FPGA board MAC after confirming the current board config.

## Logic Analyzer And DSView

Use DSView screenshots, `.dsl` captures, CSV exports, or decoder tables as first-class hardware evidence.

- Inspect available screenshots or capture files directly before asking the user for manual transcription.
- Local DSView 1.3.2 is primarily a GUI. `DSView.exe --help` shows only file-open plus `--loglevel`, `--version`, `--storelog`, and `--help`; do not assume it can perform headless capture/export. If `sigrok-cli.exe` is not installed separately, use screenshots, saved `.dsl` captures, CSV exports, or controlled GUI inspection.
- For scriptable DSLogic Plus work, check `LISTENAI/dsview-cli` release bundles. Keep the extracted bundle intact; do not copy only the `.exe`. Useful commands include `dsview-cli devices list`, `dsview-cli devices options --handle 1`, `dsview-cli capture --handle 1 --sample-rate-hz <hz> --sample-limit <n> --channels 0,1,2,3,4,5 --output <file.vcd>`, and `dsview-cli decode list/inspect/run`.
- Treat `LIBUSB_ERROR_ACCESS` from DSView/libsigrok as likely exclusive USB ownership by the DSView GUI or another process. Ask the user to close DSView or stop the competing process before CLI capture; do not change HDL because of this error.
- Decoder IDs can be namespaced, such as `0:spi` or `1:spi`; run `decode list` before `decode inspect/run` instead of assuming the ID is plain `spi`.
- Start by reconstructing the channel map from the capture and the HDL/CST pin map. If the decoder works, trust the decoded bytes only after the channel labels match the real pins.
- For SPI RAM/Flash checks, explicitly identify `CS#`, `SCK`, `MOSI`, `MISO`, `IO2`, and `IO3`. In plain SPI mode, only `CS#`, `SCK`, `MOSI`, and `MISO` are expected to toggle; `IO2` and `IO3` can stay idle or pulled high. Six connected probes with four active lines is normal for SPI and is not by itself a fault.
- Configure SPI decoders with active-low chip select, MSB first, and the mode implied by the HDL or datasheet. If the byte stream is shifted or empty, try the adjacent clock phase as a decoder-setting check before changing HDL.
- Separate evidence classes: MOSI command/address bytes prove FPGA-to-device output; MISO bytes that match a prior write prove device response; static or floating MISO with valid `CS#`/`SCK`/`MOSI` points to power, soldering, mode, direction, or pin mapping.
- Record expected protocol bytes from the HDL/testbench, then compare DSView decoded MOSI/MISO against those bytes before declaring the hardware pass/fail.

## Safety

- Do not run `programmer_cli.exe`, erase flash, write SPI flash, or program volatile/nonvolatile FPGA memory unless the user explicitly asks for programming.
- Before hardware programming, restate the selected device, memory target, and firmware file.
- When the active user task targets a connected bench board and asks to verify firmware behavior, treat volatile FPGA programming as part of the requested verification. Still avoid nonvolatile flash unless explicitly requested.
- For local 20K programming, prefer the tracked `C:\workspace\verilog\20k\programming20K.bat` flow and volatile memory (`choice=2`, power-dependent SRAM) for bench tests. Use permanent/nonvolatile/external flash only when the user explicitly asks for persistent programming.
- From Codex, program the 20K board through a versioned project script/batch file rather than a one-off manual programmer command or the programmer GUI. Use the existing tracked volatile wrapper for SRAM tests and a tracked external-FLASH wrapper for persistent writes; if a new programmer flow is needed, add the script under version control before relying on it.
- Prefer read-only inspection for logs, reports, generated netlists, and bitstreams unless a build is requested.

## ПЛИС САМА себе логический анализатор (22.08.2026)

Прежде чем идти за DSLogic, спросить: **а заходит ли этот сигнал в ПЛИС?**
Если да, внешний прибор не нужен вовсе. ПЛИС видит провод своим выводом, а
захват вычитывается по уже существующему командному каналу — без кабеля, без
USB и без человека рядом.

Повод, по которому это выяснилось, стоит помнить: DSLogic ушёл в состояние
занятости, которое снимается только физическим перетыком кабеля, прав на
программный перетык не было, и отладка встала целиком. Наблюдаемые при этом
сигналы всё время заходили в ПЛИС.

**Правило: внешний анализатор — только для того, что до ПЛИС не доходит.**

### Как это устроено (проверенная схема)

Реализация — `src/MCU_FPGA/logic_capture/logic_capture.sv` в дереве лидара,
вычитывание — `Utils/fpga_logic_capture.py` в дереве МК.

| Решение | Почему так, а не иначе |
|---|---|
| запись СЖАТАЯ: смена состояния плюс её длительность | побайтная запись тратит память на паузы; тысяча отсчётов по такту закрывается за 20 мкс — короче одной транзакции |
| запуск по СОБЫТИЮ на шине, а не по команде взвода | взвод приходит по той же шине, за которой следим, и захват по команде съедает его собственная хвостовая часть |
| счётчики фронтов идут ВСЕГДА, независимо от буфера | иначе на вопрос «идёт ли обмен вообще» приходится каждый раз терять буфер |
| выдача окнами по 16 байт через перехват чтения ячейки | ячейка уже есть, второй протокол не нужен |
| адрес выдачи ВНУТРИ массива памяти | образ без анализатора отдаст по нему эхо записанного, а не нули: «анализатора нет» отличится от «анализатор молчит» |
| номер окна ставится явной записью, а не счётчиком внутри | повторённый из-за помехи запрос тогда не сдвинет чтение |

Наблюдать надо **обе стороны** провода сразу: что ведущий выдаёт и что дошло
до ведомого, что ведомый ответил и что вернулось. Только такая пара отвечает
на вопрос «кто замолчал первым»; одна сторона на него не отвечает никогда.

### Чего этот приём НЕ даёт

Разрешение равно такту системы. При 50 МГц это 20 нс, а бит шины на 17,2
Мбит/с длится 58 нс — три отсчёта на бит. Фронты различимы и считаются точно,
но **восстанавливать байты пересчётом отсчётов нельзя**: это счёт фронтов, а
не декодирование. Нужны байты — снимать их отдельным съёмом по фронту такта,
это другая задача и другой модуль.

Второе ограничение: буфер конечен и закрывается на начале события. Чтобы
увидеть КОНЕЦ длинной транзакции (например, где именно замер обмен), нужен
кольцевой буфер с остановкой по событию, а не однократный с запуском по нему.

## Тестбенч обязан тактироваться ТОЙ ЖЕ частотой, что и кристалл (26.08.2026)

Полупериод, записанный в тестбенче числом, — это молчаливое второе объявление
системной частоты. Разъехавшись с первым, оно превращает весь набор тестов в
проверку машины, которой не существует.

Измерено на `R120M.BF2_TDC7201`: `CLK_FREQ_HZ` = 50e6, а **148 тестбенчей из
204** тактировались `always #1 clk` — то есть на 500 МГц. Все временные
константы RTL (`TIME_S_TO_TICK`, сторожевые таймеры, делители UART и SPI,
угловое упреждение) считались от 50 МГц, а такт шёл вдесятеро быстрее. Каждая
величина, выраженная временем, в симуляции означала вдесятеро не то, что в
кристалле.

Такой тест не просто бесполезен — он ЗЕЛЁНЫЙ по неверной причине.
`MSOP_TCP_SPI_sender_tb` проходил окном `run 30 us` при паузе CS между кадрами
`TIME_S_TO_TICK(100e-6)`: на 50 МГц это 5000 тактов, а при такте 2 нс — 10 мкс
вместо задуманных 100. Стоило свести частоты, и окно перестало покрывать паузу.

Правило:
- полупериод берётся из макроса (`CLK_HALF_PERIOD_NS` в `machine_header.sv`), а
  числом пишется ТОЛЬКО там, где такт моделирует ЧУЖУЮ фиксированную частоту:
  опорный клок RMII 50 МГц, входной генератор 10 МГц, второй домен в тесте CDC;
- паузы стимула, зависящие от скорости внешней линии, выражаются в единицах этой
  линии (байтах SPI), а не в тактах: число тактов на байт зависит от делителя, а
  тот — от системной частоты;
- разрешение симулятора обязано ДЕЛИТЬ полупериод. При 500 МГц `-t 1ns` точен;
  при 200 МГц полупериод 2,5 нс и нужен `-t 100ps`. Округление разрешения — это
  тихий сдвиг частоты.

## Тесты одного каталога параллелить НЕЛЬЗЯ (26.08.2026)

`init_tb` создаёт рабочую библиотеку в `_sim` рядом со сценарием и чистит её при
старте. Два прогона из одной папки одновременно затирают библиотеку друг другу, и
это выглядит как дефект теста: `** Error (suppressible): (vsim-19) Failed to
access library 'work'`. Поймано на четырёх ТБ каталога `MSOP_TCP_sender`.

Параллелить можно РАЗНЫЕ каталоги. Готовый прогонщик с такой раскладкой —
`run_tbs.sh` в ветке `feat/clk-500mhz`.

## Базовый прогон набора тестов снимать ДО правок (26.08.2026)

На нетронутой боевой ветке `R120M.BF2_TDC7201` из 89 тестбенчей боевой цепочки
**23 не проходят**, и почти все — не по функции, а по инфраструктуре: ТБ отстал
от модуля (обращается к интерфейсу обёртки, которой в модуле давно нет; ждёт
порт под прежним именем; переопределяет исчезнувший параметр), не включает то,
что сам объявляет, ссылается в `add wave` на удалённую иерархию, тянет исходники
абсолютными путями в `C:\workspaceerilog`. Настоящий отказ по существу один
(`table_index_finder_tb`).

Без базового прогона любая своя правка будет выглядеть причиной этих падений.

## Подбираемое число делай настройкой, а не константой (23.08.2026)

Признак, по которому это распознаётся без раздумий: **в файле лежит столбик
закомментированных вариантов одного и того же присваивания.** Это не мусор, а
след того, как число подбиралось — правкой исходника и пересборкой образа на
каждую пробу. У лидарного дирижёра так подбиралась пауза между выстрелами: в
`lidar_conductor.sv` осталась дюжина строк с разными паузами.

Перевод такого числа в настройку окупается сразу: обмер всего диапазона
занимает секунды вместо часа пересборок, а найденное значение возвращается
одной командой, а не правкой и новой заливкой.

Умолчание при этом обязано СОВПАДАТЬ с прежней константой, и это проверяется
первым же замером: если умолчание дало не ту частоту, что была, — ошибся в
переводе единиц, и лучше узнать это сразу.

Заодно: перед тем как заводить новое поле, поискать существующее. У того же
дирижёра поле под эту паузу — `ticks_for_IDLE_wait`, «для установки частоты
работы алгоритма» — было объявлено с самого начала и ни разу не использовано.

## Осциллограмма и счётчик отвечают на РАЗНЫЕ вопросы (23.08.2026)

Захват в буфер отвечает на «как это выглядело», счётчик фронтов — на «сколько
их всего». Путать их дорого в обе стороны.

Мерить частоту буфером не выходит, когда рядом идёт быстрый сигнал: такт шины
измерителя заполняет тысячу записей за микросекунды, и до интересного события
запись не доживает. Частоту меряет счётчик, который идёт всегда и от буфера не
зависит.

Обратное тоже верно: счётчик не покажет, ЧТО стояло на соседних проводах в миг
события, — для этого нужен буфер.

**Правило: в анализаторе внутри ПЛИС держать оба, и счётчик вести по тому
разряду, частота которого интересна.** У лидара нулевой разряд каждого набора
выбран так, чтобы счётчик сразу считал главное: такт шины у набора флеши,
поджиг у набора выстрелов.

## Предел ищется по РАСХОЖДЕНИЮ пары, а не по одному числу

Дирижёр лидара считает «выстрелов разрешено» и «выстрелов принято». Пока они
сходятся, конвейер успевает; миг, когда принято отстаёт, и есть найденный
предел — видно сразу и без порогов.

Одно число на этот вопрос не отвечает: рост принятых прекращается плавно, и
отличить насыщение от разброса приходится на глаз. Заводя счётчик нагрузки,
заводи и счётчик отказа рядом с ним.

## Условие, вынесенное из ветки, теряет её предусловие (28.08.2026)

Главный приём разгона на этом кристалле — считать условия заранее, в регистрах,
чтобы в такте не стояло двух широких действий подряд. У приёма есть ловушка,
на которой я потерял вечер.

В планировщике выстрелов стояло так:

```systemverilog
else if (in_abs_pos_180 >= phi_raw_target) begin      // угол дошёл до цели
    if (in_abs_pos_180 - phi_raw_target > 4*res) ...  // и обогнал слишком сильно
```

Разность вычислялась ВНУТРИ ветки, где она заведомо неотрицательна. Вынеся оба
условия в отдельные регистры, я стал считать разность всегда — а пока угол не
дошёл, она отрицательна и в беззнаковой записи выглядит как четверть миллиона.
Признак «узел протух» встал намертво, и планировщик пропускал каждый узел без
выстрела: ноль выстрелов вместо девяти на кадр, при том что собиралось всё
чисто и частота выросла со 106 до 260 МГц.

Отсюда два правила.

- **Выносишь условие из ветки — вынеси и её предусловие.** Либо восстанови его
  явно (здесь: обнулять разность, пока угол не дошёл), либо оставь условие на
  месте. Само по себе выражение верно только там, где стояло.
- **Признаки, принимающие одно решение, должны быть с одного среза.** Если один
  готов через три такта, а другой через пять, решение принимается по двум разным
  замерам входа. Выравнивать задержкой, а не надеяться, что «обычно совпадёт».

Ловится это только тестом: синтез, размещение и оба симулятора собирают такой
код молча. Правило отсюда — **после каждой перестройки ради частоты гонять
функциональный тест, а не только замер Fmax**. Замер показывает, что схема
быстрая, и ничего не говорит о том, что она считает.

## Лишние ступени на GW2A-18 делают ХУЖЕ: замер 28.08.2026

Правило «разложи широкое действие по тактам» работает не всегда, и вот граница.

Делитель `div_uint_pipe` держал тракт энкодера на 149.4 МГц: в каждой ступени
вычитание остатка и делителя на 21 разряд, 6.9 нс. Разложил шаг на два такта —
младшие половины с заёмом, затем старшие, — то есть ровно тот приём, который
поднял планировщик выстрелов со 107 до 260 МГц. Получилось **134.4 МГц**,
на пятнадцать хуже исходного.

Почему. Вычитание стало вдвое короче, но регистров вдвое больше, и размещение
разъехалось: путь `mid_shf[14] -> sub_hi -> fits -> rem[15]` занял 7.65 нс при
одиннадцати разрядах арифметики. Считает уже не логика, а трассы между
разбросанными триггерами.

Тот же приём применён к ВТОРОМУ делителю, последовательному — там ступень одна
и используется многократно, то есть случай, который я считал подходящим. Замер
28.08.2026: 200.9 МГц до раскладки, **148.6 после**. Ещё хуже.

Отсюда граница приёма, уточнённая двумя замерами:

- **Помогает** там, где в одном такте стоят РАЗНЫЕ действия подряд — сложение,
  потом сравнение, потом решение автомата. Развести их по тактам — чистый
  выигрыш: так планировщик выстрелов прошёл со 107 до 260 МГц.
- **Помогает** там, где широкое действие идёт «вперёд», из регистра в регистр,
  и его можно разложить половинами конвейером (add_split, cmp_split): новая
  пара операндов принимается каждый такт, ответ выходит через два.
- **Вредит** там, где широкое действие замкнуто в ОБРАТНУЮ СВЯЗЬ: остаток →
  вычитание → остаток. Половина разрядов короче, но в цикле остаётся тот же
  мультиплексор и те же операнды, а регистров прибавляется — и размещение
  разъезжается. Оба делителя, и конвейерный и последовательный, потеряли на
  этом от пятнадцати до пятидесяти мегагерц.

Проверять надо замером, а не рассуждением: я предсказал, что последовательному
делителю раскладка поможет, и ошибся ровно наоборот.

Откат — нормальный исход попытки, и его тоже надо записывать: без записи
следующий подход повторит ту же попытку.

## Разгон упирается в трассы, а не в вентили: где кончается RTL (28.08.2026)

Тракт обработки энкодера прошёл со 129 до 209 МГц при цели 300, и дальше RTL
перестал помогать. Признак, по которому это видно, стоит запомнить.

К концу работы все двадцать пять путей, не помещающихся в 3.33 нс, лежали в
полосе слаков от −1.386 до −1.458 нс — то есть отличались друг от друга на
семьдесят пикосекунд. Разбор одного пути: пять переходов, каждый по 0.5–0.66 нс
при задержке вентиля около 0.35 и соседней трассы около 0.15. То есть считают
средние перегоны между разнесёнными ячейками.

Схема занимает 11% логики кристалла, и размещение свободно расползается по всей
площади. Пока владелец худшего пути менялся по кругу — то фильтр, то делитель,
то пересчёт угла, — сама полоса не двигалась: чинишь один модуль, ровно такой же
путь вылезает в соседнем.

**Fmax от сборки к сборке скачет сильнее, чем стоит любая отдельная правка.**
Один и тот же исходник давал от 192 до 221 МГц — плюс-минус восемь процентов, —
и по одному замеру улучшение в десять мегагерц от разброса размещения не
отличить. Устойчивая величина не Fmax, а РАСКЛАДКА непроходящих путей по
владельцам: она меняется только когда меняется схема. Поэтому мерить надо не
«стало быстрее», а «путей в этом модуле стало меньше», и останавливаться, когда
раскладка выровнялась — ни одного главного владельца больше нет.

**Признак, что RTL исчерпан:**

- слаки непроходящих путей сбились в узкую полосу (единицы процентов друг от
  друга) — значит упор общий, а не в конкретном месте;
- уровней логики на пути мало (четыре-пять), а времени много;
- переход стоит около половины наносекунды вместо полутора десятых.

Пока признаков нет — работает разбор по владельцам путей: посмотреть, какой
модуль держит больше всего непроходящих путей, и чинить его. За вечер так
прошли: делитель угла (25 путей → 0), гейт выстрела, фильтры, сторожевые
таймеры (9 → 1), делитель интерполяции (18 → 1), пересчёт угла (17 → 3).

Дальше нужно размещение, а не RTL — и вот чем это кончилось.

Синтаксис из SUG935 «Gowin Design Physical Constraints», приложение A4:

```
GROUP grp = { "ins_1" "ins_2" };
GRP_LOC grp R[1:3]C[1:4] exclusive;
```

Диапазон пишется `R[a:b]C[c:d]`, а не `R10C10[24][24]` — эту форму парсер
отвергает. Имя иерархии (`obj_encoder_processing`) он не находит: объектом
считается экземпляр ПОСЛЕ синтеза.

**Маски инструмент не понимает, и молчит об этом.** Запись
`GROUP grp = { "obj_encoder_processing/*" }` разбирается без единого замечания,
но не совпадает ни с чем. Проверяется это так: задать заведомо тесную область,
`R[1:4]C[1:4]`, в которую схема физически не влезает. Если размещение проходит —
группа пустая. У меня прошло.

Значит загнать в область можно, только перечислив экземпляры поимённо — а имена
меняются от синтеза к синтезу. Через .cst задача не решается; остаётся Floorplanner
в графической оболочке, то есть ручной и невоспроизводимый путь.

Полтора часа на это ушло. Проверку пустой группы тесной областью делать СРАЗУ,
до всяких замеров.

Заодно исчерпаны и настройки инструмента: `-place_option` принимает только 0, 1
и 2 (на тройку отвечает «unknown place option value»), двойка на этой схеме дала
211 против 201 у единицы, а `-route_option 2` не дал ничего сверх единицы.

## Замеры разгона тракта энкодера, итог 28.08.2026

Ограничение 300 МГц, зонд probe/enc300 (весь тракт), GW2A-18C, усилие
размещения 2, ретайминг включён.

| что сделано | МГц |
| --- | --- |
| исходно | 129.1 |
| гейт выстрела разведён по тактам | 146.7 |
| угол умножением на обратную величину вместо деления каждый такт | 163.8 |
| порог метки одним действием, проверка смены периода защёлкнута | 177.8 |
| фильтр усреднения сохранением переносов, предел разрыва защёлкнут | 200.9 |
| усилие размещения 2 вместо 1 | 211.4 |
| сужение шин по фактическим диапазонам (угол 24→20, делители по ширине делителя) | 221.4 |
| второй делитель убран — он делил на уже обращённое | 211.7 |
| предделитель сторожа со сбросом, мёртвая проверка переполнения убрана | 211.7 |
| выдача на интерфейс защёлкнута, признак насыщения из переноса | 199.9 |
| счётчик мгновенного периода разложен на половины | **222.7** |

Планировщик выстрелов отдельным зондом: 106.8 -> 252.6.

Числа в столбце скачут на восемь процентов от размещения, поэтому смотреть надо
на слаки: за работу полоса непроходящих путей ужалась с −4.4 нс до −0.82…−1.16,
то есть до цели остаётся меньше наносекунды на самом длинном пути.

Функционально всё это время тракт проверялся `encoder_processing_tb` — ALL PASS,
12 373 выстрела против 3 212 у исходной схемы (переделка обменяла такты на
частоту, и на целевой частоте обмен окупился вчетверо).
