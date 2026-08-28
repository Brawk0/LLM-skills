# Open-Source EM Solvers

Use this reference when COMSOL is unavailable, when a second independent solver
is needed to check a COMSOL or analytic result, or before spending time on an
open-source package that was already evaluated here.

Each entry states what was actually tried on the user's Windows machine and what
the outcome was. Do not re-litigate a rejected package without new evidence: the
rejection reasons below are reproducible failures, not opinions.

## femwell — validated, use this one

FEM mode solver for photonic and plasmonic waveguide cross-sections, built on
`scikit-fem` and `gmsh`. Install: `pip install femwell` (pulls `gmsh`, `shapely`,
`scikit-fem`, and numpy 2.x).

**Validation status: `validated` (2026-08-19).** Checked against the COMSOL 6.2
mode-analysis exports stored in `phd_lerer/edp/metal_strip_w800/`: a 20 nm silver
strip on an n=1.45 substrate, air above, 6 x 4 um domain, with the same silver
permittivities that were fed to COMSOL. Over the 450-800 nm sweep at 800 nm strip
width femwell reproduces the COMSOL eigenvalues to **0.476 % in `Re(n_eff)` and
1.53 % in `Im(n_eff)`**. Reproduce with
`python edp/metal_strip_w800/scripts/validate_femwell_vs_comsol.py`.

Working practices learned while doing that validation:

- **The computational domain must comfortably exceed the mode's decay length.**
  For weakly bound long-range plasmon modes this is the dominant error source,
  not the mesh. A 3 um wide LR-SPP strip whose field decays over ~200 um returned
  `Re(n_eff)` *below* the cladding index in a 26 um domain — that is a box mode,
  not a waveguide mode. Always compute `1/(k0*sqrt(n_eff^2 - n_clad^2))` from the
  result and compare it with the half-domain; if the mode is not bound, say so
  instead of reporting the number.
- **Mesh the thin metal, but keep the graded zone small.** For 14-20 nm films a
  resolution of 4-6 nm across the metal is enough. The `distance` parameter of the
  resolution dict controls how far that fine zone extends and is what makes the
  mesh explode: 0.5 um around two metal strips in a 44 um domain did not finish,
  while 0.12 um in a 30 um domain solved in minutes at 89k nodes.
- **`n_guess` selects a branch, it does not identify a mode.** A metal strip
  supports a ladder of plasmonic modes; request several and sort them yourself.
  Filter by "above the cladding index and visibly lossy" to drop the nearly
  lossless substrate-slab and box modes, then take the largest `Re(n_eff)` as the
  fundamental. Never trust the solver's ordering.
- femwell requires numpy 2.x. That is incompatible with `emepy` (see below), so
  the two cannot share one environment.

**A caution that came out of the same validation.** femwell exposed a defect in
our own COMSOL post-processing: for one and the same configuration the two
summaries in `edp/metal_strip_w800/results/` disagreed, because the width-sweep
selection had drifted onto modes 1, 2, 3 and 5 as the strip widened. The summary
that carried an explicit field-based `selection_rule` column was the correct one.
Treat a stored COMSOL summary without a documented selection rule as unverified.

## Sphere scattering — Mie packages, validated

For a homogeneous or layered sphere the exact answer is Mie theory, so the
"independent solver" question splits in two: an exact reference, and a
grid-based method that is genuinely independent of it.

**Exact reference — `miepython` and `scattnlay`, both validated (2026-08-19).**
Both install cleanly with `pip install` on native Windows / Python 3.12. A
hand-written Bohren-Huffman implementation (`comsol_au_validation/scripts/
mie_reference.py`) agrees with `miepython` 3.3.0 to **1.3e-9 %** and with
`scattnlay` to **2.8e-10 %** on Au spheres in vacuum and in an n=1.77 matrix
across 400-800 nm — machine precision, so any of the three can serve as the
reference and the other two as its check. Watch the sign convention: BHMIE and
`scattnlay` take `m = n + ik`, while `miepython` 3.x uses `m = n - ik`. Feeding
the wrong one silently returns a *negative* absorption efficiency rather than an
error.

**Independent numerics — discrete-dipole approximation, useful but not a
0.05 %-class arbiter for plasmonics.** An FFT-accelerated DDA with LDR
polarizability (`scripts/dda_solver.py`, ~250 lines of numpy/scipy, no external
package) is genuinely independent of Mie: it discretizes the particle volume and
solves the coupled-dipole system iteratively. Findings from the Au-sphere
validation:

- **On a lossless dielectric it behaves as advertised**: `m = 1.33`, `x = 1`,
  σ_sca converges 0.80 % → 0.31 % as resolution goes 8 → 20 dipoles per radius.
  Run this case first — it certifies the Green tensor, the FFT convolution, the
  wrap-around indexing and the cross-section formulas in seconds.
