---
name: knowledge-refactoring
description: Refactor Obsidian vault notes and other knowledge bases into linked sources of truth, and keep the vault clean. Use when the user asks to remove duplicates, consolidate notes, choose canonical notes, replace repeated explanations with [[Obsidian links]], audit stale facts against source files or code, reorganize technical knowledge without moving files, delete junk/temporary/backup files, or resolve sync "(conflict ...)" duplicate files.
---

# Knowledge Refactoring

## Core Rule

Make knowledge DRY without making it cryptic. Each durable fact should have one canonical home; other notes should mention the concept briefly and link to the canonical note or section.

Reusable scientific and technical term definitions should be canonical standalone term notes. If a note defines a term inline, extract or consolidate the reusable definition into the term note and replace repeated explanations elsewhere with `[[Term]]` links plus only the local context needed by that note.

Granularity is not the enemy of DRY: do not avoid creating a term note just because the concept is small, elementary, or seems minor — a focused note the reader can open beats an unexplained term, and many small non-overlapping notes are healthier than a few bloated ones. The only hard constraint is non-duplication: the same definition must live in exactly one canonical note. Before creating a new note, search the whole vault (not just the current folder) to confirm the definition does not already exist elsewhere; if it does, link or consolidate instead of writing a second copy.

## Scientific Refactoring Scope

When the user says `научный рефакторинг`, interpret it as refactoring the
scientific knowledge layer around a project or article: explanatory notes,
simple-language derivations, formula notes, term notes, source notes, and
repeated definitions. It does **not** mean rewriting the article's argument,
claim order, or manuscript structure under the label of refactoring.

For an article-development workflow, apply scientific refactoring after the
companion explanations have been written:
1. keep the manuscript as its own reader-facing scientific artifact;
2. create or update separate simple-language explanations of the physics,
   mathematics, numerical method, figures, and limitations;
3. extract reusable concepts into exact standalone term notes;
4. choose canonical notes and replace repeated definitions in the companion
   notes with Obsidian links plus only the needed local context;
5. feed corrections back into the manuscript only when the note work exposes
   an actual scientific error, ambiguity, missing limitation, or terminology
   defect — never merely to make the manuscript mirror the note hierarchy.

The result should be two coordinated but non-identical layers: a compact
submission manuscript and a linked explanatory knowledge base that makes the
science understandable and reusable.

The same reading applies to notes produced by PDF→Markdown conversion
(textbooks, papers, datasheets — see `pdf-textbook-to-markdown`): when the
user asks to refactor them («отрефакторить»), they primarily mean this
scientific refactoring, not merely vault heading style (user clarification,
2026-08-06). For a converted note that means: remove conversion artifacts
(running headers/footers, watermarks such as `ptg...`, broken hyphenation,
duplicated TOC noise), restructure into readable sections, convert formulas
to `$...$`/`$$...$$` where checkable against the source, extract reusable
concepts into canonical term notes, and wiki-link the note into the vault
term web while keeping the note itself the source-backed home of the
document's own content.

## Self-Improvement And Publishing

When knowledge-refactoring work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact canonicalization rules, anti-duplication heuristics, validation checks, or reusable search/refactor workflows in this skill or a focused reference file. Do not store private note content, customer material, credentials, generated logs, or one-off project facts in the skill.

Before materially editing this skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check: fetch `origin main`, compare local `HEAD` with `origin/main`, fast-forward if local is behind and the relevant working tree is clean, and inspect dirty/ahead/diverged states before continuing.

After materially updating this skill, validate it when feasible, then commit and push the relevant skill changes to the owning repository by default unless the user explicitly says not to. Stage only relevant skill files and repository metadata.

If publishing encounters remote changes or merge conflicts, resolve them autonomously when the intended final meaning can be determined from the files, commit history, nearby rules, and the user's instruction. Preserve compatible rules from both sides, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.

## Workflow

