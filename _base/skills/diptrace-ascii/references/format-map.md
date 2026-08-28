# DipTrace Schematic ASCII Format Map

Use this reference when reconstructing or editing a DipTrace Schematic ASCII `.asc` file. The observations apply to the common parenthesized export format, including v45; verify unfamiliar versions instead of assuming identical fields.

## Text Envelope

- The file is a parenthesized tree headed by a source/version record such as `(Source "DipTrace Schematic ASCII" "v45")`.
- Exports may use Windows-1251 and CRLF without a BOM. Encoding and newline style are part of the artifact and must be fingerprinted before editing.
- **The importer ignores a UTF-8 BOM and decodes the file as a single-byte codepage.** Converting the document to UTF-8 therefore does not gain Unicode — it corrupts every non-ASCII character in the file, because each multi-byte sequence is read back as one character per byte. Observed on a v45 round-trip: `Ω` (`CE A9`) → `О©`, `µ` (`C2 B5`) → `Вµ`, the sheet name `Лист 1` → `Р›РёСЃС‚ 1`, and Cyrillic `LibPath` values likewise. Keep the source encoding; verify with a strict re-encode before writing.
- Windows-1251 cannot encode the Greek omega `Ω`, so an ASCII exchange file writes ohms as `Ohm` / `kOhm` / `MOhm`. The glyph belongs in the `.dch`, set there after import; the project's own CSV/ASCII exports will still render it `?`, which is a limitation of those exports rather than a defect.
- A corrupted round-trip can damage more than the encoding: in the same v45 test the `!` characters vanished from most strings, breaking a `NC!!!___` do-not-populate marker. A clean same-codepage round-trip preserved them. Re-check any marker built from punctuation after every import.
- Parentheses inside quoted strings are data, not tree delimiters. A validator must ignore quoted content and escaped quotes while calculating depth.
- Paths can contain spaces, non-ASCII text, drive letters, UNC prefixes, and backslashes. Do not normalize them as component text.

## Major Sections

Typical top-level sections include:

- `Components` — placed schematic component instances;
- `Shapes` — page-level graphics and text;
- `Nets` — electrical nets, endpoints, and drawn line geometry;
- `CacheLib` — embedded library/cache definitions copied into the document.

The active placed component and its cache-library source are separate objects. Editing a top-level `Part` value does not automatically edit `cl_Value`, and changing only the cache does not update the placed instance.

## Components And Multipart Symbols

A placed instance begins approximately as:

```text
    (Part "library-name" "C1"
      (Number 3)
      (Value "100 uF, 25 V")
      ...
      (PartName "Part 1")
      ...
    )
```

Important rules:

- Each placed `Part` has its own direct-child `(Number N)`. Net endpoints refer to this object ID, not the block's position in the file. IDs may have gaps after deletions; build a dictionary keyed by `Number`. Do not silently fall back to list order when an ID is missing or duplicated.
- A multipart component can have several top-level `Part` blocks with the same reference designator. Preserve them all and distinguish them by object `Number` and `PartName`.
- Fields such as `Value`, `BaseName`, `Manufacturer`, `Datasheet`, and user fields may disagree. Such disagreement is a BOM/library defect even when connectivity is correct.
- `LibPath` and `LibPath_Variable` are provenance/path metadata. Historical Cyrillic text in a path is not a Cyrillic component name.

## Pins

Inside a placed part, pins appear as:

```text
      (Pins
        (Pin 0 ...
          (Number 1)
          (NetNumber 26)
          (Name "PLUS")
          (StringNumber "1")
          ...
        )
      )
```

Interpret the identifiers separately:

- the first integer after `Pin` is the zero-based pin ordinal used by a net endpoint;
- `Number` is a numeric pin field and is not always sufficient for alphanumeric pin numbers;
- `StringNumber` is the authoritative displayed/physical symbol pin number;
- `Name` gives the pin function;
- `NetNumber` refers to the net's own direct-child `(Number N)`, not its position in the list; `-1` means unconnected. Cross-check it against endpoint reconstruction.

