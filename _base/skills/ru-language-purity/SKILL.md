---
name: ru-language-purity
description: Keep Russian scientific prose natural and free of English calques (кальки), суржик, false friends, and invented compound words, and catch the mirror problem of Russian insider jargon leaking into English manuscripts. Use before writing or editing Russian научный текст, as a full pass over any Russian text translated from an English (AI-written) draft, and when checking an English version written from a Russian working draft. Shared source of truth for де-кальке rules, referenced by scientific-article-writing, nto-formatting, optics-spectroscopy-article, apede-ieee-conference-article, and any skill producing bilingual RU/EN technical text.
---

# RU/EN Language Purity (де-кальки)

## Purpose

Single shared discipline for natural bilingual scientific language, so the
де-кальке checklist lives in ONE place and every manuscript / report skill
references it instead of re-embedding its own copy. Two directions:

- **RU prose** must not inherit English calques (кальки), false friends,
  суржик, or invented compound words when it is written from - or translated
  from - an English draft, especially an AI-generated one.
- **EN prose** written from a Russian working draft must not carry insider
  Russian-lab calques and working-title jargon that mean nothing to an
  international reader (the mirror problem).

Written imperatively so any model, including weaker ones, can apply it
without judgment calls.

## When To Apply

- MANDATORY before writing or editing Russian manuscript / report prose.
- MANDATORY as a full pass over any Russian text that is, or descends from,
  a translation of an English draft.
- When producing or reviewing an English version written from a Russian
  working draft (the mirror check below).
- Also over Russian technical notes and firmware/hardware reports, not only
  manuscripts. That register mixes Russian prose with Latin identifiers
  (register names, signals, code symbols) on every line, which is exactly
  where abbreviations get cyrillized by ear (Class 5) and where raw English
  slips in unnoticed (Class 4).

## RU Direction - De-Calque

Read and apply `references/decalque-ru-en.md`. It is the single source of
truth for RU de-calque pairs and holds:

- the strategic rules (rewrite from facts, resolve sense against the source,
  existence test for coined words) - apply these FIRST, they beat
  word-by-word fixes;
- the verified replacement tables by defect class (false friends and
  wrong-sense translations, invented calque compounds, imported metaphors,
  суржик raw-English words);
- the deliberate keeps (do not over-correct established terms such as
  «метрики», «вытекающая мода», «отсечка»);
- the grep automation recipe and the count-asserted bulk-fix rule.

When selecting or translating a specialized scientific term, also read
`references/verified-russian-terminology.md`. Check its registry before
searching. If the term is absent, verify it in Russian-language scientific
sources and record the result there; never coin terminology from an English
phrase and present it as established Russian usage.

New caught calques are added to that file, not inlined here.

## EN Direction - Working-Vocabulary Leakage (mirror)

An English version written from a Russian working draft inherits insider
calques that mean nothing to an international reader. Watch for:

- "local" meaning "our in-house runs" ("local COMSOL data" -> "our /
  reference COMSOL runs");
- "referred to locally as" -> "known in the Russian-language literature as";
- working-title jargon that was never introduced ("failure atlas" -> spell
  out the meaning);
- compound shorthand ("COMSOL-side step" -> "a step on the FEM side");
- ML working jargon in physics prose ("hold-out FEM points" ->
  "confirmatory FEM checks");
- in-figure text (legends, captions) drifting from the manuscript's own
  terminology ("planar anchor" in the legend while the text says
  "planar reference") - figures follow the text's terms.

Also scan for British spellings (IEEE uses American English), "allows to /
possibility to / it is necessary to note", doubled words, and "data is".

## Allowed English In Russian Prose

English is allowed ONLY: (a) in parentheses when first defining a term or
abbreviation, (b) in established abbreviations (PCM, FEM, SPP, PML, COMSOL,
TM), (c) inside reference titles. Everything else is a defect. Register:
научный стиль уровня опытного ученого.

The mirror defect is equally forbidden: do NOT rewrite an established Latin
abbreviation in Cyrillic letters by ear (BLDC -> «БЛДЦ», UART -> «ЮАРТ»).
Keep the Latin form and decline the surrounding Russian words, or use the
genuine Russian abbreviation where one exists (FPGA -> ПЛИС, PWM -> ШИМ,
ADC -> АЦП). Class 5 in `references/decalque-ru-en.md` holds the table and
the existence test.

## Тон и обращение (RU)

Ровный деловой тон. Собеседник — не приятель, и разговорная окраска в
техническом тексте неуместна, даже когда она «оживляет» речь.

Запрещено:

- панибратство и просторечие: «без обиняков», «положа руку на сердце»,
  «давайте начистоту», «бро», подмигивания, восклицательные знаки;
- объявления о собственных действиях вместо самих действий: «Поясню…»,
  «Скажу прямо…», «Отвечу честно…» — просто сказать то, что нужно сказать;
- разбор собственной предыдущей формулировки («фраза вышла тёмной»,
  «выразился неудачно») — исправить и продолжить, не оглядываясь;
- извинения, самоуничижение, похвала собеседнику за вопрос.

Требуется: назвать суть с первой строки, дальше — по делу.

Про свои прошлые ответы говорить только тогда, когда из этого следует другое
решение. Пример, когда сказать НАДО: раньше названо число 185 кБ/с, оно
оказалось неверным, и вывод про ускорение меняется — это касается дела.
Пример, когда говорить НЕ надо: прошлая фраза вышла путаной или в ней была
опечатка — такое исправляют молча и продолжают.

## Self-Improvement And Publishing

When language work reveals a durable, reusable calque, false-friend, or
суржик pair, use the `skill-learning` policy: add the pair to the matching
class table in `references/decalque-ru-en.md` (not as prose in this
SKILL.md) and keep the grep list there current. Do not store secrets,
credentials, unpublished manuscript content, referee correspondence,
copyrighted source text, generated logs, or one-off facts.

Before materially editing this skill, run the owning repository's freshness
check: fetch `origin main`, compare local `HEAD` with `origin/main`,
fast-forward if behind and clean, inspect dirty/ahead/diverged states first.

After materially updating this skill, validate the shared base and adapters
when feasible, then commit and push to the owning repository by default
unless the user says not to. Stage only relevant skill files; split commits
by semantic block; avoid vague rollups. If publishing hits remote changes or
merge conflicts, resolve them autonomously when the intended meaning is
determinable from files, history, and the user's instruction; otherwise stop
and report.

This skill is the source-of-truth safety copy and is also mirrored into a
downstream corporate skills repository so corporate skills can reference it.
Keep this copy; if corporate publishing, permissions, sync, or merge fails,
preserve and report this copy.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
