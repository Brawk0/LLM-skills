# Footprints: copper, numbering and orientation

Use the exact package variant; equal pin counts alone are insufficient. Separate physical package/contacts, manufacturer-recommended PCB lands and custom PCB lands. Ball/lead dimensions do not establish copper-pad dimensions. Document solder-mask/paste choices separately.

## BGA

Take the row alphabet and skipped letters from the drawing. Preserve alphanumeric names and NC balls; NC is not a missing physical ball. Do not assume the grid is full. Check every identifier, coordinate, pitch and diameter. In a full 22×22 grid at 1 mm pitch, extreme ball centres span 21 mm, independently of body size.

KiCad footprint Y is normally down; Cartesian STEP Y is up. With top-view A1 upper-left, KiCad A1 Y is negative and STEP A1 Y positive. Compare all four corner relationships, view direction and rotation/mirroring before and after import.

## QFN

Confirm the drawing's view and numbering direction. The helper's top-view order is left top→bottom, bottom left→right, right bottom→top, top right→left. Adapt if the actual drawing differs.

An electrical exposed pad must appear in the symbol/pad map, using the manufacturer's ID or a documented CAD identifier. A physical EP chamfer and rectangular PCB copper land are different objects. Subdivided paste apertures are custom unless explicitly recommended; do not accidentally generate full paste over an accepted window pattern.

## `build_footprint.py` input

BGA: `kind="bga"`, `name`, `body=[width,height]`, explicit `rows`, `columns`, `pitch`, `pad_diameter`, and `land_pattern_status` provenance.

QFN: `kind="qfn"`, `name`, `body`, `pins_per_side`, `pitch`, `land_length`, `land_width`, `land_center_offset`; optional `ep={"number":"0","width":…, "height":…}` and explicit `paste_windows=[{"x":…, "y":…, "width":…, "height":…}]`. Windows keep EP off full F.Paste. Dimensional provenance lives in the input/report, not in the helper's successful exit code.

Import standalone KiCad footprint through Pattern Editor → Library → Import → KiCAD. Inspect the native transformed geometry and symbol mapping. Preserve accepted footprint/STEP files during symbol restyling and keep original CAD archives/source drawings.
