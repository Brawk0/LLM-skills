---
name: spiritual-literature
description: Read, write, review, and quote from Christian spiritual literature — sermons, teacher notes, devotionals, Bible studies, systematic theology, catechesis, homiletics, apologetics, and church camp/Sunday-school materials. Use for проповедь, конспект проповеди, богословие, толкование, библейское исследование, курс библейского института, воскресная школа, лагерь, катехизация, or any note under `Церковь/`, `Литература/духовная/`, or with a `Проповедь …` prefix, especially when the text must quote Scripture accurately. All Bible references are resolved from the user's local Synodal Bible at `Церковь/Библия/Библия/`.
---

# Spiritual Literature

## Scope

This is the general skill for working with Christian spiritual and theological texts in the user's vault: writing new material, reviewing existing notes, resolving Bible references, and keeping citations honest.

**Related skills — don't duplicate their scope:**
- `christian-presentations` — slide decks and .pptx safety. When making a deck, use both skills together; that one owns visual layout, this one owns Scripture accuracy.
- `presentation-creation` — deck mechanics.
- `knowledge-refactoring` — deduplication, canonicalization, `[[wiki-link]]` reshaping.
- `scientific-article-writing` — academic manuscripts (do not apply that skill's conventions here).

## Bible: source of truth

The user's local Synodal Bible is at `Церковь/Библия/Библия/` with this layout:

```
Церковь/Библия/Библия/
├── Ветхий завет/<abbr>/<abbr> Глава <N>.md
└── Новый завет/<abbr>/<abbr> Глава <N>.md
```

**Filename gotchas** — check both when resolving:
- **Псалтирь uses `Псалом` instead of `Глава`** in filenames: `Пс Псалом 138.md`. Every other book uses `Глава`.
- **Case-insensitive filenames.** Some chapter files use lowercase "глава" (e.g. `Иак глава 4.md`) even when siblings use the capitalised form. Match filenames case-insensitively; do not assume `\bГлава\b` is exact.

Each chapter file uses this exact structure — verses are `###### N:V` headings followed by the verse text:

```markdown
---
cssclasses:
  - synodal-bible-chapter
---
#### Ин
##### Глава 3
###### 3:1
Между фарисеями был некто, именем Никодим, …
###### 3:2
Он пришёл к Иисусу ночью и сказал Ему: …
```

**Absolute rule:** never quote a Bible verse from memory. Every direct quote must be read from the chapter file. If the reference doesn't resolve (unknown book, missing chapter, missing verse) — say so plainly and stop; do not fabricate wording, do not silently substitute a nearby verse.

## Reference syntax

Supported reference forms (used both in user notes and in your output):

| Form | Meaning |
|---|---|
| `Ин 3:16` | single verse |
| `Ин 3:16-18` | inclusive range |
| `Ин 3:16, 18` | discontinuous verses in one chapter |
| `Ин 3:16-4:2` | range crossing a chapter boundary (read both files) |
| `Ин 3:16; Рим 5:8` | multiple independent references |
| `Пс 22` | whole chapter (avoid quoting; give a pointer only) |
| `1 Кор 13:4-8` | numbered book |

Whitespace and dashes are forgiving: `1Кор.3:16-18`, `1 кор 3:16–18` (en-dash), and `1 Кор 3:16—18` (em-dash) all normalise to `1 Кор 3:16-18`.

## Resolver algorithm

To resolve a reference `<book> <chapter>:<verse-spec>`:

1. **Normalise the book name** using `references/bible-abbreviations.md`:
   - strip trailing dots, collapse whitespace, lowercase for matching;
   - map any synonym (`Иоан.`, `От Иоанна`, `Ев. Иоанна`, `1-е Петра`, `Первое послание Коринфянам`) to the canonical abbreviation used as a folder name (`Ин`, `1 Пет`, `1 Кор`);
   - reject unknown books — do not guess.
2. **Locate the chapter file** at `Церковь/Библия/Библия/<testament>/<canon>/<canon> Глава <N>.md`. The testament (`Ветхий завет` / `Новый завет`) is fixed per book — see the table.
3. **Extract verses**: read the file, find the `###### <chapter>:<verse>` heading, take every line up to the next `###### ` heading (or end of file). Strip trailing whitespace; keep the exact Synodal wording, including archaic forms (`лице`, `тобою`, `рождённое`).
4. **For cross-chapter ranges** (`Ин 3:16-4:2`), read both files and concatenate.
5. **Never** normalise the verse text — no modernising spelling, no punctuation edits, no "corrections" of `[один]` bracket-style clarifications.

## Output formats

**In vault notes** — use an Obsidian wiki-link with block anchor so the reader can jump straight to the verse in the chapter file:

```markdown
> [[Ин Глава 3#3:16|Ин 3:16]] Ибо так возлюбил Бог мир, что отдал Сына Своего Единородного, дабы всякий верующий в Него, не погиб, но имел жизнь вечную.
```

Multi-verse quote — group under one link, keep verse numbers inline:

```markdown
> [[1 Кор Глава 13#13:4|1 Кор 13:4-7]]
> ⁴ Любовь долготерпит, милосердствует, любовь не завидует, любовь не превозносится, не гордится, ⁵ не бесчинствует, не ищет своего, не раздражается, не мыслит зла, ⁶ не радуется неправде, а сорадуется истине; ⁷ всё покрывает, всему верит, всего надеется, всё переносит.
```

Verse numbers as superscript unicode (`¹²³⁴⁵⁶⁷⁸⁹⁰`) or plain `(4)` — match what the note already uses; don't invent a third style.

**In chat** — cite with a plain reference and put the quoted text below, no wiki-brackets:

```
Ин 3:16 — Ибо так возлюбил Бог мир…
```

## Operations

**Expand a reference into a quote.** Given a bare `Ин 3:16` in a note, replace with the wiki-link quote block above. Ask before editing more than a handful in one pass.

**Collapse a quote back to a reference.** Given a full quote block, replace with `[[Ин Глава 3#3:16|Ин 3:16]]` alone. Useful when a draft has ballooned.

**Audit a note.** Walk the text, extract every candidate reference, resolve each, and report:
- refs that don't resolve (bad book, missing chapter/verse);
- quoted text that doesn't match the Synodal wording at the cited reference;
- refs written in an unusual abbreviation that should be normalised to the folder-name canon for consistency.

Do not silently rewrite the note during an audit — return a list first.

**Bulk-linkify an existing document** (e.g. a converted PDF, imported study). Use `scripts/resolve_bible_refs.py`:

```powershell
python scripts/resolve_bible_refs.py "<file.md>" "<vault_root>"
```

It rewrites the file in place, replacing each recognised reference with an Obsidian wiki-link to the verse anchor, and writes a JSON report `<file.md>.bible-refs.json` listing unresolved cases. **Always back up the file first** — this is a large in-place edit. Unresolved refs typically fall into three classes: source typos (e.g. `Лев. 24:26` when Lev 24 has 23 verses), reversed ranges (`Отк. 13:11-8`), and PDF extraction artifacts where page numbers glue onto verse ranges (`2Кор. 4:1-\n36` — the `36` is a footer). Do not auto-fix these; report and let the user decide.

The script bakes in five non-obvious rules discovered on real texts — don't remove them if you edit it:

1. **Word-boundary check on book names.** Match only when the preceding char is non-letter, otherwise short synonyms like `Ам` (Amos) fire mid-word on Russian dative-case endings (`программам`, `людям`) and produce phantom refs.
2. **Colon strictly required between chapter and verse.** A bare `.` risks matching version numbers like `2.0` in prose as `Ин 2:0`.
3. **Trim trailing `, <digit>` when followed by a Cyrillic letter.** The greedy verse-list regex will otherwise steal the `1` from a following numbered book: `5:1-3, 1Тим. 3:15` gets grabbed as `5:1-3, 1` + orphan `Тим. 3:15`.
4. **Skip text inside `[[...]]` wiki-links.** Without this, a second run on an already-linkified file nests every match inside its own link (`[[Ин Глава 3#3:16|[[Ин Глава 3#3:16|Ин 3:16]]]]`). Idempotency is a hard requirement — safe re-runs after manual patch passes are the whole workflow.
5. **Latin-lookalike normalization: `Mк` → `Мк`.** PyMuPDF sometimes decodes a Cyrillic letter as its visually identical Latin twin (`M`/`М`, `K`/`К`, `C`/`С`, `A`/`А`, `H`/`Н`, `T`/`Т`, `O`/`О`, `P`/`Р`, `B`/`В`, `E`/`Е`, `X`/`Х`, `Y`/`У`). Applied only when a Latin capital is immediately followed by a Cyrillic lowercase letter, so real Latin words after Cyrillic (`аgape`, `«Ave`) are untouched.

## Recipe: convert a PDF book of spiritual literature

End-to-end pipeline. Combines `pdf-textbook-to-markdown` for extraction/polish with this skill's Bible resolver. **Do not stop at "raw extract + resolver"** — the raw extraction is a debugging artifact, not a readable book. A user seeing `## Page N` breaks, running headers repeated 100+ times, page-number footers, and mojibake `×èñëî` where `Число` should be will (correctly) call this a broken conversion.

1. **Extract:** `python <pdf-skill>/scripts/extract_pdf_textbook.py extract "<src>.pdf" --output "<dst>.md" --media-dir "<dst>_media"`. Media stays in the media folder; the polisher drops the auto-emitted `![Page N image]` embeds so the user can add back only the figures that matter.
2. **Back up the raw extract** to your scratchpad — subsequent passes rewrite in place; keep a safety copy for `diff`.
3. **Resolve Bible references:** `python scripts/resolve_bible_refs.py "<dst>.md" "<vault_root>"`. Idempotent — safe to re-run. Report at `<dst>.md.bible-refs.json`; classify unresolved into three buckets (source typo, reversed range, PDF footer artifact) and surface to the user rather than a raw dump. Fix the ones the user confirms; remove refs for the ones they say to drop.
4. **Polish:** `python <pdf-skill>/scripts/polish_pdf_extraction.py "<dst>.md" "<src>.pdf"`. Fixes mojibake, marks PUA glyphs, drops page images, marks broken tables (cells saved to `.table-NNN.txt` sidecars), strips running headers, inserts `## Chapter …` from the PDF outline (or from `ГЛАВА N` text fallback), drops page markers, and reflows wrapped paragraphs. Idempotent. Report at `<dst>.md.cleanup.json`.
5. **Split by chapters:** `python <pdf-skill>/scripts/split_by_chapters.py "<dst>.md"`. Creates `<dst>/` folder with one `NN — <Title>.md` per chapter; the original .md becomes an index note.
6. **Manual title fixup (if needed).** When the PDF has no outline and the chapter title *is* the running header (repeats on every page), the running-header stripper eats the title, leaving auto-inserted chapter headings as short labels like `## ГЛАВА 1` without the full name. In that case rename the chapter files by hand from the book's own TOC — 30 seconds; there is no clean automatic fix.
7. **Keep reports** (`.bible-refs.json`, `.cleanup.json`, `.table-NNN.txt`) next to the index — they document what still needs a human eye.

If the target folder already has a user note under the same name (existing conspект, personal reading notes), **do not overwrite** — [[feedback-confirm-before-delete]]. Rename the user note (`<Name> — конспект.md` is a common pattern) and place the full text under the original name, or place the full text under a variant name. Ask before renaming.

## Writing spiritual prose

- **Quote vs. paraphrase.** If a sentence says what God, Christ, an angel, prophet, apostle, or biblical narrator said, use a direct quote in quotation marks with the verse reference. If simplifying (children's lesson, application), keep it clearly as your own words — do not put a paraphrase inside quotation marks.
- **Don't soften.** Keep the connection to God, Christ, sin, repentance, faith, obedience, prayer, and grace explicit when the passage requires it. Generic moralism ("будь добрым") is not the same as the biblical claim.
- **Don't speculate.** Adding scene details the text doesn't give ("Никодим нервно оглянулся…") is only OK when clearly labelled as illustrative imagination, not as what happened.
- **Reverent tone, light touch.** Serious subject, readable prose. Avoid both stiff churchly Russian and casual flippancy.

## Local sources beyond the Bible

The vault has substantial theological material worth consulting before writing:
- `Литература/духовная/` — books, courses, PDFs (курс библейского института: Библиология, Христология, Апологетика Трещев, …).
- `Церковь/Исследования/` — the user's own topical studies (о деньгах, о долгах, …).
- `Церковь/Труд в церкви/` — teaching materials, Sunday-school lessons, camp plans.
- `Церковь/Библия/Библейская энциклопедия Брокгауза.pdf` — reference encyclopedia.
- Existing `Проповедь …` notes at the vault root — the user's own past sermons; useful for tone and cross-references.

When a claim needs a source, prefer local material. Reach for the web only for background the vault clearly lacks.

## Vault safety

- **[[feedback-confirm-before-delete]]**: never delete or move existing notes without asking. This includes "cleaning up" outdated проповедь files.
- **[[feedback-no-ai-watermarks]]**: no "Generated with", no 🤖, no Co-Authored-By in commits or note bodies.
- **[[feedback-lessons-as-obsidian-notes]]**: durable lessons from a study session become notes in the project's `Уроки/` folder, not chat-only text.
- Bible chapter files (`Церковь/Библия/Библия/**/*.md`) are **read-only** from this skill's perspective — never edit verse text or headings.

## Self-improvement and publishing

When work reveals a durable, reusable rule (new synonym for the abbreviation table, a common failure mode when quoting, a lesson about which local source is authoritative), use the `skill-learning` policy. Save compact rules here or in `references/`. Do not store private pastoral content, personal counseling details, copyrighted book text beyond short necessary excerpts, or one-off facts.

Before materially editing this skill, run the owning repo's freshness check: fetch `origin main`, compare `HEAD` with `origin/main`, fast-forward if clean. After material updates, commit and push by default unless the user says otherwise. Stage only relevant files; split commits by semantic block.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
