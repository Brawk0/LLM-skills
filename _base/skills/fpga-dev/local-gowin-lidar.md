# Local Gowin Lidar FPGA Reference

Use this reference for the local lidar FPGA workspace.

## Main Paths

- FPGA repo: `C:\workspace\verilog`
- Main 20K project: `C:\workspace\verilog\20k\LDR_20K`
- Build wrapper: `C:\workspace\verilog\20k\LDR_20K\build_gowin.cmd`
- Build TCL: `C:\workspace\verilog\20k\LDR_20K\build_gowin.tcl`
- Gowin CLI: `C:\workspace\verilog\bin\IDE\bin\gw_sh.exe`
- Output directory: `C:\workspace\verilog\20k\LDR_20K\impl\pnr`
- Programmer batch: `C:\workspace\verilog\20k\programming20K.bat`
- ModelSim notes: `C:\workspace\verilog\docs\modelsim.md`

## LDR_20K Build

Run from `C:\workspace\verilog\20k\LDR_20K`:

```cmd
build_gowin.cmd
```

Equivalent explicit CLI:

```cmd
C:\workspace\verilog\bin\IDE\bin\gw_sh.exe build_gowin.tcl
```

The TCL flow sets:

- Device: `GW2A-18C` / `GW2A-LV18PG256C8/I7`
- Output base: `LDR_20K`
- Top module: `R120_M_1_1_0_brd_ifm`
- Verilog standard: `sysv2017`
- Synthesis tool: `gowinsynthesis`
- Include path: `C:\workspace\verilog\src`
- Key files:
  - `C:\workspace\verilog\20k\LDR_20K\src\o_pll_10_50\o_pll_10_50.v`
  - `C:\workspace\verilog\src\main\main.sv`
  - `C:\workspace\verilog\src\main\R120_M_1_1_0_brd_ifm.sv`
  - `C:\workspace\verilog\src\main\R120_M_1_1_0.cst`
  - `C:\workspace\verilog\20k\LDR_20K\src\20k_time_constraints.sdc`

Expected generated files include:

- `C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.fs`
- `C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.bin`
- `C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.rpt.txt`
- `C:\workspace\verilog\20k\LDR_20K\impl\gwsynthesis\LDR_20K.log`

Inspect these reports after a build before claiming success.

Test FPGA firmware builds should be copied to the shared server folder:

```text
\\192.168.2.50\e\YandexDisk\#Projects\ToF Lidar\!Firmware\FPGA\Тестовые прошивки
```

By default, copy only the generated `.bin` file to this server folder. Do not copy `.fs`,
`.rpt.txt`, timing HTML, or other build artifacts unless the user explicitly asks for them.

## 20K Soft-MCU LwIP Bench Target

Verified on 2026-06-17 on branch `dev_20k`:

- The active soft-MCU/LwIP bench top in `build_gowin.tcl` is `m20k_dev_uart_rmii_debug`, not the lidar production wrapper.
- `build_gowin.cmd` runs the `lwipdemo` firmware build first:
  `C:\msys64\usr\bin\make.exe -C C:\workspace\verilog\soft_mcu\dark_risc\src clean all APPLICATION=lwipdemo NOBANNER=1 CCPATH=C:/msys64/ucrt64/bin`
- The firmware image embedded by Gowin is `C:\workspace\verilog\soft_mcu\dark_risc\src\darksocv.mem`.
- The current 20K dev-board LwIP build produced `C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.fs` with size `7264087` bytes.
- Full-depth Gowin Analyzer Oscilloscope/RAO instrumentation can overuse BSRAM together with the soft-MCU/LwIP RAM footprint; keep analyzer profiles separate or reduce capture depth before enabling GAO in this target.

Verified on 2026-06-18 for the LwIP lidar simulator milestone:

- The same bench target now carries a soft-MCU lidar simulator in `lwipdemo`: UDP discovery/control plus TCP command/data servers for model `R120_FAKE` and firmware string `pegus_1`.
- Build-and-program still uses `C:\workspace\verilog\20k\build_and_program20K_volatile.bat`, default programmer speed, and volatile SRAM (`-r 2`).
- Successful SRAM programming evidence: `User Code: 0x00005B6C`, `Status Code: 0x00006020`, cost about 15.4 seconds.
- Generated bitstream: `C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.fs`, size `7264087` bytes, report timestamp `Thu Jun 18 11:15:43 2026`.
- PnR resources for this build: logic `3011/20736 14%`, registers `1089/16173 6%`, CLS `1917/10368 18%`, BSRAM `82%` (`SDPB 6`, `DPB 32`), PLL `0/4`.
- DDR3 is not needed for this verified build. If future simulator features outgrow internal BRAM, find and reuse an existing DDR3 example/controller before adding a new memory subsystem.
- Hardware network validation used raw Scapy/Npcap on `Ethernet 5` because adding a secondary Windows IP address to the adapter required administrator rights. UART `COM3` and packet captures confirmed ARP, broadcast discovery, UDP commands, TCP command, and TCP MSOP data.

Verified on 2026-06-18 for the TCP FPGA firmware-loader milestone:

- The same `m20k_dev_uart_rmii_debug` bench target now exposes a soft-MCU TCP firmware-loader server on port `50102` and writes the FPGA section of an lconf firmware package into external SPI FLASH.
- FLASH pins are part of the existing bench top and constraints: `FLASH_SPI_SO=P10`, `FLASH_SPI_SI=R10`, `FLASH_SPI_CS=M9`, `FLASH_SPI_CLK=L10`.
- The bitstream was still loaded to volatile SRAM for the loader itself through `C:\workspace\verilog\20k\build_and_program20K_volatile.bat`; successful evidence: `User Code: 0x00006EAC`, `Status Code: 0x00006020`, cost about `14.51` seconds.
- Gowin outputs for the loader build: `C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.fs` size `7264087`, `C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.bin` size `907418`, report timestamp `Thu Jun 18 12:21:22 2026`.
- PnR resources for the loader build: logic `3176/20736 15%`, registers `1266/16173 7%`, CLS `2094/10368 20%`, BSRAM `82%`, PLL `0/4`.
- Hardware JEDEC check through UART command `flashid` returned `fwloader flash_id=0b4016 ok=1`.
- Verified TCP FLASH upload command:
  `& 'C:\workspace\lidar\lconf\bin\Release\lconf.exe' --cli --file 'C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.bin' --channel tcp --host 192.168.15.20 --port 50102 --erase-timeout 300000 --reply-timeout 30000`
- The upload used the Windows `Ethernet 5` adapter at `192.168.15.13/24`; the board was temporarily set to `192.168.15.20` by UART and restored to `192.168.20.20` afterwards.
- Verified upload evidence: `lconf --cli` reported `FPGA=907520` bytes, erase to `100%`, `Send end`, and `OK: Данные загружена.` UART reported `fwloader end ok bytes=907520 crc=9bbd26fa flash_crc=9bbd26fa`.
- After the FLASH write, `lconf --lidar-smoke` against `192.168.15.20` passed discovery, UDP full-status, UDP/TCP firmware `pegus_1`, and TCP command, proving the SRAM-loaded firmware remained alive after the write.
- Booting from the newly written external FLASH was later power-cycle verified after the live `FLASH_SPI` readback milestone; see below.

Verified on 2026-06-18 for the live FLASH readback milestone:

- The bench firmware now handles lidar command `FLASH_SPI = 0x45` on live command port `50101`, matching the `lconf --flash-dump` path. Firmware upload still uses bootloader TCP port `50102`.
- Current build after adding `FLASH_SPI` readback: `14332 darksocv.mem`, `56816` bytes in `darksocv_uart.bin`; ModelSim 10.5b reported `Errors: 0`, `fwloader sim ok`, and `lidarsim ok`.
- Volatile SRAM programming was rechecked at default programmer speed with `User Code: 0x00006EAC`, `Status Code: 0x00006020`.
- If UART is unavailable after SRAM reload, send exact-MAC UDP `NET_CONFIG` broadcast to discovery port `50103` to move the board to the Windows bench subnet (`02:20:20:20:20:01` -> `192.168.15.20`, host `192.168.15.13`). Wait about one second before smoke tests.
- Full readback command:
  `& 'C:\workspace\lidar\lconf\bin\Release\lconf.exe' --flash-dump --flash-channel tcp --flash-host 192.168.15.20 --flash-port 50101 --flash-local-host 192.168.15.13 --flash-output $env:TEMP\ldr20k_flash_readback_907520.bin --flash-start 0 --flash-length 907520 --flash-chunk 256 --flash-timeout 30000 --flash-retries 5 --flash-connect-timeout 10000 --flash-overwrite`
- Readback evidence: `907520/907520` bytes, `retries=0`, elapsed about `204.4 s`; first `907418` bytes matched `LDR_20K.bin`, and the 102-byte lconf FPGA-only alignment tail was `0x00`.
- The default `lconf --flash-dump` chunk is `512`; with the 320-byte FPGA reply buffer, lconf receives short blocks of `303` bytes and continues correctly. For full-image reads prefer `--flash-chunk 256` to avoid warnings and reduce stress.
- Boot-from-FLASH was power-cycle verified after the user physically replugged board power: the old runtime IP `192.168.15.20` no longer answered, raw Scapy ARP found the board at default `192.168.20.20` with MAC `02:20:20:20:20:01`, then exact-MAC raw Ethernet/IP/UDP `NET_CONFIG` moved it to `192.168.15.20`.
- In that cold-boot check, ordinary Windows socket UDP broadcast `NET_CONFIG` did not move the board, while raw Scapy `sendp()` on `Ethernet 5` did. If the board boots at `192.168.20.20` and the PC adapter is only `192.168.15.13/24`, use a raw broadcast frame for `NET_CONFIG` before normal `lconf` socket tests.
- Post-boot `lconf --lidar-smoke --smoke-host 192.168.15.20 --smoke-local-host 192.168.15.13 --smoke-discovery-target 192.168.15.20 --smoke-skip-data` passed discovery, UDP full-status, UDP firmware `pegus_1`, TCP firmware `pegus_1`, and `PASS lidar-smoke`.
- Post-boot live FLASH readback also passed: `--flash-dump --flash-length 1024 --flash-chunk 256` read `1024/1024` bytes with `retries=0`, and the first 1024 bytes matched `LDR_20K.bin` (`first_mismatch=-1`, dump SHA256 `81775B43521257409089FE5F1E15B8BA92D0C097041092879A804869DAB9E48D`).

Verified on 2026-06-22 for the shared-switch Ethernet FLASH programming milestone:

- Active network: Windows `Ethernet` at `192.168.2.146`, FPGA at `192.168.2.240`, MAC `02:20:20:20:20:01`.
- Current non-DDR `LDR_20K` image built successfully, ModelSim passed, and volatile SRAM programming reported `User Code: 0x00006EAC`, `Status Code: 0x00006020`, cost `14.99` seconds. Timing was still not clean: setup violated endpoints `2`, hold `0`, `EthRefCLK` Fmax `49.735 MHz` against `50 MHz`, worst setup slack `-0.107 ns` in the DarkRISCV register-file path.
- Root `lconf --cli` bootloader upload to TCP port `50102` is not reliable in this image. With `--erase-timeout 900000`, it reached erase progress `35%` and then failed with `Send begin timeout`; the board stayed alive and post-fail smoke passed. Treat this as an open bootloader erase/main-loop starvation issue.
- The recovery and verified Ethernet programming path is the live command-port tool:
  `python C:\workspace\verilog\20k\flash_spi_live_program.py --host 192.168.2.240 --port 50101 --local-host 192.168.2.146 --file C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.bin --timeout 30 --chunk 256 --readback $env:TEMP\ldr20k_flash_live_readback_20260622.bin`
- Live programming evidence: raw `.bin` length `907418`, padded length `907520`, erase length `909312`, `.bin` SHA256 `E51E1F1CCFC114473FF2DCCE99878C0B3A196923051C9B321B7373BED54BFE41`, image CRC32 `EA28785A`, erase/write/verify all reached `100%`, readback matched the `.bin`, and the 102-byte tail was all zero.
- Independent `lconf --flash-dump` full readback from port `50101` also passed: `907520/907520`, `retries=0`, elapsed `41.3 s`, first mismatch `-1`, zero tail `True`.
- After `programmer_cli.exe -d GW2A-18C -r 1` reload from external FLASH, TCP ports `50101` and `50102` reopened and `lidar_switch_check.py --smoke --skip-data --no-net-config` passed, proving the Ethernet-written external FLASH image boots.

## Simulation And Compile Checks

Use `C:\workspace\verilog\docs\modelsim.md` as the source of truth for local ModelSim checks. It specifies ModelSim Intel FPGA Edition 10.5b:

```powershell
$MSIM = 'C:\intelFPGA\18.1\modelsim_ase\win32aloem'
```

Before programming hardware, prefer running the relevant ModelSim 10.5b testbench. If no testbench exists yet, run at least a fresh-library ModelSim compile/elaboration check for the firmware top; for simple bench firmware, add a small testbench rather than programming an un-simulated bitstream.

For a fast top compile check, run from `C:\workspace\verilog\src\main` with a fresh work library name and compile:

- `C:/workspace/verilog/20k/LDR_20K/src/o_pll_10_50/o_pll_10_50.v`
- `main.sv`
- `R120_M_1_1_0_brd_ifm.sv`

Expected syntax result is `Errors: 0`. Existing warnings in shared modules may be tolerated, but new warnings near edited files should be investigated.

For real simulation/elaboration with Gowin primitives, compile:

```powershell
C:/workspace/verilog/bin/IDE/simlib/gw2a/prim_sim.v
```

## Programming

Do not program hardware unless explicitly requested.

For local 20K bench work, use the tracked programmer batch:

```text
C:\workspace\verilog\20k\programming20K.bat
```

For Codex-friendly one-shot bench loading, prefer the tracked build-and-program wrapper when it exists:

```text
C:\workspace\verilog\20k\build_and_program20K_volatile.bat
```

It rebuilds `LDR_20K.fs` and programs it once to volatile memory (`-r 2`) without using Ethernet or entering the interactive programmer loop.

The tracked programmer batch writes the fixed `.fs` file:

```text
C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.fs
```

It then runs:

```cmd
programmer_cli.exe -d GW2A-18C -r %choice% -f "%fs_path%"
```

Memory choices used by the batch:

- `2`: volatile memory, default
- `5`: nonvolatile memory for 9K
- `37`: external flash memory for 20K

For Gowin Programmer CLI, `-r 5` is `embFlash Erase,Program`: erase and program embedded flash. This was the old nonvolatile mode used for 9K-style targets with embedded flash; it is not the same as 20K external SPI FLASH programming. For 20K dev-board persistent programming use the verified external FLASH/GAO-Bridge mode `-r 37` unless a separate diagnostic proves another exFlash mode.

Prefer `2` for ordinary bench tests: it loads the FPGA into temporary power-dependent memory and avoids changing persistent flash. Use `37` for 20K external flash only when the user explicitly asks for persistent/nonvolatile programming.

Before programming, confirm the selected `.fs` file, target `GW2A-18C`, and memory choice.

For the local 20K dev board, keep the programmer at its default speed unless there is fresh evidence pointing to JTAG signal integrity. Slowing the programmer with manual frequency options did not fix the observed `Cable lost!` failure; after replugging the FTDI cable so both `USB Serial Converter A` and `USB Serial Converter B` were `OK`, default-speed volatile programming succeeded with `Status Code: 0x00006020`.

For persistent 20K external-FLASH programming from Codex, do not run a bare long-lived `programmer_cli.exe` command. Use a tracked one-shot wrapper with a timeout/watchdog, and check for stale `programmer_cli` processes before retrying. A 60-second timeout is enough for detecting a stuck programmer attempt; do not wait 120 or 300 seconds. On 2026-06-19 an external-FLASH attempt left `programmer_cli` running at high CPU after the Codex command was interrupted; the process had to be killed before any safe retry.

Do not synchronously redirect `programmer_cli.exe` stdout/stderr unless the wrapper drains the pipes asynchronously. The CLI prints many progress updates; a direct redirected `System.Diagnostics.Process` wait hit the 60-second watchdog and had to be killed even though the board had already reloaded. For Codex wrappers, prefer `Start-Process -NoNewWindow -PassThru` with a watchdog so logs stream to the terminal and cannot fill a pipe.

The local 20K external-FLASH script historically used `programmer_cli.exe -d GW2A-18C -r 37 -f LDR_20K.fs`, and the user confirmed this mode had worked for programming. Although `programmer_cli --help` labels `-r 37` as `exFlash Erase,Program,Verify thru GAO-Bridge`, do not replace it with `-r 8` or `-r 9` without a separate short diagnostic proving the alternate mode works on this bench. If `-r 37` hangs, first check stale programmer processes, USB cable enumeration, `--scan-cables`, and a short read-code/scan command with a watchdog.

The `programmer_cli.exe` binaries under `C:\workspace\verilog\9k\Programmer\bin` and `C:\workspace\verilog\bin\Programmer\bin` were byte-identical on 2026-06-19, but 20K scripts should prefer the neutral `C:\workspace\verilog\bin\Programmer\bin` path. Do not let the legacy `9k` directory name become evidence that the wrong FPGA family is being programmed.

Use the neutral Programmer path in both tracked 20K wrappers:

- Volatile SRAM: `C:\workspace\verilog\20k\build_and_program20K_volatile.bat`, operation `-r 2`, 60-second watchdog.
- Persistent external FLASH: `C:\workspace\verilog\20k\program20K_external_flash.bat`, operation `-r 37`, 60-second watchdog.

Never run multiple `programmer_cli.exe` commands in parallel, even for read-only diagnostics such as `--scan-cables` and `-r 0`. The FTDI/programmer path is single-client; parallel calls can cause `Cable open failed`, stale zero-CPU `programmer_cli` processes, or misleading scan results. Run programmer diagnostics sequentially and clean up any leftover process before the next attempt.

Before retrying 20K programming after a hang, check Windows device state for both FTDI channels. If `USB Serial Converter B` is in `Error` while `USB Serial Converter A` is `OK`, do not retry FLASH/SRAM programming yet; `programmer_cli --scan-cables` can fail with only `Error: Error found!` and programming attempts can hang. Replug or restart the FTDI programmer device, then require both channels to return to `OK` before programming. Windows can keep stale `Unknown` FTDI entries for old USB ports; what matters for this check is an active matching `USB Serial Converter A` and `USB Serial Converter B` pair with status `OK`.

Verified on 2026-06-19 after an SRAM attempt failed with `Cable lost!` at 76%: Windows PnP showed one `USB Serial Converter A` as `OK` while all `USB Serial Converter B` entries were `Unknown`, but sequential programmer diagnostics still succeeded. `programmer_cli.exe --scan-cables` found `USB Debugger A`, and `programmer_cli.exe -d GW2A-18C -r 0` returned ID `0x0000081B`, User Code `0x00006EAC`, Status `0x00006020`; a single follow-up SRAM `-r 2` retry then completed in `15.24` seconds. Do not launch programming based on PnP alone after a failed attempt, but if scan and read-code both pass with a 15-second watchdog and no stale `programmer_cli` process exists, one SRAM retry is reasonable before asking for a physical replug.

Verified on 2026-06-19 after physically replugging the programmer: both `USB Serial Converter A` and `USB Serial Converter B` returned to `OK`, `programmer_cli --scan-cables` found `USB Debugger A`, and read-code `programmer_cli.exe -d GW2A-18C -r 0` returned ID `0x0000081B`, User Code `0x00006EAC`, Status `0x00006020`. The tracked external-FLASH wrapper using neutral path `C:\workspace\verilog\bin\Programmer\bin\programmer_cli.exe -d GW2A-18C -r 37 -f C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.fs` then completed `Program and Verify flash successfully` in `36.06` seconds, confirming that the 60-second watchdog is sufficient when the programmer is healthy.

Verified on 2026-06-19: `programmer_cli.exe -d GW2A-18C -r 1` performs a real FPGA reconfiguration from external FLASH. Before `-r 1`, the board was runtime-configured to `192.168.2.240`; after `-r 1` completed in `1.16` seconds, ARP for `192.168.2.240` stopped answering and the FLASH default `192.168.20.20` answered from MAC `02:20:20:20:20:01`. Use `-r 1` as a controlled soft reboot/reload-from-FLASH check.

