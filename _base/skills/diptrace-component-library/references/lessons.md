# Durable lessons

## Preferences

Primary CAD is DipTrace. IC reference-designator prefix is **D**, including FPGA and ADC components; use it for new symbols and leave manually corrected existing files unchanged unless asked. Every symbol annotation is Vector. Use the user's actual library/example for widths, pitch and section structure. FPGA Part 1 groups banks with VCCIO; Part 2 holds remaining power/ground/NC. ADCs group channels and signal roles. Preserve accepted footprint/models while restyling symbols. Bodies default black, contacts metallic, pin 1 visibly marked. Do not take over a shared PC for offline work.

## Demonstrated failures

1. A local library copy lacked the user's reference; the current copy was on a server. Resolve the active path.
2. Only reading `Pin Name` lost LVDS and DQ/DQS fields from separate columns. Check all applicable columns; retain full data and meaningful alternate functions.
3. Reading undocumented internal ELI values as mm tripled the body width. A known pitch revealed a factor of three in that file. Prefer XML export, and do not universalize the binary heuristic.
4. Vector pin labels did not make TrueType headers vector. Assert the flag on every text Shape, with no leftover font face.
5. Long duplicate PLL names made symbols excessively wide. Keep short useful functions visible and verbose full data in a mapping; respect requested/reference width.
6. Valid EAGLE XML and complete pin mapping did not prevent an import access violation. Report the observed failure without inventing its cause; use another supported route.
7. Independent PDF/Helvetica previews approximate the built-in vector font; they are not exact DipTrace typography or GUI proof.
8. A generic STEP with matching grid had an incompatible total height. Read the exact drawing and reimport the actual exported model.
9. Assembly export retained black/metallic/light-dot styles. Checking only RGB records falsely misses predefined black colors.
10. Physical QFN leads/EP chamfers and PCB lands/paste windows describe different geometry.
11. PDF table extraction moved an underscore to the end of a pin name and split `LVDS` into `LV DS`. Read the pin-name cell's positioned text, preserve punctuation, and normalize whitespace when checking function keywords. Reconcile every contact against an independent source map before drawing.

## Evidence and privacy

Keep source-table checks, output-file parsing, footprint geometry, STEP reimport, actual GUI import, native pin-pattern mapping and 3D alignment as separate evidence levels. Retain future compact lessons here; keep raw/confidential datasheets and project pin tables with user assets, outside the public skill repository.
