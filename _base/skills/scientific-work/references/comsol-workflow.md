# COMSOL Workflow

Use this reference for COMSOL, CST, FEM, mode analysis, `.mph`, Java automation, and numerical validation tasks.

## Safety

- Do not edit original `.mph` files directly.
- Work on a copy or generate a new model.
- Keep raw simulation files separate from concise Obsidian decision notes.

## Modeling Hygiene

- Record geometry, materials, boundary conditions, mesh settings, solver settings, and swept parameters.
- Record units explicitly.
- Note what changed between simulation runs.
- Validate against analytic estimates, convergence checks, or an independent reference when possible.

## Reporting

- Distinguish observed results from hypotheses.
- Write conclusions as next modeling actions: what to refine, compare, sweep, or verify.
- Be sparing with plots of DERIVED quantities: a curve earns its place when it supports a
  decision, not because the data existed.

**A report on a computation must show the model, not only numbers** (explicit user requirement,
2026-08-26). Tables of effective indices and losses are unreadable as a description of what was
actually built, and a reader cannot tell a correct model from a wrong one without seeing it.

- Every modelling note carries at least two pictures exported FROM THE SOLVER: the structure as
  it was built - the permittivity or material map, which is the geometry after meshing and
  material assignment - and the field of the working solution. Keep the solver's own title
  strip: it carries the frequency and the effective mode index, and that is what ties the
  picture to the table.
- **A hand-drawn schematic does not substitute for the export, and the export does not
  substitute for the schematic.** The schematic shows what was intended, at a scale and with
  labels a person can read; the export shows what was actually solved. Publishing only the
  schematic is how a geometry error survives review - the 110 nm buffer of 2026-08-25 was drawn
  correctly in every schematic while the solver had something else.
- **Choose the view that shows the feature under discussion.** A lateral taper needs a top view,
  a vertical step needs a side view, a mode needs the cross-section. The default view a tool
  picks usually shows none of them, and a picture of the wrong plane is worse than none because
  it still looks like evidence. When the feature is three-dimensional, show two planes.
- When variants are compared, export at least the baseline and the winner. A bar chart of the
  comparison is not a picture of the models.
- Frame and brighten afterwards when the exporter cannot - mechanics are in the traps section
  and in `scripts/` - but never crop away a field picture's title strip, which is its
  provenance.

## Automation

- Prefer scripts for repeatable parameter sweeps or model generation.
- Keep generated files named by date, model variant, or parameter set so results are traceable.
- On Windows, prefer `comsolbatch.exe` for non-interactive runs. Avoid `comsol.exe batch` unless a visible interactive COMSOL session is explicitly needed.
- For Java model scripts, compile with `comsolcompile.exe <ModelScript>.java` first, then run `comsolbatch.exe -inputfile <ModelScript>.class -batchlog <run>.log`. Do not rely on `comsolbatch.exe -inputfile <ModelScript>.java`: COMSOL can try to open the Java source as a model file, write an error to the log, and still return process exit code `0`.
- Treat the batch log and expected output files as the success signal, not only the shell exit code. After every COMSOL run, inspect the tail of the `.log`, check that exported `.csv` or status files exist, and verify the model saved under the intended final name.
- When a script calls `model.save("final_name.mph")`, COMSOL may also create a duplicate `<ClassName>_Model.mph` plus `.status` or `.recovery` files. After confirming the intended `.mph` and exported tables are present, remove redundant generated duplicates so later work does not confuse them with authoritative results.
- Export numerical results directly from the Java script with `model.result().table(...).save(...)` and write a small UTF-8 status or summary file. This makes headless runs auditable without opening the `.mph`.
- For `ModeAnalysis`, set the eigenvalue shift near an analytic or previous numerical estimate, request enough eigenmodes, and choose the physical branch by an explicit rule such as field localization, continuity through a sweep, or closest complex `n_eff`. Do not assume the first table row is the mode of interest.
- Record the complex-material sign convention used in COMSOL, especially for metals. If source code or tables use a different convention for loss, state whether COMSOL used `eps=(n+i*k)^2` or another equivalent representation.
- In COMSOL mode-analysis tables, the displayed sign of `Im(n_eff)` or `Im(beta)` can follow the chosen time-dependence convention. When converting to attenuation, propagation length, or insertion loss, use the positive attenuation value, usually `abs(Im(n_eff))` or `abs(Im(beta))`, and state this convention in the note.
- For finite/open plasmonic waveguide checks without a full boundary-convergence study, label the result as diagnostic. Record domain size, boundary treatment, mesh settings, and the missing convergence checks before comparing it to analytic or EDP results.