Verified on 2026-06-19: the tracked volatile wrapper `C:\workspace\verilog\20k\build_and_program20K_volatile.bat` rebuilds the 20K project, uses the neutral Programmer path, and programs SRAM with `-r 2` under a 60-second watchdog. The SRAM programming phase reported User Code `0x00006EAC`, Status `0x00006020`, and cost `14.13` seconds; after the load, the board answered ARP at default `192.168.20.20`. A direct no-redirect `-r 2` run also completed in `13.31` seconds; before the run the board answered at runtime IP `192.168.15.20`, and after the run `192.168.15.20` stopped answering while default `192.168.20.20` answered. Treat `-r 2` as a real FPGA reload into SRAM that clears volatile runtime network config.

Verified on 2026-06-19: the tracked external-FLASH wrapper `C:\workspace\verilog\20k\program20K_external_flash.bat` completed `-r 37` again in `36.33` seconds and the board reloaded the user design from FLASH. Before `-r 37`, the board had been runtime-configured to `192.168.15.20`; immediately after `Program and Verify flash successfully`, ARP for `192.168.15.20` stopped and default `192.168.20.20` answered. This proves that on the current 20K bench board/image, `-r 37` through GAO-Bridge does not preserve the running runtime config and effectively returns the design to FLASH defaults. Still verify with ARP or `lconf --lidar-smoke` after every persistent write before claiming the device is operational.

Verified on 2026-06-19 for the shared switch network: after moving the board Ethernet cable from direct USB-Ethernet bench to the common switch, the old `Ethernet 5` bench interface stopped seeing the board and the Windows `Ethernet` interface at `192.168.2.146/24` could configure and test it at `192.168.2.240`. Use `C:\workspace\verilog\20k\lidar_switch_check.py --iface Ethernet --host-ip 192.168.2.146 --lidar-ip 192.168.2.240 --smoke` for this scenario. The helper first checks that `.240` is not occupied by a non-target MAC, sends raw exact-MAC `NET_CONFIG` to board MAC `02:20:20:20:20:01`, verifies ARP, then runs `lconf --lidar-smoke`.

Verified on 2026-06-19 for the discovery-compatible persistent lidar simulator image:

- The firmware defaults directly to the shared switch network: MAC `02:20:20:20:20:01`, IP `192.168.2.240`, host/remote IP `192.168.2.146`, ports `50100/50101/50103`, model `R120_FAKE`, firmware `pegus_1`.
- ModelSim 10.5b passed with `Errors: 0`, `lidarsim discovery reply broadcast=0 direct=0`, `fwloader sim ok`, and `lidarsim ok`.
- Volatile SRAM programming through `C:\workspace\verilog\20k\build_and_program20K_volatile.bat` completed with `User Code: 0x00006EAC`, `Status Code: 0x00006020`, cost about `13.1` seconds.
- Normal Windows socket discovery on `192.168.2.146 -> 255.255.255.255:50103` received `LIDAR_RESP` from `192.168.2.240:50103`; `poll_lidar_discovery.py --adapter-ip 192.168.2.146 --broadcast 255.255.255.255 --timeout 1 --json` returned the FPGA device.
- `lconf --lidar-smoke --smoke-host 192.168.2.240 --smoke-local-host 192.168.2.146 --smoke-discovery-target 255.255.255.255 --smoke-timeout 5000` passed discovery, UDP full-status, UDP/TCP firmware `pegus_1`, TCP command, and TCP MSOP data. MSOP frames were `758` bytes with `180` points and `angle_res=2000`.
- Persistent external-FLASH programming through `C:\workspace\verilog\20k\program20K_external_flash.bat` completed `Program and Verify flash successfully` in `36.18` seconds.
- Controlled reload-from-FLASH with `programmer_cli.exe -d GW2A-18C -r 1` completed in `1.04` seconds. Wait about two seconds after this reload before the first socket discovery; after that, `poll_lidar_discovery.py` and full `lconf --lidar-smoke` passed again from the FLASH-loaded image.
- Physical power-cycle was verified after the user replugged board power. After waiting about two seconds, `poll_lidar_discovery.py --adapter-ip 192.168.2.146 --broadcast 255.255.255.255 --timeout 2 --json` found the FPGA at `192.168.2.240`; ARP showed `192.168.2.240 -> 02:20:20:20:20:01`; full `lconf --lidar-smoke --smoke-host 192.168.2.240 --smoke-local-host 192.168.2.146 --smoke-discovery-target 255.255.255.255 --smoke-timeout 5000` passed discovery, UDP full-status, UDP/TCP firmware `pegus_1`, TCP command, and TCP MSOP data from the external-FLASH boot image.

## IS66WVS1M8 SerialRAM Bring-up

Use this section for the old R120_M board with a soldered ISSI
`IS66WVS1M8ALL/BLL` 8 Mbit SPI/QPI SerialRAM.

Local files:

- Before using web search for this board, check the local vault/repo first. The
  user keeps board notes, datasheets, DSView captures, and task checkpoints
  locally, and these should be treated as the primary source for R120_M
  hardware work unless they are missing or internally inconsistent.
- Datasheet: `C:\Users\User\...\Obsidian\...\RAM\IS66WVS1M8ALLBLL.pdf`
- Pin note: `R120_M + IS66WVS1M8BLL-104NLI (connections).md`
- Local repo sandbox: `C:\workspace\verilog\src\RAM\is66wvs1m8`
- Bring-up task note: `C:\workspace\verilog\CODEX\is66wvs1m8_psram_bringup.md`

Board connections recorded from the user's note:

- `CE#` -> `J5`
- `SIO1/SO/MISO` -> `G12`
- `SIO2` -> `H13`
- `SIO0/SI/MOSI` -> `H14`
- `SCLK` -> `J13`
- `SIO3` -> `N10`
- `VDD` -> `+3V3_D`
- `VSS` -> `GND`

Important datasheet facts:

- The chip is byte-addressable, organized as 1M x 8, address bits `A19:0`.
- Power-up default is SPI mode; wait at least `150 us` after VDD is stable.
- Provide at least one clock pulse while `CE#` is high before normal operation.
- Page length is 1024 bytes, and read/write operations wrap within the page.
- Useful bring-up commands:
  - SPI write `02h`
  - SPI read `03h`
  - SPI fast read `0Bh`, 8 wait cycles
  - SPI Quad I/O write `38h`
  - SPI Quad I/O read `EBh`, 6 wait cycles
  - Enter QPI `35h`
  - Exit QPI `F5h`
  - Reset enable/reset `66h` then `99h`

Performance baseline from ModelSim on 2026-07-01:

- The current R120 LwIP/MSOP integration uses `darkpsram_mmio.sv` with
  ordinary SPI `02h` write and `03h` read, 32-bit operations only, and
  firmware polling through MMIO. In the integrated image, `clk_50` drives
  `EF_PSRAM_CTRL`, whose SCK is `clk/2`, so PSRAM SCLK is about `25 MHz`.
- `EF_PSRAM_CTRL_is66wvs1m8_tb.do` now prints raw controller benchmark lines.
  Verified fast regression log:
  `C:\Users\User\AppData\Local\Temp\r120_ext_ram_regression_psram_bench_fast_20260701_130047.log`.
- Raw controller throughput at `clk_50`, before CPU/MMIO/LwIP overhead:
  ordinary SPI `02h+03h` write/read32 pair: `8 bytes / 262 cycles = 1.527 MB/s`;
  QSPI `38h+EBh` pair: `8 bytes / 106 cycles = 3.774 MB/s`;
  QPI `38h+EBh` pair: `8 bytes / 82 cycles = 4.878 MB/s`.
- Treat these as simulator ceilings, not hardware throughput. A real hardware
  benchmark must report effective bytes/s, `op_count`, elapsed cycles/time, and
  readback pass/fail from the actual board. Still, the numbers show that a
  QSPI adapter mode is a better first optimization than only raising SCK in
  the current 1-bit SPI mode.

Open-source controller candidate:

- `https://github.com/efabless/EF_PSRAM_CTRL`
- The controller was designed after the ISSI WVS family, supports SPI, QSPI,
  and QPI modes, and has a small low-level core plus an AHB-Lite wrapper.
- A local sandbox copy of the low-level core is in
  `src/RAM/is66wvs1m8/EF_PSRAM_CTRL.v`; it keeps the Apache-2.0 header and has
  two local bring-up fixes:
  - read sampling uses `counter < final_count` to avoid one extra data sample;
  - QPI short commands use 2 cycles, while SPI short commands use 8 cycles.

Simulation:

```powershell
cd C:\workspace\verilog\src\RAM\is66wvs1m8
& 'C:\intelFPGA\18.1\modelsim_ase\win32aloem\vsim.exe' -c -do EF_PSRAM_CTRL_is66wvs1m8_tb.do
```

Expected final line:

```text
IS66WVS1M8 controller simulation PASS
```

Verified on 2026-06-29 with ModelSim Intel FPGA Edition 10.5b:
compile `Errors: 0, Warnings: 0`; simulation `Errors: 0, Warnings: 0`.

Next hardware tasks:

- Add board-level pin names and `.cst` constraints for `J5/G12/H13/H14/J13/N10`.
- Start with a standalone low-speed SPI RAM self-test before using Quad I/O or QPI.
- Add the 150 us power-up delay and a simple write/read walking-pattern test.
- Program volatile SRAM only for first hardware checks; do not touch persistent
  FPGA flash unless explicitly requested.

## R120_M Ethernet Physical Bring-up

Use this section for the old R120_M/GW2A board Ethernet PHY checks.

Verified on 2026-06-30:

- The working R120 RMII TX clocking mode drives `Ethclkin/R13` from the FPGA
  50 MHz PLL (`H11` 10 MHz -> `o_pll_10_50`), leaves `EthRefCLK/P8` high-Z,
  leaves `EthnlntSel/T6` high-Z, and registers RMII TX outputs on the falling
  edge of `clk_50`.
- Static UDP image
  `C:\workspace\verilog\20k\LDR_20K\impl\pnr\R120_STATIC_UDP_SCOPE_R13CLK.fs`
  was volatile-programmed successfully (`User Code: 0x00005AC1`,
  `Status Code: 0x00006020`) and produced `4873` UDP frames in 5 seconds in
  capture `C:\Users\User\AppData\Local\Temp\r120_static_udp_physics_20260630_1330.pcapng`.
  Source MAC was `02:20:20:20:20:01`, payload was
  `FPGA_STATIC_UDP_R120_20260629!`.
- The same static UDP physical path was rechecked later the same day after
  integration work. Volatile SRAM programming again reported
  `User Code: 0x00005AC1`, `Status Code: 0x00006020`; capture
  `C:\Users\User\AppData\Local\Temp\r120_static_udp_physics_recheck_20260630_141112.pcapng`
  saw `4938` FPGA frames in 5 seconds from `02:20:20:20:20:01`,
  `192.168.2.240 -> 192.168.2.255`, UDP `50100 -> 50100`, payload
  `FPGA_STATIC_UDP_R120_20260629!`. This confirms cable/switch/PHY TX/RMII TX
  and the `Ethclkin/R13` mode are still working; it does not prove PHY RX.
- A third static UDP/R13CLK physical recheck on 2026-06-30 15:48 after the
  user's "check physics first" request used the same volatile SRAM image and
  again reported `User Code: 0x00005AC1`, `Status Code: 0x00006020`. Capture
  `C:\Users\User\AppData\Local\Temp\r120_static_udp_physics_recheck_20260630_154848.pcapng`
  on Windows `Ethernet` saw `5177` total packets and `4957` FPGA UDP frames in
  5 seconds from `02:20:20:20:20:01`, `192.168.2.240 -> 192.168.2.255`, UDP
  `50100 -> 50100`, payload `FPGA_STATIC_UDP_R120_20260629!`. Treat the R120
  cable/switch/PHY TX/RMII TX/R13CLK path as healthy until contradicted by new
  hardware evidence; this still does not prove the PHY-to-FPGA RX path.
- Reproduce the static UDP verdict with:
  `python C:\workspace\verilog\scripts\analyze_r120_static_udp_pcap.py C:\Users\User\AppData\Local\Temp\r120_static_udp_physics_recheck_20260630_154848.pcapng --min-frames 4900 --min-duration 4.9`.
  Verified output: `PASS`, backend `scapy`, matching frames `4957`, total UDP
  frames `4965`, duration `4.989225 s`, first frame `1`, last frame `5177`,
  payload `FPGA_STATIC_UDP_R120_20260629!`.
- The R120 board on this bench has no usable UART path for Codex hardware
  diagnostics. Do not wait for UART evidence; use packet capture, LEDs,
  scope/DSView/GAO, or user-confirmed physical behavior.
- In the LwIP/PSRAM integration image, CPU `netif_up` and FPGA RMII TX were
  proven by diagnostic UDP marker source MAC `02:20:20:20:20:01`, but raw
  `EthCrsDv` marker `02:20:20:20:20:04` stayed at zero during broadcast
  discovery and during 200 raw unicast Ethernet frames sent directly to
  `02:20:20:20:20:01`.
- The RXSCOPE/LwIP diagnostic image
  `C:\workspace\verilog\20k\LDR_20K\impl\pnr\R120_LIDAR_EXT_RAM_RXSCOPE.fs`
  was volatile-programmed on 2026-06-30 15:52 (`User Code: 0x000052FE`,
  `Status Code: 0x00006020`). Passive capture
  `C:\Users\User\AppData\Local\Temp\r120_rxscope_passive_20260630_155322.pcapng`
  saw marker `...:01 = 49`, `...:02..06 = 0`. Active probe capture
  `C:\Users\User\AppData\Local\Temp\r120_rxscope_active_probe_20260630_155418.pcapng`
  confirmed the host put `50` broadcast NET_CONFIG frames and `200` unicast UDP
  frames on `Ethernet`, while FPGA markers were still `...:01 = 79`,
  `...:02..06 = 0`.
- In `R120_lidar_ext_ram_brd_ifm.sv`, marker `02:20:20:20:20:04` is latched
  directly from `if (rmii_rst_n && EthCrsDv) diag_crs_seen <= 1'b1`; it does
  not depend on LwIP, MAC filtering, `eth_rx_check`, or PSRAM.
- A later FPGA-only RX pin monitor clarified the physical picture. Build
  `R120_STATIC_UDP_RXMON.fs` from top `R120_static_udp_rxmon_brd_ifm` with
  `R120_STATIC_UDP_CST=R120_static_udp_rxmon_brd_ifm.cst` and
  `R120_STATIC_UDP_SDC=R120_static_udp_rxmon.sdc`. The top sends UDP reports
  from source MAC `02:20:20:20:20:10` with payload
  `R120_RXMON L=x R=xxxxxxxx H=xxxxxxxx E0=xxxxxxxx E1=xxxxxxxx`, where
  `L={CRS_DV,RXD1,RXD0}`, `R/H` count CRS rises/high cycles, and `E0/E1`
  count any `RXD0/RXD1` transitions. Keep `PSRAM_CE_N=1` on `J5` in this
  profile so Gowin reports bank 4 (`EthRXD0/T4`) as BankVccio `3.3`, matching
  the real R120 integration build.
- RXMON hardware evidence on 2026-06-30 16:13: volatile SRAM programming of
  `R120_STATIC_UDP_RXMON.fs` reported `User Code: 0x0000A9C9`,
  `Status Code: 0x00006020`. Active capture
  `C:\Users\User\AppData\Local\Temp\r120_rxmon_active_probe_vccio33_20260630_161340.pcapng`
  contained all `250` host raw Ethernet probe frames and `390` FPGA RXMON
  reports. First/last payloads were
  `R120_RXMON L=3 R=000005BA H=00094A26 E0=00000001 E1=00000001` and
  `R120_RXMON L=3 R=00000825 H=000E1431 E0=00000001 E1=00000001`, so
  `delta_R=619`, `delta_H=313867`, `delta_E0=0`, `delta_E1=0`.
- Reproduce the RXMON pcap verdict with:
  `python C:\workspace\verilog\scripts\analyze_r120_rxmon_pcap.py C:\Users\User\AppData\Local\Temp\r120_rxmon_active_probe_vccio33_20260630_161340.pcapng --min-reports 300 --expect-crs-activity --expect-rxd-static`.
  Verified output: `PASS`, backend `scapy`, reports `390`, duration
  `7.780852 s`, `delta R=619 H=313867 E0=0 E1=0`, `L distribution {'0x3': 390}`.
  The inverse check with `--expect-rxd-activity` exits `1` and prints
  `expected RXD0/RXD1 activity`, which is the intended fail evidence for the
  current hardware blocker.
- Use the combined physical-evidence gate when both captures are available:
  `powershell -NoProfile -ExecutionPolicy Bypass -File C:\workspace\verilog\scripts\check_r120_physics_evidence.ps1 -StaticUdpPcap C:\Users\User\AppData\Local\Temp\r120_static_udp_physics_recheck_20260630_154848.pcapng -RxmonPcap C:\Users\User\AppData\Local\Temp\r120_rxmon_active_probe_vccio33_20260630_161340.pcapng -Mode current-blocker`.
  `current-blocker` must pass for the present known-bad hardware state: static
  UDP TX works, `CRS_DV` is active, and `RXD0/RXD1` stay static. After hardware
  rework or a strap/reset fix, rerun the same command with `-Mode hardware-pass`;
  that mode currently fails with `expected RXD0/RXD1 activity` and should pass
  only when `RXD0/T4` and `RXD1/R11` transitions are present in RXMON.

Resolved RX blocker:

- Before the hardware rework, the FPGA saw some `EthCrsDv/P11` activity, but
  saw `EthRXD0/T4` and `EthRXD1/R11` as static high during real
  broadcast/unicast probes. This was below LwIP, `darketh_mmio`, and PSRAM:
  static UDP TX success by itself was not proof that PHY-to-FPGA RX worked.
- After the user soldered all RXD0/RXD1 jumpers on 2026-07-01, volatile RXMON
  evidence resolved this blocker. `R120_STATIC_UDP_RXMON.fs` was programmed to
  SRAM with `User Code: 0x0000A9C9`, `Status Code: 0x00006020`; active capture
  `C:\Users\User\AppData\Local\Temp\r120_rxmon_after_jumpers_20260701_114305.pcapng`
  produced `389` RXMON reports in `7.760784 s`, with
  `delta_R=588`, `delta_H=209479`, `delta_E0=62650`, and `delta_E1=66518`.
  The combined gate
  `check_r120_physics_evidence.ps1 -Mode hardware-pass` passed using that pcap
  and the known-good static UDP TX pcap from 2026-06-30.
- The same post-rework bench check then volatile-programmed
  `R120_LIDAR_EXT_RAM.fs` (`User Code: 0x00007563`,
  `Status Code: 0x00006020`). `Test-NetConnection` showed TCP ports `50100`
  and `50101` open at `192.168.2.240`, and `run_r120_lconf_smoke.ps1` passed
  real `lconf --lidar-smoke`: discovery, UDP full-status, UDP/TCP firmware
  `pegus_1`, TCP command, and TCP MSOP data. The MSOP proof included frames
  `758` bytes long, `180` points, `angle_res=2000`, `dist_bytes=2`,
  `echo=3/2`. Smoke log:
  `C:\Users\User\AppData\Local\Temp\r120_lconf_smoke_after_jumpers_20260701_114447.log`.
- Persistent external-FLASH programming of the same
  `R120_LIDAR_EXT_RAM.fs` was later verified at the FPGA configuration level:
  after a user power-cycle, read-code returned `ID 0x0000081B`,
  `User Code: 0x00007563`, and `Status Code: 0x00006020`. Treat this as
  proof that the FPGA loads the expected image from FLASH, not as proof that
  the LwIP application is healthy after cold boot. The post-power-cycle
  application check on 2026-07-01 failed discovery:
  `C:\Users\User\AppData\Local\Temp\r120_lconf_smoke_after_power_replug_20260701_123505.log`.
  A simultaneous active-probe pcap
  `C:\Users\User\AppData\Local\Temp\r120_after_power_replug_probe_20260701_123527.pcapng`
  saw `100` FPGA heartbeat frames from `02:20:20:20:20:01`,
  `192.168.2.240:50100 -> 192.168.2.255:50100`, payload
  `FPGA_STATIC_UDP_R120_20260629!`, but no FPGA discovery response and no
  diagnostic marker sources `02:20:20:20:20:04`/`:05` for raw
  `EthCrsDv`/`eth_rx_byte_valid`. TCP connects to ports `50100`, `50101`, and
  `50102` timed out. Current open blocker: persistent/cold-boot configuration
  and RMII TX are alive, but the integrated image does not show a working
  receive/application path in this pcap; compare `EthRST`, `EthCrsDv/P11`,
  `EthRXD0/T4`, and `EthRXD1/R11` on the `0x7563` image or load RXMON/RXSCOPE
  as a deliberate diagnostic step before changing LwIP logic.