- **On plasmonic gold it converges only to first order in the lattice step** —
  measured exponent **0.98** on an Au sphere R=25 nm at its 512 nm absorption
  peak (error 13.0 % → 4.4 % as resolution went 8 → 24 dipoles per radius). That
  is far too slow to reach the accuracy COMSOL delivered: 1 % on `σ_abs` would
  need roughly 180 dipoles per radius, i.e. ~2.4e7 dipoles. Scattering converges
  faster (1.9 % → 0.26 % over the same range).
- **Richardson extrapolation in 1/N is what makes it usable.** Fitting three or
  four resolutions and extrapolating to zero step took the R=25 nm vacuum sweep
  to **1.0 % on σ_abs at the resonance peak and 0.9 % worst-case on σ_sca**,
  versus 35 % raw at 20 dipoles per radius. Always report the extrapolated value
  together with the raw series, never the raw value alone.
- **The error is worst where the cross-section is small, not where the resonance
  is.** Intuition says the plasmon pole is the hard place; measurement says
  otherwise. For R=10 nm in an n=1.77 matrix the relative error on σ_abs ran
  -1.9 % at 450 nm, -13 % at 550 nm, then +88 % at 650 nm and +157 % at 800 nm —
  monotonically worse toward the red, where `|eps_Au|` is large, `Im eps` is
  small and `Q_abs` has fallen to ~0.01. Large `|eps|` is the DDA's known weak
  spot, and a nearly-transparent particle turns a small absolute error into a
  huge relative one. Judge a DDA metal run by absolute error against the
  reference, and do not quote its relative error where the cross-section is
  near zero.

## Rejected after evaluation

**PyMieScatt** (`pip install PyMieScatt`) — *not usable as of scipy 1.18*. The
package installs, but `import PyMieScatt` dies with
`ImportError: cannot import name 'trapz' from 'scipy.integrate'`; `trapz` was
removed in scipy 1.14 and the package still imports it at module load. There is
no import-time workaround short of pinning old scipy. Use `miepython` or
`scattnlay` instead — both cover the same single-sphere ground.

**smuthi** (T-matrix multiple scattering) — *install fails* on native Windows /
Python 3.12; the build errors out during dependency compilation. Not pursued
further, because for a *single* sphere a T-matrix code reduces to the Mie
coefficients anyway, so it would not have been an independent check.



**emepy** (eigenmode expansion, `pip install emepy`) — *not usable*. Import fails
because `emepy` depends on `EMpy_gpu`, whose `__init__` does
`from numpy.testing import Tester`, removed in numpy >= 1.25. Pinning
`numpy < 1.25` does not help on Python 3.12: no wheels exist for that
combination, and the source build dies on the missing `distutils`. It would need
a separate Python <= 3.11 interpreter, and even then could not share an
environment with femwell.

**CAMFR** — *not usable*. The `camfr` package on PyPI is a 5.6 kB placeholder
whose `__init__.py` only prints "Camfr: coming soon!". The real project is a
2007-era C++/Python 2 codebase with no maintained Windows or Python 3 build.

**ngslab** (FEM modes of unbounded multilayer planar waveguides with PML/TBC) —
*not installable here*. It is otherwise a good fit, shipping demos for exactly our
problem class (IMI/DMD and MDM gold waveguides). But it builds against PETSc, and
PETSc's configure refuses native Windows Python outright: "Windows python
detected. Please rerun ./configure with cygwin-python." Reconsider only under WSL
or Cygwin.

**MLSWG** — *not usable as a tool, no loss*. MATLAB (GPL-3.0), and there is no
MATLAB on this machine. It solves 1D multilayer TE/TM modes with complex indices,
which is exactly what `phd_lerer/lrspp_coupling/slabmodes/tmm.py` already does,
and that module is validated against Maier's coupled-film equations, the
single-interface SPP limit and a COMSOL-checked three-layer formula. Useful only
as a published cross-check of method, not as software to run.

## Choosing a checking tool

- Homogeneous or layered sphere, any material: exact Mie. Use `miepython` or
  `scattnlay`, and keep a second one as the cross-check — they disagree only at
  machine precision, so a real discrepancy is always your own bug.
- Sphere scattering where an independent *numerical* method is wanted (checking
  a FEM/FDTD setup rather than the physics): DDA with Richardson extrapolation,
  at the few-percent level near the plasmon resonance. Do not promise better,
  and do not use it in the spectral wings.
- Planar multilayer stack, any number of layers, lossy metals: use the analytic
  transfer-matrix solver in `phd_lerer/lrspp_coupling/slabmodes/`. It is exact for
  this class and needs no mesh.
- Two-dimensional cross-section, finite strip width, lossy metals: femwell.
- Propagation along a slowly varying cross-section: no validated open package is
  available. If the transverse problem is single-mode, the adiabatic limit plus a
  Love-criterion check answers the question analytically; see
  `phd_lerer/lrspp_coupling/slabmodes/eme.py`.
- Whenever a reduced model and a full-vector solver disagree, first check whether
  the measured or reference quantity is even a modal quantity. A finite-width
  strip cannot absorb more than the infinite film of the same stack, so a measured
  loss above that ceiling proves a non-modal contribution is present.