## Keeping Models

A model that exists only in a local scratch folder will be lost. The rule is in the skill's
"Computational Artifacts Leave The Local Disk" section; the COMSOL mechanics are here.

- Run with `-nosave` while iterating, but produce and keep one saved `.mph` per model family when
  the work is finished. An env-gated `model.save(...)` just before `ModelUtil.remove(tag)` costs
  nothing and makes that reproducible on demand.
- Strip before syncing with `scripts/Compress-MphModel.ps1`. Measured on this vault: a solved
  3D scattering model 181 MB -> a few MB, a 2D periodic cell 16.9 MB -> 0.5 MB, i.e. 2-5 %.
  The strip clears `model.sol(tag).clearSolutionData()`, `mesh(tag).clearMesh()`,
  `result().table(tag).clearTableData()` and `model.resetHist()`. History alone is often the
  largest single contributor.
- The stripped file still opens, still shows the geometry and every setting, and re-solves with
  one Compute. That is what makes it worth keeping next to the note rather than a screenshot.
- Keep the `.java` next to the `.mph`. The script is the authoritative definition; the model is
  the convenient one.
- Do not sync the debris a batch run leaves: `.class`, `.status`, `.recovery`, `<Class>_Model.mph`
  duplicates, and logs of successful runs.

## Java Model API — Recurrent Traps

Lessons from writing a headless 3D scattering model on COMSOL 6.2 (learned 2026-07-31, driving `sphere_vacuum.java` for Level-1 Mie validation). Batch typically prints exit code 0 on model-build errors — always read the tail of `-batchlog` for `/*Error*/` and expected output files.

- **Material `refractiveindex` / `refractiveindexkappa` are scalars for isotropic media.** Passing a 9-element `String[]` tensor gives `A scalar value expected. Parameter: Refractive index (null) - Owner: Basic (def)` and the run dies before mesh. Use `.set("refractiveindex", "n_expr")` and `.set("refractiveindexkappa", "k_expr")`.
- **Interpolation function calls need consistent argument units.** With `argunit="nm"` and `nargs=1`, call `n_Au(ewfd.lambda0)` directly — COMSOL converts the SI-meters argument. Do not hand-multiply `*1[1/nm]`; the double conversion silently gives wrong numbers.
- **Scattering boundary feature is `"Scattering"`, not `"ScatteringBoundary"`.** The wrong name errors as `Unknown feature ID: ScatteringBoundary` after the mesh visualization step (misleading location).
- **The mesh has a built-in `size` node at creation.** `mesh1.create("size", "Size")` errors as `An object with the given name already exists. Tag: size`. Modify `mesh1.feature("size")` in place; only `create` for additional local sizes (`sz_au`, etc.) with different tags.
- **Physics-controlled mesh (`autoMeshSize(N)` + `mesh1.run()`) can fail as `Failed to set up physics-controlled mesh. Failed to set mesh size automatically.`** in a scattered-field EWFD scattering setup when called before or without a properly wired study. Fall back to user-controlled: modify the default `size` node, add one `FreeTet`, run.
- **`Sphere` needs `createselection="on"` to expose the auto-named selections** `geom1_<tag>_dom`, `geom1_<tag>_bnd`, and for a layered sphere `geom1_<tag>_lyr_<layer_name>_dom`. Without it these selection names do not exist and downstream `.selection().named(...)` calls fail cryptically.
- **Frequency-domain `plist` must be a `range()` expression string, NOT space-separated literal list, NOT setIndex-per-value.** All three of `set("plist","749.481 705.394 ...")`, `set("plist","749.481, 705.394, ...")` and `for i: setIndex("plist", value_i, i)` visibly save all N tokens in `p:plist.valueMatrix` in the XML but the solver reads `p:plist.value` (the expression) and sees an empty/single-token evaluation — sweeps ONE point. GUI-generated Java always emits `set("plist", "range(a[unit], step[unit], b[unit])")` — that is the only form the solver parses correctly. For a NON-uniform freq sweep, either resample to uniform-in-frequency (accept non-uniform wavelength) or use a separate `Parametric` study feature with `plistarr = "range(400,25,800)"` and `punit="nm"`, driving Frequency's `plist` from a global param `f_curr = c_const/lam0` (learned 2026-08-01).
- **PML — the working COMSOL 6.2 Model API pattern**, reverse-engineered from `Wave_Optics_Module/Couplers_Filters_and_Mirrors/single_mode_fiber_coupling.mph` XML:
    ```java
    model.component("comp1").coordSystem().create("pml1", "PML");  // 2 args, NOT 3
    model.component("comp1").coordSystem("pml1").selection().geom("geom1", 3);
    model.component("comp1").coordSystem("pml1").selection().named("geom1_<sph_out_tag>_lyr_<layer_name>_dom");
    model.component("comp1").coordSystem("pml1").set("coord", new String[]{"x","y","z"});
    model.component("comp1").coordSystem("pml1").set("d",     new String[]{"x","y","z"});
    model.component("comp1").coordSystem("pml1").set("dmax",  new String[]{"d_pml","d_pml","d_pml"});
    ```
    Prior failure `Unknown geometry. Tag: PML` came from passing `"geom1"` as third arg to `.create()`. It's a Coordsys `op="PML"` node (2-arg create), not a coordSystem-with-geom node. `p:coord`/`p:d`/`p:dmax` are String[] with unit-carrying items. Layered spheres decompose the PML shell into multiple sub-domains — use the auto-named `geom1_<sph_out>_lyr_<pml_layer_name>_dom` selection to catch all of them (requires `createselection="on"` on the outer sphere). Keep a `Scattering` BC on the outermost boundary as a residual-reflection sink alongside PML — that is the standard closure.
