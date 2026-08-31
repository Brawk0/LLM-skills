# BOM sanity checks

Run these against `BoM.csv` before rendering. Every finding is fixed in DipTrace
and re-exported — never patched in the generated `.md` or `.pdf`.

Each check below has been caught on a real R120 export at least once.

## 1. Duplicate part numbers across lines

Group lines by the leading order code of `Value` (strip `NC!!!___` first). Two
lines with the same part number mean the schematic carries two spellings of one
value and the purchase list will double-count it.

Seen: `RC0603JR-075K1L  (RC21 5.1 kOhm)` and `RC0603JR-075K1L  (5.1 kOhm)` — the
same resistor, split only by a missing `RC21` prefix.

**Legitimate exception:** a `NC!!!___` line always pairs with its fitted twin.
That pair is correct and must stay split.

## 2. Two order codes for one electrical value

Same value and footprint, different manufacturer part. Sometimes deliberate
(different dielectric or tolerance), often an oversight. Report it as a question,
not as a defect.

Seen: `CC0603MRX7R9BB105` and `CC0603KRX5R9BB105`, both 1 uF 0603 — X7R vs X5R.

## 3. Footprint in the component Name vs the order code

The size embedded in the order code (`RC0402…`, `CC1206…`) must match the digits
in the DipTrace component `Name` (`RES_0603`, `CAP_1206`). A mismatch means the
part will not fit the pad.

Seen: sixteen resistors named `RES_0603` carrying `RC0402JR-0751RL`.

## 4. Resistor code vs the printed value

Decode the EIA-96-style suffix and compare with the value in brackets:
`5K1` = 5.1 kOhm, `10K` = 10 kOhm, `0R1` = 0.1 Ohm, `330R` = 330 Ohm. A
disagreement means one of the two was edited and the other was not.

## 5. Quantity vs refdes count

`Quantity` must equal the number of comma-separated designators in `RefDes`, and
no designator may appear on two lines. Both are hard errors in the export.

## 6. Refdes numbering gaps

Report once, as an observation. Gaps are the normal residue of deleted parts, but
a missing decoupling capacitor hides here too, so it is worth a glance.
