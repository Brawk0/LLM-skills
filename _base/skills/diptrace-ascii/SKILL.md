---
name: diptrace-ascii
description: Inspect, audit, safely edit, and validate DipTrace Schematic ASCII .asc files. Use for DipTrace ASCII netlist reconstruction, component and pin mapping, Cyrillic-to-Latin normalization, encoding-preserving edits, footprint/pad and component-height checks, datasheet-backed electrical review, BOM metadata checks, or diagnosing logical schematic errors beyond visible wire connectivity.
---

# DipTrace ASCII

## Core Goal

Treat a DipTrace ASCII schematic as both a structured netlist and an electrical design. Preserve its exact text format while reconstructing component, pin, net, package, and cache-library semantics; then verify voltages, tolerances, logic levels, timing, thermal requirements, protection, and BOM identity against authoritative datasheets.

## Required Workflow

1. **Establish scope.** Determine whether the user asked for review, diagnosis, editing, or all three. A review request authorizes read-only inspection, not electrical redesign. A requested textual normalization authorizes only those exact string edits unless the user also asks to fix the circuit.
2. **Fingerprint the source.** Record absolute path, byte length, SHA-256, encoding, BOM state, and newline style before editing. If the file changes before the write, stop rather than overwriting concurrent work.
3. **Inspect structurally.** Run `scripts/inspect_diptrace_ascii.py` before relying on screenshots or manual search. Inspect requested references and nets explicitly. For format semantics, read [references/format-map.md](references/format-map.md).
4. **Reconstruct intent.** Map every relevant net endpoint through the top-level part index and pin ordinal to the component reference, `StringNumber`, and pin name. Check the footprint pad numbers separately; symbol pins do not prove that a package pad exists.
5. **Audit electrically.** Read [references/electrical-audit-checklist.md](references/electrical-audit-checklist.md) and use primary manufacturer datasheets for every material conclusion. Check the exact orderable suffix, not merely the family name.
6. **Edit minimally.** Make only deterministic, counted replacements. Preserve encoding and newline style. Do not globally transliterate project paths, sheet titles, library paths, manufacturer part numbers, or net names unless the user explicitly requests those exact fields.
7. **Validate after editing.** Re-run the inspector, compare structural counts and connectivity against a pre-edit copy when available, rescan old/new strings, and recompute SHA-256. Open/import the result in DipTrace and run ERC when the application is available.
8. **Report by severity.** Lead with production blockers, then significant risks, lower-priority deviations, confirmed-good sections, exact edits, validation evidence, and limits of the review. Distinguish proven faults from items that require layout inspection or bench measurement.

## Inspection Commands

Use the bundled read-only inspector from the shared-base skill directory:

```powershell
python scripts/inspect_diptrace_ascii.py "D:\path\design.asc" --strict
python scripts/inspect_diptrace_ascii.py "D:\path\design.asc" --ref D2 --net GND --net "{VIN}"
python scripts/inspect_diptrace_ascii.py "D:\path\edited.asc" --compare "D:\path\before.asc" --strict
python scripts/inspect_diptrace_ascii.py "D:\path\design.asc" --json
```

The script is intentionally read-only. It reports encoding, line endings, balanced structure, top-level parts, nets, resolved endpoints, symbol pins, footprint pads, Cyrillic lines, and connectivity changes.

## Safe Editing Rules