- A repeat cold-boot check on 2026-07-01 after another user power replug
  reproduced the same split. Read-code returned `ID 0x0000081B`,
  `User Code: 0x00007563`, and `Status Code: 0x00006020`. TCP ports
  `50100`/`50101`/`50102` on `192.168.2.240` timed out, and
  `C:\Users\User\AppData\Local\Temp\r120_lconf_smoke_after_power_replug_active_20260701_125153.log`
  failed discovery, seeing only the real `R120_BM1` at `192.168.2.225`.
  Active pcap
  `C:\Users\User\AppData\Local\Temp\r120_after_power_replug_active_20260701_125153.pcapng`
  contained `90` FPGA heartbeat UDP frames from `02:20:20:20:20:01`,
  `192.168.2.240:50100 -> 192.168.2.255:50100`, payload
  `FPGA_STATIC_UDP_R120_20260629!`, but no FPGA `R120_FAKE` discovery/TCP
  response and no diagnostic marker sources `...:04`/`:05`.
- Immediately volatile-programming the identical
  `C:\workspace\verilog\20k\LDR_20K\impl\pnr\R120_LIDAR_EXT_RAM.fs`
  (`SHA256 F246456614737DBCA7E7996B8D2730CFC259B26AD07145547AB59FD39717A2C9`)
  with `program20K_volatile_fs.bat` returned `User Code: 0x00007563`,
  `Status Code: 0x00006020`, and the same bench passed full
  `lconf --lidar-smoke` in
  `C:\Users\User\AppData\Local\Temp\r120_lconf_smoke_after_volatile_reload_20260701_125333.log`
  including discovery, UDP status/firmware, TCP command, and TCP MSOP frames
  `758 bytes`, `180 points`, `angle_res=2000`, `dist_bytes=2`, `echo=3/2`.
  Treat the present blocker as a cold power-up/reset/init sequencing issue
  around soft-MCU, PHY RX, or PSRAM startup, not as a bad persistent image,
  cable/link failure, or missing RXD jumper.
- The post-rework acceptance audit passed with `-AllowLocalBundleOnly`. For a
  remote-clean handoff, `soft_mcu/dark_risc` commit
  `e02e5511e0cc786ab8d83d965379e76c522dad92` still must be published to the
  configured remote or the superproject gitlink must be moved to an equivalent
  reachable commit.
- `rdch.asc` shows the relevant R120 routing as jumpers/series links, not
  direct pin names: `LAN8742A D9 pin 8 RXD0/MODE0 -> R83 51R -> EthRXD0 ->
  J12 -> FPGA T4`; `D9 pin 7 RXD1/MODE1 -> R85 51R -> EthRXD1 -> J14 ->
  FPGA R11`; `D9 pin 11 CRS_DV/MODE2 -> R81 51R -> EthCrsDv -> J18 -> FPGA
  P11`. `EthRXD0/EthRXD1/EthCrsDv` can also be strapped toward the STM32 via
  `R159/R160/R158 0R`. Hardware rework/population of `J12/J14/J18` and these
  resistors matters.
- First scope checks during raw unicast/broadcast traffic: probe `D9 pin 11`,
  both sides of `R81`, both sides of `J18`, and FPGA `P11` as the known CRS
  control path. Then probe `D9 pin 8`, both sides of `R83`, both sides of
  `J12`, and FPGA `T4`; repeat for `D9 pin 7`, `R85`, `J14`, and FPGA `R11`.
  If the PHY/R83/R85 sides toggle but FPGA `T4/R11` do not, inspect
  `J12/J14` solder and board rework. If PHY `RXD0/RXD1` pins themselves do not
  toggle while `CRS_DV` does, inspect PHY reset/strap/RMII mode or receive
  state.
- Also verify `EthRST/T8` goes low for about 10 ms after programming and then
  high, and that `EthnlntSel/T6` is held high by the board strap while the FPGA
  leaves it high-Z.
- Keep `EthRXD0/T4`, `EthRXD1/R11`, and `EthCrsDv/P11` with `PULL_MODE=NONE`:
  these LAN8742A pins are strap pins `MODE0/1/2`, so FPGA pull-ups can perturb
  PHY mode during reset.
- The standalone RX logic is not the current suspect by itself. ModelSim 10.5b
  command
  `vsim.exe -c -do "do C:/workspace/verilog/src/Ethernet/RMII/eth_rx_check/eth_rx_check_tb.do; quit -f"`
  passed on 2026-06-30 with compile `Errors: 0`, simulation `Errors: 0`, and
  final `ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО`. It covers valid RMII frames, bad CRC
  reject, consecutive frames, non-4-byte-aligned frames, loopback through
  `rmii_tx_w_buf`, and destination-MAC filter classes. If scope proves activity
  at FPGA pins `P11/T4/R11` but the R120 diagnostic marker for raw `EthCrsDv`
  still stays absent, inspect the R120 board wrapper/constraints/diagnostic
  latch wiring before rewriting `eth_rx_check`.
- The R120 board-interface RX path itself was strengthened on 2026-06-30 16:29.
  `R120_lidar_ext_ram_diag_tb` now injects a valid 60-byte Ethernet frame into
  physical wrapper inputs `EthCrsDv/EthRXD0/EthRXD1` through
  `rmii_tx_w_buf #(.WITH_PR_AND_CRC32(1))`, checks that all 60 bytes reach
  `eth_rx_check`, and waits for diagnostic UDP source MACs `...:02`
  (`eth_rx_frame_valid`), `...:04` (raw `EthCrsDv`), and `...:05`
  (`eth_rx_byte_valid`). Verified command:
  `cd C:\workspace\verilog\src\main; vsim.exe -c -do "do R120_lidar_ext_ram_diag_tb.do; quit -f"`.
  Result: compile/runtime `Errors: 0`; proof lines included
  `R120 eth_rx_frame_valid seen at FPGA wrapper`,
  `R120 valid RMII frame reached eth_rx_check: 60 bytes match`,
  `R120 diag marker source MAC 02:20:20:20:20:02 seen`, and
  `R120_lidar_ext_ram_diag_tb PASS`. This means that if scope proves real
  RMII transitions at FPGA `P11/T4/R11`, the current HDL wrapper can accept
  them; this was the active blocker until the 2026-07-01 RXD0/RXD1 jumper
  rework and RXMON hardware-pass evidence above.

## Lconf Integration Notes

The `lconf` Qt app is not the FPGA build project, but it contains FPGA-facing docs and tools:

- `COMPENSATION_TABLES.md` documents runtime FPGA compensation table selectors and source HDL paths.
- `FLASH_BIN_BLOB_RULES.md` documents protected FPGA firmware area handling and BIN blob writes.
- `third_party\comp_export` converts compensation CSV files into `.hex` and `.bin` payloads.

When working on compensation tables, connect changes across:

- HDL defaults in `C:\workspace\verilog\src`
- generated `.hex` or `.bin` files
- lconf upload/flash behavior

## Пресеты «Режим Эхо» из ПО

Выпадающий список в lconf задаёт `msop_tcp_echo_mode` (регистр 1240, байт 2).
Контракт со стороны ПЛИС:

| Значение | Пресет | Что уходит в кадр | `echo_count` |
|---|---|---|---|
| `1` | `first` | первое эхо | 1 |
| `2` | `last` | второе эхо; **если его нет — первое**, вместе со своей интенсивностью | 1 |
| `3` | `first+last` | оба как есть, подстановки НЕТ | 2 |

Выбор делает `msop_tcp_pack_filler`; `echo_count` выводится из режима, а не
задаётся отдельно (легаси-байт 1240[0] на кадр не влияет). Смена режима
применяется только на границе пакета — это проверяет
`msop_tcp_pipeline_echo_count_tb`.

**Ловушка, стоившая молчаливого дефекта:** признак «второе эхо ЕСТЬ» нельзя
брать из `in_dst_cmp_valid_stb`. Этот строб означает «значение доехало» и в
режимах `last` и `first+last` приходит на КАЖДУЮ точку, потому что конвейер
требует cmp-дистанцию и ждёт её (`lcl_cmp_distance_required`). Подстановка в
`last`, написанная на этом стробе, не срабатывала никогда: при отсутствии
второго эха в кадр уходил НОЛЬ вместо первого эха. Наличие эха определяется
ЗНАЧЕНИЕМ: `distance2 != 0`. Ноль — это общее для обоих трактов «эха нет»
(`ltdc_point_builder` при `no_hit`, `tdc_processing` при интенсивности вне
окна), а настоящего эха на нулевой дистанции не бывает: `TOF = 0` и означает
«измерения не было».

В режиме `first` второе эхо до сборщика тела вообще не доезжает: при
`echo_count = 1` конвейер его не требует и не защёлкивает, поэтому в поле
`distance2` остаётся `INVALID_DISTANCE`, а не значение со входа. Это не дефект,
но при написании проверок легко ожидать обратного.

Дефект прожил долго потому, что ТБ проверял только ФОРМАТ кадра — счётчик эх,
число байт дистанции, границу применения — и ни разу не смотрел, какие
ДИСТАНЦИИ попадают в тело. Проверка тела добавлена на все три пресета, включая
`last` без второго эха; на неисправленной логике она падает именно на нём
(`body.distance1 got=000000 expected=007000`).

## MSOP TCP Stream Debugging

Use these checks before changing HDL when the GUI point cloud looks wrong.

Quick port probe from the shared switch bench:

```powershell
Test-NetConnection -ComputerName 192.168.2.220 -Port 50100
Test-NetConnection -ComputerName 192.168.2.220 -Port 50101
Test-NetConnection -ComputerName 192.168.2.220 -Port 50102
```

`lconf --lidar-stream` is useful for GUI-equivalent parsed batches and telemetry,
but its `batch` JSON lines are emitted from `DataReaderTcp` storage flushes. One
line can contain points from one or more MSOP frames. Use it for a quick
application-level view, not for proving frame boundaries:

```powershell
& 'C:\workspace\lidar\lconf\bin\Release\lconf.exe' --lidar-stream `
  --smoke-host 192.168.2.220 `
  --smoke-local-host 192.168.2.146 `
  --smoke-discovery-target 192.168.2.220 `
  --smoke-skip-discovery `
  --smoke-timeout 5000
```

For protocol-level MSOP TCP frame debugging, use the skill script. It parses
`TcpHeaderV1` directly from the TCP stream, cuts packets by `FF FE ... FF 9B`,
prints header angle range, point count, echo format, and first/last body points,
and can save raw frame packets:

```powershell
python C:\workspace\verilog\.agents\skills\fpga-dev\scripts\msop_tcp_sniff.py `
  --host 192.168.2.220 `
  --local-host 192.168.2.146 `
  --frames 20 `
  --timeout 5 `
  --jsonl $env:TEMP\msop_192_168_2_220.jsonl `
  --raw-dir $env:TEMP\msop_192_168_2_220_frames
```

Interpretation notes:

- `first_point_angle_mdeg` and `angle_res_mdeg` are in millidegrees.
- `last_point_angle_mdeg = first_point_angle + (point_count - 1) * angle_res`.
- For `echo_num=2`, the script reports primary distance and second echo/width
  fields separately. The second field meaning depends on `echo_mode`.
- A mismatch between body point order and `first_point_angle/angle_res` can make
  the GUI cloud look mirrored, bent, or split even when packet markers and point
  counts are valid.
- If the direct MSOP stream shows a physical reference in the expected low-angle
  sector but the GUI shows it on the opposite side, inspect `lconf` rendering
  before changing FPGA. In `C:\workspace\lidar\lconf`, the parser assigns
  `angle_deg = first_point_angle + index * angle_res`; Cartesian side placement
  is controlled later by `MainWindow::newData` in `mainwindow_data_flow.cpp`.
  Check saved `HKCU:\Software\R-Lidar\lconf` values such as `MirrorX`,
  `MirrorY`, `StartAngle`, `GraphType`, and `MirrorsMode`. The default
  non-mirrored Cartesian convention should match session playback:
  `sfx = mirror_x ? -1.0 : 1.0`.

To reproduce the GUI-side left/right check from raw frames saved by
`msop_tcp_sniff.py`, render the captured packets through the old and fixed
`lconf` Cartesian sign conventions:

```powershell
python C:\workspace\verilog\.agents\skills\fpga-dev\scripts\msop_lconf_xy_check.py `
  --raw-dir $env:TEMP\msop_192_168_15_15_direct_frames `
  --frames 4 `
  --png $env:TEMP\lconf_msop_xy_old_vs_fixed.png
```

With `MirrorX=false`, the low-angle reference centroid should move from
negative X under the old formula to positive X under the fixed formula.

## Live FPGA FLASH Checks

Before any live FLASH write on a production lidar, do read-only checks first.
For the local `0x45` fixed FLASH command, `MemoryPresense::OK` is decimal `103`
and `MemoryPresense::ERROR` is decimal `105`. Do not treat `status=103` as a
failed erase/write response; it means the MCU-side operation reported OK.

Read-only memory presence check:

```powershell
python C:\workspace\verilog\20k\flash_spi_live_program.py `
  --host 192.168.2.220 `
  --port 50101 `
  --local-host 192.168.2.146 `
  --timeout 30 `
  --check-memory
```

Read-only full-image verify against the current local Gowin `.bin`, without
erase or write:

```powershell
python C:\workspace\verilog\20k\flash_spi_live_program.py `
  --host 192.168.2.220 `
  --port 50101 `
  --local-host 192.168.2.146 `
  --file C:\workspace\verilog\20k\LDR_20K\impl\pnr\LDR_20K.bin `
  --timeout 30 `
  --chunk 256 `
  --skip-erase `
  --skip-write `
  --readback $env:TEMP\ldr20k_flash_verify_readback.bin
```

If an earlier live write stopped after an erase, verify the affected sector
before doing anything else. For sector 0, a dump whose first `4096` bytes are all
`0xFF` means the sector is erased. If the rest of the dump matches the intended
image from offset `0x001000`, recover narrowly by writing only the first sector
from the matching `.bin` with `--skip-erase`, then run the full read-only verify.

## R120 UART Debug Channel (verified 2026-07-02)

- The R120 debug connector pads route to FPGA balls `D3` and `C1` (confirmed
  electrically with a fabric UART banner generator streamed on both pads and a
  USB-TTL FT232R at the user side, plus a sticky low-detector probe).
- Working pinout in `src/main/R120_lidar_ext_ram.cst`: `UART_TX -> D3`,
  `UART_RX -> C1`, LVCMOS33; USB-TTL: adapter RX -> D3 contact, adapter TX ->
  C1 contact, common GND required.
- The USB-TTL adapter on this bench is FT232R serial `A5069RR4` = `COM4`
  (115200 8N1). `COM3` is channel B of the Gowin FT2CH programmer cable and is
  NOT wired to the board.
- darkuart at `BOARD_CK=50 MHz` gives a clean 115200 stream; the boot banner
  is `lidarsim start`.
- CAUTION: with a live UART every `printf` busy-waits ~87 us/char. Unthrottled
  prints on per-frame events (e.g. RX overflow flags on a busy LAN) form a
  print storm that slows the main loop enough to distort behaviour -
  rate-limit such prints (see `lidarsim rx flags` 5 s limiter in lwipdemo).
- Fabric probes that proved the path (reusable patterns): UART banner
  generator (~30 lines SV, clk/434 divider) and sticky low-seen detectors
  reported via IPORT/beacon.

## R120 wedge investigation status (2026-07-02)

- Original wedge root causes found and fixed: (1) lwIP MEM heap too small
  (1024) for 758-byte tcp_write(COPY) MSOP frames - raised to 2560; (2) a heap
  pbuf double-free caught by MEM_OVERFLOW_CHECK at mem.c "double free" during
  real lconf exchanges (etharp PENDING hand-off vicinity, `ARP_QUEUEING=0`).
- Mitigations in lwipdemo: periodic `etharp_request` host refresh (first after
  2 s of uptime - earlier requests desync the scripted ModelSim TB);
  `net_self_heal()` full lwIP re-init when `pbuf_alloc(PBUF_POOL)` fails 32x
  in a row (proven on hardware: recovers a wedge within one soak cycle).
- Fabric watchdog in the R120 wrapper: firmware toggles `OPORT[0]` each main
  loop; the wrapper pulses darksocv `XRES` after 5 s of no toggling. MUST be
  arm-on-first-toggle: a watchdog армed from reset caused a permanent
  reset-loop (fabric alive, CPU never served).
- Best verified run: 12/12 soak cycles STABLE (lconf smoke + 200-frame MSOP
  through PSRAM), self-heal observed recovering mid-soak. A rare residual
  freeze under combined load (MSOP client + ambient large frames) remains
  under investigation; isolated large-frame no-pbuf drains are exonerated
  (bracket prints prove drain completes).

## R120 PSRAM CDC bridge / psram100 profile (verified 2026-07-03)

- `darkpsram_ctrl_cdc.sv` (dark_risc rtl) moves `EF_PSRAM_CTRL` into its own
  clock domain: toggle req/rsp handshake, quasi-static latched command fields
  (darkddr3_ui_cdc pattern). `done` must be masked with the incoming start
  (`assign done = done_r & ~start`) or the darkpsram_mmio FSM samples the
  stale done level on the same edge it issues a new start.
- `darkpsram_mmio` has `USE_CDC` parameter (generate cdc/direct; direct path
  is verbatim the original controller instance). `darksocv` forwards
  `PSRAM_USE_CDC` + `PSRAM_CLK`/`PSRAM_RST_N` ports (under DARKPSRAM_MMIO).
- Gowin profile: `R120_LIDAR_EXT_RAM_PROFILE=psram100` builds thin top
  `R120_lidar_ext_ram_psram100_brd_ifm` (CDC=1, PLL `o_pll_10_100`, 10->100
  MHz: FBDIV_SEL=9, ODIV_SEL=8, VCO 800 MHz). PnR verified: Setup/Hold
  violated = 0, clk_psram actual Fmax 271 MHz (headroom up to 160 MHz domain).
- SDC gotcha: nets inside the thin-top hierarchy need the instance prefix -
  `get_nets {core/clk_psram}`; bare `clk_psram` fails with TA2003/TA2004
  (while bare `clk_50` happens to resolve at top level). Separate
  `R120_lidar_ext_ram_psram100.sdc` adds the 100 MHz clock and
  `set_clock_groups -asynchronous` for clk_50/clk_psram.
- SoC-level sim of the full lidar exchange incl. MSOP through PSRAM:
  firmware must be built with `LIDARSIM_PSRAM_MMIO=1
  LIDARSIM_PSRAM_TCP_SIM_SELFTEST=1` (else main() exits after the UDP flags
  and the TB TCP phase never runs); TB defines
  `+define+DARKETH_LWIP_FRAME +define+DARKETH_LWIP_TCP_DATA_FRAME
  +define+DARKPSRAM_MMIO [+define+DARKPSRAM_CDC]`. Pass criterion:
  `darketh sim tcp data msop payload ok` + `lidarsim ok`.
- Stack budget recurrence: selftest firmware with MEM_SIZE 2560 leaves <300 B
  of stack (false-failure zone, need >=600 B) - lwipopts.h trims MEM_SIZE to
  2048 for the sim selftest builds only. Always re-check COMMON/bss end vs
  0x10000 in `src/darksocv.map` after changing build flags.
- Restore `src/darksocv.mem` after sim experiments:
  `git -C soft_mcu/dark_risc restore -- src/darksocv.mem`.

## R120M.BM2BF1X1 Board Layer (verified 2026-07-03)

New board revision R120M.BM2BF1X1; board layer files (branch
`codex/r120m-bm2bf1x1-brd-ifm`):

- `src/main/R120M_BM2BF1X1_brd_ifm.sv` + `src/main/R120M_BM2BF1X1.cst`.
- Pin map source: DipTrace ASCII export
  `\192.168.2.50\e\YandexDisk\#Projects\ToF Lidar\Схемы\РЖД\R120\R120_M\R120M.BM2BF1X1\Schematic.asc`
  (FPGA refdes `D7`). Extract pin->net tables with
  `python docs/skills/fpga-dev/scripts/parse_diptrace_asc.py <asc> D7,D8,...`
  (file is cp1251; each `(Pin ...)` carries `StringNumber` = ball and
  `NetNumber`; net names come from `(Net "...") (Number N)` blocks).
