---
name: optics-spectroscopy-article
description: Prepare, format, review, and package a journal article for «Оптика и спектроскопия» (Optics and Spectroscopy, Ioffe Institute) and structurally similar Ioffe journals (ЖТФ, ФТТ, ФТП). Use for статья в Оптика и спектроскопия, правила для авторов journals.ioffe.ru, структура рукописи, СПИСОК ЛИТЕРАТУРЫ по правилам ОиС, подача через OJS, сопроводительные документы, submission package/checklist, converting an Obsidian draft note into a submission-ready DOCX manuscript with correctly formatted title block, abstract, formulas, tables, figures, and references.
---

# Optics And Spectroscopy Article

## Purpose

Turn the user's research results (Obsidian notes, phd_lerer calculations,
figures) into a manuscript that passes the formal requirements of
«Оптика и спектроскопия» on first submission. The journal returns
non-compliant manuscripts without review, so formal compliance is part of
the science getting published at all.

Primary rule sources (in priority order):
1. `references/journal-rules.md` in this skill - verified digest of the
   official «ПРАВИЛА ДЛЯ АВТОРОВ» (ospr-7.pdf, received from A.M. Lerer)
   plus the OJS submission checklist;
2. the live pages https://journals.ioffe.ru/journals/rules/5 and
   https://ojs.ioffe.ru/index.php/os/submissions - recheck them before an
   actual submission in case the rules changed after 2026-07.

## Division Of Labour With Other Skills

- Universal venue-agnostic manuscript discipline (source-of-truth selection,
  claim/number QA, citation-order checks, safe count-asserted bulk edits):
  `scientific-article-writing`. Rules in this skill override it on conflicts.
- Natural Russian scientific language, де-кальке (avoid English calques,
  false friends, суржик) in the Russian manuscript, title, and abstract:
  `ru-language-purity`. Mandatory before finalizing Russian prose.
- Scientific content, claim control, checkpoints, final GPT review:
  `scientific-work` (final-review rule is mandatory for submission drafts)
  and `plasmonics-photonics` (domain claim rules).
- Markdown -> DOCX mechanics (pandoc/reference docx, formula sanitizing,
  QA of the generated file): `markdown-to-docx`. This skill defines WHAT
  the manuscript must contain; `markdown-to-docx` defines HOW to convert.
- Repository work for calculation code cited in the article: `phd-lerer-repo`.

## Self-Improvement And Publishing

When article-preparation work reveals a durable, reusable lesson, use the
`skill-learning` policy. Save compact rules about journal formatting,
editor feedback, submission-portal behavior, reference formatting, or
conversion pitfalls in this shared-base skill or a focused shared-base
`references/<topic>.md` file. Do not store secrets, credentials, private
content, unpublished manuscripts, referee correspondence, copyrighted
source text, generated logs, or one-off facts in the skill.

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

## Workflow: From Notes To Submission

1. **Checkpoint first.** Create or update the project checkpoint
   (`CODEX/Контекст задачи ... .md`) per `scientific-work`: objective,
   target journal and rubric, source notes, figure inventory, claim
   status, open risks.
2. **Draft as an Obsidian note** in the article's own folder near the
   source notes. Use the manuscript structure from
   `references/journal-rules.md` from the start (title block, abstract,
   keywords, sections, СПИСОК ЛИТЕРАТУРЫ, then tables, then figures with
   captions) so conversion is mechanical, not creative.
3. **Claim control.** Every quantitative claim must trace to a validated
   calculation (repo script + commit) or a cited source. Follow
   `plasmonics-photonics` rules: no "first ever" claims without literature
   verification; mark reduced-order results as such; state the sign
   convention for eps explicitly when both e^{+iwt} and e^{-iwt} sources
   are mixed.
4. **Apply the formal rules** - read `references/journal-rules.md` fully
   and walk the manuscript against its checklist section by section
   (volume, title block, abstract, formulas, tables, figures, references).
5. **Convert to DOCX** with `markdown-to-docx` (12 pt, 1.5 line spacing,
   numbered display formulas in the equation editor, tables as real Word
   tables, figure captions collected after references). Produce the
   companion PDF. Export each figure as a separate file (vector where
   possible).
6. **Assemble the submission package** - the full list is in
   `references/journal-rules.md` (manuscript, PDF, authors file, license
   agreement, institutional direction letter, terms-translation file,
   list of >=3 suggested reviewers with affiliations and e-mails).
7. **Final review.** Run the `scientific-work` final GPT/ChatGPT review
   pass on the near-final draft (argument, novelty framing, missing
   literature, venue fit), verify its suggestions against sources, then
   fix. Only then call the draft submission-ready.
8. Record the resulting files and their status in the checkpoint.

## User Feedback Lessons (2026-07-04, manuscript review by user)

Hard requirements from the user's review of the first generated DOCX; check
every one of them before calling a DOCX ready:

1. **Headings must be black.** Pandoc/Word default blue headings are an
   instant "AI-generated" tell. Recolor Heading/Title styles to RGB(0,0,0)
   (python-docx pass); standard blue hyperlinks in references are fine.
2. **Only the plain hyphen "-".** No TeX-style `--` and no long dashes
   `—`/`–` anywhere in the manuscript text - the user wants ordinary "-"
   even where Russian typography would use an em dash. Write it literally
   in the source; do not rely on smart punctuation.
3. **Word-safe math only.** No `\operatorname{}` and no `\text{}` inside
   TeX math - via pandoc they surface in Word as literal `operatorname` and
   quoted subscripts (`ε_"eff"`). Use `\mathrm{}` (e.g.
   `\mathrm{Im}\,\varepsilon_{\mathrm{eff}}`). Keep display formulas simple
   (introduce shorthand symbols instead of deep nested fractions).
4. **Convert with plain pandoc markdown, not the gfm+sanitizer path** - see
   the corresponding lesson in `markdown-to-docx`.
5. **QA the produced DOCX by inspecting `word/document.xml` and
   `word/styles.xml`**: zero matches for `operatorname`, `--`, `—`,
   `<m:t>"`; no blue heading colors; equations present as `<m:oMath>` with
   stacked fractions `<m:f>`; then verify the title block against the
   sample in ospr-7.pdf (`© И. О. Фамилия¹, И. О. Фамилия¹,*` +
   `*e-mail:`).

## Output Conventions

- Keep the article draft note, the generated DOCX/PDF, and the submission
  package files in the article's folder near the source notes; figures in
  a `<article>_media` or `figures/` subfolder, one file per figure.
- Russian manuscript by default (the journal publishes a parallel English
  version itself); axis labels, units, and in-figure text in English only.
- File naming: `<КороткоеНазвание>_рукопись.docx`, `..._рукопись.pdf`,
  `..._авторы.docx`, `..._термины.docx`, `..._рецензенты.docx`,
  `fig1.eps`/`fig1.png` etc.

## Guardrails

- Do not invent affiliations, e-mails, grant numbers, or reviewer names -
  take them from the user's materials or leave clearly marked
  placeholders `[УТОЧНИТЬ: ...]` and list them when reporting.
- Do not submit anywhere; prepare the package and stop. Submission through
  OJS is the user's action.
- Do not silently drop journal requirements that the draft violates -
  list every unresolved violation in the final report.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
