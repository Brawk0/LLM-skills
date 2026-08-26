---
name: presentation-creation
description: Create, review, improve, regenerate, and verify presentations and slide decks. Use when Codex works with PowerPoint .pptx files, Google Slides, Canva decks, slide plans, speaker notes, visual prompts, or requests in Russian such as "презентация", "слайды", "переделай презентацию", "посмотри презентацию", or "создай презентацию", especially when local vault knowledge, existing decks, GPT/browser image work, or copy-preserving edits are involved.
---

# Presentation Creation

## Core Goal

Create practical presentation artifacts: slide decks, improved deck copies, slide-by-slide outlines, speaker notes, visual prompts, and handoff notes. Prefer work the user can immediately open and use over abstract advice.

## Required Context

- Read the user's brief, target audience, duration, venue, required tool, and source folder before changing a deck.
- If the user gives an existing presentation, inspect its slide count, text, visual pattern, and apparent purpose before deciding whether to edit, add, or regenerate.
- Work from the user's local vault, source files, and existing assets first. Use web sources only for current facts, missing visuals, or verification.
- For scientific, technical, or popular-science talks, also use `scientific-work` and read `scientific-work/references/presentation-workflow.md` when relevant.
- For Christian, church, Bible, Sunday school, sermon, youth, camp, or devotional decks, also use `christian-presentations` for Scripture accuracy, Bible quotation rules, and church lesson tone.
- When a request mentions Canva, Google Slides, Figma, or a browser-based GPT workflow, use the matching app/plugin/browser skill when available.

## Workflow

1. Protect originals. If editing or regenerating an existing deck, create a clearly named copy unless the user explicitly asks to modify the original.
2. Gather sources. Search nearby project notes, briefs, images, prior decks, and relevant vault material. Record the local notes and external sources that materially shape the deck.
3. Choose the output. If the user asks for a deck, create or update a local `.pptx`, Google Slides/Canva file, or the requested format when feasible. If a full deck is not feasible, create an Obsidian-ready Markdown source note with slide plan, speaker notes, visual suggestions, and source notes.
4. Shape the narrative. Define one main point, audience promise, section flow, and closing takeaway. Keep one main idea per slide.
5. Build or revise slides. Prefer concise slide text, strong visual hierarchy, and visuals that clarify the actual subject. Avoid decorative filler, dense paragraphs, and unsupported claims.
6. Add speaker support. Include presenter notes or a companion note when the deck needs explanation beyond slide text. Put facilitator-only prompts, teaching cues, activity directions, and labels like "Question for children" in speaker notes, not on the visible slide, unless the user explicitly asks for audience-facing instructions.
7. Validate. Check slide count, readable text, broken media, layout overflow, source attribution, and whether the original stayed untouched. For `.pptx` details, read `references/powerpoint-file-workflow.md`.
8. Handoff. Report the exact file path, what changed, assumptions, validation performed, and any remaining manual checks.

## Existing Deck Review

- Extract slide text and summarize the current structure before proposing changes.
- Prefer targeted improvements when the deck is already coherent. Regenerate only when the current structure, visuals, or audience fit are substantially wrong.
- When adding from the user's knowledge base, choose material that strengthens the lesson or argument; do not add facts merely because they match keywords.
- Keep changes traceable: know which slide was changed and why.

## Visuals And GPT/Browser Work

- Use existing local images and deck style first.
- Keep the main subject visible. Do not place text panels, callouts, logos, or translucent overlays across faces, bodies, gestures, key objects, symbolic animals, or the focal action of an illustration/photo. A translucent card still counts as covering the subject if the person, animal, or object remains visible beneath it. Protect the whole visible silhouette/extent of important subjects, not only the face; "the head is clear but the tail/body/hand/hat is under the card" is still a composition failure. In group or children's scenes, protect all visible or partially visible foreground people, not only one named protagonist. Reposition, narrow, shorten, or split text before accepting a slide where the visual subject becomes background for the text.
- Size text panels to their content with only modest breathing room. Avoid oversized white/translucent cards whose empty area dominates the slide, washes out the illustration, or turns meaningful scenery into blank space; shrink, split, or reposition the panel before accepting a slide with a large unused field.
- Do not fix overlap by shrinking slide text until it becomes hard to read. If a safe open area cannot hold the current wording at readable size, reduce the visible text to the core audience-facing line and move the extra detail, comparison list, or facilitator support into speaker notes.
- Keep visible slide text audience-facing. Do not show presenter cues such as "ask the children", "question for children", "show/point out", "game", "activity", or similar facilitation labels on the slide surface; move them to speaker notes or a companion teacher note.
- When the user asks to use GPT in the browser for presentation images or regeneration, use the browser/GPT surface as requested, keep prompts and selected source URLs in a handoff note, and stop if login, CAPTCHA, or unavailable browser state blocks progress.
- For AI-generated images, write prompts that specify subject, audience, aspect ratio, style, historical/context constraints, and text-free output unless text is required.
- For internet images, prefer official, open-license, public-domain, or clearly attributable sources. Record URLs.
- Do not use dark, blurry, cropped, or purely atmospheric imagery when the audience needs to inspect the actual object, scene, event, person, or diagram.

## PowerPoint And File Work

Read `references/powerpoint-file-workflow.md` when inspecting, validating, or modifying `.pptx` files directly. Use structured APIs or Office file formats instead of ad hoc text replacement. Preserve existing design language unless a redesign is requested.

## Self-Improvement And Publishing

When presentation work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact domain rules, command patterns, parser improvements, validation checks, visual workflow notes, reusable examples, or tooling notes in this shared-base skill or a focused shared-base `references/<topic>.md` file. Do not store secrets, credentials, private content, copyrighted source text, generated logs, raw project/customer material, or one-off facts in the skill.

Before materially editing this skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check: fetch `origin main`, compare local `HEAD` with `origin/main`, fast-forward if local is behind and the relevant working tree is clean, and inspect dirty/ahead/diverged states before continuing.

After materially updating this skill, validate the shared base and adapters when feasible, then commit and push the relevant skill changes to the owning repository by default unless the user explicitly says not to. Stage only relevant skill files and repository metadata. Split commits by semantic block when the update contains independent concerns; avoid vague rollups such as "skill update".

If publishing encounters remote changes or merge conflicts, resolve them autonomously when the intended final meaning can be determined from the files, commit history, nearby rules, and the user's instruction. Preserve compatible rules from both sides, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