- Key board facts vs R120_M-1.1.0:
  - FPGA clock: 10 MHz on `H11` from a TLV3502-based oscillator shared with
    the STM32H723 HSE, through solder jumper `J4`; `o_pll_10_50` still applies.
  - Ethernet is a W5500 (SPI), no RMII PHY. W5500 SPI routes to FPGA via
    J10..J15 or to MCU SPI1 via J22..J27. `~RST` is pulled to GND by R58 —
    the FPGA must drive `WIZNET_RST_N` high to enable the chip.
  - PSRAM IS66WVS1M8 is now factory-routed: SCLK=C1, CE_N=D3, SIO0..3 =
    C2/D1/D2/E3.
  - LTDC-X3 (ScioSense lidar TDC, D19) on QSPI: SCK=E14, SS_N=F14,
    D0..D3=E16/E15/D16/D15, INTERRUPT=F15, REINIT=D14, STOPMASK=C16,
    FIRE (STARTP) from G14. Registers, opcodes, startup sequence, and the
    eval-proven register config are in `ltdc-x3.md` next to this file.
  - Two TDC7201 (D23/D24, channel groups 12/34); FPGA `TDC7201_FIRE`/L14
    drives START1/2 of both chips through R140 (net `7201_FIRE_AR`).
  - MCU command SPI: STM32 SPI2 is Full_Duplex_Master (per `.ioc`), FPGA is
    slave: SCK=P13, MOSI=T14, MISO=T15, HSS_N=N14 — mapped to `if_SPI3`
    (CMD slot) of `interface_MCU_FPGA`.
  - External FLASH pins unchanged: P10/R10/M9/L10 (MSPI dual-purpose).
  - Debug UART header X1: FPGA_TX=M11, FPGA_RX=T13.
  - All IO banks are +3V3_F -> LVCMOS33 everywhere.
- Fast ModelSim compile check needs the src include root and separate
  compilation units, otherwise `Eth_common.svh` fails to open
  `machines/machine_header.sv` and `$unit` types collide:
  `vlog -sv +incdir+.. <o_pll_10_50.v>; vlog -sv +incdir+.. main.sv;`
  `vlog -sv +incdir+.. R120M_BM2BF1X1_brd_ifm.sv` (run from `src/main`,
  fresh work lib). Verified: Errors: 0.
- Gowin PnR check (throwaway tcl, device GW2A-LV18PG256C8/I7, options
  `use_mspi/ready/done/reconfign_as_gpio`): bitstream generated,
  Setup/Hold violated endpoints = 0, PLL clk Fmax 73.6 MHz @ 50 MHz,
  all 101 ports Constraint=Y.

## R120M.BF2: LTDC-only branch boundary (verified 2026-07-28)

- The active `R120M.BF2` branch uses LTDC-X3 only. The preserved 2x TDC7201
  implementation belongs to the separate `R120M.BF2_TDC7201` branch.
- Do not carry `interface_TDC7201`, `USE_LTDC`, `tdc_processing`, or the
  TDC7201 fallback through `lidar_measurement_pipeline` and `main` in `R120M.BF2`.
- Keep the physical TDC7201 pins in `R120M_BM2BF1X1_brd_ifm`/CST while the
  board pinout still exposes them, but drive them to a tested safe state:
  `EN=0`, `MOSI=0`, `SCLK=0`, `CS_N=1`, `TDC7201_FIRE=0`.
- Verify this boundary with
  `src/main/R120M_BM2BF1X1_cmd_spi_tb.do`; the TB must assert the safe pin
  levels in addition to compiling the full active hierarchy.
- Keep `lidar_measurement_pipeline` as the coordination layer for `ltdc_processing`,
  `encoder_processing`, and `msop_tcp_pipeline`. Point correlation, MSOP
  frame-boundary selection, stuffing, packet filling, and SPI transmission
  belong to `src/TDC/msop_tcp_pipeline/msop_tcp_pipeline.sv`, not back in
  `lidar_measurement_pipeline`.
- The former large tail of `lidar_measurement_pipeline` was not an unused TDC-driver fallback:
  it is the active MSOP path that drives `if_mcu_fpga.if_SPI2` to the MCU.
  Commit `8d9ecebe` records why its point/angle association and short-gap
  stuffing are required at 80 mdeg resolution and includes hardware evidence.
  Do not delete that behavior while MSOP-over-SPI2 is part of the product.
  The synthesis-dead `shot_pending` state from the old block was removed when
  the path moved into `msop_tcp_pipeline`.
- Focused MSOP regressions live next to that functional node:
  `msop_tcp_pipeline_mirror_packet_tb.do` checks that a ready point keeps its
  mirror through the packet boundary, and `msop_tcp_pipeline_echo_count_tb.do`
  checks that the requested point format changes only at a packet boundary.
  Both passed with ModelSim Errors=0 on 2026-07-28; the full active hierarchy
  also passed `R120M_BM2BF1X1_cmd_spi_tb.do`, including the safe TDC7201 pin
  assertions.
- Verified post-refactor Gowin build:
  `20k/LDR_20K/build_r120m_bm2bf1x1.tcl`, top
  `R120M_BM2BF1X1_brd_ifm`, device `GW2A-LV18PG256C8/I7`. Result:
  bitstream generated, 0 setup/hold violated endpoints, Fmax 63.656 MHz at
  50 MHz, logic 11434/20736 (55%), registers 10375/16173 (64%). The
  pre-refactor baseline was Fmax 66.220 MHz with the same rounded logic and
  register utilization; the refactor still meets the 50 MHz constraint, but
  report this timing delta rather than presenting it as a timing improvement.
- Production debug cleanup is recorded by commit `14d1fe81`. The active
  hierarchy no longer exports `virtual_enc_ch`, Z-rejection, stale-drop, or
  behind-drop debug strobes and no longer instantiates the board UART reporter,
  event counters, encoder-rate meter, or MSOP SPI sniffer. The functional
  encoder PLL event path, Z rejection, stale/behind scheduling guards, and
  multi/last-echo packet behavior remain. Physical X1/X14 service outputs stay
  in the board/CST contract but are driven to defined static idle levels.
  Dedicated bring-up tops still own their isolated UART diagnostics.
- Behavioral acceptance after that cleanup:
  `R120M_BM2BF1X1_cmd_spi_tb.do` passed the full active hierarchy and safe
  TDC7201-pin assertions; both focused `msop_tcp_pipeline_*_tb.do` tests passed;
  `encoder_processing_guard_tb` reproduced the baseline false-pair bug and
  proved zero guarded false pairs with recovery (all ModelSim Errors=0).
  `shot_scheduler_tb.do` is not a release gate in its current form: its
  endpoint-count expectations are stale (expects 8/9 fires while the unchanged
  scheduler produces 9/10) and it reports four TB errors. Fix that TB before
  using it as scheduler acceptance evidence.
- Verified post-cleanup Gowin build on 2026-07-29 with the same TCL/top/device:
  bitstream generated at `impl/pnr/R120M_BM2BF1X1.fs`, UserCode
  `0x000074CB`, setup/hold violated endpoints 0/0, Fmax 66.702 MHz at 50 MHz,
  logic 10694/20736 (51%), registers 9825/16173 (60%), and all 101 ports
  `Constraint=Y`. Relative to the immediately preceding build, the cleanup
  removed 740 logic cells and 550 registers while improving Fmax by 3.046 MHz.
- LTDC processing cleanup is recorded by commit `33230329`.
  `ltdc_processing` is now a thin coordinator over
  `ltdc_measurement_engine` and `ltdc_point_builder`. The measurement contract
  is scalar and quad-LTDC-only; the inactive fallback, the then-unconsumed
  second intensity converter, pulse-width outputs, and propagated LTDC
  debug-error chain were removed. The later two-echo payload correction is
  recorded below; do not infer from this historical cleanup that PW2 may be
  discarded.
- Verification of that LTDC split passed at all required levels. The focused
  point-builder TB passed delay compensation, two echoes, no-hit and saturation
  cases. The full LTDC integration TB produced two 2006-byte packets, 509 fires
  and 509 interrupt falls, with the first distance at 44968 mm. The 100 ms
  sector regression finished `[OK]`: 9 frames, 6344 fires, projection
  `ok=8`, `bad=0`, ModelSim Errors=0.
- The exact post-refactor Gowin build generated UserCode `0x0000B57F`, with
  0 setup/hold violated endpoints, Fmax 63.142 MHz at 50 MHz, logic
  10693/20736, registers 9755/16173, and all 101 pin constraints present.
  Against the captured baseline this is -1 logic cell, -70 registers, and
  -3.560 MHz Fmax; timing still meets the constraint, but this is a timing
  regression and must be reported as such.

## `edge_detector` public port contract (verified 2026-07-29)

- Treat `src/edge_detector/edge_detector.sv` as the shared canonical helper.
  Keep `clk` as the clock-name exception and use `in_raw_wire` for the sampled
  signal. Its one-cycle event outputs are `out_edge_detected_stb`,
  `out_rising_edge_detected_stb`, and
  `out_falling_edge_detected_stb`.
- Do not reintroduce the legacy module/path `front_detector`, legacy generic
  terms `front_detected` or `backfront_detected`, or compatibility aliases.
  A shared-helper rename must update the directory, file, module, guard,
  focused TB/`.do`, include and project files, configuration fields, instance
  names, all named port maps, and directly connected implementation signals.
  Keep domain-event names only when they describe the consumer semantics.
- Make every output connection explicit at all `edge_detector` instances.
  Use an empty named connection for an intentionally unused output; this keeps
  elaboration free of missing-port warnings and makes repository-wide contract
  audits deterministic.
- The focused TB must cover both `is_fast=1` and `is_fast=0`, a multibit bus,
  rising edges, falling edges, simultaneous per-bit transitions, and a
  no-change sample.
- Commit `24d2dfca` renamed the complete contract and all 34 repository
  instances. The stale-name audit returned zero references. The focused TB,
  standalone MSOP TB, and full active LTDC integration TB passed; the full TB
  produced two 2006-byte packets from 509 fires/interrupt falls with both
  echoes at 44968 mm and 89937 mm.
- The fresh active Gowin PnR was bit-identical to the pre-rename build:
  UserCode `0x0000F5D8`, setup/hold violated endpoints `0/0`, Fmax
  `63.596 MHz` at 50 MHz, logic `10805/20736`, registers `9783/16173`,
  BSRAM `56%`, PLL `1/4`, and all 101 pin constraints present.
- Hardware acceptance on 2026-07-29: the user confirmed that the exact
  pre-verification branch tip
  `f76b8223fbd2868fd873cd82fb507602d72d8fae` works on the current
  `R120M.BF2` hardware target. That tree contains the functional
  `edge_detector` change in
  `24d2dfcaa93b1614c58e3191f4c8d4ddbb7b8c90`; its active Gowin image
  fingerprint is UserCode `0x0000F5D8`. Evidence class: user-confirmed
  physical behavior. No packet, UART, or analyzer details were supplied, so
  this is a functional hardware smoke `PASS` for the tested tree, not proof
  of unspecified per-signal or protocol metrics.

## R120M TDC7201 branch history (sim PASS 2026-07-06)

- Milestone: боевой `main` (lidar_measurement_pipeline) работает через прослойку
  `R120M_BM2BF1X1_brd_ifm` с двумя TDC7201; LTDC-X3 отложена (чип не введён).
  This section describes the preserved `R120M.BF2_TDC7201` line, not the
  active LTDC-only `R120M.BF2` branch.
  ТБ: `src/main/R120M_BM2BF1X1_tdc_tb.sv` + `.do` (модели `class_TDC7201`,
  энкодер стоит -> автоподжиг ~20 кГц, LTDC_INTERRUPT неактивен, SPI2 молчит).
  PASS-факты: 2 валидных MSOP-кадра (маркеры FF FE/FF 9B, 500/246 точек,
  angle_res=360, echo=3/2), 1258 поджигов, дистанция первой точки
  3766 мм = 0.14989 x 25125 пс — аналитически сходится с TIME1 модели.
- **Маппинг чипов**: в актуальном `tdc_processing` рабочая пара интерфейсов —
  56 (TDC переднего фронта, дистанция) и 34 (TDC среза, ширина);
  `if_TDC7201_12` в lidar_measurement_pipeline ЗАГЛУШЕН (en=0, cs=11). На R120M чип D23
  (пины TDC_*12/CS1/CS2) -> if_56, D24 (пины *34/CS3/CS4) -> if_34.
  Какой из D23/D24 ловит передний фронт — сверить по цепям компараторов.
- **Sim-vs-synth ловушка (боевой RTL)**: в `TDC7201_v2` порт `set_config_stb`
  SPI-контроллера был не подключён, а он входит в busy-выражение →
  в симуляции busy=X и `TDC7201_logic` вечно ждёт `!busy` (первый симптом:
  поджиги идут, стартовый конфиг TDC прошёл, а prep/чтений нет). На железе
  работало — синтезатор вяжет висящий вход в 0. Исправлено `.set_config_stb(1'b0)`.
  Урок: при переносе живого RTL в симуляцию проверять неподключённые входы,
  участвующие в управляющих выражениях.
- **Модель TDC7200 не умела auto-increment**: контроллер читает CAL1+CAL2
  одной транзакцией 6 байт (бит7 команды), модель отдавала только 3 байта —
  хвост повторял последний байт (симптом: cal2=0x9E9E9E, TOF в ~120 раз
  меньше). Исправлено в `class_TDC7200`: `read_reg(regAddr + out_cnt/3)`
  при cont_read_flag. Также параметризован TIME1 (конструктор), чтобы фронт
  и срез давали разные TOF — при равных тракт честно даёт дистанцию ~0.
- Выход MSOP: `MSOP_TCP_SPI_sender` (внутри lidar_measurement_pipeline) — ПЛИС SPI-мастер,
  1 CS-транзакция = 1 кадр, из `if_mcu_fpga.if_SPI2`; на R120M выведен на
  пины `MSOP_SPI_SCK/MOSI/CS_N` = R6/T5/R5 (бывшие MCU_FPGA_6/7/8).
  Соответствие SPI-slave ножкам STM32 — открытый вопрос.
- PnR прослойки после правок: Setup/Hold=0, Fmax 62.3 МГц, 101 порт constrained.
- Формула TOF тракта: TOF[пс] = TIME1 x 900000/(CAL2-CAL1) при
  CALIBRATION_PERIODS=10, TDC_DIGIT_FREQ=10 МГц; DST[мм] ≈ 0.149896 x TOF;
  LSB ≈ 10.47 пс при модельных CAL 2206/88175.

## R120M: заход в железо №1 — TDC-тракт запущен (verified 2026-07-06)

- Milestone на плате: поджиг ~21 кГц, оба TDC7201 отдают INT, вычитка идёт,
  ~86 MSOP-кадров/с на выходном SPI (R6/T5/R5). Доказательство — счётчики
  UART-репортера на COM4, без логanalyzer'а.
- **Корень отказа «TDC молчит»: подтяжки INTB.** INTB у TDC7201 — open-drain,
  MISO при CS=1 — Hi-Z. В новом cst стояло явное `PULL_MODE=NONE` → INTB
  повис в 0: i/j замерли на 1, уровни INT1/INT3=0, при живом SPI (c рос
  с частотой поджига). Старая плата (R120_M_1_1_0.cst) молча жила на
  **дефолте Gowin PULL_MODE=UP** — там строки закомментированы. Урок:
  для open-drain входов подтяжку писать ЯВНО (`PULL_MODE=UP`), а при
  портировании cst не заменять «пусто» на `NONE` — это разные вещи.
- **Диагностика через UART-репортер-«мультиметр»** (`r120m_dbg_uart_reporter`):
  строка `R120M f=.. i=.. m=.. c=.. j=.. s=..` раз в 0.5 с — счётчики
  поджигов/INT1/MSOP/CS1/INT3 + байт мгновенных уровней
  {EN12,INT1,INT3,MISO1,MISO3,fire,CS1,SCLK12}. Паттерны:
  c растёт, i стоит, уровень INT=0 → нет подтяжки/чип не отвечает;
  c стоит малым → SPI-контроллер застрял; всё растёт → тракт жив.
- **Стороны UART на гребёнке X14**: подписи пользователя «E1 - tx uart,
  E2 - rx uart» были со стороны USB-TTL адаптера → ПЛИС слушает E1,
  передаёт на E2. Та же ловушка, что D3/C1 на старом стенде: имена
  RX/TX всегда уточнять «чей TX».
- **Артефакт драйвера FTDI (COM4, FT232R)**: после перепрошивки порт может
  отдавать реплей устаревшего куска буфера на «невозможной» скорости
  (~73 кБ/с при 115200; одна и та же строка тысячами копий + обрезки).
  Лечится перециклом: открыть порт на другом бауде (230400), прочитать,
  закрыть, снова открыть на 115200. Настоящие строки узнаются по
  инкременту счётчиков. Не путать с отказом ПЛИС.
- Вачдог INTB (`TDC_INTB_monitor`, WD 4 с) в боевом RTL перезапускает цикл
  измерения при пропаже INT — поэтому при мёртвом INTB поджиги продолжаются,
  а конвейер тихо стоит: без счётчиков это выглядит как «всё работает».

## R120M: полная проверка корректности данных на железе (verified 2026-07-06)

- **DSView (сторона MOSI фронт-чипа D23)** подтвердил командный тракт SPI:
  ПЛИС шлёт `40 81` = write CONFIG1(0x00)=0x81 (FORCE_CAL+START_MEAS),
  затем `10 00 00 00` = read TIME1(0x10)+3 dummy, затем `9B 00 00 00 00 00 00`
  = auto-increment (бит7) read CAL1(0x1B)+CAL2, 6 dummy. Ровно как в симуляции.
  data-байты на MOSI = 0x00 (ПЛИС тактирует нули, читая ответ); настоящие
  TIME1/CAL приходят по MISO (H1) — их этот декод не показывает.
- **Снайфер выходного MSOP-SPI в прослойке** (без правки боевого RTL): тем же
  способом, что примет STM32, реконструирует байты кадра и достаёт дистанцию
  первой точки (offset 36..37 LE) + интенсивность (байт 38) в UART-репортёр.
  Сверен в главном ТБ бит-в-бит с независимым декодером (3766 мм в обоих).
- **Результат на стенде**: дистанция стабильна 12008..12033 мм (±12 мм),
  80 нс TOF = 12020/0.149896. Стабильность и точное совпадение с боевой
  константой 0.149896 мм/пс доказывают исправность тракта TDC → расчёт TOF →
  MSOP-упаковка → SPI-провод. Абсолютные 12 м на стенде БЕЗ мишени и с
  выключенным лазером (LSR_CHRG_CTRL=0) — электрический самозапуск STOP на
  перебросе START/FIRE, а не оптическое эхо; ширина импульса ≈0 (срез в тот же
  миг). Реальный оптический дальномер проверять с зарядом лазера + мишенью.
- **Оба чипа живы**: MSOP-кадры формируются, а tdc_data_ready требует
  готовности И D23 (фронт), И D24 (срез) — значит оба TDC завершают измерение.
- **Ловушка PnR: рулетка разводки на плотном дизайне.** База (регистры 76%)
  разводится стабильно, но маргинальная добавка снайфера дала PR0004
  «unrouted nets», причём НЕДЕТЕРМИНИРОВАННО (114 -> 329 при *меньшей* логике).
  Признак — не жёсткий потолок ёмкости, а перегрузка роутера. Лечение:
  освободить логику (убрать отладочные счётчики решённых проблем) + ужать
  добавку (счётчик байт 6 бит с насыщением, запись прямо в финальные регистры
  вместо промежуточных + защёлки). Не полагаться на перезапуск PnR.
- **«Cable lost» программатора** (FT2232 канал A) — снять зависший
  `programmer_cli.exe`, проверить `Get-PnpDevice` (канал A должен быть OK),
  повторить. Обычно транзиент после серии прошивок.

## W5500 на ПЛИС: SoC-сим PASS, standalone-топ bring-up заблокирован (2026-07-06)

