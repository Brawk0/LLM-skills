---
name: apede-ieee-conference-article
description: Prepare, format, review, and package a conference paper for APEDE (IEEE "Actual Problems of Electron Devices Engineering", Saratov) and any conference that uses the standard IEEE two-column Xplore paper template. Use for APEDE paper, IEEE conference article, IEEE Xplore camera-ready, two-column IEEE format, title/abstract without math or symbols, IEEE numbered [1] reference list, figure/table styling, equation-editor formulas, converting an Obsidian draft note into a submission-ready IEEE DOCX, and removing template guidance text before submission.
---

# APEDE / IEEE Conference Article

## Purpose

Turn the user's research results (Obsidian notes, phd_lerer calculations,
figures) into a camera-ready paper that passes the formal requirements of
the **IEEE conference template** used by APEDE and similar IEEE conferences,
so it is accepted into IEEE Xplore on first submission. Non-compliant papers
(especially ones that still contain template guidance text) can be rejected
or left unpublished, so formal compliance is part of the science getting out.

APEDE = International Conference "Actual Problems of Electron Devices
Engineering" (Saratov State Technical University, Russia); proceedings are
published in **IEEE Xplore**, in **English**, using the standard IEEE
conference paper template.

Primary rule sources (in priority order):
1. `references/conference-rules.md` in this skill - verified digest of the
   official IEEE conference template supplied for APEDE
   (`plasma_mdm_modulator_article_2026/APEDE/APEDE правила написания статьи.docx`,
   which is the stock IEEE two-column template);
2. the live IEEE author resources - recheck before an actual submission:
   - https://www.ieee.org/conferences/publishing/templates.html (Word/LaTeX templates),
   - the specific APEDE call-for-papers / conference site for the current year
     (page limit, submission portal, PDF-eXpress or IEEE PDF check requirements),
   - the conference's IEEE Xplore-compliant PDF checker instructions.

## Division Of Labour With Other Skills

- Universal venue-agnostic manuscript discipline (source-of-truth selection,
  claim/number QA, citation-order checks, safe count-asserted bulk edits,
  submission-blocker checks): `scientific-article-writing`. Venue rules in
  this skill override it where they conflict.
- English kept free of Russian-lab insider calques and working-title jargon
  when the paper is written or translated from a Russian working draft (the
  mirror check), and де-кальке for any Russian-language version:
  `ru-language-purity`.
- Scientific content, claim control, checkpoints, final GPT review:
  `scientific-work` (final-review rule is mandatory for submission drafts)
  and `plasmonics-photonics` (domain claim rules).
- Markdown -> DOCX mechanics (pandoc/reference docx, formula sanitizing,
  QA of the generated file): `markdown-to-docx`. This skill defines WHAT
  the paper must contain; `markdown-to-docx` defines HOW to convert.
- Repository work for calculation code cited in the paper: `phd-lerer-repo`.
- Journal (not conference) manuscripts for «Оптика и спектроскопия» and
  other Ioffe journals: `optics-spectroscopy-article`. Many WORD-mechanics
  lessons are shared with this skill, but the FORMAL rules differ (see
  "Where IEEE differs from the Ioffe journal rules" below) - do not copy
  journal rules blindly.

## Self-Improvement And Publishing

When paper-preparation work reveals a durable, reusable lesson, use the
`skill-learning` policy. Save compact rules about the IEEE template,
reviewer/editor feedback, submission-portal behavior (IEEE PDF eXpress,
IEEE Author Portal), reference formatting, or conversion pitfalls in this
shared-base skill or a focused shared-base `references/<topic>.md` file. Do
not store secrets, credentials, private content, unpublished manuscripts,
referee correspondence, copyrighted source text, generated logs, or one-off
facts in the skill.

Before materially editing this skill, applying self-learning updates, or
publishing changes, run the owning repository's freshness check: fetch
`origin main`, compare local `HEAD` with `origin/main`, fast-forward if
local is behind and the relevant working tree is clean, and inspect
dirty/ahead/diverged states before continuing.

