---
name: pdf-textbook-to-markdown
description: Convert, extract, segment, clean up, and review PDF textbooks into Markdown or Obsidian notes. Use when Codex needs to process born-digital or scanned textbook PDFs, preserve page anchors, extract figures, handle OCR, split chapters into .md notes, clean headers/footers/hyphenation, convert formulas and tables where possible, or prepare source-backed study/research notes from a .pdf book.
---

# PDF Textbook To Markdown

## Core Goal

Turn a PDF textbook into useful, source-backed Markdown without silently losing structure. Preserve the original PDF, keep page-level traceability, prefer a faithful draft before cleanup, and mark uncertain OCR, formulas, tables, or figure captions instead of inventing missing content.

## Repository Model

This skill is stored in both the user's personal skills repository and the corporate skills repository. Keep the personal repository copy as the safety copy so work is not lost if corporate publishing, permissions, sync, or merge resolution fails. Keep both copies aligned when the user asks to publish or synchronize this skill across repositories, but do not delete the personal copy merely because the skill is mirrored to corporate.

## Workflow

1. Identify the source PDF, target folder, output style, language, and split policy: one Markdown file, one file per chapter, or an Obsidian index plus chapter notes.
2. Triage the PDF before conversion:

```powershell
python ".\scripts\extract_pdf_textbook.py" inspect "input.pdf"
```

3. Choose the extraction route:
   - Fast triage / bulk conversion of born-digital PDFs (datasheets, papers, batch runs): `pip install pdf-inspector` (firecrawl, Rust; no OCR, no LLM). `pdf_inspector.process_pdf(path)` returns `.pdf_type` (`text_based`/`scanned`/`image_based`/`mixed`) and `.markdown` with headings and Markdown tables; Cyrillic survives. Verified 2026-08-06 on a 185-PDF vault batch (170 OK). Known limits: vector-only schematic PDFs fail with `invalid content stream`; a broken ToUnicode CMap yields `text_based` with empty markdown (pdftotext outputs garbage too — treat as needs-OCR). No page anchors — for page-level traceability use the bundled script instead.
   - Born-digital text: use the bundled script for a page-anchored draft and extracted images.
   - Scanned or low-text PDF: create a separate OCR copy first, then extract from the OCR PDF.
   - Layout-, formula-, or figure-heavy born-digital PDF: compare the default PyMuPDF draft with `--engine pymupdf4llm`. Use the better structure from PyMuPDF4LLM and the complete text/embedded images from PyMuPDF as a hybrid when neither route is sufficient alone.
   - Math-heavy or table-heavy book: read `references/pdf-tooling.md` and choose a specialized route; keep screenshots or image fallbacks for content that cannot be converted safely.
4. Extract a first-pass Markdown draft:

```powershell
python ".\scripts\extract_pdf_textbook.py" extract "input.pdf" --output "book.md" --media-dir "book_media"
```

For a layout-aware comparison:

```powershell
python ".\scripts\extract_pdf_textbook.py" extract "input.pdf" --engine pymupdf4llm --output "book.layout.md" --media-dir "book.layout_media"
```

5. Restructure the draft into textbook notes. Use the PDF table of contents, bookmarks, or visible headings to create stable chapter/section boundaries. Keep page markers such as `<!-- source-page: 42 -->` near converted content.
6. Clean the Markdown: remove repeated running headers, page numbers, broken line wraps, OCR artifacts, bad hyphenation, and duplicate boilerplate. Convert formulas to KaTeX only when the result can be checked against the PDF.
7. Verify against the source. Compare representative pages, check image links, inspect headings, and keep a short source note with the PDF filename, page ranges, extraction/OCR method, and remaining manual-review items.
8. Refactor, not just restyle. When the user asks to refactor converted notes («отрефакторить»), they primarily mean scientific refactoring per the `knowledge-refactoring` skill (its "Scientific Refactoring Scope"), not merely vault heading style: clean conversion artifacts, restructure into readable sections, extract reusable concepts into canonical term notes, and wiki-link the note into the vault term web. Vault style (`####` headings, no H1, no blank line after a heading) is the cosmetic baseline, not the deliverable (user clarification, 2026-08-06).

## Obsidian Conventions

