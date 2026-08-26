---
name: jlink-mcp-runtime
description: "Use when work requires the portable SEGGER J-Link MCP plugin from the ToF-LIDAR MCU repository: probe discovery, target connection, register or memory inspection, RTT, flash operations, or J-Link GDB server handoff."
---

# J-Link MCP Runtime

This shared skill preserves a synchronized, runnable snapshot of the J-Link Codex plugin from the ToF-LIDAR MCU firmware repository. The complete plugin is under `plugin/`; resolve paths below relative to this file.

## Self-Improvement And Publishing

When J-Link runtime work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact rules about probe discovery, connection diagnostics, safe read workflows, launcher checks, portable configuration, mirror validation, or recurring failure modes in this shared-base skill or a focused reference. Do not store probe serial numbers, credentials, private firmware data, generated logs, memory dumps, or one-off target state.

Before materially changing the runtime workflow or applying a self-learning update, inspect the authoritative firmware checkout and the owning repository state. Runtime or bundled-plugin changes must be made in the authoritative source first, validated there, and then copied into this mirror; never let a mirror-only fix silently diverge. Validate and publish the relevant repository changes under each owning repository's contribution policy.

## Startup

1. Read `plugin/skills/jlink-mcp-runtime/SKILL.md` completely for the runtime's current tool workflow and safety rules.
2. If installation or dependencies are uncertain, run `python launcher.py --check` from the `plugin/` directory. This check does not connect to hardware.
3. With the `jlink` MCP server registered, inspect defaults with `get_project_debug_defaults`.
4. If the user has not specified a probe serial number, list probes with `list_jlink_devices` before connecting.
5. Use `connect_project_mcu` for the configured target and check the result with `get_connection_status`.

## Hardware Safety

Require clear user intent before any operation that changes target state or flash contents:

- `reset_target`
- `halt_cpu`
- `run_cpu`
- `write_memory`
- `write_register`
- `erase_flash`
- `program_flash`
- `start_project_jlink_gdb_server`

Read-only discovery and inspection are allowed when they are within the user's debugging request. This includes listing probes, checking status, reading target information, registers, and memory.

## Runtime Defaults

- Device: `STM32H723ZG`
- Interface: `SWD`
- Speed: `auto`
- GDB server port: `54526`
- GDB server selector: `USB`

The plugin documents environment-variable overrides in `plugin/README.md` and `plugin/AGENTS.md`. Do not assume these MCU-specific defaults for another project.

## Source And Mirror Policy

The firmware checkout is authoritative for runtime code. This Google Drive copy is a synchronized safety mirror and portable installation source, not an independent fork.

- Source on this PC: `C:\workspace\ToF-LIDAR-R\.codex\jlink-mcp-runtime`
- Mirrored runtime: `plugin/`
- Snapshot metadata: `references/source.md`

When refreshing the mirror, first update and inspect the MCU repository, then replace the entire plugin snapshot from the project source. Compare relative file lists and hashes, scan for credentials or generated logs, run `python launcher.py --check`, and validate both the shared skill and Codex adapter. Make runtime changes in the MCU repository first, then recopy them here so the two copies do not silently diverge.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
