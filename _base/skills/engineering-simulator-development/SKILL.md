---
name: engineering-simulator-development
description: Design, implement, validate, package, and maintain source-faithful engineering simulators and digital twins. Use for симулятор, эмулятор, цифровой двойник, optomechanical/LiDAR/scanner/ray simulators, hardware or FPGA/firmware behavior emulation, calibration tables, fixed-point interpolation, device-protocol reconstruction, engineering GUI visualization, and reproducible Windows EXE delivery.
---

# Engineering Simulator Development

## Core Goal

Build a simulator that reproduces the observable behavior of the selected real system, not merely a plausible mathematical picture. Keep physical truth, device behavior, transmitted data, and client reconstruction distinct and traceable to authoritative sources.

## Required Reference Loading

- Read `references/source-fidelity-checklist.md` whenever the simulator must match real hardware, firmware, FPGA, a protocol, or production software.
- Also read `references/scanning-lidar-lessons.md` for scanning, ranging, mirror, ray-grid, angular-resolution, sector, or LiDAR work.
- Also read `references/windows-exe-release.md` when building or replacing a Windows executable.
- Also read `references/host-software-bench-lessons.md` when the emulator is used to reproduce a defect in the production client software without hardware: memory growth, freezes, throughput cliffs, reconnect storms.

## Repository And Workspace Boundaries

1. Resolve every project path before editing and classify it as:
   - writable simulator target;
   - read-only production software reference;
   - read-only firmware/FPGA reference;
   - read-only documentation or measurement source.
2. Treat similarly named products as separate repositories until their Git roots and remotes prove otherwise. Never merge, overwrite, or clone one product into another product's directory.
3. Keep project checkouts and builds under `C:\workspace` by default. Use the synced Obsidian vault for skills, notes, and requested reports, not as a software build workspace.
4. Record the exact branch, commit, configuration, and protocol revision used as the behavioral baseline.
5. Modify, commit, and push only the writable target repository. Preserve unrelated changes in every reference checkout.

## Source-Backed Workflow

1. **Define the observable contract.** Write acceptance criteria for inputs, outputs, timing, coordinate frames, table formats, packet reconstruction, GUI controls, and release artifact.
2. **Build an authority matrix.** Assign each behavior to its actual source of truth:
   - mechanics and optics: drawings, geometry, measurements;
   - accepted values and import/export rules: production configuration software;
   - scheduling and arithmetic: active firmware or RTL;
   - packet meaning: producer, wire format, and consumer together;
   - displayed point cloud or profile: client reconstruction code.
3. **Separate layers.** Model at least:
   - physical scene and intersections;
   - device sampling/scheduling;
   - calibration and digital arithmetic;
   - packetization and missing-data behavior;
   - client-side reconstruction;
   - visualization.
4. **Establish coordinates explicitly.** State origin, axes, positive rotation, units, zero mark, face numbering, normals, source position, and every offset. Do not use one offset to conceal a different physical translation or axis error.
5. **Port algorithms exactly.** Reproduce integer widths, signedness, intermediate truncation, wrapping or saturation, clamping, division rounding, lookup boundary selection, interpolation, and invalid-node handling. Do not substitute floating-point interpolation for a digital implementation.
6. **Expose diagnostics.** Show selected segment/table nodes, interpolated value, corrected raw coordinate, packet start, discarded samples, overflow risk, and the source revision behind the result.
7. **Design controls around the real product.** Match accepted ranges, integer-only fields, monotonicity, row counts, presets, manual overrides, import/export encoding, and interpolation between table nodes.
8. **Compare representations.** When useful, display the physical rays and what the client reconstructs side by side. Label why they differ.
9. **Validate before polishing.** Establish golden vectors and boundary tests first; then improve layout, zoom, pan, labels, and packaging.

## Fidelity Rules

- Never infer behavior from a screenshot when source code, RTL, packet captures, or executable behavior can settle it.
- Never assume the newest local branch is the production baseline; identify the deployed or explicitly selected revision.
- Never invent a gap, point, angle, or return that the protocol cannot encode.
- Treat exact table nodes, first/last nodes, overflow transitions, sign changes, and skipped samples as mandatory test cases.
- Preserve user-facing constraints independently from internal arithmetic. A GUI-valid table can still trigger an RTL overflow; report both facts.
- Keep model units explicit at every boundary. Convert once at named interfaces rather than scattering scale factors.
- Use deterministic scenario files and exported result tables so regressions can be reproduced.
- Mark approximations visibly and keep them outside the source-faithful mode.

## GUI And Interaction

- Provide both useful presets and arbitrary manual values when the real configuration permits them.
- Make dense plots inspectable: zoom under the mouse cursor, allow substantial zoom depth, pan while zoomed, and provide fit/reset controls.
- Size table columns and labels for real values and units; do not accept clipped headings as complete.
- Apply the same validation and bounds to keyboard entry, paste, import, and mouse-wheel editing.
- Keep expensive rendering responsive through decimation or separate display resolution without changing simulation results.
- Put advanced scan-space, calibration, and protocol controls on a dedicated tab or panel when mixing them into the mechanical view reduces clarity.

## Validation And Definition Of Done

Require evidence proportional to the claimed fidelity:

- unit tests for geometry, scheduling, calibration, protocol, and serialization;
- golden vectors derived independently from authoritative source behavior;
- RTL/firmware testbench comparison when digital arithmetic is involved;
- GUI smoke tests plus visual inspection at realistic window sizes;
- packaged-artifact smoke test from a neutral working directory;
- repeatable build instructions committed with the simulator;
- final repository status, remote synchronization, executable path, size, and hash.

Do not declare exact hardware equivalence while any relevant layer is still an assumption. State the verified scope and remaining unknowns.

## Delivery

- Push source, tests, configuration examples, and build instructions needed to recreate the executable.
- Do not add generated binaries to Git unless repository policy or the user explicitly requires them.
- Build a verified candidate separately from the canonical executable, then replace the canonical path after the candidate passes smoke tests.
- If the canonical simulator executable is running, close it autonomously and continue the release instead of waiting for the user. Match processes by resolved executable path, request normal window closure first, wait briefly, then terminate only the remaining exact-path processes if required. Treat the launcher and child processes of a one-file packager as one application instance.
- Scope autonomous closure to the simulator executable being replaced. Do not close unrelated editors, production tools, or engineering applications that may contain unsaved documents.

## Self-Improvement And Publishing

When simulator work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact fidelity rules, protocol pitfalls, arithmetic edge cases, validation checks, reusable examples, or release notes in this shared-base skill or a focused file under `references/`. Do not store secrets, credentials, private customer material, raw proprietary source, unpublished measurements, generated logs, or one-off project facts.

Before materially editing this skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check: fetch `origin main`, compare local `HEAD` with `origin/main`, fast-forward if local is behind and the relevant working tree is clean, and inspect dirty/ahead/diverged states before continuing.

After materially updating this skill, validate the shared base and adapters when feasible, run the learning-coverage audit, then commit and push the relevant skill changes to the owning repository by default unless the user explicitly says not to. Stage only relevant skill files and repository metadata. Split commits by semantic block when independent concerns justify it.

If publishing encounters remote changes or merge conflicts, resolve them autonomously when the intended final meaning can be determined from the files, commit history, nearby rules, and the user's instruction. Preserve compatible rules, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.
