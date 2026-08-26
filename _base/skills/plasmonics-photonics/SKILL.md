---
name: plasmonics-photonics
description: Specialized PhD/research workflow for plasmonics, nanophotonics, integrated photonics, SPP/ППП, DLSPP/DLSPPW, LR-DLSPP/LR-DLSPPW, MDM/MIM/IMI plasmonic waveguides, optical antennas, phase-change-material photonics and modulators (PCM, GST, GSST, Sb2S3, Sb2Se3, IST), EIM/ЭДП/effective-index screening, COMSOL/FEM/CST mode analysis, branch tracking, propagation loss, L_pi, insertion loss, and source-backed article or literature-review work in this domain.
---

# Plasmonics Photonics

## Purpose

Use this skill for the user's specialized plasmonic and photonic research context. It narrows broad scientific work into domain-specific reasoning about guided optical modes, plasmonic waveguides, PCM photonics, reduced-order models, and full-wave validation.

For general Obsidian note style, checkpoint discipline, paper-note structure, term-note capture, and PhD vault hygiene, use the general `scientific-work` rules when available. This skill adds the plasmonics/photonics physics and claim-control layer.

## Note Capture (non-negotiable)

Plasmonics/photonics conceptual work must be captured back into the vault by default, applying `scientific-work` note-capture rules 12-14 even when that skill is not separately loaded. Do not wait to be asked, and do not answer only in chat:
- for "объясни / разбери / что тут происходит / как это получается" explanations of PhD/vault material, create or update the nearest relevant note and answer with a link (scientific-work rule 12);
- for a clarifying question about the content of an existing note - for example "это точная формула или приближение", "откуда берётся эта формула", "почему одна формула, если параметр/χ⁽³⁾ не универсален", "что здесь означает этот множитель" - after answering, add a compact clarification to the relevant section of the source note, following `references/obsidian-style.md` from the shared `scientific-work` skill (rule 14);
- for a stated physical guess or hypothesis, record it in the nearest appropriate note with an explicit status (rule 13);
- whenever a note in this domain is opened or edited for any reason, run the illustration check from the `Visuals` section of `references/obsidian-style.md` over the whole note, including notes written before that rule existed. In this domain the missing picture is almost always one of five: a mode profile, a dispersion branch, a geometry/layer stack, a loss budget, or a state-paired comparison. Search the vault first — earlier paper notes and calculation folders usually already hold a usable figure — and caption a reused figure for the geometry and materials it was actually computed for.

Skip the note update only when the user explicitly asks not to write files, or the question is clearly casual and unrelated to vault content. When a task begins touching vault notes, load the `scientific-work` note-capture and `obsidian-style` rules if they are not already in context, so this behavior does not depend on remembering to open that skill.

## Self-Improvement And Publishing

When plasmonics-photonics work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact domain rules, validation checks, reusable modeling patterns, source-audit lessons, or formula conventions in this skill or a focused `references/<topic>.md` file. Do not store secrets, credentials, private raw datasets, unpublished full measurements, copyrighted source text, generated logs, raw project/customer material, or one-off project facts in the skill.

Before materially editing this skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check: fetch `origin main`, compare local `HEAD` with `origin/main`, fast-forward if local is behind and the relevant working tree is clean, and inspect dirty/ahead/diverged states before continuing.

After materially updating this skill, validate it when feasible, then commit and push the relevant skill changes to the owning repository by default unless the user explicitly says not to. Stage only relevant skill files and repository metadata.

If publishing encounters remote changes or merge conflicts, resolve them autonomously when the intended final meaning can be determined from the files, commit history, nearby rules, and the user's instruction. Preserve compatible rules from both sides, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.

## Start Of Work

For nontrivial domain work, first preserve context:
- read or create the nearest project-local `CODEX/Контекст задачи Codex - <topic>.md` or `CODEX/План задачи Codex - <topic>.md`;
- record the objective, current status, local source notes/files, key formulas, numerical facts, caveats, assumptions, and next steps;
- keep reviewed-works registers for literature and source audits;
- after compaction, interruption, or a long gap, read the active goal/plan and project checkpoint before substantive reasoning.

