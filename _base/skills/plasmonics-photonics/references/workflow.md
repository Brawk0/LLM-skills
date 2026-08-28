# Plasmonics-Photonics Workflow

Use this reference for substantial plasmonics/photonics tasks: article planning, literature review, EIM/ЭДП benchmarking, PCM material comparison, COMSOL/FEM validation, and mode-branch debugging.

## Work Breakdown

Start by writing the target of the task in one sentence:
- explain a concept;
- create or update an Obsidian note;
- review a paper;
- compare literature;
- validate a reduced-order model;
- debug a COMSOL/CST/FEM result;
- draft or revise an article.

Then identify the relevant object:
- single-interface SPP;
- thin-film LR/SR SPP;
- DLSPP/DLSPPW;
- LR-DLSPP/LR-DLSPPW;
- MDM/MIM/IMI waveguide;
- hybrid plasmonic waveguide;
- PCM-loaded phase shifter/modulator;
- optical antenna or phased-array channel;
- resonator, metasurface, or finite-length structure.

## Required Physical Quantities

For guided-mode work, keep these quantities explicit:
- wavelength or frequency;
- material optical constants and their source;
- geometry and coordinate convention;
- polarization or dominant field components;
- $n_\mathrm{eff}$ and $\beta$;
- propagation length convention: field or power;
- loss convention: dB/length, dB/$\pi$, insertion loss, or extinction ratio;
- light-line/cutoff/leaky-mode position;
- field overlap with metal, PCM, ridge, substrate, and cladding.

Use KaTeX in notes:

$$
n_\mathrm{eff}=\frac{\beta}{k_0},\qquad k_0=\frac{2\pi}{\lambda_0}.
$$

$$
L_\mathrm{power}=\frac{1}{2\operatorname{Im}\beta}
=\frac{\lambda_0}{4\pi\operatorname{Im}n_\mathrm{eff}}.
$$

$$
L_\pi=\frac{\lambda_0}{2\Delta Re(n_\mathrm{eff})}.
$$

$$
IL_{a,c}=\alpha_{a,c}L_\pi,\qquad
\alpha=8.686\,\operatorname{Im}\beta.
$$

Always state whether $Im(n_\mathrm{eff})$ was reported by the solver with a negative sign and then converted to positive attenuation.

## PCM Photonics Checklist

For PCM tasks, record:
- material name and composition: GST, GSST, GSS4T1, Sb2S3, Sb2Se3, In3SbTe2, or other;
  expand ambiguous PCM shorthand at first use. In particular, `GSS4T1`
  is a source-used shorthand for `Ge2Sb2Se4Te1` and should be written as
  `Ge2Sb2Se4Te1 (GSS4T1, a GSST-family composition)` in manuscripts so it
  is not mistaken for a typo of `GSST`;
- amorphous/crystalline/partial state;
- $n(\lambda)$ and $k(\lambda)$ source;
- deposition/crystallization caveat when relevant;
- whether lossless $k=0$ is physical, an artificial control, or a screening simplification;
- switching metric: phase shift, amplitude modulation, trimming, memory, or resonator tuning;
- electrical/thermal switching assumptions if the claim depends on energy, speed, endurance, or heater geometry.

When partial crystallization, intermediate PCM states, or an effective-medium material model is actually part of the task, never merge two approximations without naming them:
- EIM/ЭДП is a waveguide cross-section reduction;
- EMA is a material model for partial crystallization.

Do not add this distinction to a manuscript that compares only amorphous and crystalline PCM states and never uses EMA; introducing an out-of-scope approximation creates an unsupported side topic.

## EIM/ЭДП Benchmarking

Use EIM/ЭДП as a reduced-order workflow:
1. Define vertical slab cuts and horizontal effective waveguide.
2. Solve local TM-like slab modes.
3. Convert local $n_{\mathrm{eff},m}$ to $\varepsilon_{\mathrm{eff},m}\approx n_{\mathrm{eff},m}^2$ only after checking that each root is meaningful.
4. Solve the horizontal effective waveguide.
5. Compare against FEM using state-paired metrics.

Report the result by trust zone:
- `safe`: sign of phase tuning and approximate $L_\pi$;
- `uncertain`: material or geometry ranking that needs hold-out FEM points;
- `FEM-required`: absolute loss, leaky modes, near-light-line operation, residual loss in low-loss PCM cases, final device metrics;
- `breakdown`: no valid slab root, fallback material value, branch swap, or unphysical mode.

## FEM/COMSOL/CST Validation

Before treating a solver result as reference:
- verify material assignment to domains;
- verify wavelength/frequency and unit conversions;
- inspect the field profile;
- run or cite mesh convergence when the claim depends on precision;
- test PML/boundary/domain-size sensitivity for leaky modes;
- compare one or more analytic sanity checks when available;
- track the physical branch across sweeps by field overlap, confinement factor, and power distribution.

