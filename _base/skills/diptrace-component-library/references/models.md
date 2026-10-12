# STEP: mechanical envelope, appearance and pin 1

Try an exact manufacturer STEP first. A generic model can match pin count/pitch yet have the wrong height. Check the actual mechanical drawing; distinguish nominal/maximum height and undocumented variant selection. Preserve the user's selected variant when procurement details remain unresolved.

If reconstructed, label the model as simplified nominal geometry, with source/page and assumptions. Use mm, centered XY and Z=0 at the board seating plane. Physical leads/balls differ from PCB lands; paste windows do not belong in the STEP. A flattened ball is an envelope approximation, not a reflow/internal-die simulation.

User appearance: black body, metallic contacts and a light pin-1/A1 dot unless requested otherwise. Recolor STEP assembly styles, not a preview PNG. A flush top-face inlay can mark orientation without increasing total height. Distinguish a confirmed factory mark from illustrative dot diameter/position/color.

## `build_step.py` input

BGA: `kind`, `body=[width,height]`, `height`, `standoff`, `ball_diameter`, explicit `rows`, `columns`, `pitch`. Generates a full grid; a depopulated package needs an explicit adaptation.

QFN: `kind`, `body`, `height`, `contact_height`, `contact_length`, `contact_width`, `contact_center_offset`, `pins_per_side`, `pitch`; optional physical `ep` width/height/thickness. These are physical contacts, not `land_length`/`land_width` from the PCB footprint.

Both accept `marker={"x":…, "y":…, "diameter":…, "depth":…}`, `source` and `model_status`. The helper does not infer dimensions from the MPN. Run with an existing CadQuery runtime or `uv run --with cadquery`.

## Actual export checks

Use an assembly/color-capable exporter, reimport the written STEP, and assert valid solids, expected count, full X/Y/Z envelope, contact seating and unchanged height after marking. Check actual exported color styles. Black can be `DRAUGHTING_PRE_DEFINED_COLOUR('black')` instead of RGB zeros; accept both valid representations.

Compare pin-1/A1 position to the footprint's view convention. Successful CadQuery reimport is not DipTrace display/alignment verification. State the latter separately when the editor is inaccessible.
