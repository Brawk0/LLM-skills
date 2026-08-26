---
name: obsidian-canvas
description: Create, edit, reorganize, validate, and maintain Obsidian .canvas files. Use when Codex needs to turn notes, outlines, tables, protocols, architectures, or process descriptions into Obsidian Canvas nodes and edges; adjust Canvas layouts such as top-down trees or horizontal main splits with deeper detail levels; repair Canvas JSON; or inspect/validate .canvas structure.
---

# Obsidian Canvas

## Core Workflow

1. Locate the target vault and `.canvas` file, or choose a clear new filename when creating one. Preserve unrelated user edits.
2. For nontrivial creation or relayout, read `references/canvas-patterns.md` before editing.
3. Model the information as a hierarchy first: root, primary branches, secondary groups, then leaves. Put the user's requested reading direction into coordinates and edge sides.
4. Edit `.canvas` as UTF-8 JSON. Preserve existing node text, especially non-English text, unless the user asked for content changes.
5. Validate with `python scripts/inspect_canvas.py <path-to-canvas>` after material edits.

## Layout Rules

- For "main split horizontally, detail below", put the root above, primary sections on the same `y` level, and each branch's details on progressively lower `y` levels.
- For top-down trees, use `fromSide: bottom` and `toSide: top` for parent-to-child edges.
- For left-to-right flows, use `fromSide: right` and `toSide: left`.
- Keep repeated detail nodes aligned by level. Prefer a wide, readable canvas over cramped overlapping cards.
- Use side reference cards, such as formulas or legends, outside the main tree and connect them with lateral edges only when the relationship matters.

## Editing Rules

- Use stable, descriptive node IDs such as `packet-body`, `header-time`, or `echo-field`.
- Text nodes should use concise Markdown headings and bullets; avoid recreating a giant table inside one node.
- Prefer structured JSON edits or targeted patches over ad hoc string rewrites.
- Do not create separate Markdown notes for Canvas nodes unless the user explicitly asks.
- When Obsidian has already serialized the file compactly, it is acceptable to reformat JSON if the content and node IDs are preserved.

## Validation

Run the inspector from the skill directory:

```powershell
python "C:\Users\User\Мой диск\Obsidian\.codex\skills\obsidian-canvas\scripts\inspect_canvas.py" "C:\path\to\file.canvas"
```

The inspector checks JSON syntax, duplicate IDs, edge endpoints, edge sides, positive dimensions, and likely node overlaps. Treat overlap warnings as layout prompts rather than hard failures.

## Self-Improvement And Publishing

When Obsidian Canvas work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact domain rules, layout recipes, validation checks, reusable examples, or tooling notes in this skill or a focused reference file. Do not store secrets, credentials, private content, copyrighted source text, generated logs, raw project/customer material, or one-off facts in the skill.

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