After materially updating this skill, validate the shared base and
adapters when feasible, then commit and push the relevant skill changes to
the owning repository by default unless the user explicitly says not to.
Stage only relevant skill files and repository metadata. Split commits by
semantic block; avoid vague rollups such as "skill update".

If publishing encounters remote changes or merge conflicts, resolve them
autonomously when the intended final meaning can be determined from the
files, commit history, nearby rules, and the user's instruction. Preserve
compatible rules from both sides, consolidate duplicates, rerun
validation, commit the resolved result, and push. Stop only when
resolution would require guessing unavailable technical meaning, exposing
protected content, discarding user work, or using unavailable repository
permissions.

## Workflow: From Notes To Camera-Ready

1. **Checkpoint first.** Create or update the project checkpoint
   (`CODEX/Контекст задачи ... .md`) per `scientific-work`: objective,
   target conference and track, source notes, figure inventory, claim
   status, page-limit budget, open risks.
2. **Draft as an Obsidian note** in the paper's own folder near the source
   notes. Use the IEEE structure from `references/conference-rules.md` from
   the start (title, author block, Abstract, Keywords, numbered sections,
   Acknowledgment, References, then tables and figures with captions) so
   conversion is mechanical, not creative. Write in **English**.
3. **Claim control.** Every quantitative claim must trace to a validated
   calculation (repo script + commit) or a cited source. Follow
   `plasmonics-photonics` rules: no "first ever" claims without literature
   verification; mark reduced-order results as such; state the sign
   convention for eps explicitly when both e^{+iwt} and e^{-iwt} sources
   are mixed.
4. **Apply the formal rules** - read `references/conference-rules.md` fully
   and walk the paper against its checklist section by section (title/abstract
   restrictions, headings, abbreviations, units, equations, figures, tables,
   references, page limit).
5. **Convert to DOCX** with `markdown-to-docx` (see WORD-mechanics lessons
   below; reuse the `optics-spectroscopy-article` conversion lessons for
   Word-safe math and broken-formula QA, but keep the IEEE dash rule). The
   camera-ready target is the two-column IEEE template; when a real IEEE
   `.docx` template file is available, convert with it as pandoc
   `--reference-doc` or paste content into the template and apply its named
   styles (paper title, Author, Abstract, Keywords, Heading 1-5, figure
   caption, table head, references).