Never report `pt 1 1` as physical pin 1 without resolving ordinal 1 through that part's pin block.

## Nets And Endpoints

A net contains an endpoint list:

```text
    (Net "{VIN}"
      (Number 26)
      ...
      (Parts
        (pt 3 0)
        (pt 18 1)
      )
      ...
    )
```

For endpoint `(pt A B)`:

- `A` is the direct-child `Number` of a top-level placed `Part` block;
- `B` is that part's zero-based `Pin` ordinal;
- resolve `A` to the placed reference and `B` to `StringNumber` plus `Name`;
- repeated references from multipart units are expected and must not be deduplicated prematurely.

Other `(pt ...)` records occur in line and shape geometry and can contain coordinates. Only the two-integer records inside a net's `Parts` subsection are electrical endpoints.

The inspector exposes these explicit object IDs as `Part.index` and `Net.index`. Never replace them with `enumerate(...)` in downstream scripts. A sudden set of unresolved endpoints after deleting a component warrants checking ID handling before reporting schematic faults.

## Footprint Pads

Footprint data embedded in a placed component can contain records like:

```text
          (Pad 1 "13" "" ...)
```

The first integer is a pad-object ordinal; the first quoted string is the physical pad number. Check the quoted pad-number set when validating a package. A 28-lead symbol named for an exposed-pad package does not prove that pad 29 or an unnamed thermal pad exists.

Also inspect `IntCon` or equivalent internal-connect records. An exposed thermal pad must have both geometry and the intended electrical connection; a symbol-side ground pin cannot substitute for missing package copper. `(IntCon 7 9)` binding pad 9 to the GND pad is what makes an ESOP-8 thermal pad netted; `(IntCon 1 2)` merges the two anode pads of a PowerDI-5 diode.

### Judging a land pattern by geometry, not by its name

Footprint names are user text and can be wrong or renamed wholesale. Measure instead. Pad geometry lives in `PadWidth` / `PadHeight` inside each `Pad` block, in the file's internal units; calibrate the scale against a footprint of known size (a 2220 land pad is about 5,3 mm across the body) and apply it to the rest.

Chip sizes that share a length are indistinguishable by pad pitch: **1206 and 1210 are both 3,2 mm long**, so both lands sit at roughly 2,9 mm pitch and only the pad height differs — about 1,8 mm for 1206 against about 2,7 mm for 1210. Comparing pitch will pass a mismatched pair; comparing pad height catches it.

Cross-check the pad geometry against the case size encoded in the MPN. Murata GRM: `GRM15`=0402, `GRM18`=0603, `GRM21`=0805, `GRM31`=1206, `GRM32`=1210. Yageo CC/RC carry the size in the code itself. A `GRM32…` part on a 1206 land is a real defect, and so is the reverse after someone "fixes" it by swapping the land.

Renaming or replacing a footprint moves **every** component that used it. After such an edit, re-run the MPN-versus-land comparison across the whole design, not only the parts that were meant to change.

## Cache Library

Cache objects use names such as `cl_Part`, `cl_Value`, `cl_Pattern`, `cl_PossibleName`, and `cl_UserField`. They may contain stale supplier metadata, package aliases, and original library paths.

When the request is to rename placed components, edit the top-level component fields and report cache leftovers separately. When the request explicitly covers all component/library strings, normalize matching cache values too, but preserve paths and genuine manufacturer codes.

## Safe Structural Comparison

For a text-only edit, compare before and after:

- source/version header;
- encoding, BOM, and newline style;
- balanced structural parentheses and terminated strings;
- top-level part count and ordered reference list;
- per-part pin ordinals, `StringNumber`, pin names, and pad numbers;
- net names and ordered endpoint pairs;
- requested old/new string counts.

A matching byte count is neither required nor sufficient. A changed file size is normal after transliteration; unchanged connectivity signatures are the relevant proof.
