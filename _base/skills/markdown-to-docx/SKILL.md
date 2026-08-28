---
name: markdown-to-docx
description: Create, convert, polish, and validate Microsoft Word .docx documents from Markdown .md drafts, Obsidian notes, scientific/technical articles, reports, and conference materials. Use when Codex needs to turn Markdown into a clean DOCX, apply a Word reference/template, preserve headings/lists/tables/images where possible, sanitize Markdown or LaTeX-like artifacts such as escaped pipes, raw underscores in formulas like SiO_2 or lambda_0, or QA a generated Word document before delivery.
---

# Markdown To DOCX

## Core Workflow

1. Preserve the source `.md`; write the generated `.docx` beside it or to the explicitly requested path.
2. Inspect whether the user expects a template/reference document. If a `.docx` template is supplied, use it as Pandoc `--reference-doc` or match its style manually.
3. Prefer Pandoc for production conversion when available:

```powershell
python ".\scripts\convert_md_to_docx.py" "input.md" --output "output.docx" --reference-doc "template.docx"
```

4. If Pandoc is unavailable and a simple document is acceptable, use the script's basic DOCX writer. It supports headings, paragraphs, simple lists, simple pipe tables, captions, code blocks, and formula-like subscripts.
5. After conversion, validate the generated DOCX. Treat raw Markdown/LaTeX leftovers as defects, especially escaped pipes, raw formula underscores, raw `$...$` math, broken captions, and image-only placeholders.

## Artifact Rules

- Read figures from the source's own embed syntax; do not require a custom marker. When the source is an Obsidian note, `![[file.png|width]]` is the input the converter must accept, expanding it to a real path and a page-appropriate width. Introducing a build-only placeholder (`**РИСУНОК 1: file.png**`) splits the artifact from its source: the DOCX comes out correct while the note the user actually reads shows a caption over an empty line. Keep one string that both a human and the script understand (lesson 28.08.2026).
- Never let Markdown escape syntax become visible Word text. Convert `air\ |\ PCM\ |\ SiO_2` into readable text such as `air | PCM | SiO_2` with the `2` rendered as a subscript or Word equation text.
- Do not place layer-stack, equation, or list lines immediately after a figure caption unless they are part of the caption. If Markdown conversion causes them to appear under the caption, move them back into the body text before or after the figure.
- Render scientific tokens such as `SiO_2`, `lambda_0`, `k_0`, `n_eff`, `L_pi`, and `L_power` as Word subscripts, Unicode-safe text, or equation objects. Plain underscores are acceptable only in file names, code, identifiers, or explicit user-requested literal text.
- Do not fake multi-letter subscripts or Greek-symbol subscripts in running prose. Strings such as `nₑff`, `εₑff`, `Imnₑff`, `Renₑff`, `ΓAu`, or `Gamma_Au` are visible artifacts. In prose, either rewrite as words ("effective index", "real part of the effective index", "gold-overlap factor") or emit a real OMML inline/display equation; in compact tables, plain `n_eff`/`Gamma_Au` is safer than pseudo-subscript text, but prose is usually better.
- For final scientific papers, replace important display equations with Word equation objects when feasible. If that is not feasible in the current run, leave a clear follow-up note in the document or report it to the user.
- When generating a camera-ready document, unzip or programmatically inspect `word/document.xml` and search for `\|`, `\ |`, raw formula underscores, and raw Markdown markers before saying the DOCX is ready.
- Never render equations by deleting TeX commands and braces. In particular,
  `\frac{\beta}{k_0}`, `\frac{2\pi}{\lambda_0}`, and
  `\frac{1}{2\operatorname{Im}\beta}` must become either real Word
  fraction objects (`<m:f>` inside `<m:oMath>`) or unambiguous plain text
  with explicit `/` and parentheses. Collapsed text such as `βk0`,
  `2πλ_0`, `12Imβ`, or `λ04πImn_eff` is a hard artifact failure.
- Treat layer-stack expressions as structured text, not fragile math cleanup:
  render `air | PCM | SiO2` as `air | PCM | SiO₂` (or real Word subscripts),
  never as visible TeX escapes such as `air\ |\ PCM\ |\ SiO_2`.