- The extracted conversion note MUST link its source PDF with an Obsidian `[[filename.pdf]]` wikilink in the header (the `extract` command emits `> Source: [[<name>.pdf]]`), never a bare backtick path - a path string is not a backlink, so the source document shows no incoming links even though the whole study derives from it. When a separate analysis/paper note exists, cross-link it too. This mirrors the `obsidian-style.md` "Paper Notes" rule (explicit user requirement, 2026-07-09).
- Write inline math as `$...$` and display math as `$$...$$` in Obsidian Markdown. Do not leave LaTeX delimiters `\(...\)` or `\[...\]`: Obsidian can show their contents as raw text in Reading view even when the formula is valid LaTeX. Before handoff, search the converted notes for stray `\(`, `\)`, `\[`, and `\]`, then visually inspect representative inline formulas with subscripts, fractions, and Greek letters in Reading view (user feedback, 2026-07-14).
- Store media in a nearby folder such as `<book-stem>_media/`.
- Keep Obsidian attachment filenames short and stable, especially on Windows. Prefer names such as `<book-key>-fig-02-02.png` over caption-derived names; long full paths can fail in Obsidian/Electron even when the same files open in external viewers.
- Visually inspect extracted figure crops before relinking or translation. Page-region crops can accidentally include neighboring formulas, paragraphs, or captions; recrop/regenerate the PNG so only the figure artwork and its own internal labels remain.
- For Obsidian image embeds, use wikilinks with only the attachment filename, for example `![[Figure 2.2 - Geometry.png]]`; do not include `attachments/` or another media-folder prefix inside the wikilink. If filenames would collide in the vault, rename the extracted media files to unique descriptive names instead of path-qualifying the embed.
- When renaming or relinking extracted media for a book, update and verify every sibling or derived Markdown folder under the book root, including translations. Do not stop after the source Markdown folder; scan the full book root for old image embeds and validate that every linked filename exists and is unique in the vault.
- Every Markdown table must be preceded by a blank line, unless it starts directly under a heading. Extraction routinely emits a table glued to its lead-in sentence; a GFM table cannot interrupt a paragraph, so it gets folded into that paragraph and Obsidian renders raw `|` text while the Markdown source still looks correct. This is the highest-volume conversion defect in this vault: one sweep found 157 such tables across 35 notes, nearly all of them converted manuals and textbooks. Check converted notes with `scientific-work` `scripts/Test-Note.ps1 <note> -Strict` and repair in bulk with its `scripts/Repair-NoteTables.ps1 <paths> -Apply`, which inserts only the missing blank line and touches no cell text.
- Use an index note for the book when splitting chapters. Link chapter files with `[[...]]` and include source page ranges.
- Prefer descriptive chapter filenames with stable ordering, for example `01 - Fundamentals.md`.
- Do not replace technical definitions with Obsidian links until canonical notes have been found or created.
- For Russian or multilingual textbooks, preserve the source language unless the user explicitly asks for translation.

## Tooling Reference

Read `references/pdf-tooling.md` when OCR is needed, formulas/tables are important, the PDF has weak text extraction, or the best toolchain is not obvious.

Read `references/pdf-textbook-lessons.md` before converting Word-printed PDFs (theses, NTO reports), formula-heavy documents, or 200+ page books — it holds verified artifact patterns (broken REF fields, per-glyph formula scatter) and the parallel per-chapter subagent workflow.

**Read it also before dispatching any multi-agent conversion or refactoring sweep**, not only before converting a single book: it carries the fan-out lessons that cost the most to relearn — the shared-rules-file pattern that keeps each agent's reading phase short, the mandatory completeness-audit script (a hand-written fan-out silently dropped 8 of 170 notes and no agent reported it), the protocol that forbids parallel agents from creating term notes, the revision pass over blocks agents stamped "unrecoverable", and what does and does not survive when a session quota kills a fan-out mid-run.

## Extraction Script

Use `scripts/extract_pdf_textbook.py` for repeatable local work:

- `inspect` reports page count, metadata, text-layer coverage, pages with little or no extractable text, and PDF outline entries when available.
- `extract` writes a page-anchored Markdown draft and, with PyMuPDF available, extracts embedded images.
- `extract --engine pymupdf4llm` optionally preserves headings, reading order, and page-region image/formula crops more effectively for complex born-digital pages. Treat converted equations as candidates for visual verification, not as authoritative transcription.
- `check` verifies Markdown and Obsidian image embeds and reports page-anchor counts.

The default route prefers PyMuPDF (`pymupdf`) and falls back to `pypdf`/`PyPDF2` for text-only extraction when possible. PyMuPDF4LLM (`pymupdf4llm`) is an optional comparison engine, not a mandatory dependency. Install only the package needed for the selected route.

## Self-Improvement And Publishing

When PDF textbook work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact domain rules, command patterns, parser improvements, validation checks, or tooling notes in this skill or `references/pdf-tooling.md`; create `references/pdf-textbook-lessons.md` if lessons start to accumulate. Do not store private book text, copyrighted chapter content, credentials, extracted full chapters, or one-off project facts in the skill.

After materially updating this skill, validate it when feasible, then commit and push the relevant skill changes to the owning repository by default unless the user explicitly says not to. Stage only relevant skill files; never stage `secrets/`, API keys, local credentials, generated logs, extracted textbook text, or copyrighted source material.

Before materially editing this skill, applying self-learning updates, or publishing changes, run a lightweight freshness check like the NTO skill policy: fetch `origin main`, compare local `HEAD` with `origin/main`, fast-forward if local is behind and the relevant working tree is clean, and inspect dirty/ahead/diverged states before continuing. Leave unrelated user changes unstaged; stop and report only when target skill files or repository state make the intended update unsafe to determine.

If publishing encounters remote changes or merge conflicts, resolve them autonomously when the intended final meaning can be determined from the local changes, remote changes, commit history, and the user's instruction. Preserve compatible rules from both sides, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