When the target is a scientific or technical Obsidian note, use `scientific-work` alongside this skill and read `../scientific-work/references/obsidian-style.md` before the first edit, including for small standalone term notes. After editing, run `../scientific-work/scripts/Test-Note.ps1 <path> -First 24 -Strict`; add `-CheckLinks` when the note contains Obsidian links. This style load and strict validation are mandatory, not optional cleanup after writing.

1. Search the relevant folder first, then widen the search only as needed.
2. Identify duplicated claims, tables, code layouts, procedures, and checklists.
3. Assign a role to each note before editing:
   - canonical specification;
   - route map or workflow;
   - audience summary;
   - diagnostic checklist;
   - archive or historical context.
4. Keep complete details only in the canonical note. In other notes, replace duplicated details with `[[Note]]` or `[[Note#Section]]`.
5. Preserve unique context: decisions, caveats, chronology, diagnostics, and project-specific warnings should not be deleted just because related facts are canonical elsewhere.
6. When a note describes software, protocols, schemas, hardware behavior, or APIs, verify the canonical facts against the actual source files before treating them as truth.
7. Do not move or rename notes unless the user explicitly asks.
8. After material edits, run the vault note validator when available.

When reorganizing term notes, do not assume every term note already lives in a folder named `terms`, `Термины`, or `thermins`. Search for scattered standalone term notes in the relevant vault area, including project folders and root folders, but do not move paper notes, reports, course notes, modeling diaries, or other context-rich notes merely because they contain definitions.

## Vault Hygiene (Junk Cleanup)

Cleaning junk is destructive: identify candidates, verify, then delete, and report exactly what was removed. Respect any explicit user boundary (e.g. "keep and just list") over your own judgment.

Deletion consent depends on what the file is. Two regimes:

- **Obviously temporary and useless artifacts — delete autonomously, then report** (explicit user rule, 2026-07-30: "если папка очевидно временная и бесполезная - удаляй"). This covers the junk classes listed below plus whole scratch directories left by tooling (`.tmp_*/`, `tmp_*/`, unpacked-`docx` working dirs, `*_raw.md`/`*_tmp.md` pandoc intermediates), including ones an earlier session or another agent created — "not mine" is not a reason to leave junk in the vault. Do not ask first; do verify first: confirm the real original still exists (hash it when the artifact is a copy), confirm nothing links to the artifact, then delete and state exactly what was removed and how it was verified.
- **Content files where survivorship is a judgement call — ask first.** Permanently delete only when a content-level comparison (diff of full text, not file size or timestamps) shows the surviving copy genuinely supersedes it, and notify the user with that evidence before deleting. Moving verified-stale files to the vault `.trash/` is an acceptable autonomous holding step, but always report what was moved and why; emptying `.trash` or any other irreversible removal of content requires the user's explicit go-ahead.

Respect any explicit user boundary ("keep and just list") over both regimes.

Treat as junk and safe to delete:
- temp extraction artifacts: `_tmp*`, `tmp_*`, `.tmp_*`, `*.tmp` — files **and directories** (including orphaned Word temp files `~WRL*.tmp`, and unpacked-`docx` scratch dirs holding a zip copy of a document plus its `word/*.xml`);
- conversion intermediates left beside a finished note: `*_raw.md`, `*_tmp.md`, `*-raw.md` — pandoc output superseded by the cleaned note; verify the final note contains their text, then delete;
- editor/auto backups: `*~` (e.g. `.kra~`, `.psd~`, `.bmp~`), `*.bak`/`*.orig`/`*.old`/`*.swp` outside intentional backup folders — but verify the real original exists before deleting any `*~` backup;
- OS junk: `.DS_Store`, `Thumbs.db`, `ehthumbs.db`.

Never delete without checking — these look like junk but are not:
- `desktop.ini` in a Google Drive vault hold folder icons (`IconResource=...GoogleDriveFS.exe`); harmless, regenerated by Drive — leave them unless the user explicitly asks to remove all;
- empty `.md` notes are usually intentional stubs/skeleton (exam topics, term placeholders) — do not bulk-delete empty notes;
- `.obsidian/` config and `.obsidian/backups/*.bak` are intentional app state; only the sync-conflict copies of config (see below) are junk;
- the Obsidian `.trash/` folder is the user's safety net — do not empty it without asking;
- `.venv/`, `site-packages/`, `node_modules/`, `__pycache__/` are real dependencies/tooling, never vault junk — prune these paths from every search and deletion.