Mode numbers are only local labels. Avoid statements like "mode 20 is the same mode" unless the field/overlap evidence supports it.

Distinguish three levels of mode selection and report the level actually used:
- a fixed mode number or sorting by $Re(n_\mathrm{eff})$ provides no continuity evidence;
- choosing the complex root nearest to a reference root is root continuation and can reject an obvious branch swap, but it is not field-based proof that two states contain the same physical mode;
- physical mode tracking requires several candidate modes at each sufficiently small parameter step, consistent field normalization, maximum normalized field overlap, and checks of symmetry, confinement, and power distribution.

Continuation is also the way to separate two branches that become degenerate in
some limit. Coupled thin-film SPP branches merge into the single-interface mode as
the film thickens, so seeding both from one guess at large thickness returns the
same root twice; start where the branches are far apart and step towards the
degenerate limit. When the two branches obey separate parity equations, continue
each equation on its own. Watch for a solver that silently returns a higher-order
mode outside a single-mode window: a bisection on a "monotonic" modal index breaks
there, because monotonicity holds only for the fundamental.

For a large state change such as amorphous-to-crystalline PCM, introduce intermediate numerical continuation steps. If the best overlap is low or two candidates have comparable overlap, reduce the step and temporarily track both solutions instead of forcing a single assignment. Treat an interpolation used only for continuation as a numerical path, not as a physical model of partial crystallization unless an EMA or another material model has been defined.

When reconstructing a bound-mode field from transfer-matrix coefficients, enforce the forbidden growing-wave coefficient in each exterior half-space as exactly zero before normalizing or integrating the field. A small root residual can multiply an exponentially growing tail over the numerical padding and create false confinement jumps or low field overlaps. Verify the result by reducing the continuation step and increasing the field-integration padding.

## Validating A Reconstructed Field

A dispersion root that matches literature does not prove the reconstructed field
vector is right. Quantities normalised by their own power - overlap integrals,
confinement factors, propagation loss - are blind to a constant factor on a single
field component, so a scaling error in one component can survive every check a
mode solver usually runs and only surface when the field is plotted or fed to a
downstream calculation.

Substitute the reconstructed `E` and `H` back into Maxwell's equations. Check the
**order of the residual in the grid step, not its magnitude**. The magnitude is
set by the step, and in a plasmonic problem the step is dictated by the metal skin
depth of tens of nanometres, so any absolute threshold has to be retuned per
geometry and will mask a real error. A correct field leaves only the
finite-difference error, which falls by four when the grid is halved; a wrong
formula gives a step-independent residual. Report the observed order.

Three ways this check is easy to get wrong, all seen in practice:

- refine every axis at once. Refining only the transverse grid leaves the
  longitudinal contribution constant and drives the observed order to zero, which
  looks like a broken field but is a broken test;
- make the validation grid resolve the thinnest metal layer. If no point inside a
  14 nm film carries a full stencil, the metal is excluded from the residual at
  the coarse level and re-enters at the fine level with its own large error, and
  the observed order comes out negative;
- exclude stencils that straddle a material interface. Normal `E` is discontinuous
  there and the derivative of tangential `E` is kinked, so a finite difference
  across an interface measures the discontinuity, not the residual.

Add one independent scale check that does not involve derivatives at all, for
example the ratio of field components in a cladding against its closed form.

**An orthogonality test on a mirror-symmetric structure proves nothing.** In a
symmetric stack the coupled modes have opposite parity, the integrand is odd, and
the conjugated and unconjugated overlaps both vanish - by symmetry, not because
either form is the right one. A wrong choice of form passes such a test and
survives until the first asymmetric problem. Test on a structure that is both
lossy and free of mirror symmetry; breaking the cladding indices apart is enough.
For a 14 nm gold film a cladding asymmetry of 2e-3 separates the two forms by
five orders of magnitude, while both stay at 1e-11 in the symmetric case. Note
that a long-range mode unbinds quickly with asymmetry, so check that the modes
are still bound at the asymmetry used.

## Literature And Article Claim Control

For article drafts and literature reviews, maintain a reviewed-works register with:
- title, year, authors/venue;
- DOI/URL/local path;
- how it was found;
- verification status;
- one-line relevance;
- caveat.

Use primary sources for:
- device performance metrics;
- "first" or novelty claims;
- material optical constants;
- solver/method limitations;
- conference requirements.

Prefer reviewer-safe claims:
- "failure-aware screening workflow";
- "state-paired EIM-vs-FEM comparison";
- "phase metrics are usable, loss metrics require FEM";
- "branch-aware validation is required before final device claims".

Avoid unsafe claims unless verified:
- first PCM modulator;
- first EIM use for plasmonic waveguides;
- EIM replaces FEM;
- good $L_\pi$ agreement validates absolute propagation loss;
- a fixed solver mode number proves branch continuity.