- **A spherical `Sphere` with `layername` decomposes the PML shell into multiple sub-domains.** Point-`Ball` selections to identify PML by coordinates miss most sub-domains. Use the auto-named domain selection `geom1_<sph_tag>_lyr_<layer_name>_dom` (requires `createselection="on"` on that sphere).
- **Solve cost for a 3D Au-in-vacuum scatterer, R=25 nm, `hmax=40[nm]`, `hmax=3[nm]` on Au surface, PML shell = λ_max/2, r_domain ≈ 1 μm, first-order elements: about 4.3 million DOFs, ≈28 s per frequency, ≈1.4 GB RAM.** Full 17-point λ-sweep ≈8–10 min on the user's Windows machine. Halve the domain, coarsen to `hmax=60[nm]` for smoke tests before committing to fine grids.
- **When the model is correctly configured with materials that have real losses (Au with n,k) and dispersive material assignment, MUMPS direct solver silently falls back to iterative multigrid due to memory pressure.** In that regime, per-point cost rises to 3–7 min and RAM usage climbs to 8+ GB (of 16 GB), and near LSPR (~525 nm for Au R=25 nm) iterations stall for 10–20 min at ~57% "Solving linear system". Full 16-point sweep took ≈70 min on the user's Ryzen 5 2500U. Symptom `Warning: MUMPS is switching to out-of-core mode` in `-batchlog` is the tell; consider halving the domain or accepting slow solve for the validation pass.
- **`ewfd.Qh` does NOT exist in Wave Optics EWFD physics — use `ewfd.Qrh` (resistive heat).** Trying `ewfd.Qh` yields `Failed to evaluate expression / Undefined variable: ewfd.Qh` at the EvalGlobal stage (or silent zero if wrapped in an integration). Other candidates: `ewfd.Qav`, `ewfd.Qsrh`, `ewfd.Qsh` all fail; only `ewfd.Qrh` works. Numerically verified against analytic ω/2·ε₀·ε''·|E|² integrand. (learned 2026-08-01)
- **EWFD physics reads `n, ki` from a dedicated `RefractiveIndex` property group, NOT from `def.refractiveindex/refractiveindexkappa`, and requires an explicit `DisplacementFieldModel = "RefractiveIndex"` on the Wave Equation Electric feature.** Without both, Au domain solves as vacuum (n=1, no losses → σ_abs = 0). Working pattern:
    ```java
    mat.propertyGroup().create("RefractiveIndex", "Refractive index");
    mat.propertyGroup("RefractiveIndex").set("n",  "n_Au(ewfd.lambda0)");
    mat.propertyGroup("RefractiveIndex").set("ki", "k_Au(ewfd.lambda0)");
    // + on physics:
    model.component("comp1").physics("ewfd").feature("wee1")
         .set("DisplacementFieldModel", "RefractiveIndex");
    ```
    The `def` group holds appearance/coloring properties (color, roughness, etc.), not the dispersion table EWFD reads at solve.