- **Архитектурное решение**: релизный тракт — ПЛИС SPI-МАСТЕР шлёт MSOP в
  STM32 (fabric TDC7201 → MSOP → SPI, сборка R120M_BM2BF1X1, HWOK), а
  W5500/Ethernet держит STM32. W5500-на-ПЛИС (soft-MCU DarkRISCV + W5500
  bit-bang) — bench/fallback, **отложен** на этом блокере.
- **SoC-сим W5500 — PASS** (чистый submodule-коммит 656f2ef, прошивка
  w5500demo): version=04, netcfg 192.168.2.240, listen 50100, established,
  2 MSOP-кадра x758 байт, w5500demo ok. Транспорт логически исправен.
- **Блокер на железе — ядро darkriscv в НОВОМ standalone-топе
  (R120M_w5500_brd_ifm) не стартует.** Доказанная бисекция:
  - клок 50 МГц и конфиг ПЛИС ЖИВЫ — фабричный heartbeat даёт на DSLogic
    чистый меандр ровно 24.41 кГц (2048/50МГц = 40.96 мкс);
  - ROM ЗАГРУЖЕН — в нетлисте `defparam MEM_*_s.INIT_RAM_XX=256'h...` с
    реальным кодом (НЕ нули; формат — `256'h`, не `INIT_RAM="..."`);
  - darkpll для Gowin — passthrough (`assign CLK=XCLK`), двойного PLL нет;
  - пробованы XRES=0 (внутр. IRES, как в m20k_dev_uart_rmii_debug) и явный
    reset-hold — оба не помогли;
  - darkuart молчит на всех бодах; сеть 192.168.2.240 недоступна (нет ARP).
  - Итог: CPU имеет клок+сброс+ROM, но не исполняет. Причина не найдена
    (standalone darksocv-топ в этом worktree на железе ранее не гонялся;
    подозрение — выборка инструкций/интеграция BRAM или недостающий дефайн).
  - Диагностика для след. захода: cpu_ran = sticky «OPORT хоть раз != 0»
    (LED2 + DSLogic-F2, ровный уровень), + ФАБРИЧНЫЙ UART-репортёр на E2
    (UART_tx, работает, читается на COM4) сообщает cpu_ran/oport_seen —
    self-service, без походов к стенду. Битстрим собран, НЕ прошит.
- **Ловушка: светодиоды модуля W5500 горят ВСЕГДА** (power/PHY-LED модуля),
  даже без прошивки — НЕ признак, что CPU поднял OPORT[9]. Живость CPU
  проверять только по OPORT/fabric-защёлкам, не по LED модуля.
- **DARKETH_MMIO**: если топ его определяет — добавить `darketh_mmio.sv` в
  список файлов сборки (иначе EX3937 unknown module 'darketh_mmio').
- **FT2232 JTAG «Cable lost»/статус Unknown** после серии прошивок —
  снять зависший programmer_cli не всегда хватает; глубокий залип лечится
  только физическим перетыком USB (disable/enable требует админа).

## Публикация тестовых прошивок (сетевая шара, verified 2026-07-09)

Готовые тестовые битстримы для лидара складываются на сетевую SMB-шару (не в
git — `.fs`/`.bin` это generated artifacts):

```
\\192.168.2.50\e\YandexDisk\#Projects\ToF Lidar\!Firmware\FPGA\Тестовые прошивки
```

- **`.fs`/`.bin` НЕ коммитить в git** — только на эту шару.
- **Выкладывать на шару только по явному запросу пользователя** (как прошивка
  железа — не по своей инициативе).

- Доступна напрямую из PowerShell по UNC-пути (`Test-Path -LiteralPath`,
  `Copy-Item -LiteralPath`; путь с пробелами/`#`/`!`/кириллицей — только
  `-LiteralPath`). Это YandexDisk-папка на хосте 192.168.2.50.
- **Конвенция имён** (по существующим файлам в папке):
  `<TOP>_<YYYYMMDD>_<HHMM>_<git8>_<описание>_<STATUS>.fs`
  - `<TOP>` — имя проекта/битстрима (`R120M_LTDC_MSOP`, `LDR_20K`, …);
  - дата/время — `LastWriteTime` файла `.fs` (напр. `20260709_1137`);
  - `<git8>` — короткий хэш коммита сборки; если рабочее дерево грязное,
    добавляй суть незакоммиченного в `<описание>`;
  - `<STATUS>` — `HWOK` (проверено на железе и работает), `BUILDOK`
    (только собралось), `HWRUN` (крутится на железе, фича ещё не подтверждена);
  - полезно вложить `UC0x….` (User Code) в имя — сверять по fingerprint,
    какой битстрим реально прошит (см. gowin-usercode-fingerprint).
- Рядом можно класть одноимённый `.rpt.txt`/`.bin`, как уже сделано в папке.

## Грабли стенда LTDC/Gowin (проверено 2026-07-09)

Повторяющиеся ловушки — чтобы не жечь токены заново:

- **CWD gw_sh дрейфует вглубь → вложенные `impl/pnr/impl/pnr/...`.** Если запускать
  `& gw_sh.exe build.tcl` подряд, вывод каждый раз оказывается на уровень глубже
  (gw_sh не восстанавливает CWD после `run all`, а PowerShell-сессия его хранит).
  **Симптом:** UserCode НЕ меняется между сборками при реальных правках — значит
  читаешь устаревший `.fs`. **Фикс:** перед каждой сборкой `Set-Location
  C:\workspace\verilog`; свежий `.fs` искать рекурсивно по всему дереву
  (`Get-ChildItem -Recurse -Filter R120M_LTDC_MSOP.fs | Sort LastWriteTime`) и
  сверять UserCode/время, а не по фиксированному `impl/pnr`.
- **SPI-транзиент LTDC после каждой прошивки.** После заливки (SRAM/FLASH) конфиг
  чипа иногда не проходит: `cfg_error`→`LS_ERROR`, либо FSM залипает `dev=0,busy=1,
  f=0`. FSM выхода из `LS_ERROR` не имеет. **Фикс:** просто перешить ещё раз (сброс
  FPGA перезапускает power_up+config). Диагностировать по полю `s=`(line_status).
- **COM-порт репортёра переномеровывается после прошивки.** Общий FT2232
  (`VID_0403 PID_6010`) переэнумерируется, COM репортёра (был COM4) может пропасть
  или сменить номер. Канал B FT2232 (UART программатора) — НЕ репортёр (молчит).
  Репортёр — отдельный USB-UART донгл на `FPGA_TX`(M11/X1) или `DBG_E2`(E2/X14).
  Пересканировать порты и опознать по устройству.
- **Потолок фабрики GW2A-18 зависит от ГЛУБИНЫ пути, а не от кристалла.**
  Замерено 26.08.2026 прямыми сборками, зонд `probe/fabric_fmax/` в ветке
  `feat/clk-500mhz` (GW2A-LV18PG256C8/I7, среда 1.9.8.07, ограничение 500 МГц):

  | Дизайн | Уровней логики | Actual Fmax | Нарушений setup при 500 МГц |
  |---|---|---|---|
  | счётчик 8 бит + сравнение | 3 | **513.6 МГц** | **0** |
  | счётчик 32 бита + сравнение | 4 | 308.3 МГц | 43 |
  | боевой `R120M_BM2BF1X1` как есть | 11 | 76.4 МГц | **15 869** из 23 127 |

  То есть rPLL 500 МГц (FBDIV_SEL=49, ODIV_SEL=2, VCO 1000 МГц) кристалл выдаёт,
  и фабрика её ДЕРЖИТ — но только на путях глубиной до трёх уровней. Уже четыре
  уровня роняют предел до 308 МГц. Отсюда практический смысл: частота не
  «выбирается», она СЛЕДУЕТ из глубины самого длинного пути, и перевод проекта на
  более высокую частоту — это переконвейеривание датапата, а не правка PLL.

  Тот же боевой проект при ограничении 50 МГц даёт Fmax 70.3 МГц, при
  ограничении 500 МГц — 76.4 МГц: PnR выжимает из НЕИЗМЕННОГО RTL около 8 %, не
  больше. Просить у инструмента частоту, которой нет в схеме, бесполезно.

  Обычная логика не влезает в 250 МГц надёжно. Тяжёлую арифметику (сумматоры/mux) держать в медленном домене, в
  быстрый передавать уже готовые СТАБИЛЬНЫЕ значения (там только счётчик+сравнения).
  Даже так захват квазистатического вектора через CDC стоит ~0.5нс роутинга.
  **200 МГц (5 нс/такт) — безопасная цель фабрики** (0 нарушений, запас +1нс).
  Худший путь смотреть в `impl/pnr/.../R120M_LTDC_MSOP.timing_paths` (блоки `SETUP`,
  первая строка после — slack; отрицательный = нарушение).
- **PowerShell sandbox блокирует `& cmd.exe /c "..."` внутри условий/функций**
  (ошибка вида «Remove-Item on system path '/c' is blocked»). Запускать `.bat`
  прошивки отдельной верхнеуровневой командой, не в `if/function`.
- **Gowin sim-примитивы** (OSER/rPLL/CLKDIV) лежат в `bin/IDE/simlib/gw2a/`. Но
  проще для сима не тянуть их, а **заглушить PLL в ТБ** поведенчески (генерить
  нужную частоту `always #<半period> c=~c`), синтез подставит реальный примитив.
- **pdftotext** — в `/mingw64/bin` (Git-for-Windows), НЕ в msys64; `-layout` для
  таблиц даташита.
- **pdf-inspector** (firecrawl, Rust) — лучше pdftotext для даташитов: PDF → Markdown
  со структурными таблицами/заголовками и классификацией `text_based`/`scanned`
  (сканы без OCR не берёт — сразу видно, что нужен OCR). `pip install pdf-inspector`;
  Python API: `pdf_inspector.process_pdf(path)` → `.pdf_type`, `.markdown`.
  Проверено 06.08.2026 на LTDC-X3-Datasheet.pdf (`text_based`, 76 КБ md) и батче
  185 PDF вольта (170 OK, кириллица/таблицы целы). Ограничения (проверено):
  векторные схемы плат (Tang Dock/SOM) падают с `invalid content stream`;
  битый ToUnicode CMap даёт `text_based` с пустым markdown (тогда и pdftotext
  выдаёт кашу — нужен OCR). CLI `pdf2md`/`detect-pdf` — отдельно через
  `cargo install pdf-inspector`.
- **Мульти-хит на ОДИН канал LTDC на этом стенде не набирается** (ловится 1 хит/
  канал и на STOP2, и на ch1 в combine). 2 эха берём как 2 канала × 1 хит
  (`CHANNEL_COMBINE`); 3 эха (2 хита на ch1) упираются в тот же аналоговый лимит
  входа. Детали — заметка Obsidian [[LTDC-X3 режимы STOP]].

## Заливка FPGA в R120M через lconf CLI (проверено 23.07.2026)

Заливка на боевой лидар R120M (МК STM32 пишет FPGA-флеш) идёт через бутлоадер-порт
`50102`. Прямой вызов БЕЗ `--reset-before-flash` на 192.168.2.206 воспроизводимо
падал: после шага «Send boot» блок закрывает TCP, переподключение проходит, второй
вход в загрузчик снова обрывается → `Не дождались ответа от блока (New step timeout)`,
прогресс 0%, флеш не тронут.

Рабочий вариант — послать лидару UDP `LIDAR_ACTION RESET` перед заливкой; при этом
lconf сам отключает шаг JmpBoot (`Runtime profile: JmpBoot step disabled because
--reset-before-flash is active`):

```powershell
& 'C:\workspace\lidar\lconf\bin\Release\lconf.exe' --cli --file <образ.bin> `
  --channel tcp --host 192.168.2.206 --port 50102 `
  --reset-before-flash --reset-mac 00:80:E1:07:00:11 `
  --reset-target 192.168.2.206 --reset-local-host 192.168.2.145 `
  --reset-delay 4000 --reconnect-after-boot `
  --erase-timeout 300000 --reply-timeout 30000
```

С lconf `54b256d` (ветка dev, 23.07.2026) ключи больше не нужны — сброс включён
ПО УМОЛЧАНИЮ для каналов tcp/udp, MAC запрашивается у лидара UDP-обнаружением
по `--host`, цель сброса = сам лидар, пауза после сброса 4000 мс. Достаточно:

```powershell
& 'C:\workspace\lidar\lconfin\Release\lconf.exe' --cli --file <образ.bin> `
  --channel tcp --host 192.168.2.206 --port 50102
```

Вернуть прежнее поведение (шаги JmpBoot профиля) — ключ `--no-reset-before-flash`.
Пауза 1500 мс (старый дефолт) не работала: блок не успевал поднять сеть,
заливка падала на `Ошибка TCP connect: timeout`.

- MAC можно задать и явно (`--reset-mac`), например из ARP:
  `arp -d <ip>; ping -n 2 <ip>; arp -a <ip>`.
- Признак успеха: `Send end` и `OK: Данные загружены.`, 886 кБ при `.bin` 907418 Б
  (lconf сам добивает образ до 907776 Б, blockSize=256, 3546 блоков).
- Лидар автоматически перезагружается после заливки — это норма. Через ~10 с снова
  отвечают порты 50100/50101/50102.
- ПО собирается из ветки `dev` репозитория `ak-tech-electronics/TOF_lidar_GUI`
  (`MSBuild lconf.vcxproj /p:Configuration=Release /p:Platform=x64`), exe —
  `C:\workspace\lidar\lconf\bin\Release\lconf.exe`.

## LTDC runtime intensity thresholds (verified 2026-07-29)

- Commit `7712b47e` replaced elaboration parameters
  `MIN_INTENSITY`/`MAX_INTENSITY` with the runtime fields
  `ltdc_min_intensity_ps`/`ltdc_max_intensity_ps`. The active fields live in
  `interface_MCU_FPGA`; ordinary input ports carry them through
  `ltdc_processing` and `ltdc_point_builder` into `intensity_to_color`.
- The command address/write source is intentionally deferred. Defaults remain
  `2500/4500 ps`. The standalone top has the same fields for both echoes, but
  Gowin folds them to their defaults until a synthesizable writer is connected;
  do not claim live-hardware reconfiguration from a hierarchical `force`.
- Same-elaboration ModelSim evidence: `intensity_to_color_tb` changed thresholds
  and produced `127 -> 0 -> 255`; `ltdc_point_builder_tb` produced `127 -> 0`;
  standalone MSOP proved both echo intensities `0 -> 255`; the active full top
  produced two 2006-byte frames, 509 fires/interrupt falls, distances
  `44968/89937 mm`, and intensity `0` at `100000..200000`. The command-SPI and
  legacy distance-width regressions also passed with zero errors.
- Fresh Gowin outputs were generated without programming hardware.
  `R120M_BM2BF1X1`: UserCode `0x0000F5D8`, setup/hold `0/0`, Fmax
  `63.596 MHz` at `50 MHz`, logic `10805`, registers `9783`, BSRAM `56%`.
  `R120M_LTDC_MSOP`: UserCode `0x00006C5A` (previous artifact
  `0x0000C29F`), setup/hold `0/0`, Fmax `106.839 MHz`, logic `2905`,
  registers `2084`, BSRAM `34%`.

## LTDC direct QSPI integration (verified 2026-07-29)

- Commit `d7fa85e4` removed the pass-through LTDC quad-read wrapper and its
  wrapper-only TB. The active measurement engine and standalone MSOP top now
  instantiate `qspi_1_4_4_sdr_read_master` directly with `COMMAND=8'h6B`.
- The transport, handler, standalone MSOP, and full active ModelSim regressions
  passed. The integrations proved both echoes and recovery after an injected
  illegal transport state.
- Fresh Gowin builds were bit-identical to their pre-removal baselines:
  `R120M_BM2BF1X1` UserCode `0x0000F5D8`, Fmax `63.596 MHz`, logic `10805`,
  registers `9783`; `R120M_LTDC_MSOP` UserCode `0x00006C5A`, Fmax
  `106.839 MHz`, logic `2905`, registers `2084`; setup/hold `0/0` for both.
  No hardware was programmed.

## Active LTDC second-echo intensity (verified 2026-07-29)

- Commit `564f4afc` completed the active 12-byte LTDC result contract:
  bytes `0..2=TOF1`, `3..5=PW1`, `6..8=TOF2`, and `9..11=PW2`.
  Both PW values now reach `ltdc_point_builder` and the existing MSOP
  `intensity1/intensity2` payload fields. Mirror association is held in a
  dedicated register; it is no longer hidden in the low bits of `intensity2`.
- This is the existing 8-bit PW-to-intensity conversion, not a lossless export
  of the raw 24-bit PW. A raw-PW protocol format remains a separate decision.
- TB-first evidence reproduced the old defect with `PW1=5000 ps`,
  `PW2=20000 ps`, runtime thresholds `6000..19000 ps`, and serialized
  `intensity1/intensity2=0/0` instead of `0/255`. After the fix, the focused
  point-builder and both MSOP pipeline regressions passed. The full active TB
  produced two 2006-byte packets, distances `44968/89937 mm`, intensities
  `0/255`, and 509 fires / 509 interrupt falls. The full command-SPI TB also
  passed the active hierarchy and safe TDC7201 pin assertions; all reported
  ModelSim errors were zero.
- A direct second `intensity_to_color` instance was functionally correct but
  cost `11227` logic cells, `10128` registers, and reduced Fmax to
  `55.521 MHz`. Commit `4664450f` therefore time-multiplexes one existing
  converter across both PWs, with latched PW2/runtime thresholds and an enum
  state that associates each result with its echo. The focused TB additionally
  changes the runtime thresholds while conversion is in flight and enforces a
  200-cycle completion bound; the full-rate integration regression still
  passed with the same 509/509 event counts.
- Fresh active PnR for `4664450f`: UserCode `0x0000D9CB`, setup/hold violated
  endpoints `0/0`, Fmax `74.810 MHz` at `50 MHz`, logic `10704/20736`,
  registers `9920/16173`, BSRAM `56%`, PLL `1/4`, and all 101 ports
  constrained. Against the parallel implementation this saves 523 logic cells
  and 208 registers while adding 19.289 MHz Fmax. Against the pre-feature
  baseline it uses 101 fewer logic cells, 137 more registers, and adds
  11.214 MHz Fmax. No hardware was programmed.

## R120M.BF2 sector handling hardware acceptance (verified 2026-07-29)

- The user confirmed that the exact source state
  `e6c310598a5b73f6be5a57b728ad35b6c447e726` was tested on the
  `R120M.BM2BF1X1` board and that sector handling works correctly. Branch:
  `R120M.BF2`; top: `R120M_BM2BF1X1_brd_ifm`. Status: `HWOK`; verdict:
  `PASS`.
- Evidence class: user-confirmed physical behavior on the target hardware.
  This proves the reported sector behavior for the tested tree. Exact sector
  bounds, angular resolution, LTDC register configuration, scene conditions,
  sample count, and packet/UART/analyzer artifacts were not supplied, so no
  additional quantitative or per-signal claims are made.
- A reproducible clean Gowin build of that SHA has UserCode `0x0000D9CB`,
  setup/hold violated endpoints `0/0`, Fmax `74.810 MHz` at `50 MHz`, and all
  101 ports constrained. The documentation commit that records this result
  was not the programmed source state; the tested SHA remains
  `e6c310598a5b73f6be5a57b728ad35b6c447e726`.

## Измерение углового сдвига тела кадра MSOP (инструменты)

Связка трёх скриптов рядом с `msop_tcp_sniff.py`; ими найден и закрыт дефект
сдвига тела кадра (раздел ниже). Работают по сырым кадрам, снятым сниффером.

```powershell
$S = "C:\workspaceerilog\.agents\skillspga-dev\scripts"
# 1. поставить сектор (и/или формат пакета) сырой командой, минуя лимиты ПО
python $S\lidar_cmd_client.py --host 192.168.2.206 --local-host 192.168.2.145 `
  --sector 20000 160000
# 2. снять кадры
python $S\msop_tcp_sniff.py --host 192.168.2.206 --local-host 192.168.2.145 `
  --frames 24 --timeout 20 --raw-dir refA --jsonl refA.jsonl --allow-partial
# 3. профиль сцены по узлам сетки
python $S\msop_angle_profile.py refA
# 4. целочисленный сдвиг проверяемого захвата относительно эталона
python $S\msop_body_shift_scan.py refA test50
```