## Sync-Conflict Resolution

Google Drive / Obsidian Sync leave duplicate files named `X (conflict YYYY-MM-DD-HH-MM-SS).ext` (timestamps may stack). Never delete them in bulk or by size heuristic — a conflict copy can hold edits made on another device that exist nowhere else.

For each conflict file, derive the base by stripping every ` (conflict ...)` segment, then diff against it and classify. Classification prepares the action: verified-stale copies may be moved to `.trash/` autonomously with a report, but permanent deletion still requires the user's go-ahead per the deletion-consent rule above:
- base missing → the conflict copy is the only copy and holds real content; do not delete it. Rename it to the clean base name to drop the `(conflict ...)` suffix, first confirming the clean name is free and that no note links to the suffixed name (otherwise fix or keep the links);
- identical to base → pure duplicate, delete the conflict copy;
- conflict is a strict subset / older snapshot (only removals, trivial reflow, or raw pre-cleanup OCR vs cleaned LaTeX) → the base is canonical, delete the conflict copy;
- conflict has unique or newer lines (real differing content) → do not delete; merge the unique fragment into the base, or escalate to the user. When the base is empty but the conflict has content, the conflict is the valuable copy.

Config conflict copies under `.obsidian/` (`app (conflict ...).json`, `core-plugins (conflict ...).json`, etc.) are app-state junk — the live config beside them is canonical, delete the conflict copies.

## Canonicalization Heuristics