- **`Ball` selection for a domain-in-larger-domain (Au sphere at origin inside air sphere, `posx=0,posy=0,posz=0,r=r_np*0.5,entitydim=3`) can return 1 entity that is NOT the intended domain — often it returns the enclosing air domain if a boolean union collapsed the inner sphere.** Diagnostic: `intop(1)` on a Ball-selected Au should equal `(4/3)πR³`; if it returns the enclosing volume instead, the Ball missed. Use auto-named `geom1_<sph_tag>_dom` (needs `createselection="on"`) — it survives union and is exactly the Au domain.
- **A material with no explicit selection does not fill in "the rest" — every domain must be covered.** `mat_air` without `.selection()` triggers `Undefined material property 'n' required by Wave Equation, Electric 1` on the empty domain. Set `.selection().all()` on the background material and let a later material with narrower selection override on top. (Latest-created material wins on overlap, so `mat_Au` created after `mat_air` with `.selection().named("geom1_sph_np_dom")` overrides on Au.)
- **`nx, ny, nz` (bare) are boundary outward-normal components and are always defined on real boundaries; `ewfd.nX, ewfd.nY, ewfd.nZ` are physics-scoped and undefined on any boundary where the EWFD physics isn't active (interior slice surfaces, virtual observation spheres that never got Boolean-cut).** Use bare `nx, ny, nz` for post-processing flux integrals; anything requiring physics-side up/down splitting stays in `ewfd.*`.
- **An observation `Sphere` created inside `air` without a Boolean cut becomes virtual after `geom.run()` — its boundary either does not exist in the finalized geometry, or exists but the flux integral returns garbage (values of the wrong magnitude/sign).** Skip the observation sphere entirely and compute σ_sca as the flux of scattered Poynting through the Au particle boundary (`geom1_sph_np_bnd`), pointing outward from Au. Numerically identical to a proper observation-surface integral when PML absorbs cleanly.
- **User-defined coupling operators (`Integration`) created via `component().cpl().create(...)` AFTER a `study.run()` are not attached to the stored solution and evaluate as `Unknown function or operator` in `EvalGlobal`.** For post-solve integration of a pre-existing `.mph`, use result-side derived values instead: `result().numerical().create("iv1","IntVolume")` / `IntSurface`. These take a selection directly and work against any stored dataset without a re-solve. Alternatively, define all `cpl` operators (`auint`, `abint`) in the Java source BEFORE `study.run()` so they're baked into the solved dataset.
- **`System.out.println` and `System.err.println` from `comsolbatch` are largely lost — only the very last few prints from `main()` reliably reach the process stdout that the shell redirects; anything inside `run()` may disappear even without an exception.** Reliable debug channel: open a `PrintWriter` on `logs/<name>_debug.log` and flush after every message. Print to that file for anything you must be able to see.
- **`Result → Global Evaluation` (`EvalGlobal`) with N expressions in one shot returns a truncated `double[expr][sol][ri]` on the first failing expression** — shape ends up `2 × nSol × 1` instead of `4 × nSol × 1` when expression 3/4 could not evaluate. Wrap each expression in its own `EvalGlobal` in a `try/catch` loop when isolating an eval failure; the batch API silently omits failed rows.
- **In a scattered-field formulation the background field MUST itself satisfy Maxwell's equations in the background medium, or the entire domain becomes a spurious distributed source.** `.set("Eb", new String[]{"0","E0","0"})` — a constant vector — is the classic trap: it is a static uniform field, satisfies no Helmholtz equation at `k0≠0`, and the solver's residual never cancels anywhere. The run converges silently, no warnings, and cross-sections come out **~19× too large** (Au sphere R=25 nm: σ_abs 37 789 nm² vs Mie 1 967 nm²). Insidiously, the *resonance position stays roughly right* (512 nm vs true 500 nm) and the spectral shape looks plausible, so the error masquerades as a mesh/boundary problem. Correct form is a propagating plane wave with the phase factor, `.set("WaveType","userdef")` + `.set("Eb", new String[]{"0","0","E0*exp(-j*ewfd.k0*x)"})` (E‖z, k‖+x), or the built-in generator `.set("WaveType","LinearPolByAngle")` with `incAngle`/`polAngle`/`Eampl`. After the fix: σ_abs 1 966.1 nm² vs Mie 1 967 nm² — **0.05 %** (learned 2026-08-03).
- **Empty-domain test is the cheapest way to validate a scattered-field setup, and it should precede any long sweep.** Remove the scatterer, make the whole domain background medium, solve one frequency: `E_scat` must be identically zero, i.e. `⟨|ewfd.E|²⟩ = |E_b|²`. With a constant `Eb` this returned 19.6 instead of 1.0 — instant, unambiguous diagnosis in a few minutes of solve time. Remember `ewfd.E` is the TOTAL field, so compare against `|E_b|²`, not against zero.
- **`ewfd.E` (`ewfd.Ex/Ey/Ez`, `ewfd.normE`) is the TOTAL field even when `SolveFor = "scatteredField"`.** The scattered part is the degree of freedom the solver works with, but post-processing exposes `E_total = E_b + E_scat`. Get the scattered part explicitly as `ewfd.Ex - ewfd.Ebx`, etc. Consequently `ewfd.Qrh` already integrates losses on the *total* field, so `σ_abs = IntVolume(ewfd.Qrh)/I0` is correct as written — do not hand-add the background. Verified on an empty domain: `|ewfd.Ez|² = 1.0` matching `Eb = (0,0,1[V/m])`.
- **Image export from `comsolbatch` is only partly possible — there is no graphics context.** Available: `PlotGroup3D`/`PlotGroup1D` with `Slice`, `Global`, `Mesh` features, exported via `result().export().create(tag, "Image3D"|"Image1D")`. NOT available (all fail `Operation cannot be created in this context`): plot features `Geometry` and `MeshPlot`, and datasets of type `Selection`. Plot-feature-level selection fails as `Entity has no selection`. Net effect: you cannot restrict the plotted region, so the camera always frames the whole domain — for a 25 nm particle in a 1225 nm domain the object is a single pixel and the image is useless. For close-ups, either drive a real `comsol.exe` session with graphics, or build the plot groups headlessly (they persist in the saved `.mph`) and take the snapshots in the GUI.
- **Correct property names for an image-export node** (obtained from `model.result().export(tag).properties()`, 92 entries — use that call rather than guessing): `sourcetype` = `"plotgroup"`, `sourceobject` = plot-group tag, `imagetype` = `"png"`, `pngfilename`, `unit` = `"px"`, `width`, `height`, `lockratio`, `antialias`, `zoomextents`. There is **no** `background` or `backgroundcolor` property, and no `plotgroup` property — setting either throws `Unknown property` and takes down the whole export node, which reads as if the export type itself were wrong.
- **Before blaming the solver for a few-percent mismatch against an analytic reference, remove the comparison artefacts.** Two of them cost 15 % on the Au-sphere Mie validation and looked exactly like physics: (a) the reference was computed on a round wavelength grid and *interpolated* onto COMSOL's points — but COMSOL's `range()` sweep is uniform in frequency, hence non-uniform in wavelength, and linear interpolation across a 25 nm step shaves the LSPR peak; (b) the two sides used different interpolation schemes for the same tabulated `n(λ), k(λ)`. Fix (a) by computing the reference at exactly the solver's wavelengths, (b) by matching the scheme. **COMSOL's `interp="piecewisecubic"` is monotone piecewise-cubic Hermite = `scipy.interpolate.PchipInterpolator`, NOT `CubicSpline`** — measured max error on σ_sca: linear 3.57 %, natural cubic spline 1.85 %, PCHIP 0.34 % (σ_abs: 5.55 % / 3.26 % / 0.04 %). Only after both are matched does the residual represent actual FEM discretization error (learned 2026-08-11).
- **Rule of thumb for a systematic multiplicative error: suspect the source, not the mesh.** A factor-of-N discrepancy that survives halving the mesh size, doubling the domain, and disabling the PML entirely is not a discretization error. In this case refining `h_Au` from 3 nm to 1 nm plus 4 boundary layers changed σ_abs by <0.01 %, doubling `d_air` made it worse, and removing the PML changed nothing — all three "converged" on the wrong answer because the excitation itself was ill-posed.