- In two-column Word outputs, pipe tables must have a real fixed table grid.
  With python-docx, setting only `cell.width` is insufficient because Word can
  retain a page-wide `w:tblGrid` and make the table span both columns. Set
  `w:tblW`, `w:tblLayout w:type="fixed"`, each `w:gridCol`, and each
  cell `w:tcW`; then inspect `word/document.xml` and confirm the grid-width
  sum is less than or equal to the target column width.
- Do not leave `_fixed`, `_test`, `_v2`, or backup-named DOCX files as the
  delivered state when the user expects the canonical filename. If a target
  DOCX is locked by Microsoft Word, close only the target Word document(s)
  for that path via Word COM, rebuild the canonical filename, and clean up
  temporary variants before reporting completion. Use alternate names only
  as short-lived recovery artifacts, not as the final answer.
- For generated DOCX QA, inspect both paragraph text and OMML math text.
  Count important display equations and verify that expected formulas are
  present as `<m:oMath>` with `<m:f>` fractions where fractions are required;
  text extraction alone can concatenate numerator and denominator.

## TeX-Math Manuscripts (lesson 2026-07-04)

For documents whose math must become real Word equations (journal
manuscripts, theses), do NOT use the gfm+sanitizer path: the sanitizer
mangles `$...$` content (splits `$K_{1,2}$`, turns subscripts into literal
text), and the `gfm` reader leaves `--` unconverted. Instead run pandoc
directly on the preserved source:

```powershell
pandoc "input.md" --from markdown-smart --to docx --standalone --wrap=none --resource-path "<folder with figures>" --output "output.docx"
```

Rules for the Markdown source in this mode:

- no `\operatorname{}` or `\text{}` inside math - pandoc's OMML output
  shows them as literal `operatorname` text and quoted subscripts
  (`ε_"eff"`); use `\mathrm{}`;
- write final punctuation literally (the reader has smart disabled): if the
  user wants plain "-", put "-" in the source, never `--`/`—`;
- keep display formulas shallow (introduce shorthand symbols rather than
  nesting parentheses inside `\frac`);
- avoid commas in subscripts of inline math (`$K_{1,2}$` is fragile; write
  `$K_1$ и $K_2$`).

Post-process with python-docx: body styles 12 pt / 1.5 spacing / journal
font, and recolor Heading/Title styles to black - pandoc's default
reference doc ships blue headings, which users read as an AI tell.

DOCX QA for this mode - scan `word/document.xml` and `word/styles.xml` for:
`operatorname`, `--`, `—`, `<m:t>"`, blue heading colors
(`4F81BD|345A8A|365F91|2E74B5|1F4D78` outside Hyperlink/TOCHeading), and
confirm `<m:oMath>` count roughly matches the number of formulas.

If Word COM is used to export PDF, `Quit()` may leave a zombie WINWORD.EXE
that locks the DOCX against the next conversion - stop lingering WINWORD
processes after export.

## Detailed Guidance

Read `references/conversion-checklist.md` when the task involves a publication, report, thesis material, image captions, equations, tables, or a user complaint about bad DOCX formatting.

Use the conversion script for repeatable work:

```powershell
python ".\scripts\convert_md_to_docx.py" "input.md" --output "output.docx" --method auto --strict
```

Useful options:

- `--reference-doc <file.docx>`: apply a Word reference document when Pandoc is available.
- `--method pandoc`: require Pandoc and fail if it is missing.
- `--method basic`: use the built-in lightweight DOCX writer.
- `--keep-sanitized`: save the sanitized Markdown beside the output for inspection.
- `--strict`: return a nonzero exit code if post-conversion artifact checks find suspicious text.

## Self-Improvement And Publishing

When Markdown-to-DOCX work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact domain rules, command patterns, parser improvements, validation checks, reusable examples, or tooling notes in this skill or a focused `references/` file. Do not store secrets, credentials, private content, copyrighted source text, generated logs, raw project/customer material, unpublished measurements, or one-off facts in the skill.

Before materially editing this skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check: fetch `origin main`, compare local `HEAD` with `origin/main`, fast-forward if local is behind and the relevant working tree is clean, and inspect dirty/ahead/diverged states before continuing.

After materially updating this skill, validate it when feasible, then commit and push the relevant skill changes to the owning repository by default unless the user explicitly says not to. Stage only relevant skill files and repository metadata.

If publishing encounters remote changes or merge conflicts, resolve them autonomously when the intended final meaning can be determined from the files, commit history, nearby rules, and the user's instruction. Preserve compatible rules from both sides, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