- Put byte layouts, packet formats, constants, enum mappings, and selectors in one specification note.
- Put reusable term definitions in standalone term notes; project notes, report sections, and literature notes should link to them rather than becoming the only definition source.
- Put end-to-end procedures in a route-map note that links to the specification sections.
- Put troubleshooting in a diagnostic note or section, linking to the relevant specs instead of copying field lists.
- Put human-facing briefings in short summary notes with links to the authoritative details.
- If two notes both look canonical, choose the one whose title names the concept most directly, then turn the other into a workflow, index, or summary.
- For a tutorial or lesson series, keep one overview/route-map note (e.g. a course plan) that links to the detailed lessons instead of re-explaining them, and make each lesson the canonical home for its own topic. Extract tooling/API/language primitives that recur across sibling lessons (e.g. CMake `OBJECT`/`INTERFACE` libraries, `PUBLIC`/`PRIVATE` visibility, toolchain files, presets) into standalone concept notes; in each lesson replace the inline definition with a short context phrase plus a `[[concept]]` link.
- When that link points to a recurring primitive whose canonical note does not yet exist, create the standalone note in the same pass rather than leaving a dangling placeholder link — especially when sibling primitives already have their own notes. Reserve placeholder `[[links]]` for genuinely out-of-scope future notes, and verify whether the target already exists before assuming it is missing. Point every reference at the exact note title, using `[[Note|alias]]` when the filename carries a qualifier (e.g. `[[find_package (CMake)|find_package]]`).
- Concept-note scoping (essence vs. everything else): a note titled X must serve a reader who wants X. Audit EVERY section against the title — not just the one the user flags — and cut two kinds of intruder: (a) implementation details of the *example* used to illustrate X (a peripheral's registers, bus/SPI dumps, exact device constants, register-level HDL, waveform screenshots) → move to that example's own note; (b) domain-adjacent siblings that merely co-occurred in the same working scratchpad (a different quantity's sizing calc, an unrelated derivation — e.g. counter bit-width or distance-from-time-of-flight sitting in a note about *division*) → move to their own note. Same folder, same source scratchpad, or same project domain is NOT a reason to keep a section. Trim intruders in the concept note to at most a one-line mention plus a `[[link]]`, and relocate the unique content into its proper note rather than deleting it (user feedback, 2026-07-07).

## Recurrent Patterns And Lessons

- Cyrillic duplicate-note check must not rely on case-insensitive matching. `grep -i`, `rg -i`, and `find | grep -i` frequently fail to case-fold Cyrillic in Git Bash/MSYS, so a search for `стек` silently misses `Стек.md` and the "no existing note" conclusion is wrong. Before creating any Russian-titled term note, run a case-explicit filename scan (`find . -name "*.md" | grep -E "Стек|стек"`, or a Glob on `**/*Стек*.md` plus the lowercase variant) and a separate content grep for both capitalizations. A missed duplicate is worse than a redundant search: it splits the term web and leaves the older note orphaned (learned 2026-07-23, after a `Стек.md` stub in a project folder was missed and a second stack note was created).
- Term notes hide in project/lesson folders, not only in `Терминология`. A short stub like `Стек.md` sitting beside `stack pointer.md` in a hardware-project folder is still the canonical home for that term as far as existing `[[links]]` are concerned. Check inbound links (`grep -rn "\[\[Term\]\]\|\[\[Term|"`) before deciding which copy is canonical, and never repoint an existing link to a new note until the duplication is resolved - repointing first makes the old note look orphaned and hides the conflict.
- Apply a prompted fix comprehensively, not locally: when the user flags one instance of a scoping/cleanup problem, treat it as a spec for the whole artifact — in the same pass sweep every analogous section, note, or paragraph and fix them all, instead of patching only the flagged spot and waiting to be told about the rest section by section. A correction is a rule to generalize across the artifact, not a one-off edit. This is a cross-cutting work habit (applies to code edits and any refactor, not just notes) (user feedback, 2026-07-07).
- Inconsistent partial refactors: when two copies of a note coexist (e.g. a stray `Untitled/` copy beside a numbered copy), DRY refactoring may have been applied to only one — and split unpredictably across both. `diff` each pair and pick the copy with more `[[links]]` and fewer inline definition blocks as canonical, merging any unique content from the other before deleting.
- A folder literally named `Untitled` (or notes named `Untitled*`) is a strong duplication/junk signal — its contents are usually older copies or scattered term notes that belong in the parent section folder.
- Windows `MAX_PATH` (260) truncates long note titles, leaving a `~` mid-filename (e.g. `...коле~ельных систем...`); such truncated names silently break `[[full title]]` links and the index that points to them. Prefer short stable filenames (e.g. topic numbers) with the full title as an `# H1` heading inside the note, and point the index at them with `[[short|Full Title]]` aliases.
- Bare short filenames like `1.md` collide across the vault (e.g. an Excalidraw plugin `1.md`), making `[[1]]` ambiguous; qualify such links with a folder or full vault path (`[[Folder/1|...]]`), and verify with a duplicate-basename scan (`find ... -printf '%f\n' | sort | uniq -d`).
- Distributed-but-linked is not duplication: a concept split into a general note plus a specialization (e.g. `TE волны` + `TE волны … в прямоугольном волноводе`), or a term web spread across `PhD/Термины`, the vault root, and a section folder, is correct DRY structure when each note covers a distinct facet and they cross-link. Do not merge these; only merge true same-concept duplicates.
- The `Test-Note.ps1` validator indexes only `.md`, so it reports `.pdf`/image/`.canvas` attachment links as missing — false positives. Confirm the attachment exists before treating such a link as broken.
- `Test-Note.ps1` bracket balancing does not strip fenced code blocks, so Tcl/shell code containing `]]` (e.g. `[file rootname [file tail $path]]`) false-positives as an unbalanced wiki link. Verify with a real `[[`/`]]` count outside code fences before "fixing" valid code (learned 2026-07-29 on ModelSim notes).
- `Test-Note.ps1` link checking uses `\[\[([^\]]+)\]\]`, which cannot match a target containing `]`. Wikilinks to files whose names carry brackets (e.g. `[[2 labVIEW/[2].Алгоритм LabVIEW.pdf|…]]`) are therefore skipped **silently** — the run still prints "link targets resolved". Verify such targets on disk by hand; a green validator is not evidence they resolve (learned 2026-07-30).
- Fixing a term note's folder vs. its filename are different-risk operations: Obsidian resolves `[[Note]]` by basename, so **moving** a note between folders keeps every inbound link working (verify the basename is unique first), while **renaming** breaks them all. Prefer a move when only placement is wrong; when a rename is genuinely needed, rewrite `[[old]]`, `[[old|`, and `[[old#` across the vault in one pass and re-scan for residual references before validating (learned 2026-07-30, relocating/renaming 6 freshly created term notes).
- An aliased wikilink dropped into a Markdown table needs `\|` (see Obsidian Links); the validator reports it as resolved, so only visual inspection or a targeted grep catches it. When inserting the same link into several places in one pass, check whether each landing site is a table cell before writing it, rather than reusing one string everywhere (learned 2026-07-30).
- Chat-prose wikilinks are live: any `[[Name]]` written in a chat reply is a real Obsidian link the user will click, and clicking a name that resolves to nothing **creates an empty stub in the vault root**, not in the sensible folder. Before emitting `[[Term]]` for a concept the user is likely to have, run a case-explicit filename search for both the Russian and English name (Glob `**/*Term*.md` in RU and EN forms) and, if the canonical note exists, use its actual title verbatim — the vault convention is `Русское (English)`, so a bare English-only label like `[[Mie theory]]` misses an existing `PhD/Термины/…/Теория Ми (Mie theory).md` and spawns a root-level stub. Applies to chat replies, not only to note edits; the "verify before linking" rule is not limited to placeholder links inside notes (learned 2026-07-30, after `[[Mie theory]]` in a chat reply created an empty `Mie theory.md` in vault root while the canonical `Теория Ми (Mie theory).md` already existed under `PhD/Термины/Электродинамика/`).

## Obsidian Links

Use exact wiki links for local notes:

```text
[[Canonical Note]]
[[Canonical Note#Section]]
[[Canonical Note|display text]]
```

Prefer the shortest resolvable wiki link. If the note title is unique in the vault, use `[[Note]]` or `[[Note|display text]]` instead of a vault-root path. Add only the minimal folder path needed to disambiguate duplicate filenames.

**Aliased links inside Markdown tables must escape the pipe as `\|`.** In a table row, a bare `|` inside `[[Note|alias]]` is consumed as a cell separator, so the link is split across two cells and renders as literal `[[Note` / `alias]]` text — not a clickable link. Always write `[[Note\|alias]]` in table cells (`| [[Медиана абсолютных отклонений (MAD, Median Absolute Deviation)\|σ робастная (MAD)]] | 1.48 мм |`). Also never pad the separator with spaces (`[[Note | alias]]`); Obsidian treats the spaces as part of the target/alias. Outside tables the plain `[[Note|alias]]` form is correct — do not escape there.

`Test-Note.ps1 -CheckLinks` does **not** catch this: the unescaped form still contains a balanced `[[...]]` pair, so the run prints "link targets resolved" while the note renders broken. After adding any aliased link to a table, grep the note for `\[\[[^]]*[^\\]\|` and confirm every table-cell hit is escaped (learned 2026-07-30, MAD term note linked from four report tables).

Do not write meta-comments inside notes such as "removed duplication here". Make the note read naturally.

## Verification

For technical refactors:

- Treat a project-specific validator and Obsidian link validation as separate gates: after structural checks pass, run `Test-Note.ps1 -CheckLinks` or an equivalent vault-indexed resolver across every relevant Markdown file and require zero unresolved wiki links; verify non-Markdown attachments separately because note-only indexes can report them falsely.
- cite source paths inside the note when they are useful for future checking;
- distinguish verified facts from hypotheses;
- remove or qualify stale statements that no longer match source code;
- prefer source code, primary docs, and generated artifacts over memory.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
