---
name: skill-learning
description: Shared self-learning and reusable-lesson policy for the user's shared skill base and AI-specific thin adapters. Use when creating or updating a skill that should persist durable lessons, user preferences, reusable commands, failure modes, validation rules, or self-improvement behavior without duplicating the same learning instructions in every domain skill or every AI adapter.
---

# Skill Learning

## Purpose

Use this skill with `skill-creator` and `skill-management` when a shared-base skill needs a self-learning or self-improvement rule. Keep domain skills focused on their domain; put only domain-specific learning targets in the shared base and rely on this policy for the shared behavior.

## Self-Improvement And Publishing

When this self-learning policy itself needs a durable update, keep the rule compact and repository-agnostic. Before materially editing this skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check; after updating, validate, commit, and push the relevant skill changes by default unless the user explicitly says not to. Resolve merge conflicts autonomously when the intended final meaning can be determined safely.

## Common Repetitions Found

The Obsidian and corporate skill set repeats these general rules:

- keep one source of truth for each skill and avoid independent copied skill folders;
- keep AI-specific Codex/Claude adapters thin, with durable lessons stored once in `_base/skills/<skill-name>/`;
- persist durable lessons instead of relying on chat memory;
- save only reusable rules, workflows, commands, failure modes, preferences, or validation checks;
- reject secrets, credentials, personal data, confidential customer content, raw report text, unpublished measurements, and one-off project facts;
- keep `SKILL.md` concise, move growing details to `references/`, and move repeatable utilities to `scripts/`;
- validate a changed skill and follow the repository's commit/push rules;
- publish material self-learning updates by default for user-owned skills unless the user explicitly says not to;
- resolve semantic merge conflicts autonomously when the intended result can be determined safely.

## Learning Workflow

1. Decide whether the new fact is durable. It should be likely to recur across future tasks, not merely explain the current artifact. Treat a direct user correction to wording, style, workflow, or tool choice as durable by default when it generalizes beyond the current artifact. If the user asks to save their corrections into skills, persist each reusable correction during the same task without waiting for another reminder; exclude clearly one-off edits and protected content.
2. Classify the lesson:
   - domain behavior, style, or checklist rule: add a concise rule to the shared-base domain skill or a shared-base domain reference;
   - growing examples, lessons, or troubleshooting history: create or update `references/<topic>-lessons.md`;
   - repeatable command, parser, validator, or file operation: create or update `scripts/` and test it;
   - templates, boilerplate, media, or static resources: use `assets/`;
   - skill storage, sync, naming, publishing, adapter/base separation, or cross-PC behavior: update the shared base of `skill-management`.
3. Check safety before saving. Do not persist secrets, credentials, private keys, API tokens, personal data, customer-confidential material, raw report sections, unpublished measurements, or facts whose access policy is unclear.
4. Keep the saved rule minimal. Prefer a short decision rule, command pattern, checklist item, or reference pointer over a chat transcript or long example.
5. Before materially editing a skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check. For user-owned skills, follow `skill-management`; for corporate skills, follow the corporate checkout's freshness, validation, commit, push, and downstream-pointer rules. Validate and publish according to those rules. If remote changes or merge conflicts appear, resolve them autonomously when the intended final meaning can be determined from the files, commit history, and current user instruction. Preserve compatible rules, consolidate duplicates, rerun validation, commit, and push. Stop only when resolving would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.

## Domain Skill Pattern

When creating a new domain skill that should learn from future work, include only a short domain-specific section such as:

```markdown
## Learning

When work reveals a durable, reusable lesson for this domain, use the `skill-learning` policy. Save only the domain-specific rule, example, command, script, or reference here; do not store secrets, raw private content, or one-off project facts.
```

For domains with many operational lessons, point to a lessons file instead:

```markdown
## Learning

Before nontrivial work, read `references/<topic>-lessons.md`. Afterward, use the `skill-learning` policy to append compact reusable lessons there.
```

For user-owned skills, include the expectation that material self-learning updates are saved in the shared base, validated, committed, and pushed to the owning repository by default, with autonomous semantic merge-conflict resolution when safe.

## Update Checklist

Before finishing a learning update:

- confirm the rule is reusable and scoped to the right skill;
- confirm sensitive or one-off content was not persisted;
- run the skill validator when feasible;
- report exactly which skill or reference changed;
- commit and push only under the owning repository's rules.

## Coverage Audit

After adding, importing, or broadly updating skills, run `scripts/Test-SkillLearningCoverage.ps1` from this shared base. The script finds every canonical `_base/skills/<skill-name>/SKILL.md` under the selected repository, including initialized nested repositories, and verifies that each one either points to the shared `skill-learning` policy or has an actionable learning section with durable or reusable lesson language.

Thin Codex, Claude, and plugin adapters inherit behavior from their canonical shared base and should not duplicate the learning policy. Fix a reported gap in the canonical shared base, then rerun the audit until it exits successfully.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