## Mode Analysis And Periodic Cells - Recurrent Traps

Lessons from the 2026-08-25 queue run on COMSOL 6.2: an LR-DLSPPW baseline, an Ag-strip
convergence study, a coupled thin-film study and a biperiodic metasurface cell.

- **A "lossless metal" is a metal with zero imaginary PERMITTIVITY, not zero `k`.** Setting
  `ki = 0` while keeping `n = 0.6389` turns gold into a dielectric with `eps = +0.41`: a
  low-index slot, not a plasmonic layer. The field fraction inside it jumped from `1e-4` to
  `0.12` and the whole branch changed character. Convert properly instead: for
  `eps = (0.6389 + 11.1748i)^2 = -124.468 + 14.279i`, the lossless counterpart is
  `eps = -124.468`, i.e. `n = 0`, `k = sqrt(124.468) = 11.156521`. The same applies to any
  "switch the loss off" experiment on a metal.
- **A periodic `Port` launches its `Pin` (default `1[W]`), not the amplitude in `Eampl`.**
  `Eampl` only fixes the polarisation of the port mode. Normalising reflectance and absorption
  by `0.5*E0^2/Z0_const*Area` is therefore wrong by the ratio of 1 W to the cell's actual
  plane-wave power - fifteen orders of magnitude for a 500 nm cell. Set `Pin` explicitly and
  divide the integrals by it. Read the port's real settings with
  `model.component("comp1").physics("ewfd").feature("port1").properties()` (42 entries in 6.2)
  rather than guessing names; `PortExcitation`, `Pin`, `InputType`, `PortSlit` and `n` are the
  ones that matter.
