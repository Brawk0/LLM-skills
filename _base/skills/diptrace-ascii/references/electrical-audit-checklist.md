# Datasheet-Backed Electrical Audit Checklist

Use this checklist after structural net reconstruction. Do not mark a schematic production-ready from visual wire continuity alone.

## Source Discipline

1. Identify the exact manufacturer, package, and orderable suffix from the schematic and BOM fields.
2. Prefer the current official manufacturer datasheet and product page. Record document revision/date when it affects limits.
3. Treat distributor pages and mirrors as secondary evidence. They are useful for inaccessible PDFs or exact ordering metadata, not as the sole authority for destructive limits.
4. Separate a directly observed netlist fact, a datasheet requirement, a calculated consequence, and an engineering recommendation.

## Power Tree

- Trace every rail from connector to load, including enable and shutdown pins.
- Check recommended operating range and absolute maximum separately for every powered pin. An IC whose main input is valid can still have an overvolted `EN`, feedback, or logic pin.
- Calculate nominal and worst-case regulator output using reference tolerance and resistor tolerances.
- Check startup sequencing, back-power paths, supervisor thresholds, reset release, and default pull states.
- Verify capacitor polarity from resolved physical pin names/numbers, not symbol orientation.
- Check voltage rating against steady state plus switching, cable, regenerative, and fault transients.

## Switch-Mode Regulators

- Recalculate output voltage, switching frequency, inductor ripple/current rating, diode voltage/current, and compensation.
- Compare actual capacitance, ESR, DC-bias derating, and component count with the datasheet's characterized range.
- A type or family recommendation is not proof of loop stability. Large mixed ceramic/electrolytic banks require calculation and preferably load-step or Bode verification.
- When replacing a regulator, recalculate the whole power stage rather than carrying over divider, inductor, and compensation blindly.

## MCU And Digital Logic

- Resolve alternate functions from the exact MCU package datasheet, including remap state.
- Verify timer channel grouping, complementary outputs, break input, idle state, boot/debug multiplexing, and startup behavior.
- Check every external input for voltage tolerance; do not assume all GPIO are 5 V tolerant.
- Classify outputs as push-pull, open-drain/open-collector, tri-state, or analog. Two outputs on one net need explicit arbitration or isolation.
- Check pull-up voltage, sink current, RC rise time, and whether power-off domains can inject through protection diodes.

## Analog And Sensors

- Check input common-mode range, output swing, bias current, offset, source impedance, ADC sampling requirements, and reference limits at the actual supply.
- Place and bias every unused op-amp/comparator section. Hidden or absent units are not automatically safe.
- Include component tolerance, temperature drift, internal reference spread, comparator offset, and sensor timing in thresholds.
- Verify exact sensor output type and required pull-up. Include RC filtering in the maximum event-frequency budget.

## Motor Drivers And Current Protection

- Reconstruct the driver's truth table: which input selects high/low, which enables high impedance, and where PWM produces synchronous versus asynchronous decay.
- Check that a fault or comparator signal really disables energy delivery. An interrupt-only signal is not a hardware current limit.
- For timer break inputs, determine the physical output state after break. Driving all phase inputs low while enables remain high may command braking rather than coast.
- Calculate threshold minimum/nominal/maximum and shunt dissipation at continuous, peak, and fault current.
- Check driver recommended supply minimum with regulator worst case, not only nominal voltage.
- Account for regenerative energy in bulk-capacitor voltage and rating.

## Packages, Thermal, And Layout Dependencies

- Compare symbol pin numbers with footprint physical pad numbers.
- Verify exposed pads, internal connections, thermal vias, copper area, and package variant.
- When the design has a height or envelope limit, enumerate every populated component by exact MPN or defensible package family. Compare the limit with the datasheet maximum dimension including tolerance, not only a nominal or typical height.
- Report generic LEDs, connectors, test hardware, incomplete ordering suffixes, and fitted wires/posts as unverified rather than silently treating the footprint height as the assembled height.
- For a proposed low-profile replacement, recheck voltage, ripple current, ESR, DC-bias derating, saturation/current rating, reliability grade, footprint, and control-loop consequences; matching capacitance or inductance alone is insufficient.
- Identify Kelvin-sense requirements and keep current-sense traces out of power-return voltage drop.
- Flag conclusions that require PCB evidence: current-loop area, decoupling distance, creepage/clearance, thermal resistance, EMI, and connector protection placement.

## BOM And Library Integrity

Cross-check these fields as one identity:

- reference and symbol function;
- `Value` and exact MPN;
- footprint/package;
- manufacturer;
- supplier/order code;
- datasheet URL;
- electrical pinout.

A correct symbol with another device's supplier fields is a production defect even when ERC passes.

Weight the fields by whether they actually reach a purchaser:

- **`Name` and `Value` are the BOM.** DipTrace's export is `RefDes;Name;Value;Quantity`, so these two carry the ordering identity and must be right.
- **`MP`, `Manufacturer` and the distributor part numbers** are what someone orders from inside the editor. Treat a mismatch here as a real defect.
- **`Description` is out of scope — do not report it.** It is SnapEDA import text, it does not reach the BOM, and it routinely keeps describing the original donor part after a deliberate substitution.
- **`BaseName` is historical** in long-lived projects (`Cap 0603` under a `CAP_0603` name) and is not exported. Note it only when it contradicts the device's *function*, and say plainly that it does not reach the BOM.

Read the ordering code itself rather than trusting the human-readable half beside it. In the IEC 60062 R-notation used by Yageo and others the letter is the decimal point: `RC0603FR-074K7L` is 4,7 kΩ while `RC0603FR-0747KL` is 47 kΩ. A one-character slip silently ships the wrong decade — check the code against the stated value on every edited resistor.

Decode a capacitor's rated voltage from its code the same way. Yageo `CC` puts it in the character before `BB`/`BN`: `5` = 6,3 V, `6` = 10 V, `7` = 16 V, `8` = 25 V, `9` = 50 V, `0` = 100 V, `Y` = 250 V. Murata `GRM` uses `0J` = 6,3 V, `1A` = 10 V, `1C` = 16 V, `1E` = 25 V, `1H` = 50 V, `2A` = 100 V, `2E` = 250 V. `CC1206KKX5R8BB106` labelled `50 V` is a 25 V part; this mislabel has recurred across boards, so check every capacitor, not only edited ones.

An orderable code needs its package and packaging suffix. A bare family name such as `UC2845B` is not orderable; `UC2845BD8G` is.

### Proving a ground-domain split

To show that two ground domains are actually separate, do not read the net member lists. Build a graph over nets joined only by components that conduct DC between their own pins — resistors, inductors, jumpers, ferrites — excluding capacitors, ICs and the isolators themselves, then check whether the two ground nets land in one region. Separately list every component with pins on both ground nets: the result should contain only the intended isolators. Both tests are cheap and neither depends on reading a long list correctly.

## Severity And Confidence

- **P0 — blocker:** reverse polarity, absolute-maximum violation, missing mandatory thermal/power pad, wrong pin mapping, direct destructive contention, or another fault likely to damage hardware.
- **P1 — significant:** operation outside a guaranteed range, uncontrolled protection threshold, inadequate voltage/power margin, unverified regulator stability, floating analog section, or unsafe external interface.
- **P2 — deviation:** datasheet recommendation mismatch, lifecycle/BOM metadata issue, firmware dependency, or margin that should be clarified before release.
- **Verified good:** state why the node is acceptable and which datasheet condition was checked.
- **Unverified:** name the missing PCB, exact suffix, upstream protection, firmware configuration, or measurement needed to close the item.