For reusable plasmonics/photonics calculation code, mode-analysis scripts, and validated diagnostics, make intermediate git commits when a repository is available and the user has not opted out. A commit is useful when the code is reproducible and scientifically interpretable: it either agrees with an analytic estimate, literature value, previous COMSOL/FEM/CST result, or another check, or it exposes a meaningful discrepancy. Commit messages or nearby notes should state what the result was compared against and whether the status is `validated`, `diagnostic`, `discrepant`, or `unverified`. Do not commit bulky raw solver artifacts such as large `.mph` files unless the user explicitly wants them versioned.

Search local PhD/vault context before giving scientific conclusions. Prefer local notes, model diaries, PDFs, extracted tables, scripts, and COMSOL/CST logs over memory. Mark uncertain statements as hypotheses.

## Domain Workflow

Separate every task into four layers:
- **physics:** SPP/DLSPP/LR-DLSPP mode type, confinement, light-line position, cutoff/leaky behavior, material overlap;
- **materials:** optical constants, PCM state, wavelength, composition, crystallization assumption, metal loss convention;
- **method:** analytic dispersion, EIM/ЭДП, transfer matrix, FEM/COMSOL, CST, volume integral, FDTD, or experiment;
- **claim:** what the result can and cannot support in an article, report, or dissertation.

For PCM/plasmonic phase shifter work, compare state-paired metrics rather than isolated states:
- $Re(n_\mathrm{eff})$, $Im(n_\mathrm{eff})$, and $\beta=k_0n_\mathrm{eff}$;
- $\Delta Re(n_\mathrm{eff})$ between amorphous and crystalline states;
- $L_\pi=\lambda_0/(2\Delta Re(n_\mathrm{eff}))$;
- propagation length and loss per length;
- insertion loss on $L_\pi$;
- branch identity and field overlap.

## Validation Rules

For EIM/ЭДП and other reduced-order models:
- treat them as screening/pre-design tools unless full validation supports stronger claims;
- use them confidently for phase-trend checks only after confirming the mode branch is meaningful;
- never present agreement in $L_\pi$ as proof of accurate absolute loss;
- mark no-root or fallback values as `EIM-breakdown / no valid root`, not ordinary numerical results;
- when a manuscript discusses a missing local EIM root and a fallback material index, state three facts explicitly: which local mode was not found, which numerical value was substituted, and that the resulting value is diagnostic rather than a physical mode. Explain why the next EIM step still needs a value for that region and distinguish a numerical assignment in the equivalent model from a physical material replacement. Do not compress this into phrases such as «the region is replaced by the cladding», «not an ordinary operating point», or «the result was obtained with a conditional substitution of the SiO₂ index». When no bound mode exists, do not call the omitted contribution the film's «guiding action»: a high-index film may redistribute the field without supporting a bound mode. State instead that assigning the cladding index to the equivalent region removes the film's refractive-index contrast from that model and therefore omits its influence on the field distribution;
- explain a fallback in a short causal sequence: the local mode is absent, the next EIM step still requires a regional effective index, an auxiliary value is assigned only to continue the reduced calculation, that value is not a modal result, and the point requires full-vector verification. Do not begin with «this does not mean...» before explaining why the assignment was introduced, and do not pack the whole chain into one dense disclaimer;
- retain negative examples as part of a failure atlas.

For COMSOL/FEM/CST mode analysis:
- define the sign convention for $Im(n_\mathrm{eff})$, $\operatorname{Im}\beta$, propagation length, dB/length, and dB/$\pi$;
- validate mesh, domain size, PML/boundary settings, and material assignments before calling a solver result a reference;
- track modes by field profile, overlap integral, confinement factor, and power distribution rather than by fixed mode number alone;
- check whether residual loss comes from PCM, metal absorption, radiation/leaky channels, boundaries/PML, or numerical artifacts.
- If mesh/domain/PML convergence, wavelength sweep, or field-based branch
  tracking has not actually been performed, describe the solver comparison as
  diagnostic or preliminary. Do not leave a manuscript placeholder for this
  inside the article body, and do not upgrade a fixed-mode-label run into a
  final FEM benchmark by wording alone.
- Do not introduce PML, scattering-boundary, or other solver-implementation terminology into a manuscript that does not use that full-vector model. State the general validation requirement (mesh, domain size, and external-boundary sensitivity) in the paper; keep concrete future solver settings in the project checkpoint until they are actually used and reported.