- **Recompile before every batch run, and verify the switch you just added actually switched.**
  A new environment-variable override was added to a Java model and the run launched without
  `comsolcompile`, so the old class ran and silently ignored it. The "lossless metal" study
  therefore ran with almost the original metal and produced the opposite conclusion, which
  looked physically interesting rather than wrong. Cheap guard: make the first case of any
  such study one whose answer is known in advance, or print the resolved material back into the
  status file and read it before trusting the numbers.
- **The outer boundary condition is part of the convergence study for a bound mode with a
  small `Im(n_eff)`, not a cosmetic setting.** On the LR-DLSPPW baseline
  (`Im n_eff = 3.9e-5`), swapping the electric wall for a scattering boundary changed
  `Im(n_eff)` by 22.5% while `Re(n_eff)` moved by 0.002%. For a mode that decays exponentially
  the correct treatment is a closed domain large enough to pass a domain-size check; a
  first-order absorbing condition adds attenuation of its own on the evanescent tail. When the
  mode is lossy (`Im/Re ~ 0.05`, the Ag-strip case) the same swap changed nothing, so the
  sensitivity scales with how small the physical loss is.
- **A planar structure computed as a 2D cross-section needs the lateral invariance imposed, not
  assumed.** A laterally finite window with electric walls is itself a waveguide, and its
  transverse modes land in the same range of effective index as the surface wave, which is what
  made an earlier 2D `ewfd` attempt return window modes. Use a narrow strip - 200 nm was enough
  at 1550 nm - with `PeriodicCondition` of type `Continuity` on the two side walls: only
  harmonics with `k_x = 2 pi m / w` survive, and for a narrow strip every `m != 0` is far above
  the modal range. After this the 2D result matched the analytic root to `2e-9`.
- **`getData()` is not available on an `EvalGlobal` numerical feature.** The error reads
  `Only supported by 'Eval', 'Interp' and 'Global'`. Use `getReal()` and `getImag()`, which
  return `double[expr][solution]`, and set `data`, `innerinput = "manual"` and `solnum` when all
  eigenmodes are wanted. `Interp` does support `getData()`.
- **`setInterpolationCoordinates` takes coordinates in the geometry length unit, not in metres.**
  A model built with `lengthUnit("um")` and fed metre-scale coordinates sampled a region a
  million times too small; the exported "mode profile" came out constant because the whole cut
  sat inside the metal film. Check the model's `lengthUnit` before building the coordinate grid.
- **Pick the number of eigenmodes from where the branch sits relative to the shift, not from
  habit.** With shift-and-invert around a good estimate the target branch is rank 1 by distance,
  and the rest of a 20-mode request is spent on substrate light-line modes of the window. Ranking
  the modes of one solved case by `|N - shift|` costs nothing and showed 10 modes were enough,
  which more than halved the runtime of the whole convergence study.

## Layered Cross-Sections - Recurrent Traps

Lessons from the 2026-08-25 transition model (silicon feed coupled to a PCM plasmonic phase
shifter, COMSOL 6.2).

- **Overlapping rectangles silently thin the layer underneath.** A metal strip drawn as
  `rect(x0, -t_au, w, t_au)` inside a buffer drawn as `rect(x0, -t_pcm, W, t_pcm)` does not sit
  ON the buffer - it occupies its top `t_au`. Under Form Union the overlap becomes its own
  domain and takes whichever material was assigned last, so the stack actually solved is
  `buffer (t_pcm - t_au) | metal | ...`, not `buffer t_pcm | metal | ...`. Ten nanometres of
  gold inset into a 120 nm buffer moved the planar branch from 2.113987 to 2.044375, a shift of
  3 %, with nothing in the log to show for it. Draw each layer from the top of the previous one
  and let the geometry sum the thicknesses.
- **The only reliable check on a two-dimensional cross-section is the planar limit.** Widen
  every lateral dimension of the guiding core together and the answer must walk onto the
  transfer-matrix result for the same vertical stack. If it converges to something else, the
  stack is wrong; if it does not converge at all, the branch is being lost. This caught the trap
  above: the scan plateaued 0.07 away from the film value instead of approaching it.
