---
name: schematic-bom-export
description: Build the assembly Markdown BOM note and the matching print-ready PDF from a DipTrace BoM.csv export. Use when asked to make, refresh, or check a board BOM for an Obsidian assembly folder, to add batch quantity columns, to exclude non-purchasable mechanical placements, or to sanity-check a BOM export for duplicate part numbers, footprint/part-number mismatches and wrong resistor codes.
---

# Schematic BOM Export

## Core Goal

Turn a DipTrace `BoM.csv` export into two artefacts that always agree: an
Obsidian note for review and a print-ready PDF for the assembly bench. The CSV is
the single source of truth — never retype rows into the note, and never edit one
output without regenerating the other.

## Required Workflow

1. **Take the CSV, not the schematic.** Ask the user to re-export `BoM.csv` from
   DipTrace after any schematic change. Parsing `.asc` directly is a fallback for
   when no export exists; DipTrace merges rows by value in ways a naive parser
   will not reproduce, so a hand-parsed table will disagree with the official one.
2. **Audit the CSV before rendering.** Run the checks in
   [references/bom-sanity-checks.md](references/bom-sanity-checks.md) and report
   what they find. A duplicate part number or a wrong resistor code is the
   developer's to fix in DipTrace — fix it there and re-export, do not patch the
   generated files.
3. **Render both formats in one run** with `scripts/bom_export.py`. It emits the
   `.md` and the `.pdf` from the same parsed rows, so counts, exclusions and
   numbering cannot drift apart.
4. **Report the totals and the exclusions.** State line count, placements per
   board, fitted/DNP split, and which mechanical placements were dropped.

```powershell
python scripts/bom_export.py `
  --csv "D:\...\<BOARD>\BoM\BoM.csv" `
  --out-dir "G:\...\Schematics\<PROJECT>\<BOARD>\assembly" `
  --title <BOARD> --date <YYYY-MM-DD> --batches 1,2,5
```

Outputs are named `<BOARD> BOM.md` and `<BOARD> BOM.pdf` inside `assembly/`.

## What Belongs In A BOM

A BOM is a purchase and mounting list. Include only what somebody buys or places.

- **Exclude footprint-only entities**: solder jumpers (`Solder_JMP*`), bare lead
  pads (`Lead_*`), test points (`TP_*`), mounting holes, fiducials, logos. They
  occupy a refdes and appear in the DipTrace export, but nothing is ordered for
  them and they only push real parts onto an extra printed page. The script drops
  them by default and lists what it dropped; `--keep-mechanical` restores them
  when a fabrication document genuinely needs them.
- **Renumber after exclusion** so the printed `No.` column runs 1..N without
  gaps. The script does this; the DipTrace `#` column is not preserved.
- **Keep DNP lines.** A part prefixed `NC!!!___` is a real design decision and
  must stay visible, marked `DNP` and shaded, so the assembler can see it was
  deliberately left unfitted rather than forgotten.
- Gaps in refdes numbering (`C3`, `TP6` missing) are normal after deletions.
  Mention them once as an observation; they are not BOM defects.

## Ohms

Write `Ohm` / `kOhm` / `MOhm`, never `Ω`. DipTrace's single-byte CSV and ASCII
exports cannot carry the glyph and already emit a literal `?`; the script
rewrites `?` to `Ohm`. See the `diptrace-ascii` skill for the encoding rule this
follows.

## Quantity Columns

Emit one `Qty X<n>` column per planned batch, ascending, via `--batches`.
`Qty X1` is always present so a single-board build needs no arithmetic. Ask the
user for the batch sizes rather than assuming the count used on a sibling board.

## Print Layout

The PDF reproduces the house style of the existing R120 assembly sheets. Keep it
stable — the assembler recognises the sheet by its shape:

- A4 landscape, Arial, frame width 762.52 pt, left margin 40.02 pt.
- Title 19 pt bold; the summary paragraph 10 pt; table body 8.2 pt; header 8.6 pt
  bold on `#f1f3f5` with a rule under it; grid `#d1d5da`.
- The `Part / value` cell holds the component name in black and the value in
  `#666666` on a second line.
- DNP rows are shaded `#d9d9d9`.
- Footer on every page: `<BOARD> BOM - updated <date>` left, `Page N` right,
  7.5 pt, `#666666`. The table header repeats on each page.

The Markdown note carries `cssclasses: bom-print` plus `source_file`, `boards`
and `updated` in the frontmatter, and wraps cells in `<span class="bom-part">` /
`<span class="bom-value">` so Obsidian prints it the same way.

## Dependencies

`reportlab` is required for the PDF. Install it into the user's Python if
missing, and say so. `pypdf` is optional and only used to verify the result.

## Completion Criteria

- Both files regenerated from the same CSV run, in the board's `assembly/` folder.
- No mechanical placement appears in either output, and the exclusion list was
  reported to the user.
- Totals in the summary paragraph match the rendered rows for every batch column.
- The sanity checks were run and their findings reported, or explicitly stated as
  clean.

## Self-Improvement And Publishing

When a BOM run reveals a durable rule — a new class of non-purchasable part, an
export quirk, a layout constraint — record the generalized lesson here or in
`references/`, never the customer's part choices, stock levels or project paths.
Follow the `skill-learning` policy, then validate the shared base and both
adapters before committing.
