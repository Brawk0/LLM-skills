---
name: ru-official-documents
description: Write and review Russian official personnel and academic paperwork — рекомендательное письмо, характеристика, отзыв научного руководителя, представление, заявление, служебная записка, конкурсная заявка на должность. Use when a document will be signed by someone else (декан, заведующий кафедрой, научный руководитель, работодатель), when the user supplies an образец to follow, or when drafting text for a конкурсный отбор, аттестация, or кадровый пакет. Not for scientific manuscripts (see scientific-article-writing) or GOST reports (see nto-formatting).
---

# Russian Official Documents (Codex adapter)

Shared base skill: ../_base/skills/ru-official-documents/SKILL.md.

When this skill triggers, read that base SKILL.md completely and follow it together with any references/, scripts/, and assets/ next to the base file. Resolve relative resource paths from the shared base skill directory.

Keep this file as a Codex-specific thin adapter: frontmatter, trigger wording, and Codex-only metadata belong here; durable domain rules, reusable workflows, scripts, references, and lessons belong in the shared base skill.

Codex-specific notes:
- agents/openai.yaml is Codex UI metadata for this adapter.
- Update the shared base first for behavior changes, then adjust Codex/Claude adapters only when their platform-specific pointers or trigger descriptions need to change.
