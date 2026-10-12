# Symbols: source data, layout and XML

## Read the full pin specification

Normalize physical identifier, full manufacturer name and electrical type. Retain configuration aliases, bank, LVDS, differential pair and DQ/DQS columns; `Pin Name` alone can omit useful alternate functions. Match the exact package sheet. For PDF tables use cell geometry when names wrap, keeping underscores intact. Independently compare PDF/XLSX when available.

## User's style

- Vector everywhere: all text Shapes have `FontVector="Y"`, `FontMono="N"` and empty `FontName`. Pin `NameFont` is vector styling too.
- Reference widths, font height and pin pitch take priority over guessed text-width heuristics. A demonstrated FPGA reference used 76.2 mm signal-body width, 38.1 mm power-body width, 2.54 mm pitch, 3.81 mm pin length, pin font scalar 5 and bank-title scalar 12. These are an example profile, not universal dimensions.
- Two columns, a central divider and bank-specific separators. Bank supplies beside their I/O; remaining power/ground/NC in another part. For ADCs group analog inputs, clock/sync, control and digital outputs by channel. Adjacent differential pairs follow P/N; data bits follow numeric order.
- Visible names: `GPIO/short clock-config/LVDS/DQ-DQS/ball` where supported. Power labels can be `AVDD/9`. Hide external duplicate numbers when a ball/pad number is included in the visible label.
- Preserve short configuration, clock and polarity names. Remove verbose repeated PLL alternatives only by an agreed display policy, with full names saved separately. Do not invent functions on contacts with no source alternatives.
- Put bank headings near the middle divider beside short supply names. Signal-only groups need a separate header row. Limited horizontal compression can fit a few long labels while preserving font height; disclose it rather than silently shrinking every name.

## Format invariants

Root: `<Library Type="DipTrace-ComponentLibrary" Units="mm">`, then nested pattern library and `Components/Component/Part`. Component-wide name/refdes/manufacturer/datasheet live on part 0. Use dense zero-based pin/shape IDs per part.

`PadNumber` is the printed contact identifier. `PadId` is a linked pattern-pad index. A symbol-only library uses `PadId=-1` until attachment; do not invent a valid pattern index. Verify all connections after assigning the existing pattern.

XML root units control geometry, not font scalars. Update `Size` and `FontSizeFloat` together: the float overrides the integer. Vector stroke `Width=-2` is normal. Font scale controls horizontal advance. Pin X/Y is the body-side end: left orientation 0 extends outward left, right 180 outward right. Positive Y is up in the helper input.

A examined legacy binary ELI stored geometry at three internal units per mm, established from a known package pitch. This is an observation about that file, not a documented universal ELI parser. Prefer DipXML export; never apply its binary scaling to XML geometry or font scalars.

## `build_symbol.py` reviewed specification

```json
{
  "name":"EXAMPLE_ADC", "refdes":"D", "manufacturer":"Example",
  "label_policy":{"append_ball":true,"include_lvds":true,"include_dqs":true},
  "pins":[
    {"ball":"1","name":"VINP1","type":"Input"},
    {"ball":"2","name":"D0P1","type":"Output","lvds":true}
  ],
  "parts":[{
    "name":"Part 1","width":38.1,"height":12.7,
    "pin_length":3.81,"pin_font":5,
    "pins":[
      {"ball":"1","x":-19.05,"y":0,"side":"left"},
      {"ball":"2","x":19.05,"y":0,"side":"right"}
    ],
    "lines":[[0,-6.35,0,6.35]],
    "texts":[{"text":"ADC1","x":0,"y":3.81,"size":7}]
  }]
}
```

List every contact exactly once across parts. Source records may also carry `aliases`, `configuration`, `dqs`, `lvds` and arbitrary full-data/provenance fields; the CSV preserves each full record as JSON. Slash-separated aliases in `name` are supported. An optional `omit_alias_regex` implements an explicit requested display policy; no function is dropped by default. Normalize electrical CSV tags to DipTrace strings (Input, Output, Bidirectional, Power, Passive, Undefined, etc.).

Pin placements support `name_scale` (default 1). Text entries support alignment, size and semantic `show` (Name, RefDes, Part Name, etc.). The helper defaults `refdes` to `D` for ICs and adds name/refdes markings unless `markings=false` is set. It creates no attached pattern and no GUI-import claim.

Import: Component Editor → Library → Import → DipXML; inspect before saving native `.eli`. A past EAGLE XML import crashed CompEdit despite syntactic/mapping checks. Its cause remains unproved; native XML/legacy KiCad are alternatives, not evidence that every EAGLE library fails.

Primary references: [CompEdit XML](https://diptrace.com/support/tutorials/xml_specs_CompEdit_html/), [DipTrace help](https://www.diptrace.com/support/tutorials/help_html/). Prefer the SDK/docs matching the installed build.