- `lidar_cmd_client.py` — сырой клиент команд на порт `50101`: `VIEW_SECTOR`
  (`0x53`) и формат пакета `ECHO` (`0x54`), запись и чтение. Нужен, чтобы
  задавать границы в обход валидации ПО и читать фактически применённое.
  Программный сброс — команда `0x31`, action `RESET=0`, поле `target_mac`.
- `msop_angle_profile.py` — медиана дистанции/интенсивности на каждом узле
  сетки по всем кадрам захвата (эталон сцены).
- `msop_body_shift_scan.py` — SSD-скан целочисленного сдвига между двумя
  захватами. Шумовой пол задаётся повтором одного и того же сектора (1-3 мм);
  сдвиг тела кадра виден как устойчивый ненулевой минимум.

Правило измерения: сцена должна быть неподвижна между эталоном и проверкой, а
после программного сброса надо дождаться выхода `point_count` на расчётное
значение сектора — иначе мотор ещё раскручивается и захват мусорный.

## Сдвиг тела кадра MSOP — корень и фикс (2026-07-29)

Дефект жил и в принятой `e6c31059` («сектора HWOK»), приёмка его не увидела.

**Симптом.** Тело кадра MSOP циклически сдвинуто относительно угловых меток:
картинка в ПО повёрнута при любом секторе, кроме одного «счастливого». Закон —
**сдвиг = Δ mod point_count** при постоянном Δ, где Δ меняется от загрузки к
загрузке. Замеры на 192.168.2.206 (профили d(метка) по 24 кадра, SSD-скан
целочисленного сдвига, шумовой пол — повтор того же сектора):

| Сектор | pc | Сдвиг | сходится с |
|---|---|---|---|
| 66–130 | 267 | +122 | 656 mod 267 |
| 50–160 | 458 | +198 | 656 mod 458 |
| 35–160 | 521 | +135 | 656 mod 521 |
| 20–160 | 583 | +73  | 656 mod 583 |

Другая сессия дала Δ=777 точек (777 mod 611 = 166, mod 694 = 83, mod 445 = 332,
mod 444 = 333, mod 777 = 0). Ранняя формула `140°/res − pc` была СОВПАДЕНИЕМ:
Δ=777 случайно равен pc юстировочного сектора 20–160 при res=180.

**Как нашли.** Пользователь заметил, что дефект снимается переключением
`Дист., байт` 2 → 3 → 2 в ПО. Это дёргает `pack_format_flush_stb` —
ЕДИНСТВЕННОЕ место в `MSOP_TCP_sender`, сбрасывающее указатели body RAM.

**Корень.** Дескриптор кадра публикуется как
`out_desc_valid_stb = close_packet_stb && !in_desc_fifo_full`
(`MSOP_TCP_frame_tracker`): при полной очереди (8 дескрипторов) кадр ТЕРЯЕТСЯ,
а его тела уже записаны в body RAM. Читатель двигал собственный
`body_read_base_addr` только по дескрипторам, поэтому осиротевшие байты уводили
чтение НАВСЕГДА. `out_desc_overflow` никуда не подключён; накопительный
`body_fifo_byte_count` осиротевшие байты тоже не вычитал. На старте (раскрутка
мотора, stopped-пакеты ~20 кГц, ещё не читающий МК) очередь переполняется —
отсюда разный Δ на каждой загрузке. Дефект воспроизводится программным сбросом
(команда `0x31`, action `RESET=0`).

Почему молчала симуляция: в ТБ очередь дескрипторов не переполняется.

**Фикс** (этот коммит): адрес начала тела кадра защёлкивается на первом
записанном байте и едет в дескрипторе (`frame_desc_t.body_start_addr`); база
чтения берётся из дескриптора, а не накапливается; готовность тела считается по
реально записанному расстоянию от старта кадра; занятость body RAM выводится из
указателей. Новый `out_frame_closed_stb` (без гейта по переполнению) снимает
захват адреса даже у потерянного кадра. Потерянный дескриптор теперь стоит
ровно одного пропущенного кадра.

**Приёмка на железе.** Сборка линии `15d6b4fc` с этим же фиксом: UserCode
`0x0000B29E`, setup/hold violated `0/0`, Fmax `62.016 MHz` при `50 MHz`,
logic `10942/20736`, registers `9911/16173`, BSRAM `58%`. После программного
сброса — сценария, до фикса воспроизводимо дававшего Δ=656 — свип пяти секторов
БЕЗ единого переключения формата: сдвиг **0** везде (остаток 1.0–1.5 мм),
против +122 / +198 / +135 / +73 до фикса. Сим: `R120M_BM2BF1X1_ltdc_tb` PASS;
`R120M_BM2BF1X1_sector_repro_tb` со сменой сектора через настоящий командный
SPI — `frames=9 ok=8 bad=0 [OK]`. В `MSOP_TCP_frame_tracker_tb` единственный
`[FAIL]` — устаревшая проверка зеркального якоря, удалённого в `3e13a234`; на
базовом коммите красная идентично.

**Правило.** `out_desc_overflow` и `out_body_overflow` в `MSOP_TCP_sender`
по-прежнему не подключены никуда. Любой счётчик «посчитано против записано»
обязан иметь наблюдаемый выход, иначе потеря снова станет невидимой.

## R120M.BF2 с фиксом сдвига тела MSOP — HWOK (2026-07-29)

- Проверенное состояние: `49825440` на ветке `R120M.BF2`, плата `R120M.BM2BF1X1`,
  top `R120M_BM2BF1X1_brd_ifm`. Gowin UserCode `0x0000DF15`, setup/hold violated
  endpoints `0/0`, logic `10739/20736 51%`, registers `9950/16173 61%`,
  ошибок синтеза нет. Заливка `lconf --cli ... --port 50102`, 192.168.2.206.
- Каноническое имя выпуска: `R120M.BF2MF6FP1X3` (`MF6` — контракт команд МК-ПЛИС
  не менялся; `FP1` — формат пакета не менялся; новая итерация `X3`).
- Приёмка: свип секторов БЕЗ переключения формата пакета, дважды — сразу после
  заливки и повторно после программного сброса (`0x31`, action `RESET=0`),
  который до фикса воспроизводимо создавал сдвиг:

| Сектор | pc | после заливки | после сброса |
|---|---|---|---|
| 66–130 | 267 | 0 (2.0 мм) | 0 (1.5 мм) |
| 50–160 | 458 | 0 (2.0 мм) | 0 (2.0 мм) |
| 35–160 | 521 | 0 (2.0 мм) | 0 (2.0 мм) |
| 20–160 | 583 | 0 (2.0 мм) | 0 (2.0 мм) |
| 66–130 (возврат) | 267 | 0 (1.5 мм) | 0 (1.0 мм) |

  Метод: агрегированные профили d(метка) по 24 кадра на сектор, SSD-скан
  целочисленного сдвига; шумовой пол — повтор того же сектора (1–2 мм).
  До фикса тот же тест давал +122 / +198 / +135 / +73.
- Симуляция на этом же состоянии: `R120M_BM2BF1X1_ltdc_tb` **PASS**, Errors 0.
- Класс доказательства: прямое измерение потока MSOP TCP сниффером; отдельные
  UART/DSView-артефакты не снимались.
- Серверный `.bin`: `\192.168.2.50\e\YandexDisk\#Projects\ToF Lidar\!Firmware\FPGA\Тестовые прошивки\R120M.BF2MF6FP1X3.git-49825440.img-73d374d90b54.uc-0000DF15.HWOK.bin`;
  SHA-256 `73d374d90b54f8b3afbe0d4f9033ac12f955b3a4e68447d4338d5c74a1edb3c8`.
- Серверный `.fs`: тот же каталог,
  `R120M.BF2MF6FP1X3.git-49825440.img-bdc72e05e905.uc-0000DF15.HWOK.fs`;
  SHA-256 `bdc72e05e905dff6104768af70ba3e259597ea7163bd33a263ddedef332ac13b`.
  Оба файла после копирования сверены по SHA-256 непосредственно на сервере.
- ВНИМАНИЕ по мотору: после программного сброса кадры несколько секунд идут
  укороченными (pc=91 и т.п.) — мотор набирает обороты. Мерить только после
  выхода pc на расчётное значение сектора, иначе захват мусорный.

## Табличная walk-компенсация на LTDC — подключение (2026-07-30)

Механизм `compensation_curve_applier`, работавший на тракте TDC7201, перенесён
на LTDC-X3. Разбор в Obsidian: `Работа/Лидар/ВЦП TDC/TDC/LTDC-X3/Табличная
walk-компенсация на тракте LTDC-X3 — подключение и что ещё не откалибровано.md`.

Ветки: боевая `R120M.BF2` — `9c6ccff7` (эхо-1 через таблицу, эхо-2 как обычно);
диагностическая `diag/walk-cmp-vs-raw` — `40d60959` (эхо-2 = то же измерение
БЕЗ поправки, аналог пары `dst`/`dst_cmp` на TDC7201). Ни одна на железо не
заливалась.

Ось ширин пришлось переделать: `width_list_64x64_ltdc.hex` = исходная ось
TDC7201, поделённая на 3 (2280..10125 пс, шаг ~124 пс). Наблюдённые ширины
LTDC 4124..4484 пс лежат НИЖЕ исходной оси (от 6840 пс), то есть без деления
`table_index_finder` зажимал бы всё в индекс 0 и поправка была бы краевой.
Ось TOF (`tof_list_64x64.hex`, 2771..148504 пс) НЕ менялась — она в единицах
времени и от типа чипа не зависит; мишень стенда ~1.5 м даёт индекс 3.

ГЛАВНОЕ, что не сделано: значения `comp_matrix_64x64_ec12185ps.hex` остались
снятыми на TDC7201. В рабочей точке стенда (TOF ~10007 пс, ширины 4124..4484 пс)
таблица вычтет ~554..611 мм, то есть мишень 1500 мм покажется как ~900..950 мм.
Постоянная часть поправки снимается перевыставлением `propagation_delay_ps`, а
вот НАКЛОН (~0.29 мм/пс по таблице) — это наклон приёмного тракта TDC7201, и
его надо снимать заново на LTDC: мишени разной отражающей способности на
фиксированной дистанции, затем несколько дистанций. На одномишенном стенде
задействованы всего 3-4 столбца матрицы из 64.

Перезапись таблиц от МК по SPI временно отключена: `interface_comp_tbl_wr`
объявлен в `ltdc_point_builder` локально, `en` в нуле. Пишет ли МК таблицу и
что именно — не выяснено (анализатор на `SSPI_CMD_SCK/MOSI/CS_N/MISO`,
полупериод ~931 нс, фильтр по адресу 1208, нагрузка `[0] sel`, `[1:2] addr` LE,
`[3:6] data` LE).

Две грабли запуска, обе стоили круга:

- Windows MAX_PATH. Applier и его глубокие зависимости (`divider`,
  `divider_uint_with_reminder`, `serial_multiplier`, `linear_interpolation`,
  `bilinear_interpolation`) подключаются короткими путями ИЗ `main.sv`. Из
  `ltdc_point_builder` цепочка вложенных `../../../math/...` и
  `../FPGA-FixedPoint-master/...` вылезает за 260 символов и Gowin падает на
  `Cannot open include file`. Фокусный ТБ компилируется отдельно от `main.sv`,
  поэтому подключает эти файлы сам.
- `R120M_BM2BF1X1_ltdc_tb` компилируется ТОЛЬКО из каталога `src`: внутри
  цепочки есть `include "machines/machine_header.sv"` без `../`, он резолвится
  относительно текущего каталога. Из `src/main` сборка падает на
  `Eth_common.svh(5)`.

Команды (пути этой машины):

```
# ModelSim ASE 10.5b
C:\intelFPGA\18.1\modelsim_ase\win32aloem\{vlib,vlog,vsim}.exe
# фокусный ТБ — из каталога модуля
cd src\TDC_LTDC_X3\ltdc_processing && vlog -sv ltdc_point_builder_tb.sv
# топовый ТБ — ТОЛЬКО из src
cd src && vlog -sv main\R120M_BM2BF1X1_ltdc_tb.sv
# сборка
cd 20k\LDR_20K && C:\workspace\verilog\bin\IDE\bin\gw_sh.exe build_r120m_bm2bf1x1.tcl
```

Не пропускать вывод `gw_sh` через `Select-String ... | Select-Object -First N`:
как только фильтр перестаёт читать, процесс убивается и получается ложный
exit 255 при исправной сборке. Писать лог в файл и грепать файл.

Приёмка боевой ветки: `ltdc_point_builder_tb` PASS (включая случай «нет эха» —
applier и на нём выдаёт строб готовности, конвейер не встаёт);
`R120M_BM2BF1X1_ltdc_tb` PASS (509 поджигов / 509 прерываний / 2 пакета 2006 Б,
эхо-1 44510 мм, эхо-2 89937 мм); Gowin CheckSum `0x6E3E`, setup/hold violated
0/0, Fmax 62.504 МГц при 50 (до таблицы было 62.016 — деградации нет),
logic 60 %, registers 69 %, BSRAM 71 %.

Приёмка диагностической ветки: оба ТБ PASS, эхо-2 отдало 44968 мм вместо
89938 мм (отклик на 600 нс тракт игнорирует), разность каналов 458 мм;
setup slack +4.094 нс, hold +0.074 нс, Fmax 62.871 МГц. Допуска ±300 мм на
дистанцию для доказательства НЕ хватает — окна каналов перекрываются, поэтому
в ТБ добавлена прямая проверка РАЗНОСТИ каналов с допуском ±10 мм.

Диагностический режим переключает у эхо-2 ТРИ источника сразу: TOF, признак
«нет эха» и ширину для раскраски. Переключать надо все три — иначе точка, где
эхо-1 есть, а второго отражения нет, дала бы во втором канале ноль при живом
значении в первом.

## Снижение СКО LTDC-X3 программными мерами (замерено 30.07.2026)

Замеры сделаны на ветке `perf/ltdc-jitter-reduction` (`ac798466`); в боевую
`R120M.BF2` перенесены вывод, отвергнутые варианты и `HIGHRES`. Стенд
192.168.2.206, мотор ОСТАНОВЛЕН (все точки смотрят в одну сторону, поэтому
разброс дистанции = СКО единичного измерения всего тракта), цель 1810 мм,
интенсивность у насыщения, 60 000 точек на прогон, скрипт
`docs/skills/fpga-dev/scripts/msop_sigma.py`.

**Природа СКО установлена: это ПЛОТНОСТЬ КОДОВ, а не шум тракта.** Гистограмма
при неподвижной цели — гребёнка из пяти зубьев с равномерным шагом
9.75 мм = 65.0 пс; внутри зуба робастная σ всего 1.48 мм = 9.9 пс. Условия
отвечают code density test (фаза START не коррелирована с внутренней опорой
чипа), значит высота моды пропорциональна реальной ширине кода. Вывод:
**фактическая ширина бина ВЦП около 65 пс при номинальном LSB 1 пс**, то есть
сильная DNL. Прежний тезис «65 пс — вклад лазера и приёмника, настройкой ВЦП не
убирается» ОПРОВЕРГНУТ: внутри одного бина тракт даёт 9.9 пс.

| Конфигурация | UserCode | σ | Вердикт |
|---|---|---|---|
| база `HIGHRES=0` | `0x0000DF15` | 9.72 мм / 64.9 пс | исходная |
| `QSPI_DIV=2` (SCK 12.5 вместо 25 МГц) | `0x0000DBD3` | 9.50 мм / 63.4 пс | ОТВЕРГНУТО: шаг гребёнки 63.4 против 65.0 пс — не изменился |
| `HIGHRES=1` | `0x0000D0DB` | 8.41 мм / 56.1 пс | бин ~33 пс, половина выигрыша |
| **`HIGHRES=2`** | `0x0000BB29` | **7.29 мм / 48.6 пс** | **принято в боевую** |
| `HIGHRES=2` + `CFG0` бит 2 | `0x0000734F` | 7.16 мм / 47.8 пс | НЕЙТРАЛЬНО (разброс прогонов ~1 пс) |
| `STOP_MASK=1` поверх `HIGHRES=2` | `0x0000252F` | 41.6 пс, дистанция 1819 мм | нейтрально, но МАСКА РАБОТАЕТ |

`HIGHRES` снижает σ ровно пропорционально сужению бина (65/33/20 пс ->
64.9/56.1/48.6 пс) — прямое подтверждение модели. Побочный и для картинки более
важный эффект: отношение обычной σ к робастной падает с 6.5 до 1.0, распределение
становится гауссовым, дискретные «неправильные» дистанции исчезают.

Что закрыто отрицательными результатами (не проверять повторно):

- **`QSPI_DIV=2`** работает, но на СКО не влияет. Тракт вычитки как источник
  дискретности закрыт.
- **`CFG0` бит 2**: даташит §6.2.1 (Table 8) и Table 46 требуют «Set 1.
  reserved», eval-конфиг вендора `Ltdcx3.cfg` (0x43) даёт 0. A/B показал
  нейтральность — оставлен вендорский 0.
- **`STOP_MASK`** перепроверен на ВАЛИДНОМ стенде: маска работает, на СКО
  нейтральна, дистанция корректная. Прежний вывод «непригодна» был артефактом
  стенда, потерявшего цель, и СНЯТ.
- **`REARM_CLKS` 32->128 и `INT_TIMEOUT_CLKS` 400->800 ЛОМАЮТ тракт**
  (UserCode `0x00002253`): поток MSOP пропадает целиком, командный порт при
  этом жив. Перевзвод 128 тактов = 2.56 мкс не укладывается в окно подготовки
  1.9 мкс из `lidar_conductor`, чип не успевает взвестись к поджигу. Это НЕ
  свободные параметры.

Чего HIGHRES=2 стоит — НЕ ИЗМЕРЕНО. Даташит §7.3.5: HIGHRES снижает СКО
единичного измерения, но ухудшает разрешение ПАРЫ импульсов (при `HIGHRES=0`
оно 15 нс). Боевой тракт работает в `CHANNEL_COMBINE`, то есть оба эха приходят
с одного стоп-провода и разбираются как пара — ровно тот режим, где цена и
проявилась бы. На плоской цели стенда второго возврата физически нет (все
`dst2 = 0`), поэтому замерить не удалось. Первый боевой прогон с `HIGHRES=2`
проверять на сцене с ДВУМЯ поверхностями.

Дальше по величине резерва мера уже не программная: подать `REFCLK` чипа от PLL
ПЛИС через перемычки J35/J36/J37 и свипировать задержку FIRE.

### Перенос HIGHRES=2 в боевую R120M.BF2 (03.08.2026)

Параметр проброшен через `lidar_measurement_pipeline` как `LTDC_HIGHRES` (дефолт 2) в
`ltdc_processing`, где он уже был. Боевые режимы НЕ трогались: `COMBINE(1'b1)`
остаётся зашитым в `ltdc_measurement_engine`, таблица walk и вычитание
`propagation_delay_ps` включены. Стендовые ручки ветки `perf/...`
(`STOP_CMOS`, `STOP1_ONLY`, `TOF_ONLY`, `PROP_DELAY_EN=0`, `WALK_NUM`) НЕ
переносились — их дефолты сломали бы боевой образ.

Приёмка в симуляции: `ltdc_point_builder_tb` PASS, `ltdc_x3_spi_hdlr_tb` PASS,
`R120M_BM2BF1X1_ltdc_tb` PASS (509 поджигов / 509 INT / 2 пакета 2006 Б,
эхо-1 44510 мм, эхо-2 89937 мм) — цифра в цифру как на базовом коммите.

ВАЖНО про класс доказательства: модель `ltdc_x3_model.sv` разрешение ВЦП не
воспроизводит, `HIGHRES` для неё — просто бит в CFG0. Симуляция доказывает
только то, что тракт не сломан. Выигрыш по СКО — исключительно железный факт
из таблицы выше.

Цена по сборке измерена РАЗДЕЛЕНИЕМ вклада, а не оценена на глаз — три сборки
Gowin на одной машине:

| Сборка | UserCode | Fmax | Logic | violated |
|---|---|---|---|---|
| база `09372a0e` | `0x00006E3E` | 62.504 МГц | 12512 | 0/0 |
| база + ТОЛЬКО `HIGHRES=2` | `0x0000CEE6` | 55.680 МГц | 12572 | 0/0 |
| полный перенос | `0x0000CEE6` | 55.680 МГц | 12572 | 0/0 |

Два вывода:

1. **PnR Gowin здесь детерминирован.** База пересобралась в тот же UserCode
   `0x6E3E` и ту же Fmax 62.504, что записаны в разделе про табличную
   компенсацию. Поэтому расхождение Fmax можно приписывать правке, а не
   разбросу инструмента — но только после такой пересборки базы.
2. **`HIGHRES=2` стоит +60 ячеек логики и −6.8 МГц запаса Fmax.**
   Ограничение 50 МГц выполняется, худший setup-слак +2.040 нс, hold +0.
   Критический путь и до, и после лежит в
   `obj_encoder_processing/obj_angle_calculator/.../ref_encoder_v4` — к тракту
   LTDC отношения не имеет, то есть НОВОГО критического пути не появилось,
   сместилась расстановка существующего. Почему один лишний единичный бит в
   константе CFG0 тянет 60 ячеек — ГИПОТЕЗА (иная упаковка массива конфигурации),
   не измерено.

Полный перенос дал БИТ В БИТ тот же образ, что и одиночный `HIGHRES=2`. Значит
параметризация `lidar_conductor` (`FIRE_PAUSE_S`/`PREP_PAUSE_S`, `parameter real`
с прежними значениями) netlist-нейтральна: Gowin сворачивает вещественную
арифметику параметра полностью. Проверять это подозрение всё равно надо было
сборкой — предположение «`parameter real` дорог» оказалось неверным.

### Железная сессия 03.08.2026: HIGHRES=2 в боевом образе даёт ПЛОХОЕ СКО

Залит `R120M_BM2BF1X1.fs`, UserCode `0x0000CEE6`, SHA-256 `.bin`
`e586533f...1df22a`, коммит `b9b1b3ef` (голова `7e1a685f` даёт тот же образ),
плата R120M.BF2 / BM2BF1X1, топ `R120M_BM2BF1X1`. Результат от пользователя:
СКО **очень плохое**. Числа и объём выборки на момент записи не сняты — это
пользовательская функциональная оценка, НЕ измерение; дополнить обязательно.

Стенд на этом же `HIGHRES=2` давал 48.6 пс, то есть боевой образ ведёт себя
иначе. Разница конфигураций известна и задокументирована выше:

- стендовые образы мерились с ВЫКЛЮЧЕННОЙ walk-компенсацией (48.6 пс) либо с
  ЛИНЕЙНОЙ поправкой (41.6 пс, `0x00004066`);
- боевой образ идёт с ТАБЛИЧНОЙ компенсацией (`LTDC_WALK_TABLE_EN=1`).

**Ведущая гипотеза (НЕ проверена):** табличная компенсация усиливает дрожание
ширины импульса в TOF. Поправка берётся по PW, а наклон матрицы ~0.29 мм/пс
(≈1.9 пс TOF на пс PW), причём значения `comp_matrix_64x64_ec12185ps.hex` до сих
пор сняты на TDC7201 и под LTDC не калиброваны. Ровно по этой причине таблицу
и выключали на замерах СКО. Если гипотеза верна, `HIGHRES=2` тут ни при чём:
он сузил бин, а шум пришёл из таблицы.

**Разделяющий эксперимент (одна переменная за раз), в порядке убывания
информативности:**

1. тот же коммит, `LTDC_WALK_TABLE_EN=0` — отделяет вклад таблицы от `HIGHRES`;
2. тот же коммит, `LTDC_HIGHRES=0` при включённой таблице — проверяет обратное;
3. если виновата таблица — калибровать наклон заново на LTDC (мишени разной
   отражательности на фиксированной дистанции, затем несколько дистанций).

Мерить `msop_sigma.py` при ОСТАНОВЛЕННОМ моторе, два прогона на точку: разброс
между прогонами ~2.5 пс, без повтора разницу меньше ~3 пс от шума не отличить.

### Инструменты замера

`docs/skills/fpga-dev/scripts/`:

- `msop_sigma.py` — СКО единичного измерения из потока MSOP TCP. Печатает
  обычную И робастную (медиана/MAD) оценку, число различимых мод гистограммы и
  шаг между ними. Именно расхождение обычной и робастной оценки, а также шаг мод
  и показали, что разброс — дискретность кодов, а не белый шум. Мотор при замере
  должен СТОЯТЬ. Ключ `--tag` дописывает строку в `sigma_log.tsv`.
- `msop_hist.py` — гистограмма дистанций одного прогона.
- `msop_sweep_sigma.py` — серия замеров без перепрошивки.
- `plot_runs.py` — сводный график по накопленным прогонам.
- `sweep_step.sh` — один шаг перебора: сборка -> заливка -> два замера. Два
  замера на точку обязательны: разброс МЕЖДУ прогонами около 2.5 пс, без повтора
  разницу меньше ~3 пс от шума не отличить.
- `flash_and_measure.sh` — заливка образа и сразу замер. **ШЬЁТ ЖЕЛЕЗО**,
  запускать только по явному решению. Ждёт подъёма блока не по таймеру, а по
  факту открытия порта данных 50100: фиксированной паузы не хватало.

### ANALOG_CFG5 (0x2F, Table 42) — раскладка бит

```
[7] CMOS_ENA_STOP2  [6] CMOS_ENA_STOP1  [5] CMOS_ENA_START
[4] LVDS_ENA_STOP2  [3] LVDS_ENA_STOP1  [2] LVDS_ENA_START
[1] OSC_ENA         [0] IREF_ENA (опора LVDS-приёмников)
```

Боевое значение `0x1F` — всё LVDS. `CMOS_ENA_START` уже ломал чип (START не
регистрировался, сплошной `no_hit`), и теперь понятно почему: `VIH,CMOS` =
VDD33-0.4 = **2.9 В**, а LVDS-размах его не пересечёт. К тому же цепь START идёт
G14 -> R109 -> STARTP, через последовательный резистор, и при просадке уровень
до порога тем более не дойдёт. LVDS-приёмник в одноконцевом включении
переключается на 1.8 В.

Электрика для стендовых экспериментов: DC на пинах START/STOP допускается
-0.3..VDD33+0.3 В, то есть 3.3 В от ПЛИС в пределах абсолютного максимума.
Но `STOP1/2 P/N` приходят С КОМПАРАТОРОВ аналогового фронтенда — подача прямо
на пин даёт два драйвера на одну линию, выход компаратора надо отвязывать.

## Заливка из CLI ПОЧИНЕНА: дефект lconf (30.07.2026)

ВАЖНО: раздел «Заливка FPGA в R120M через lconf CLI» выше описывает обход через
`--reset-before-flash`. На блоке 192.168.2.240 он НЕ работает: сброс уходит и
корректно подтверждается, но блок не перезагружается (порт данных 50100 не
падает ни разу), а стирание попадает в приложение и получает `UnknownCommand`.

Корень: `ConnectionManager::closeTcp()` закрывал соединение через
`QAbstractSocket::abort()`, а `abort()` ОТБРАСЫВАЕТ неотправленные данные из
буфера записи. Шаг `JmpBoot` по замыслу профиля отправляется без ожидания ответа
и сразу закрывает соединение — в CLI его байты умирали в буфере, блок оставался
в приложении, следующий шаг падал с «New step timeout». В GUI дефект не виден:
там непрерывно крутится цикл событий и запись успевает уйти.

Исправлено в `firmware_loader`, ветка `fix/cli-tcp-jmpboot`, коммит `f6de231`;
указатель подмодуля в lconf — `f582291`. Не запушено. Правки:

- `closeTcp()`: flush + `waitForBytesWritten` + `disconnectFromHost`, потом `abort`;
- `onReconnectPoll()`: ожидание «порт пропал -> появился» было реализовано ТОЛЬКО
  для serial, TCP-ветка переподключалась мгновенно -> добавлена пауза 3.5 с
  (по захвату блок недоступен ~2.5 с);
- `beginReconnectSequence()`: флаги ожидания были зашиты константами.

Ключи `reconnectWaitDisappear`/`reconnectWaitAppear` в JSON-профиле МЕРТВЫ — в
`ProtocolStepDef` таких полей нет, парсер их не читает.

Рабочая команда (проверена на 192.168.2.240):

```powershell
C:\workspace\lidar\lconf\bin\Release\lconf.exe --cli --file <образ.bin> `
  --channel tcp --host 192.168.2.240 --port 50102 `
  --no-reset-before-flash --profile <profile_gui.json> `
  --erase-timeout 15000 --reply-timeout 2000
```

`--no-reset-before-flash` ОБЯЗАТЕЛЕН: со сбросом lconf отключает шаг `JmpBoot`
и сразу шлёт код 55 работающему приложению. Профиль нужен пятишаговый
(`JmpBoot` без ответа -> `JmpBoot` с ответом -> Begin -> Data -> End): файл
`protocol_profile.json` на диске содержит только 4 шага и перекрывает
встроенный в код правильный вариант.

Заливать надо `.bin` (907418 Б), а не `.fs` (7264087 Б — ASCII-битстрим): на
`.fs` заливка падает на стирании с `Ошибка: WrongConfig`.

Протокол загрузчика, расшифрован по логам GUI:
`12 34 | тип | длина/256 | счётчик LE16 | 00 00 | команда | данные | 55 AA | КС`

- тип 01 запрос, 02 ответ, 03 промежуточный статус;
- третий байт — длина данных в единицах по 256 (07=1792, 04=1024, 00=нет);
- КС — простая сумма всех предыдущих байт, 16 бит LE;
- статусы: 00 готово, 09 идёт стирание/запись;
- образ: 506 блоков по 1792 Б + последний 1024 Б = 907776 Б; исходный `.bin`
  907418 Б оборачивается вендорским `FirmwarePackage::buildFpgaOnly()`.

Диагностика — только ПАССИВНЫМ захватом. Активный опрос доступности порта 50102
раз в 250 мс занимает порт и не даёт шить ни из CLI, ни из GUI.

```powershell
& 'C:\Program Files\Wireshark\tshark.exe' -i 6 -a duration:300 `
  -f "host 192.168.2.240 and tcp port 50102" -T fields `
  -e frame.time_relative -e ip.src -e tcp.dstport -e tcp.flags.str `
  -e tcp.len -e data.data -E separator=";"
```

(интерфейс 6 = `Ethernet`, 192.168.2.145; tshark буферизует вывод и дописывает
файл в конце захвата.)

## Пороги компараторов THR_CTRL — H14/J14 (R120M.BM2BF1X1)

Переключатель чувствительности приёмного тракта (цепи THR_CTRL1/2 и
THR_CTRL3/4 на схеме, RC-фильтр + IRLML0030), по одному пину на пару каналов:

- `THR_CTRL12` = **H14** — компараторы 1/2 (чип TDC7201_12, фронт эха);
- `THR_CTRL34` = **J14** — компараторы 3/4 (чип TDC7201_34, срез эха);
- значение `0` → порог **100 мВ** (меньшая чувствительность);
- значение `1` → порог **50 мВ** (большая чувствительность).

Сейчас оба захардкожены в `1'b0` в `R120M_BM2BF1X1_brd_ifm.sv` («безопасные
уровни до появления управления») — то есть тракт работает на 100 мВ. При
заведении управления помнить: пороги фронта и среза независимы, а
walk-компенсация калибруется при конкретном пороге — смена порога сдвигает и
срабатывание фронта, и ширину импульса.

Команда SENSITIVITY (05.08.2026): регистр `1272` командного SPI (байт 0, биты
[1:0] -> THR_CTRL12/34), lconf `--set-sensitivity <0..3|low|high>` через опкод
`0x56`. ПЛИС-ветки: TDC7201 `1d9ed15f`, BF2 `b68a705c`; lconf `0533d6c` (dev).
МК пока не транслирует опкод 0x56 в регистр 1272 — команда уходит в таймаут
ACK; после заведения на МК проверить walk-таблицы: они калиброваны под порог.

## R120M.BF2MF6FP1X5 — HWOK (05.08.2026)

Пользователь подтвердил на LTDC-плате: картинка при вращении строится.

- Выпуск: `R120M.BF2MF6FP1X5`, статус `HWOK` (шара переименована).
- Протестированный коммит: `4d17ab67df30` (ветка `R120M.BF2`).
- Плата: LTDC-стенд `192.168.2.206` (MAC 00:80:E1:07:00:11), плата
  R120M.BM2BF1X1, топ `R120M_BM2BF1X1_brd_ifm` (LTDC-тракт).
- Отпечаток: Gowin UserCode `0x0000AA2D`; SHA-256 `.bin` `db960331c8c9…`,
  `.fs` `c91357243351…`. Setup/Hold violated = 0.
- Содержимое: фикс обрыва энкодера (4d17ab67 — сырой канал обычными
  портами, Gowin молча рвал интерфейс-порт интерфейса; регресс «окружности
  постоянного радиуса» после 283229b7) поверх фиксов линии: выводимая RAM
  тела (подмена байта), рукопожатие занятости, SPI-мастер, бюджет стоящего
  мотора, регистр SENSITIVITY (LTDC ноги не использует).
- Свидетельства: (1) числовое моё — до фикса error=1/пакеты stopped-246 при
  крутящемся зеркале, после — 100/100 кадров error=0 с живыми данными
  (35646 точек, d1 625..5563 мм); (2) подтверждение пользователем.
- Регресс X4 (`75e670a9`, «круги») локализован бисекцией по маркеру
  «Input ENCODER is unused»: чист на 9f63134f, сломан с 283229b7/0ce6f010.


## Зеркальная угловая компенсация: знак и потерянные фиксы BF1→BF2 (06.08.2026)

Таблица «угловых компенсаций» в lconf (`drive_compensation_dialog.cpp`) — это
`mirror_calib_lut` в ПЛИС: 17 узлов φ (sel=5) + Δ(mirror, node) 4×17 (sel=6)
через `interface_comp_tbl_wr`; применяется в `shot_scheduler` через
`mirror_calib_interp` (линейная интерполяция, clamp на краях).

**Конвенция знака (единственно правильная, подтверждена железом):**
`φ_raw_target = φ_grid + Δ` — положительная Δ ЗАДЕРЖИВАЕТ выстрел по сырому
углу энкодера, точка на стене уезжает ПО направлению вращения. Значения
беззнаковые 0..65535 мград (GUI отрицательных не даёт; интерполяция и
планировщик беззнаковые — отрицательные Δ трактом НЕ поддерживаются). Узел,
чья цель `φ_grid + Δ ≥ 180000`, принадлежит следующей грани и пропускается.

**История регресса (второй случай класса «фикс остался на соседней линии»,
первый — сдвиг сектора ac8215db):**

- 24.06 `988b39da` ввёл минус-конвенцию (`φ_grid − Δ`) на m20k_BDSP2 — она
  уехала в предков BF2;
- 15.07 `821af98b` развернул знак обратно на плюс, но лёг на линию
  BF1/R120LD и в BF2 не попал; в ТОТ ЖЕ день на BF2-линии `c402ea4d`
  задокументировал минус-физику убедительным комментарием — комментарий
  противоречил железу;
- 15.07 `8383abd6` (переполнение интерполяции, тоже только BF1): 24-битное
  промежуточное произведение (span φ × ΔΔ) переполняется уже на профиле
  0→880→0 мград при сегменте 10000; лечение INTERP_W = PHI_W+DELTA_W+1;
- 06.08 на железе: Δ двигала точку вправо (против вращения) → порт обоих
  фиксов в BF2-семейство: `3eb32703` (знак) + `bcadd690` (переполнение) на
  `R120M.BF2_TDC7201`, ModelSim ALL PASS оба ТБ (оракул направления в
  `shot_scheduler_tb`: положительная Δ обязана задерживать raw target).

**Уроки:**

- «Проблема, которая уже решалась» → сначала `git log --all --grep`, затем
  `git merge-base --is-ancestor <fix> HEAD` — найденный фикс может не входить
  в текущую линию. Ветвление BF1/BF2 уже дважды теряло фиксы одного дня.
- Убедительный комментарий в коде — не свидетельство: c402ea4d подробно
  «обосновал» неверный знак. Верить только железу/направленному оракулу в ТБ.
- Дефолтная `delta_4x17.hex` ненулевая: значения, прошитые под минус-
  конвенцию, после разворота двигают точки в противоположную сторону —
  таблицы подлежат перекалибровке на стенде.
- `INIT_FILE_*` в `encoder_processing.sv` — абсолютные пути на
  `C:/workspace/verilog`: сборка из воркри `bf2-*` берёт дефолтные hex из
  ОСНОВНОГО дерева (на 06.08 файлы идентичны, но при расхождении веток это
  выстрелит).

## Сектор обзора: границы включены — [start; end] (06.08.2026)

По требованию пользователя интервал сектора закрытый: узел ровно на границе
принадлежит сектору (сектор 20–160 содержит и 20, и 160). Раньше правая
граница была строгой ДВАЖДЫ: гейт `angle_in_sector` (encoder_processing) и
сетка планировщика (`frame_exhausted`). При разрешении, не попадающем в
границу, последним стреляет последний узел ПЕРЕД границей. Физический конец
кадра 180000 остаётся строгим — узел принадлежит следующей грани.
start == end по-прежнему пустой сектор (защита от неинициализированных
регистров). Коммиты: b5b289ab (боевая TDC7201), 62e412fe (cmpdiag),
7872ab88 (R120M.BF2). ТБ: shot_scheduler_tb — секторные кейсы (последний
узел 160000 при границе в сетке; 140000 при границе 150000 вне сетки);
encoder_processing_sector_tb переведён на res=200, чтобы сетка попадала
ровно в границу, ассерт нестрогий.

## Сетка зеркальной калибровки: 27 узлов 25..155° шаг 5° (06.08.2026)

Было 17 узлов (нерегулярная ось 20..160 в phi_17.hex — комментарий файла
врал про «10..170 шаг 10»). Стало: N_NODES=27, равномерно 25000..155000
мград. Файлы дефолтов: `phi_27.hex` (ось), `delta_4x27.hex` (нули — старые
значения сняты под неверную минус-конвенцию и невалидны). Адресация записи
от МК не изменилась по формату: sel=5 addr=node (0..26), sel=6
addr=mirror*27+node (0..107), addr 16-битный. ПЛИС: 97777075 (боевая
TDC7201) / 15dca5d5 (cmpdiag) / a3efecab (R120M.BF2). Сторона ПО (lconf) —
зона ДРУГОГО программиста: моя правка на 27 узлов откачена по указанию
пользователя. Контракт для ПО: 27 строк 25..155°/5°; sel=5 addr=node
(0..26), sel=6 addr=mirror*27+node (0..107); блобы sel=5 word_size=3 /
sel=6 word_size=2, fpga_address=1208. ВЕРСИОННАЯ СВЯЗКА: lconf на 17 узлов
с новой ПЛИС (27) кладёт Δ зеркал 1..3 по чужим адресам (stride mismatch) —
прошивки X4/X8 использовать только с обновлённым ПО. Регрессия переполнения интерполяции пересчитана под
сегмент 5000 (пик 4000); run интерп-ТБ 20→100 мкс — 27 узлам 20 не хватало.

## Угловое упреждение: вердикт железа — 1:1, τ пер-плата (07.08.2026)

Загадка «двойки» закрыта решающим экспериментом на LTDC-изделии
`192.168.2.241` (MAC 00:80:E1:3B:00:10): диаг-прошивка с N_τ=3300 (66 мкс)
дала rot(40 vs 80 Гц) = 0.00° (минимум MSE ровно в нуле, 792 бина).
- Упреждение Δφ = 7200·N_τ/N_ребра работает ТОЧНО 1:1; удвоение свёрткой
  учтено; никакой систематической «двойки» в реализации нет.
- Транспортная задержка τ — свойство ЭКЗЕМПЛЯРА: .241 ≈ 66 мкс,
  .231 (TDC7201-стенд) ≈ 0..4 мкс, .206 ≈ 33 мкс (исходная заметка).
  Разброс десятки мкс → пер-платная калибровка N_τ регистром 1304
  ОБЯЗАТЕЛЬНА (методика: два профиля на разных скоростях, N_τ доводится
  до нулевого поворота; скрипт scratchpad rot_check.py).
- Прошивка .241: `R120M.BF2MF6FP1X7...tau3300diag...uc-00004555.HWOK`
  (сборка с временным дефолтом 3300 из-за отсутствия поддержки 1304 в МК;
  штатный дефолт ветки остался 1650).

