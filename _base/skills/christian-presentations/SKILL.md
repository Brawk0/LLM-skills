---
name: christian-presentations
description: Prepare, review, improve, and verify Christian, church, Bible, Sunday school, youth, sermon, camp, and devotional presentations. Use for decks about Scripture, biblical stories, Christian teaching, воскресная школа, церковь, библейский урок, христианская презентация, Рожкао, ВШ, проповедь, or church children/youth materials, especially when slide text should quote the Bible accurately and use the user's local church/vault materials.
---

# Christian Presentations

## Core Goal

Add Christian and Bible-specific discipline to presentation work. Use this skill together with `presentation-creation`: that skill handles deck mechanics, visual layout, `.pptx` safety, and verification; this skill handles Scripture accuracy, church teaching context, lesson tone, and Bible-source handling.

## Source Order

1. Use the Bible text itself for key claims, memory verses, scene captions, and theological takeaways.
2. Prefer the user's local Bible and church notes when available, especially under `Церковь/Библия/Библия` and `Церковь/Труд в церкви`.
3. Use local lesson notes, prior presentations, and teacher briefs to choose emphasis and age fit.
4. Use web sources only for missing background, images, current venue details, or verification that cannot be resolved locally.

## Scripture Quote Rule

- Prefer a direct Bible quote over a loose paraphrase when the slide states what God, Jesus, an angel, prophet, apostle, or biblical narrator said.
- Cite book, chapter, and verse on every direct Scripture quote. Use the user's local citation style when visible, such as `Исх. 3:6, 12`.
- Keep quoted wording exact, including older forms such as `лице` or `тобою`, unless the user asks for a modern translation.
- Do not put paraphrases in quotation marks. If simplifying for children, separate it clearly as explanation or application, not as Scripture.
- Use short excerpts on slides and put longer passages in speaker notes or a companion handout.
- When shortening a verse, use ellipses or a clearly limited excerpt only when the remaining words still preserve the biblical meaning.

## Lesson And Audience Fit

- For children, keep one clear spiritual truth per slide and pair it with a question, observation task, or small application in speaker notes. Do not print teacher-facing labels or prompts such as `Вопрос детям`, `Спросите детей`, `Покажите`, `Попросите детей`, `Игра`, or similar facilitation cues on the visible slide; put them in speaker notes or a teacher companion note instead.
- Do not soften Scripture into generic moralism. Keep the connection to God, Christ, sin, repentance, faith, obedience, prayer, and grace explicit when the passage requires it.
- Avoid adding speculative details to Bible scenes unless clearly labeled as teacher explanation or visual imagination.
- Preserve reverent tone without making the deck heavy. For children, use concrete scenes, questions, and simple applications.

## Visual Discipline

- Follow `presentation-creation` visual rules. Do not cover the main biblical character, face, gesture, key object, or focal action with text panels.
- In children's lesson visuals, do not let lesson text cover children who are part of the scene, including partially visible children behind reeds, crowds, or other scenery. A translucent text card still counts as covering them. Use sky, margins, landscape texture, or other low-importance background areas for text.
- If an image contains a biblical character and a key object or symbolic animal, such as Moses and the burning bush, David and his sling, Peter and the rooster, or Jesus and Peter's restored conversation, protect all of them when possible; use low-importance sky, margins, rocks, water, or other background texture for text.
- Do not make Bible quotations too small just to keep all of them visible on one slide. Prefer one readable direct Scripture quote on the slide and put additional cross-references, comparison lists, and teaching prompts in speaker notes.
- Prefer images that help the audience observe the Bible story rather than decorative religious atmosphere.

## Verification

- Re-read every Scripture quote against the source after editing.
- Check that each quotation mark contains actual source wording, not a paraphrase.
- Check that each Bible reference points to the verse actually quoted.
- Check visible slides for teacher-facing prompt labels and move them to speaker notes before final handoff.
- For `.pptx`, also run the file checks from `presentation-creation/references/powerpoint-file-workflow.md`.

## Self-Improvement And Publishing

When Christian presentation work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact domain rules, Bible citation preferences, visual checks, lesson-structure patterns, validation checks, or tooling notes in this shared-base skill or a focused shared-base reference file. Do not store secrets, credentials, private pastoral content, personal counseling details, copyrighted source text beyond short necessary examples, generated logs, raw project material, or one-off facts in the skill.

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