- Prefer a byte-preserving exact-replacement script or a tool that can explicitly read and write the detected encoding. Do not let a default UTF-8 editor silently convert a Windows-1251 file.
- **Never change the file's encoding.** A Windows-1251 export must be written back as Windows-1251. DipTrace's Schematic ASCII importer decodes the file as a single-byte codepage and ignores a UTF-8 BOM, so saving as UTF-8 silently mojibakes every non-ASCII character in the document, not only the one being edited. Verified 2026-08 on a v45 export: `Ω`→`О©`, `µ`→`Вµ`, the sheet name `Лист 1`→`Р›РёСЃС‚ 1`, and Cyrillic `LibPath` values likewise; recovery required rebuilding from the pre-edit copy.
- Because a single-byte codepage that must also carry Cyrillic cannot represent `Ω`, write ohms in ASCII as `Ohm` / `kOhm` / `MOhm` in the exchange file. The `.dch` is the master, not the ASCII: if the project needs the glyph, substitute `Ohm` → `Ω` inside DipTrace after import. A CSV/ASCII export of that project will then show `?` — expected, not a defect.
- Before writing, assert that the whole result re-encodes to the source codepage with `errors='strict'`. A `UnicodeEncodeError` means a character was introduced that the format cannot carry.
- Assert the pre-edit SHA-256 immediately before writing.
- Count every source string and fail when an expected string is absent or occurs an unexpected number of times.
- Keep CRLF when the source uses CRLF and avoid adding a BOM when the source has none.
- For a value duplicated in `Components` and `CacheLib`, state whether both copies are being changed. The active placed component and the cached library copy are different scopes.
- Never infer pin identity from the visual order. Use `StringNumber` and the net endpoint's pin ordinal.
- Never identify a component by eye-scanning a long net member list — adjacent references such as `VD5`/`VD6` are trivially transposed, and a wrong reading produces a confident but false finding. Resolve every claim through `--ref` / `--net` or the net number before writing it down.
- A part block contains **two** `UserFields` blocks: the component's own, then a copy inside the embedded `Pattern`. Read the first block after `(Part`. Collapsing all `UserField` lines of a part into one dict silently keeps the footprint copy and misreports the component's supplier data.
- DipTrace re-annotates reference designators between exports. Diff two revisions by function and net membership, not by refdes.
- Never infer an exposed thermal pad from a package name. Verify an actual `Pad` entry and its electrical or internal connection.
- Keep an original hash or recoverable pre-edit copy until the edited file passes structural comparison and an application-level import check.

## Electrical Review Standard

A connectivity-only review is incomplete. At minimum, trace:

- the complete power tree and every enable, reset, pull-up, reference, and logic rail;
- nominal, minimum, maximum, absolute-maximum, tolerance, startup, and transient conditions;
- polarized parts, regulator feedback, frequency-setting parts, compensation, inductor and capacitor ranges;
- MCU alternate functions, timer break behavior, debug/boot pin conflicts, input voltage tolerance, and output-driver type;
- unused analog sections, floating inputs, open-drain pull-ups, push-pull contention, and fail-safe boot states;
- current thresholds, shunt dissipation, whether a fault signal actually disables power hardware, and the post-fault output state;
- package variant, exposed pad, pad-number mapping, thermal vias, Kelvin connections, and current-return geometry;
- exact orderable-part dimensions against mechanical limits, using maximum dimensions including tolerance rather than nominal body size;
- BOM metadata consistency among symbol, value, footprint, manufacturer, order code, and datasheet.

When only a schematic is available, explicitly leave PCB layout, creepage/clearance, copper current density, thermal spreading, EMI, and measured loop stability as unverified.

## Datasheets

Prefer manufacturer product pages and manufacturer PDFs. Use third-party mirrors only when the primary endpoint is inaccessible, label the mirror, and cross-check decisive limits against an official product page when possible. Store downloaded PDFs only in the user's authorized common datasheet location; do not create duplicate project-local collections without permission.

## Completion Criteria

The task is complete only when:

- requested edits are present and old strings are absent;
- encoding, BOM state, newline style, parentheses, part count, net count, and connectivity are verified;
- each high-severity electrical claim names the affected references/nets and cites a datasheet limit or a directly observed netlist fact;
- mechanical compliance distinguishes verified exact MPNs, known violations, and generic or unspecified parts that cannot yet be certified;
- the report states what was changed, what was intentionally left unchanged, and what cannot be verified without PCB or measurement;
- any reusable deterministic lesson is considered for this shared skill rather than left only in a project report.

## Self-Improvement And Publishing

When DipTrace work reveals a durable format rule, parser failure mode, electrical-audit check, or validation technique, use the `skill-learning` policy and save only the generalized lesson in this shared base or a focused reference/script. Do not store private schematics, customer paths, generated logs, secrets, or project-specific component decisions.

Before material updates or publishing, run the owning repository freshness check. After changes, validate the shared base and both adapters, run relevant script tests, stage only skill files and required inventory metadata, then commit and push by default unless the user says not to. Resolve compatible remote changes semantically; never reset, rebase, force-push, or discard unrelated work.