Канал управления лидаром (уточнено 07.08.2026 пользователем и проверено):
- ВСЕ команды идут по TCP 50101 — и запись регистров ПЛИС 0x44, и скорость
  0x10. Проверка: кадр 0x10 с float 160.0 по TCP вернул эхо `00 00 20 43`
  (=160.0), частота кадров пошла 50 → 64 → 86.
- UDP-канал НЕ применяет команды, хотя `lconf --channel udp` печатает
  `[ok] ... ACK`: в ответе приходит ПРЕЖНЕЕ значение — это эхо, а не
  подтверждение применения. Раннее наблюдение «по UDP скорость
  применяется» ОШИБОЧНО (совпало с инерцией мотора), как и вывод
  «привод не разгоняется» — разгон не шёл из-за неверного канала.
- `DEBUG_PACKET 0x44` = прямая запись произвольного адреса ПЛИС
  (как comp-таблицы @1208) — регистры 1304/1288 доступны с ПК без
  поддержки МК (но слетают при ребуте: МК их не восстанавливает).
- Единицы 0x47 (ANG_RES) на МК 2253 отличаются: посланные 0.45° дали
  res=80 мград в шапке — сверять фактический res только по потоку.

## LTDC: runtime-запись walk-таблиц включена и подтверждена — HWOK (07.08.2026)

Выпуск `R120M.BF2MF6FP1X8` (git `ec2442b26c93`, UserCode `0x0000142A`),
изделие `192.168.2.241` (MAC 00:80:E1:3B:00:10). Setup/Hold = 0.
- Корень «таблицы не применяются»: запись 1208 доходила до ПЛИС, но walk-
  applier LTDC питался заглушкой en=0 (диагностическое отключение 30.07,
  72baec23). Протянут настоящий if_tbl_wr: lidar_measurement_pipeline →
  ltdc_processing → ltdc_point_builder (коммит ec2442b2).
- Доказательство ЧИСЛОМ (дифференциальный тест, независим от init-значений):
  матрица комп. 1000 пс → 2000 пс сдвинула медианы d1 на −149 мм
  (q25/q75 −151/−140) при предсказании −150 мм. Поправка ВЫЧИТАЕТСЯ из TOF.
- Методика теста: оси 64 узла (width шаг 100 пс, tof шаг 10000 пс),
  константная матрица, два среза, разность медиан по бинам угла
  (scratchpad lidar_cmd.py + rot_check.py).

Канал управления (карта, проверено на МК 2253):
- 0x10 MOTOR_TARGET_SPEED (float Гц) — работает по UDP 50101;
- 0x44 DEBUG_PACKET (запись адресов ПЛИС: 1208 таблицы, 1224 сектор,
  1304 упреждение...) — ТОЛЬКО по TCP 50101; по UDP молча игнорируется.
- ЛОВУШКА: 4224 команды подряд без пауз клинят MSOP-поток (порты живы,
  данных нет; лечится ребутом). Рабочий темп: пауза ~12 мс/кадр с
  вычиткой ответов + 0.3 с каждые 16 строк матрицы (заливка ~66 с).
- После ребута RAM-значения (таблицы, 1304) слетают: МК их не
  восстанавливает. Для .241 после каждого ребута: 0x44 → 1304 = 3300.

## Командный порт лидара «занят»: сначала посмотреть, КТО держит (07.08.2026)

W5500 обслуживает ОДНОГО клиента на порт. Если 50101 (или 50100) отвечает
`ConnectionRefused`, а лидар при этом пингуется — соединение уже кем-то
занято, и команды до устройства НЕ доходят (скорость не меняется, таблицы
не пишутся), хотя со стороны клиента это выглядит просто как «нет связи».

Диагностика ДО любых выводов и действий:

```powershell
netstat -ano | Select-String "192.168.2.241:50101"      # есть ESTABLISHED?
Get-Process -Id <PID> | Select Id,ProcessName,StartTime,MainWindowTitle,Path
```

Владельцем может быть:
- **GUI пользователя** (`lconf` с непустым `MainWindowTitle`) — НЕ трогать,
  просить пользователя отключиться от лидара или менять режим самому;
- **зависшая собственная CLI-сессия** (`lconf` без окна, python-скрипт) —
  её можно снимать, это свой мусор.

Ошибка 07.08.2026: увидев ESTABLISHED, я объявил соединение «своим
зависшим» и собрался его убить — на деле порт держал GUI пользователя,
запущенный накануне. Проверка `MainWindowTitle`/`StartTime` заняла бы
десять секунд и сняла бы ложный вывод; убийство чужого процесса было бы
вмешательством в работу пользователя.

Профилактика для своих скриптов: закрывать сокет в `finally`, ставить
`settimeout`, не оставлять фоновые задачи с открытым соединением; после
убийства собственной команды по таймауту — проверять `netstat` и
добивать остаток, а не гадать, почему устройство «не отвечает».
Признак «данные идут, а команды нет»: 50100 open, 50101 refused.

## ДЕФЕКТ прошивки МК 2253: работа с FLASH сбрасывает настройки ПЛИС

НЕ архитектурное правило и не свойство ПЛИС — известная недоработка текущей
прошивки МК, которую обещано исправить. Здесь она записана только как
временное ограничение стенда, чтобы не искать несуществующие причины в HDL.

Механизм: SPI-FLASH общая. Чтобы прочитать/записать её, МК выключает ПЛИС,
забирает шину, работает с FLASH и возвращает шину обратно. ПЛИС поднимается
заново — с хардкодными дефолтами, а МК свои runtime-настройки в неё
повторно НЕ пишет (вот это и есть недоработка).

Пока не исправлено — учитывать в экспериментах:
- после операции с FLASH (заливка прошивки, `--flash-dump`, запись/чтение
  блобов 0x45, работа с файловой системой МК) в ПЛИС действуют дефолты:
  сектор обзора, угловое разрешение, таблицы walk и калибровки зеркал,
  чувствительность — всё, что жило в RAM;
- «картинка слетает» после работы с FLASH — это оно, а не сбой тракта;
- таблицы, залитые через 0x44 в RAM, исчезают при следующем обращении к
  FLASH: порядок «сначала FLASH, потом настройки»;
- пара замеров «до/после», разделённая flash-операцией, сравнивает разные
  конфигурации и недействительна.

## Пропускная способность тракта выстрелов — ЗАМЕРЕНО (07.08.2026)

Изделие `192.168.2.241` (LTDC), прошивка с упреждением 1700. Признак
нехватки быстродействия однозначен: строб выстрела принимается движком
только в `LS_READY`, иначе узел ТЕРЯЕТСЯ (не откладывается) — значит точек
в кадре станет меньше, чем узлов сетки.

Частоту выстрелов задают УГЛОВОЕ РАЗРЕШЕНИЕ и СКОРОСТЬ, сектор на неё не
влияет (уточнение пользователя): между соседними узлами проходит res/ω.
Считать надо МГНОВЕННУЮ частоту — именно её отрабатывает движок:

    ω_луча [град/с] = 180 · F_кадров
    f_мгн [Гц]      = 180 · F / res
    f_средн         = (сектор/180) · f_мгн   — только нагрузка на канал

| режим | f мгновенная | интервал | точек/кадр : сетка | потери |
|---|---|---|---|---|
| 40 Гц / 0.90° | 8.0 кГц | 125 мкс | 155 : 155 | нет |
| 160 Гц / 0.36° | 80.0 кГц | 12.5 мкс | 389 : 389 | нет |
| 100 Гц / 0.20° | 90.0 кГц | 11.1 мкс | 700 : 700 | нет |
| 128 Гц / 0.20° | **115.2 кГц** | **8.7 мкс** | 702 : 700 | нет |

Проверенный минимум способности тракта — **115 кГц** (8.7 мкс между
выстрелами), это НАБЛЮДАВШИЙСЯ максимум, а не измеренный предел. Все
пресеты ПО (самый тяжёлый — 200 Гц / 0.40° = 90 кГц мгновенных) проходят
с запасом.

Расчётный «потолок ~75 кГц» по таймингам автомата был пессимистичным:
прерывание LTDC приходит заметно раньше `INT_TIMEOUT_CLKS`, петля короче.

`FIRE_PAUSE_S = 40 мкс` в `lidar_conductor` к рабочему режиму отношения не
имеет — она только для `motor_stopped` (выстрелы без энкодера).

### Свип скорости до 180 Гц и предел по шагу сетки (07.08.2026)

Скорость поднимали при res=0.20°, выше 180 Гц не идём (требование
заказчика). Потерь нет на всём диапазоне; мотор держит заданную частоту:

| режим | кадр/с | точек : узлов | выстрелов | мгновенных |
|---|---|---|---|---|
| 140 Гц / 0.20° | 140.0 | 700 : 700 | 98.0 кГц | 126 кГц |
| 160 Гц / 0.20° | 160.2 | 702 : 700 | 112.4 кГц | 144 кГц |
| 180 Гц / 0.20° | 180.0 | 702 : 700 | 126.3 кГц | 162 кГц |

Уменьшение шага при 180 Гц ломает тракт НЕМОНОТОННО (механизм не найден):

| режим | кадр/с | точек : узлов | доля | выстрелов |
|---|---|---|---|---|
| 180 Гц / 0.15° | 166..171 | 193..215 : 933 | 21..23 % | 32..37 кГц |
| 180 Гц / 0.10° | 54..62 | 541..617 : 1400 | 39..44 % | 31..37 кГц |

При 0.10° падает и частота КАДРОВ (до 54..62 вместо 180) — деградирует не
только выдача точек. Оба режима упираются в ~35 кГц, хотя на 0.20° шло
126 кГц. Похоже на ограничение конвейера пакетизации или нештатность самих
значений шага (0.15/0.10 нет в пресетах ПО), а не на нехватку времени
измерения. НЕ РАССЛЕДОВАНО.

Вывод: рабочий диапазон — res >= 0.20° при кадровой частоте до 180 Гц.

## Релизные прошивки обеих линий — HWOK (07.08.2026)

Папка `…\Тестовые прошивки\release` — актуальные боевые образы, проверенные
на железе. Всё остальное в линиях считать историей.

**LTDC `R120M.BF2MF6FP1X9`** — git `720e009256f2`, UserCode `0x000071CE`,
Setup/Hold = 0. Проверено на изделии `192.168.2.241`: поток 160 Гц,
389 из 389 точек сетки; компенсация поворота работает — сдвиг картинки
40 против 160 Гц упал до −0.13°/0.00° по рабочим граням (медиана −0.065°)
против +0.905° без компенсации.

**TDC7201 `R120M.BF2_TDC7201.MF6FP4X12`** — git `0eb6d5a7c3ef`,
UserCode `0x00009C2F`, Setup/Hold = 0. Подтверждена пользователем на железе.

Состав обеих: живое угловое упреждение (`LEAD_TAU_TICKS = 1700`, хардкод —
явный int, прямой делитель, период ребра портом), дальность до 500 м (сняты
все четыре потолка, включая 131 м), сектор `[start; end]`, 27 узлов
калибровки зеркал, знак Δ по вращению, фильтр интенсивности 0x57 (1288).
Для LTDC дополнительно: runtime-запись walk-таблиц (протяжка if_tbl_wr).

## Ручное размещение есть, ручной трассировки нет — ЗАМЕРЕНО (24.08.2026)

Проверено на `gw_sh.exe` 1.9.8.07, `GW2A-LV18PG256C8/I7`, тестовый проект из
16 `ALU` (сумматор) в `C:\Users\User\AppData\Local\Temp\gowin_loc_test`.

**Размещение прижимается поимённо и работает.** Без ограничений цепочка легла
в `R14–R15/C37–C39`; `GRP_LOC tdl R[5:8]C[10:12] exclusive` перенёс её в
`R5C10→R5C11→R5C12`; шестнадцать строк `INS_LOC "n21_s" R7C20[0][A];` положили
каждое звено ровно в заказанную ячейку. Все три сборки — без замечаний.
Проверять размещение по `impl/pnr/<имя>_tr_content.html`: там координаты вида
`R7C20[0][A]`. Файла с трассами не выдаёт ни один отчёт.

**Имена для `INS_LOC` — из `impl/gwsynthesis/<имя>.vg`, не из исходника.**
Синтезатор даёт `n21_s`, `n20_s`, …; порядок звеньев читается по цепям
переноса (`CIN(GND)` — начало, дальше `CIN` следующего = `COUT` предыдущего).
Имена не переживают правку исходника — держать шаблон `GROUP tdl = { "n*_s" }`
или генерировать `.cst` скриптом из свежего `.vg`.

**Геометрия цепи переноса GW2A (UG288 + замер):** перенос идёт ВПРАВО ПО
СТРОКЕ, от CFU к соседнему CFU; внутри CFU занимает только `CLS0…CLS2` (по два
`ALU`), шесть звеньев на CFU, `CLS3` не участвует. Ячейки для линии задержки
заказывать подряд по столбцам ОДНОЙ строки, а не по строкам одного столбца.

**PnR у Gowin ВОСПРОИЗВОДИМ.** Повторная сборка того же дерева с тем же `.cst`
дала побитово тот же `.bin` (SHA-256 `916ee951…` дважды). Это подтверждает
правило сверки `.bin` как инструмент доказательства переносов.

**Трассировкой поимённо управлять нечем.** В `.cst` (SUG935-1.6.1E) ровно
десять видов ограничений, и единственное про трассу — `CLOCK_LOC "цепь"
BUFG[0-7]|BUFG|BUFS|LOCAL_CLOCK = CLK|CE|SR|LOGIC`. Остальное — глобальные
ручки на весь проект: `-route_option`, `-route_maxfan`, `-clock_route_order`,
`-correct_hold_violation`, `-timing_driven`.

**Ловушка `CLOCK_LOC`: имя ПОРТА не принимается.** `CLOCK_LOC "clk" BUFG[3] =
CLK;` → `ERROR (CT1020): 'clk' is 'input', port does not support CLOCK_LOC
constraint`. Вешать на внутреннюю цепь — выход входного буфера (`clk_d` в
`.vg`), в таком виде проходит.

**`NET_LOC` на обычной цепи не отвергается и МОЛЧА меняет размещение.**
По руководству у `NET_LOC` разрешены либо `V_JTAGSELN`/`V_RECONFIGN`/
`V_USERFLASHEN` (SUG935), либо клоковые значения наравне с `CLOCK_LOC` (SUG113),
но не координата ячейки. Тем не менее `NET_LOC "n21_2" R7C20;` прошёл без замечаний и утянул всю
логику в `R6–R7/C19–C22`, а `NET_LOC "n21_2" R12C30;` — в `R11–R12/C29–C31`
(причинность проверена переносом цели). Поведение недокументированное, без
проверки законности: в боевой `.cst` не тащить. Общий вывод тот же, что и с
потерянным вторым `.cst`: чистый журнал сборки НИЧЕГО не доказывает.

**Инкрементального PnR на этом кристалле нет.** `set_option -inc_place` и
`-inc_pnr` локальный `gw_sh` 1.9.8.07 отвергает как `unknown option`; в поздних
редакциях среды они ограничены семействами Arora III и Arora V, куда GW2A-18
не входит. Заморозить результат можно только back-annotate размещения в `.cst`.

**Если нужна предсказуемая ЗАДЕРЖКА, а не трасса** (линия задержки ВЦП):
позиция Gowin (`WP1155-1.0E`) — уходить в выделенные задержки блоков
ввода-вывода. Для GW2A это `IODELAY`/`IODELAYA` (`C_STATIC_DLY = 0…127`, шаг
в модели `simlib/gw2a/prim_sim.v` — 25 пс, диапазон ~3,2 нс, реальный шаг
мерить на железе), `DLLDLY`, `IEM`. Полный разбор — в заметке ваута
«Ручное размещение и трассировка в Gowin — что можно задать руками, а что нет».

## Открытый маршрут читает НАШИ образы — ЗАМЕРЕНО (24.08.2026)

На ПК стоит `C:\workspace\tools\oss-cad-suite` (сборка 08.08.2026): Yosys 0.68+40,
`nextpnr-himbaechel` 0.10-122, apycula 0.33.dev20 с базой `GW2A-18C.msgpack.xz`.
Старая копия `C:\workspace\oss-cad-suite` (2023) для GW2A НЕ годится — `nextpnr-gowin`
падает на `Failed to load chipdb 'gowin/chipdb-GW2A-18C.bin'`, скомпилированной базы
в сборке нет. Брать всегда `tools\`.

**Практическая польза прямо сейчас — `gowin_unpack` разбирает ВЕНДОРСКИЙ `.fs`:**

```bash
export PATH="/c/workspace/tools/oss-cad-suite/bin:/c/workspace/tools/oss-cad-suite/lib:$PATH"
gowin_unpack.exe -d GW2A-18C -o out.v LDR_20K.fs
grep -E "^ALU R[0-9]+C[0-9]+" out.v | grep -oE "R[0-9]+C[0-9]+" | sort | uniq -c
```

Ячейки в выводе именуются координатами (`R13C38_LUT4_3`), поэтому образ можно
проверить НЕЗАВИСИМО от вендорских отчётов: чем занят кристалл, где стоит блок,
сработало ли ограничение размещения. Этим сегодня подтверждено, что `INS_LOC`
реально двигает цепочку `ALU` (базовый образ `R15C36…R15C39`, с ограничением —
`R7C19…R7C22`). Полезно и при разборе «что залито в прибор»: образ из флеши
читается тем же способом.

**Собрать образ открытым маршрутом тоже получается** (проверено на тестовом
проекте, не на продукте): `yosys -p "read_verilog top.v; synth_gowin -json top.json"`,
затем `nextpnr-himbaechel --json top.json --write pnr.json --device GW2A-LV18PG256C8/I7
--vopt cst=<файл>.cst --vopt family=GW2A-18C`, затем `gowin_pack -d GW2A-18C -o out.fs pnr.json`.
Размер вышел 4 620 140 Б против 4 620 631 Б у вендорского. Для продукта не
применять: временной анализ не вендорский, покрытие примитивов неполное,
SystemVerilog фронтенд Yosys требует `read_slang` или sv2v.

## Линии задержки на GW2A: ЗАМЕРЫ и ловушка синтеза (24.08.2026)

Числа взяты из `.sdf` временной модели Gowin (`set_option -gen_sdf 1`), кристалл
GW2A-18C, среда 1.9.8.07. Это модель поставщика, НЕ железо.

| Механизм | Шаг | Ход | Углы |
|---|---|---|---|
| цепь переноса, `IOPATH CIN COUT` | 28 пс номинал | 100 звеньев = 2,8 нс | 21 пс быстрый / 35 пс медленный |
| `IODELAY`, `C_STATIC_DLY` 0..127 | 18 пс, строго линейно | 0,300 → 2,586 нс | модель одинакова во всех углах |

Связь между звеньями цепи переноса стоит РОВНО НОЛЬ
(`INTERCONNECT ...COUT ...CIN (0.000:0.000:0.000)`) — перенос идёт по жёсткой
связи. Зато вход в цепочку по обычной трассе дорог: вывод → первое звено дал
0,957/1,269/1,581 нс.

**ЛОВУШКА, из-за которой линии нет в кремнии.** GowinSynthesis сворачивает
инферированный широкий сумматор целиком, `syn_keep` НЕ спасает: «все единицы
плюс hit» вычисляется на бумаге, `sum` вырождается в размноженный `~hit`.
Проверено на модуле проекта `tdc_fine_line.sv` (`NTAP = 100`): отчёт PnR даёт
**`135 LUT, 0 ALU`** при сотне уцелевших триггеров.

Рабочая запись — прямое инстанцирование примитивов (даёт `102 ALU`):

```verilog
(* syn_keep = 1 *) ALU #(.ALU_MODE(0)) obj_alu (
    .SUM(sum[i]), .COUT(carry[i+1]),
    .I0(1'b1), .I1(1'b0), .I3(1'b0), .CIN(carry[i]));
```

В режиме 0 при `I0=1, I1=0` звено вырождается в повторитель переноса
(`COUT = CIN`), а `SUM = ~CIN` даёт отвод.

**Следствие для ВЦП:** при 200 МГц (5 нс) сотня отводов покрывает лишь 2,1…3,5 нс
периода. Считать перекрытие надо по БЫСТРОМУ углу: нужно ~240 звеньев, а не 100.
Зато LSB выходит 28 пс вместо расчётных 50 пс, СКО квантования ~8 пс (~1,2 мм).

Повторить замер: `grep -A 8 'CELLTYPE "ALU"' impl/pnr/<имя>.sdf | grep "IOPATH CIN COUT"`.