For manuscript and DOCX work in this domain:
- distinguish the method from the modal quantity in Russian prose. When the manuscript identifies EIM with the established Russian term «метод эффективной диэлектрической проницаемости (ЭДП)», introduce the full method name and then use ЭДП. Introduce the quantity separately as «эффективный показатель преломления (ЭПП) моды», $n_\mathrm{eff}$; never shorten it to the ambiguous «эффективный показатель». After the first definition in an independent scope, use ЭДП for the method and ЭПП or $n_\mathrm{eff}$ for the quantity consistently. An IEEE abstract and the main text are independent abbreviation scopes;
- in Russian prose, call $\lambda_0$ «длина волны в свободном пространстве» and $k_0$ «волновое число свободного пространства». Reserve «в вакууме» for a physical statement in which vacuum is actually the propagation medium, not as the default name of the free-space reference quantities;
- describe each planar reference by its actual layer stack and invariant direction before using a short label such as S3. If the planar model is invariant perpendicular to the slice plane, say so explicitly and state the resulting infinite layer width. Avoid undefined phrases such as «central active slice»: use «the vertical stack through the metal strip and ridge» at first mention, then the defined slice label;
- when symmetry belongs to identical dielectric surroundings of a metal film, do not write «симметричная металлическая плёнка»: the film itself is not the symmetric object. Write «тонкая металлическая плёнка между одинаковыми диэлектрическими средами» or name a «симметричная структура dielectric/metal/dielectric». In reader-facing prose, prefer «две моды» to unexplained «две ветви» unless the dispersion branches have already been introduced;
- when a manuscript repeatedly uses local-cut labels such as S1, S2, and S3, map them visually to the waveguide cross-section instead of relying only on a prose list. Show representative cut positions on the geometry, the corresponding layer stacks, or both. Verify that every marked line intersects exactly the materials named for that cut and that labels remain legible at the final one- or two-column size. If cut lines collide with dimensions or material labels, use a companion stack panel or a full-width combined figure rather than crowding the cross-section;
- do not call a reduced model a «strict planar calculation» without naming what is solved exactly and which approximation is omitted. If a dispersion equation is solved directly for S3 but finite strip width is still absent, write «calculation of the planar S3 structure without the horizontal EIM approximation», then shorten it to «S3 calculation». Never let «strict» imply a full-vector reference or an exact device model;
- translate mesh refinement concretely as «последовательное уменьшение размера элементов расчётной сетки». Do not write «измельчение сетки» or imply that only one generic cell is reduced; mesh convergence requires repeated calculations on successively finer finite-element meshes;
- do not use «полновекторный расчёт», «полноволновой расчёт», «векторный расчёт», or «строгий расчёт» as unexplained umbrella labels in reader-facing Russian prose. At first mention, name the actual problem and method, for example «расчёт собственных мод поперечного сечения волновода с полоской конечной ширины методом конечных элементов». Thereafter shorten by the local purpose: «расчёт методом конечных элементов», «модель, построенная методом конечных элементов», «проверка распределения поля в структуре конечной ширины», «расчёт потерь методом конечных элементов», or «оптимизация поперечного сечения методом конечных элементов». The forms «конечно-элементный расчёт», «конечно-элементный анализ» and «конечно-элементная модель» are attested in Russian engineering literature, but in the user's reader-facing manuscripts prefer the explicit method name «метод конечных элементов» and the construction «расчёт методом конечных элементов». Use «векторная задача» only when the scalar/vector formulation itself is being discussed and defined;
- use the established Russian photonics term «гребень» / «гребневый волновод» for a ridge / ridge waveguide; do not replace it with the generic «выступ» merely to make the word sound simpler. At first use, make the geometry self-explanatory by stating where the ridge is located and, when useful, its shape, for example «кремниевый гребень прямоугольного сечения над золотой полоской». Do not rely on a reference to a figure to define the geometry in an abstract;
- do not translate *dielectric-loaded* mechanically as «с диэлектрической нагрузкой» when the phrase can be mistaken for an electrical load. At first mention, describe the geometry directly, for example «волновод с диэлектрическим гребнем над металлической полоской», and then use the defined designation LR-DLSPP. Keep the English expansion only where the abbreviation needs to be decoded;
- for a finite-width gold stripe in a plasmonic waveguide, use «полоска золота» at first mention or «золотая полоска» / «металлическая полоска» thereafter. Do not call a 100-nm-wide gold element «микрополосок»: that word is used in other fields for micrometre-scale strips and is ambiguous here. Do not use «микрополосковая линия» unless the structure is actually a microstrip transmission line. Do not introduce «нанополоска» solely because the width is nanoscale when the exact dimensions are already stated;
- distinguish the constituent parts of a waveguide from its supporting substrate. If a PCM buffer, a finite gold strip, and a silicon ridge together form the modeled waveguide, write «волновод образован буферным слоем из PCM, полоской золота и кремниевым гребнем» rather than «волновод содержит золотую полоску». State the substrate separately, for example «структура расположена на диэлектрической подложке из диоксида кремния (SiO₂)». Do not include the substrate among the waveguide constituents unless the adopted physical definition explicitly treats it as part of the waveguide;
- justify a PCM list before presenting the material names. State each material's own relevant properties at the operating wavelength: the real-index change and the loss-related imaginary part in the amorphous and crystalline states. Do not introduce better/worse comparisons with another PCM unless that comparison is an explicit research question. When the accepted 1550-nm data give a non-negligible imaginary part for crystalline GSST, justify GSST by its state-paired real-index change rather than calling it low-loss in both states; present Sb₂S₃ and Sb₂Se₃ as low-absorption choices only when the source data support low absorption in both states;
- for propagation loss per unit length in the user's Russian photonics manuscripts, prefer «коэффициент затухания $\alpha$» with explicit units such as дБ/мкм, or the standard phrase «потери распространения по волноводу». Treat «погонные потери» as an attested but less precise synonym. Distinguish this per-length quantity from «вносимые потери»: if $IL=\alpha L_\pi$ excludes coupling and transitions, call it the calculated insertion loss of the active section and state what is excluded;
- match the stated scope to the work actually performed. If the paper assesses a calculation method, write «применимость метода к расчёту», not «к проектированию». Use «предварительный» only when the text explicitly contrasts that stage with a later verification or optimization stage. For long-range modes, prefer the natural construction «мода с большой длиной распространения»;
- treat solver-assigned mode numbers as implementation labels, not physical mode identifiers. Omit them from reader-facing conclusions and limitations unless the numbering itself is part of a reproducible software-specific procedure. State the physical requirement instead: as parameters vary, the field profile should change smoothly and remain localized in the same waveguide regions. Similar values of $\operatorname{Re}n_\mathrm{eff}$ alone do not establish that two solutions represent the same mode;
- in reader-facing Russian prose, avoid the redundant adjective in phrases such as «одна и та же физическая мода» when merely distinguishing between modal solutions. Write «одна и та же мода», «другая мода», or «та же модовая ветвь». Reserve «физически допустимое решение» for an explicitly defined distinction between a modal solution and a spurious numerical root, and state the admissibility criterion;
- protect the physical divisions in the standard guided-mode formulas:
  $n_\mathrm{eff}=\beta/k_0$, $k_0=2\pi/\lambda_0$,
  $L_\mathrm{power}=1/(2\operatorname{Im}\beta)=
  \lambda_0/(4\pi\operatorname{Im}n_\mathrm{eff})$, and
  $L_\pi=\lambda_0/(2\Delta\operatorname{Re}n_\mathrm{eff})$;