- **Scale the whole core, not part of it.** Widening a ridge while leaving the metal strip
  narrow does not approach the film: the wide dielectric on either side of the metal carries its
  own higher-index modes, the tracked branch stops being the top one, and the scan wanders
  non-monotonically (2.07, 1.83, 2.09, 2.16 for successive widths). Metal and load have to be
  widened together.
- **Check that a feed can reach the branch at all before scanning its width.** A silicon strip
  of thickness `t` cannot exceed the effective index of the infinite slab of the same thickness:
  1.892394 at 220 nm, 2.085528 at 240 nm, 2.266728 at 260 nm at 1.55 um. If the branch to be
  matched sits above that ceiling, no width will ever be synchronous, and a width scan will
  quietly return the closest quasi-TE mode instead.
- **A butt joint has to be evaluated with both waveguides on the same axis.** Exporting the
  feed mode at its coupler offset and overlapping it with the phase-shifter mode gives the
  overlap of two spatially separated fields - 1.3 % where the real answer was 85 %. Recompute
  the feed mode centred before overlapping.
- **Mode Analysis forgives the sign of the loss; Frequency Domain does not.** A permittivity with
  a POSITIVE imaginary part is a gain medium under the frequency-domain convention, but a mode
  analysis on the same material still returns the right magnitude of `Im(n_eff)` - it just hands
  back the conjugate branch, and against an analytic solver written with the opposite convention
  the magnitudes agree to nine digits, so nothing looks wrong. Carry that permittivity into a
  propagating solve and the power grows along the guide: a straight lossy waveguide went from
  1.23 to 1.37 of the launched power between two planes. Use `Im(eps) < 0` for anything that
  propagates, and check it on a straight section before trusting a junction.
- **A three-dimensional junction is affordable if the metal is a boundary condition.** A 10 nm
  film meshed as a volume over micrometres of propagation is what makes such models impossible;
  `TransitionBoundaryCondition` replaces it with a sheet impedance at no mesh cost, and the whole
  model came to 32 thousand elements and under a minute. Calibrate first: the sheet has no
  thickness, so the stack is short by exactly the film, and the neighbouring layer has to be
  thickened until the sheet model reproduces the meshed cross-section. Here 180 nm of silicon
  load became 184.356 nm and the two agreed to `2.7e-4` in index. The film's properties go on a
  material assigned to the same boundary - the feature's own `userdef` switches are not named
  consistently (`epsilonr_mat` exists, `mur_mat` does not).
- **Two limiting cases pay for themselves before any junction number is believed.** Run the
  structure with each waveguide going straight through: the lossless one must transmit exactly
  one (measured 0.9967), and the lossy one must decay at exactly the rate its own cross-section
  gives (measured ratio 0.9025 against 0.9051). Both were cheap, and the second is what exposed
  the sign error above.
- **`Image` export: `size` takes `manualweb`, not `manual`.** The allowed presets are
  `current`, `manualweb`, `manualprint`, `presentation`; anything else throws "Invalid property
  value - Property: size (Preset)" and, if the call is inside a try block, silently produces no
  picture. Surface plots do export headlessly; Geometry and Mesh plot features still do not.

## Showing That A 3D Model Is 3D

A cut plane through a 3D solution is indistinguishable from a 2D calculation, and a reader who
sees only cut planes will say - correctly, on the evidence - that no 3D result has been shown
(user, 2026-08-26). Volume views cost one extra export from a run that already happened.

- `PlotGroup3D` and its features DO export from a headless batch run: `Surface` (with a
  `Transparency` subnode), `Multislice`, `Isosurface`. This is worth stating because `Geometry`
  and `MeshPlot` still do not.
- Four views answer four different doubts, and they are cheap once the solution exists: the
  computational domain in perspective with transparent walls, so the buried feature is visible as
  a body; only the bodies of the device, without the surrounding air, so the structure is legible;
  a multislice, which no 2D model can produce; isosurfaces, which show where the mode sits.
- Give every surface in one picture the SAME manual colour range (`rangecoloractive`,
  `rangecolormin`, `rangecolormax`) and one legend. With per-feature auto-ranges the same field
  value is painted differently on each body, and the picture misleads.
- Select the bodies with a `Selection` subnode on the plot feature, pointing at the geometry's own
  boundary selections (`geom1_<tag>_bnd`). Blocks only publish those when `selresultshow` is
  `"all"`; the default `"dom"` gives domains only.