6. **Strip ALL template guidance text.** The stock template's instructional
   paragraphs ("This electronic document is a live template...", "Identify
   applicable funding agency here...", etc.) must be completely removed -
   leftover template text is an explicit grounds for non-publication.
7. **Produce the IEEE-Xplore-compliant PDF** and, if the conference uses it,
   run it through IEEE PDF eXpress / the conference PDF checker (all fonts
   embedded, correct page size, no security settings). Export each figure as
   a separate high-resolution file (>=300 dpi raster, or vector EPS/TIFF).
8. **Final review.** Run the `scientific-work` final GPT/ChatGPT review pass
   on the near-final draft (argument, novelty framing, missing literature,
   venue fit, English quality), verify its suggestions against sources, then
   fix. Only then call the draft submission-ready.
9. Record the resulting files and their status in the checkpoint.

## WORD Mechanics Lessons (reused, with IEEE deltas)

These carry over from `optics-spectroscopy-article` / `markdown-to-docx`;
apply them here EXCEPT where the IEEE delta is called out.

1. **Headings must be black.** Pandoc/Word default blue headings are an
   instant "AI-generated" tell. Recolor Heading/Title styles to RGB(0,0,0)
   (python-docx pass); standard hyperlinks in references are fine. (Same as
   the journal skill.)
2. **Word-safe math only.** No `\operatorname{}` and no `\text{}` inside TeX
   math - via pandoc they surface in Word as literal `operatorname` and
   quoted subscripts (`ε_"eff"`). Use `\mathrm{}` (e.g.
   `\mathrm{Im}\,\varepsilon_{\mathrm{eff}}`). Keep display formulas shallow
   (introduce shorthand symbols instead of deep nested fractions). This is
   the "битые формулы" (broken-formula) lesson - it applies unchanged.
3. **No formulas built from pieces.** Each display (numbered) equation must
   be one Word equation object, not text + inline image + table stitched
   together. Number equations consecutively; numbers flush right in
   parentheses `(1)`; refer to them as "(1)", not "Eq. (1)" or "equation
   (1)" except at the start of a sentence.
4. **Convert with plain pandoc markdown, not the gfm+sanitizer path** - the
   sanitizer mangles math and the `gfm` reader leaves dashes unconverted.
   Use `pandoc input.md --from markdown-smart --to docx --standalone
   --wrap=none --resource-path "<figures>" --output out.docx`.
5. **QA the produced DOCX** by inspecting `word/document.xml` and
   `word/styles.xml`: zero matches for `operatorname`, `\text{`, `<m:t>"`,
   raw formula underscores, escaped pipes `\|`, and leftover template
   guidance sentences; no blue heading colors; equations present as
   `<m:oMath>` with stacked fractions `<m:f>`; `<m:oMath>` count roughly
   matches the number of formulas.

### IEEE DASH DELTA (important, differs from the journal skill)

The `optics-spectroscopy-article` rule "only the plain hyphen `-`, never
`--`/`—`" is a **Ioffe-journal-specific user preference and does NOT apply
to IEEE papers.** The IEEE template explicitly requires:
- a **long dash (minus sign, U+2212 or an en/em dash as the template shows)
  rather than a hyphen for a minus sign** in equations and math;
- an en dash `–` for page ranges in references (`pp. 529–551`).
Still never leave TeX-style `--` visible in body text; render it as the
correct typographic dash. So: keep the broken-formula/Word-safe-math reuse,
but drop the "plain hyphen everywhere" reuse.

## Session Lessons (2026-07-05, APEDE-2026 EIM/PCM paper)

Compact, verified rules from preparing a real APEDE camera-ready. Apply all
of them; automate the checks where a recipe is given.

1. **Reference order is checkable and fixable by script.** IEEE requires
   numbering by first appearance. Check: extract `[n]` and `[a]–[b]` ranges
   from the body in reading order (regex `\[(\d+)\](?:[-–]\[(\d+)\])?`,
   expand ranges), assert the first-appearance sequence equals `1..N`. Fix:
   build an old->new map, apply in ONE regex pass over the whole file, then
   re-sort the reference-list block; count-assert every replacement. Never
   renumber by hand.
2. **Abbreviations at first BODY use.** Definitions in the abstract do not
   count. Check each acronym (FEM, TM, SPP, PML, BEOL, GST, ...) has its
   `(ACRONYM)` definition at or before first body use.
3. **Typography sweep:** no `um` (use `µm`), no e-notation in prose
   (`9e-4` -> `0.0009` or a power of ten), leading zeros (`0.25`),
   `Abstract—`/`Index Terms—` with em dash, en dashes in `[1]–[4]` and
   `pp. 529–551`. Index Terms alphabetized.
4. **Figures:** >=300 dpi (matplotlib `dpi=300`), Times New Roman ~8 pt,
   axis labels `Quantity (unit)` (never `Quantity/unit` or bare units),
   multi-panel as (a)/(b) under one caption, hatch/edgecolor so bars stay
   readable in grayscale.
5. **Numeric QA before trusting any table:** recompute derivable values
   (e.g. `L_pi = lambda0 / (2 * dRe_neff)`, `IL = 8.686 * Im(beta) * L_pi`)
   and cross-check against the source CSVs in the article folder.
6. **Bilingual drafts diverge.** Establish which draft is the scientific
   source of truth (the one carrying the latest validation results) before
   formatting anything; re-sync the other language, keep reference numbering
   identical in both, and log the sync in the draft's "Правки" section.
7. **Material constants belong in the paper.** If they are missing, recover
   them from the run CSVs (e.g. `pcm_*_vs_comsol.csv` has `n_pcm_real/imag`
   columns) rather than leaving a placeholder; keep the "verify against the
   primary source" caveat.
8. **Transliteration:** щ -> shch (Клещенков -> Kleshchenkov). Verify
   author-preferred spellings before submission.
9. **The supplied APEDE template docx is ISO Strict OOXML**
   (`purl.oclc.org` namespaces): pandoc and python-docx both fail on it.
   Parse `word/document.xml` directly with namespace
   `http://purl.oclc.org/ooxml/wordprocessingml/main`.
10. **Windows file lock:** a DOCX open in Word raises PermissionError on
    save. Close only the target Word document(s) for the article path via
    Word COM, then rebuild the canonical DOCX name. Do not leave `_fixed`,
    `_test`, `_v2`, backup, or stale working-draft DOCX variants in the
    article folder as the delivered state.
11. **Check the deadline against today's date at task start** and flag if
    passed - conference deadlines are often extended, but the user must
    confirm.
12. **Author list changes** (add/reorder/respell) are bulk edits: do them
    with one count-asserted script across ALL article files (drafts in both
    languages, build scripts, metadata blocks). Default order
    student-first / supervisor-last, but confirm with the user. In the IEEE
    template each author needs their own block with e-mail.
13. **This conference template uses `Keywords—`, not `Index Terms—`.**
    "Index Terms" is the IEEE-journal habit and creeps in from old drafts -
    check the label against references/conference-rules.md, not memory.
14. **Check the template's non-body parts too**: the page-1 footer carries
    the IEEE copyright-notice placeholder and the first page a sponsors
    text box (see references/conference-rules.md) - a digest built only
    from the body text misses them.
15. **Layout defects a generator produces that must be checked against the
    template example** (all verifiable in the built DOCX):
    body text must be JUSTIFIED not left-aligned; display equations must
    carry an explicit run size equal to the body size (Word defaults OMML
    to 11 pt while body is 10 pt); tables use horizontal rules only (no box
    grid) at 8 pt; wide tables/figures span both columns via a 1-column
    continuous section.
16. **Render and LOOK, do not only parse XML.** Layout is judged by eye:
    render the built DOCX to per-page images and view them against the
    template's own "TABLE I" and figure examples before calling it done.
    Use `scientific-article-writing` scripts/render_docx_pages.py (Word COM
    or LibreOffice -> PDF -> PNG). The user must not have to catch visual
    nuances by hand.
13. **EIM/PCM formula artifacts are submission blockers.** In DOCX builds,
    propagation formulas must preserve division: `n_eff = beta/k0`,
    `k0 = 2*pi/lambda0`, `L_power = 1/(2 Im beta) =
    lambda0/(4*pi Im n_eff)`, `L_pi = lambda0/(2 Delta Re n_eff)`, and
    `IL = alpha L_pi`. Use OMML/Word equations for these in camera-ready
    outputs; at minimum, a working draft must show explicit slashes or
    stacked fractions. Reject collapsed strings like `n_eff=betak0`,
    `k0=2pilambda0`, `Lpower=12Imbeta`, and visible layer-stack escapes
    such as `air\ |\ PCM\ |\ SiO_2`.
14. **Inline scientific symbols and IEEE tables need DOCX-specific QA.**
    Do not let inline math cleanup create pseudo-subscript artifacts such as
    `nₑff`, `εₑff`, `Imnₑff`, or phrases like "real part of nₑff"; rewrite
    prose as "effective index" / "real part of the effective index" or use
    real OMML. In two-column IEEE DOCX builds, tables must have fixed
    `w:tblGrid`/`w:tcW` widths whose sum fits one column; `cell.width` alone
    can leave a page-wide grid and make the table span both columns.
15. **No internal reviewer/TODO text in the emitted paper.** If author data,
    optical-constant sources, expert-conclusion status, or FEM validation
    details are not yet available, move them to a non-emitted
    "Open pre-submission checks" section or the project checkpoint. The DOCX
    body must not contain `[УТОЧНИТЬ]`, Russian service notes, or TODO text.
    For incomplete FEM validation, state the reference data as diagnostic and
    name the missing checks; do not imply that mesh/domain/PML convergence or
    wavelength-sweep validation was performed.
16. **Visually verify every generated figure before embedding it, and verify
    immediately - do not trust that the plotting code is right.** A matplotlib
    schematic or chart can place cut lines, arrows, markers, or dimension
    annotations off the features they mark even when the code reads correctly
    (e.g. a cross-section cut line that should bisect a thin metal strip but
    visibly misses it). Keep an explanatory schematic semantically minimal:
    do not add an equation unless it explains a relationship shown in that
    figure; put material names inside their layers whenever they fit; and move
    dimension text beside the arrow so no line or arrowhead crosses the text.
    After building a figure, RENDER it and LOOK before it
    goes into the manuscript: confirm each annotation/line/marker sits on the
    feature it represents, layers and labels do not overlap, thin layers are
    visible, and in-figure text/axis labels are readable. When alignment is in
    doubt, measure it in pixels instead of eyeballing: load the PNG, find the
    colored line/feature columns (e.g. red = cut lines, the layer's fill color =
    its extent) and assert the line falls at the target's center/region. Place
    schematic cut lines at the CENTER of the region each one represents, and
    exaggerate sub-resolution layers (a 10 nm film) enough to be visible while
    keeping the true value in the dimension label. The same rule applies to any
    generated image, table, or computed number: inspect the actual artifact
    right after producing it, not after the whole DOCX is built.

## Where IEEE Differs From The Ioffe Journal Rules

Quick contrast so journal habits are not applied to an IEEE paper:

| Topic | Ioffe journal (OiS) | IEEE conference (APEDE) |
| --- | --- | --- |
| Language | Russian (English version made by journal) | **English** |
| Layout | single column, 1.5 spacing, 12 pt | **two-column** IEEE template, prescribed fonts/margins - do not alter |
| Title/abstract | informative, no abbreviations | **no symbols, special characters, footnotes, or math** in title OR abstract |
| Decimal separator | decimal point | decimal point (`0.25`, not `.25`) |
| Minus / dash | plain hyphen `-` only (user pref) | **long dash for minus**, en dash for ranges |
| References | own OiS format, all coauthors, translated version in [] | **IEEE numbered [1]** style; all authors unless >6, then "et al." |
| Reference marker | `[1]` in citation order | `[1]` in citation order (same idea, IEEE punctuation) |
| Section numbering | plain headings | Heading styles; text-head numbering done by the template - do not hand-number |
| Template text | n/a | **must be fully removed or the paper may not be published** |
| Submission | OJS package + license + reviewers | conference portal + IEEE-Xplore-compliant PDF (PDF eXpress) + copyright (eCF) |

## Output Conventions

- Keep the paper draft note, the generated DOCX/PDF, and figure sources in
  the paper's folder near the source notes; figures in a `figures/`
  subfolder, one file per figure (>=300 dpi raster or vector EPS/TIFF).
- English paper by default (APEDE proceedings are English). All in-figure
  text, axis labels, and units in English.
- File naming: `<ShortName>_IEEE_camera_ready.docx`, `..._camera_ready.pdf`,
  `fig1.eps`/`fig1.png`, etc. Keep dated backups of prior camera-ready
  versions rather than overwriting (see the existing `*.backup_*.docx`
  convention in the article folder).

## Guardrails

- Do not invent affiliations, e-mails, ORCIDs, grant numbers, or author
  order - take them from the user's materials or leave clearly marked
  placeholders `[УТОЧНИТЬ: ...]` and list them when reporting.
- Do not exceed the conference page limit; if content overflows, flag it and
  propose cuts rather than silently shrinking fonts or margins (the template
  fonts/margins must not be altered).
- Do not submit anywhere; prepare the camera-ready package and stop.
  Uploading to the conference portal / IEEE is the user's action.
- Do not silently drop template requirements the draft violates - list every
  unresolved violation (especially leftover template text) in the final
  report.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