- reject generated text where TeX cleanup collapses these into multiplication
  or adjacency, such as `n_eff=betak0`, `k0=2pilambda0`, `12Imbeta`, or
  `lambda04piImn_eff`.

For literature and article claims:
- do not claim a first PCM modulator, first PCM phase shifter, first plasmonic PCM device, or first EIM use for DLSPP unless primary literature verification supports it. Do not turn this caution into an unsolicited manuscript sentence denying priority; when priority is not part of the contribution, omit priority language and state the actual scientific or methodological result positively;
- frame EIM/ЭДП work as a failure-aware screening workflow when loss metrics diverge from FEM;
- distinguish EIM/effective-index waveguide reduction from EMA/effective-medium approximation only when partial crystallization, intermediate PCM states, or an EMA material model is actually in scope; do not introduce an EMA disclaimer into a paper that compares only amorphous and crystalline states;
- cite primary papers or official solver documentation for claims about device performance, solver behavior, or method limitations.
- before finalizing a plasmonics/photonics article or conference paper, follow the `scientific-work` final GPT/ChatGPT review rule when running as Codex. In Claude Code that rule does not apply: run the independent source-backed verification pass described in the same section instead, and do not flag the missing GPT review as a blocker.

## Detailed Reference

Read `references/workflow.md` for substantial work involving articles, literature reviews, EIM/ЭДП benchmarking, PCM material audits, COMSOL/FEM validation, or mode-branch troubleshooting.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
