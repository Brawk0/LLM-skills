---
name: diptrace-component-library
description: Create, restyle and verify DipTrace schematic symbols, PCB footprints and STEP models from manufacturer documentation or a user library reference. Use for FPGA/ADC pin grouping, native .elixml, KiCad footprint import and package-model reconstruction; schematic .asc audits belong to diptrace-ascii.
---

# DipTrace Component Library

Create a readable component for the exact device and package. Account for the symbol, contact mapping, footprint orientation and 3D alignment. Report missing manufacturer assets and unverified imports explicitly.

## Load only what the task needs

- Symbols: [symbols.md](references/symbols.md).
- Footprints: [footprints.md](references/footprints.md).
- STEP geometry/color: [models.md](references/models.md).
- Before substantial work: [lessons.md](references/lessons.md).
- Existing schematic connectivity/ASCII audits: use `diptrace-ascii` instead.

## Source and scope

Resolve the exact MPN, package variant and source pin-table sheet. Equal pin counts do not establish package equivalence. Verify ordering suffixes against manufacturer documentation. Prefer original CAD and documentation; mark reconstructions explicitly and keep source revisions, page/sheet references and hashes beside the deliverables.

Find existing assets and the actual user reference before generating replacements. Different copies of the same library name can contain different components. Resolve a network path when needed instead of silently using an old local library.

Use the requested CAD and the user's established vault/project. Resolve locations from local instructions or arguments. Do not store machine-specific paths, private library copies, confidential datasheets or project pin tables in this shared skill. Respect shared-PC foreground/mouse restrictions; use offline generation when possible. Never fake an inaccessible application handle or claim an unobserved GUI import succeeded.

## Build from a reference

Inspect the reference visually and inspect actual geometry/font fields. Extract physical widths, pin pitch, pin length, title positions and section grouping. XML `Units="mm"` coordinates, undocumented binary values and font scalars are different quantities. Calibrate binary interpretation against a known pitch before trusting it.

For this user's FPGA style, prefer two parts when the reference supports it: I/O banks with VCCIO in Part 1; remaining supplies/ground/NC in Part 2. Group ADC signals by channel and by inputs, clock/synchronisation, control and outputs. Do not follow physical pad order blindly.

For this user, integrated circuits use reference-designator prefix **D**. Use `D` in component properties and visible RefDes markings by default, including FPGA and ADC symbols. Apply this to future work; do not rewrite existing files the user has corrected manually unless requested.

All symbol text must be **Vector**, including headers and service annotations. Preserve the requested/reference font height, pitch and width. Fit meaningful labels rather than inflating rectangles. Include LVDS and DQ/DQS from separate pin-table columns where applicable. Shorten only agreed verbose alternatives in visible labels, retaining full data in a mapping.

## Portable helpers

- `scripts/build_symbol.py SPEC.json OUTPUT.elixml`: native vector-text XML from a reviewed explicit layout; also writes full/visible mapping and a report. Schema: [symbols.md](references/symbols.md). Symbol-only; attach the accepted footprint afterward.
- `scripts/build_footprint.py PACKAGE.json OUTPUT.kicad_mod`: BGA or QFN with explicit copper dimensions, numbering and optional paste windows. It does not infer PCB lands from physical contacts.
- `uv run --with cadquery scripts/build_step.py PACKAGE.json OUTPUT.step`: simplified colored BGA/QFN, STEP reimport and envelope validation. Inputs are physical contacts, not PCB lands.
- `python scripts/test_helpers.py`: synthetic symbol/footprint checks. Add `--step` with CadQuery available to check both model modes. All test output is temporary.

## Verification and handoff

Verify every contact, including NC and exposed pads: no duplicate/missing identifiers and one intended symbol assignment per physical contact. Preserve alphanumeric BGA names. Compare full and visible fields against the original table; inspect configuration, differential-pair, LVDS and DQS fields separately.

Check footprint coordinates, count, pitch and dimensions against the package drawing and recommended PCB layout if supplied. Record top/bottom view, corner relationships and rotation/mirroring. Check STEP by actual reimport, solid validity, envelope, seating plane, contact count, colors and pin-1 location.

File parsing, independent PDF preview, STEP reimport, actual DipTrace import, actual pattern binding and actual 3D alignment are separate evidence levels. Report which passed. Hash and preserve accepted footprint/STEP files during a symbol-only restyle. Deliver one clearly identified current file and a concise import path; retain prior versions outside the main recommendation.

## Self-Improvement And Publishing

Use `skill-learning` to retain reusable CAD-format, pin-table, visual-style, orientation and validation lessons here. Exclude credentials, private paths, raw confidential source materials, customer designs and generated logs.

Before material edits, fetch `origin main` and inspect cleanliness/divergence under the user's local repository instructions. Validate the shared base, adapters and changed scripts; commit only relevant files. Publish by the authorized route after access and full-range privacy checks. Preserve local work when access is unavailable; do not reset/rebase/merge divergence without applicable authorization.
