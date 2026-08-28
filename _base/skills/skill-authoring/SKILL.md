---
name: skill-authoring
description: Create, update, validate, self-improve, publish, and maintain user-owned shared skills plus Codex/Claude thin adapters with the user's defaults. Use when asked to create a new skill, update an existing skill, scaffold shared-base SKILL.md resources or AI-specific adapters, add durable skill lessons, set up self-learning behavior, run skill validation, commit and push skill repository changes, or resolve skill repository merge conflicts.
---

# Skill Authoring

## Core Goal

Create and update shared-base skills plus AI-specific thin adapters so the user does not need to repeat repository, self-learning, validation, push, and merge-conflict expectations. New user-owned skills should be born with the user's defaults already encoded once in the shared base and exposed through Codex, Claude, or other adapters.

## Required Loading

When this skill is used, also use:

- the system `skill-creator` for canonical skill anatomy, `init_skill.py`, `quick_validate.py`, and `agents/openai.yaml` rules;
- `skill-management` for the synced Google Drive skill root, GitHub mirror, corporate submodule rules, and publishing policy;
- `skill-learning` when a skill should remember durable lessons, reusable commands, preferences, failure modes, or validation checks.

Read `references/default-skill-pattern.md` before creating a new skill or adding self-improvement/publishing behavior to an existing skill.

## User Defaults

- Create user-owned skills under `C:\Users\User\Мой диск\Obsidian\.codex\skills` unless the user explicitly requests another location.
- Prefer the synced Google Drive skill copy over local bootstrap/system copies.
- Never store durable user-owned skills only in local non-synced skill folders. Use the Google Drive skill repository or a project Git repository as the durable source, and keep any local-only skill entry as a thin pointer or adapter.
- Use the system `init_skill.py` for new skills; do not hand-roll the initial directory unless the generator is unavailable.
- Keep AI-specific adapter `SKILL.md` files and adapter folders thin. Put durable behavior in the shared base `SKILL.md`, growing guidance in shared-base `references/`, repeatable deterministic utilities in shared-base `scripts/`, reusable templates/media in shared-base `assets/`, and synced local credentials outside adapter folders.
- Add Codex `agents/openai.yaml` with a clear display name, short description, and default prompt when a Codex adapter exists.
- Add or update Claude adapters under `.claude/skills/<skill-name>/SKILL.md` when Claude should expose the same shared base.
- Include a compact self-improvement and publishing section in every non-static shared-base skill.
- Validate changed skills when feasible, stage only relevant files, commit, and push by default unless the user explicitly says not to.
- Split commits by semantic block when skill work contains independent concerns. Avoid vague rollups such as "skill update"; prefer separate concise commits for changes like "add publishing policy", "update protocol workflow", or "refresh Codex adapter".
- When mirroring a personal skill to a corporate repository, keep the personal repository copy as the safety copy unless the user explicitly asks to remove it. Corporate publishing problems should not risk losing the user's skill work.

## Freshness Check

Before materially editing a user-owned skill, applying self-learning updates, or publishing changes:

1. Run `git fetch origin main` in the owning skills repository.
2. Compare local `HEAD` with `origin/main`.
3. If they match, continue.
4. If local `HEAD` is behind and the relevant working tree is clean, fast-forward with `git merge --ff-only origin/main`.
5. If the repository is dirty, ahead, or diverged, inspect the state before editing or publishing. Continue autonomously only when dirty changes are unrelated to the target skill and can be left unstaged, or when the intended integration can be determined safely.

## Creation Workflow

1. Choose a short lowercase hyphen-case skill name. Avoid names that collide with system skills; use a clearer personal wrapper name when needed.
2. Create or update `_base/skills/<skill-name>/SKILL.md` as the shared source of durable behavior.
   - When the skill is built FROM a source document (an official template, spec, style guide, or example file), do not digest it by extracted text alone. RENDER it to images and inspect it visually too: visual conventions - table rule style, heading appearance, column layout, caption placement, equation numbering, footers/headers, text boxes - are invisible in extracted text and are exactly what gets missed. For DOCX/PDF use `scientific-article-writing` scripts/render_docx_pages.py; for a web page, screenshot it. Capture the visual rules in the skill, not only the textual ones.
3. Create or update the Codex adapter at `<skill-name>/SKILL.md`; keep it to frontmatter, trigger wording, and a pointer to the shared base.
4. Create or update `.claude/skills/<skill-name>/SKILL.md` when Claude should expose the same skill; keep it to Claude trigger wording and a pointer to the shared base.
5. Add the default self-improvement and publishing section from `references/default-skill-pattern.md` to the shared base, adapting only the domain-specific lesson examples and protected-content list.
6. Add or update shared-base references/scripts/assets only when they remove real future repetition.
7. Validate the shared base and adapters with `quick_validate.py`; test scripts that were added or changed.
8. Update `skill-management` when creating a durable user-owned skill so the synced skill inventory and routing stay current.
9. Commit and push the relevant shared-base and adapter files according to the publishing policy, using separate semantic commits when the changes cover independent concerns.

## Update Workflow

For existing skills, edit the synced shared base as the source of durable behavior, preserve user changes, and keep scope tight. Work through whichever thin adapter triggered the task, but do not save reusable rules in the adapter. If the update is a durable preference about how skills should be created or maintained, update the shared base for this skill and `skill-management` instead of hiding the rule in a one-off domain skill.

## Merge Conflict Handling

Resolve skill repository merge conflicts autonomously when the intended final meaning can be determined from the conflicting files, nearby rules, commit history, and the user's current instruction. Preserve compatible behavior from both sides, keep confidentiality and repository hygiene rules, validate the result, commit, and push.

Stop and report only when resolving would require guessing unavailable technical meaning, choosing between incompatible user instructions, exposing protected content, discarding user work, or using unavailable repository permissions.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