- **`zoomextents` on the image export silently overrides the camera.** Two runs with different
  `view("view1").camera().set("position", ...)` produced pixel-identical pictures and threw
  nothing. Either accept the framing the automatic zoom picks, or turn `zoomextents` off and place
  the camera by hand, but do not expect both.
- When a model is 3D, say so in the note next to the numbers - elements, ports, what the ports
  solve - and label the slices as slices. The pictures and the sentence do different jobs.

## Units In Expressions Are Not The Model's Length Unit

A bare number in a COMSOL expression is in SI base units, whatever the geometry's length unit is
set to. A mask written as `(y>0.01)*(y<0.17)` and meant as micrometres asks for "above one
centimetre", which is false everywhere; the integral then returns exactly zero, with no error and
no warning (2026-08-26). Write the units: `(y>0.01[um])*(y<0.17[um])`.

An integral that is exactly `0.000000000e+00` at every sample point is not a physical result. It
means the integrand was identically zero, and a masking condition is the usual reason.

## Building A Wedge As A Solid

A tapered feature drawn as a staircase of blocks is a fallback, not the shape. Two routes give a
real solid with a straight edge, and both work in 6.2 (checked 2026-08-26 with a geometry-only
probe before paying for any solve).

- **`Hexahedron` with eight explicit vertices** is the simplest. A wedge whose footprint runs from
  a tip at one end out to full width and then straight to the far end is a QUADRILATERAL prism,
  so no vertex has to be degenerate. Set `p` as a 3x8 matrix, rows x/y/z, bottom face first.
- **`WorkPlane` + `Polygon` + `Extrude` also works** - the earlier failure ("Object not allowed in
  selection - Object: wp1") was not the API but the order: the work plane has to be RUN
  (`geom("geom1").run("wp1")`) before the extrude will accept it as input. The polygon also needs
  `set("type", "solid")`, otherwise it is a curve and there is nothing to extrude.
- Let Form Union partition the surrounding block with the wedge instead of subtracting it. The
  interface then splits exactly along the wedge edge, and the face under the wedge is the one to
  put a boundary condition on.
- Select that face as an `Intersection` selection of the wedge's own boundary selection
  (`geom1_<tag>_bnd`, needs `selresult on` and `selresultshow "all"`) with a thin `Box` at the
  plane. A box alone cannot separate the wedge's footprint from the rest of the same plane,
  because both reach the same outer edge. The probe returns exactly one face when it is right.
- A taper in the third dimension costs nothing extra: a transition boundary condition takes an
  expression for `d`, so the film can thin toward the tip. **Clamp that expression at BOTH ends**:
  `t_metal*min(max(z/l_wedge, 0.05), 1)`. The condition is applied to the whole metal face, and
  the face does not end where the wedge does - without the upper clamp the film goes on thickening
  along the uniform section behind it, and the structure being measured is not the one intended.
  The lower floor matters too: a zero-thickness sheet impedance is singular.
- **When two variants that should differ give the same answer, the thing you varied is not what
  dominates.** Two thickness tapers whose tips differed by a factor of ten agreed to three digits
  (2026-08-26); the tips were irrelevant because both shared a runaway film behind the wedge. A
  suspiciously equal pair is a bug report, not a physical result - look at what the variants have
  in common, not at what separates them.
- Probe the geometry first, in a program that builds and reports domain, boundary and selected
  face counts and solves nothing. It costs seconds and settles which primitive to use before a
  twenty-minute solve tests the wrong thing.

## Data-Hygiene For Material Tables

- **Tabulated optical constants are downloaded once and treated as source of truth.** Fetch scripts must be idempotent: refuse to overwrite the local CSV unless `--force` is passed, and every downstream script (Mie reference, COMSOL interpolation, plotting) must read the local file with no network call. Re-fetching on every run breaks reproducibility and hides silent format changes from refractiveindex.info / other upstream sources. Include a spot-check of a known value (e.g. Au Johnson-Christy: `n≈0.43, k≈2.455 at 548.6 nm`) at the top of the fetch script and in the README so a corrupted file is caught immediately (learned 2026-07-31).
- **refractiveindex.info raw endpoint has changed URL scheme.** As of 2026-07: the working URL for tabulated Au(Johnson-Christy 1972) is `https://refractiveindex.info/tmp/database/data-nk/main/Au/Johnson.txt` and the file contains two consecutive blocks headed `wl\tn` and `wl\tk` (identical wavelength grids). The older `.../database/data-nk/main/Au/Johnson.yml` and `.../database/data/main/Au/Johnson.yml` return HTTP 404. Parse the two blocks by tracking the current mode after each `wl\t...` header row.
