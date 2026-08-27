---
name: oniip-publications
description: Prepare, format and check abstracts (тезисы) for the ONIIP conference «Радиофизика, фотоника и исследование свойств вещества» (РФИВ / RPSM, Omsk) and related ONIIP venues. Use for РФИВ-2026, тезисы докладов ОНИИП, шаблон тезисов Cambria, двуязычный блок «Для цитирования / For citation», conf@oniip.ru submissions, and for the companion journal «Техника радиосвязи» (Перечень ВАК). Covers the venue's hard prohibitions — no formulas, tables, abbreviations or references in abstracts — which reject a paper outright.
---

# ONIIP Publications (Codex adapter)

Shared base skill: ../_base/skills/oniip-publications/SKILL.md.

When this skill triggers, read that base SKILL.md completely and follow it together with any references/, scripts/, and assets/ next to the base file. Resolve relative resource paths from the shared base skill directory. The official 2026 rules PDF and abstract template DOCX are in that skill's assets/.

Keep this file as a Codex-specific thin adapter: frontmatter, trigger wording, and Codex-only metadata belong here; durable domain rules, reusable workflows, scripts, references, and lessons belong in the shared base skill.

Codex-specific notes:
- agents/openai.yaml is Codex UI metadata for this adapter.
- Update the shared base first for behavior changes, then adjust Codex/Claude adapters only when their platform-specific pointers or trigger descriptions need to change.
