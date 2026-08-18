---
name: scientific-work
description: Work with the user's general PhD, scientific research materials, engineering explanations, and technical Obsidian notes. Use for научная работа, аспирантура, статьи, обзоры литературы, научные заметки, technical term questions, datasheet-based component selection or circuit explanations that should be saved to Work\Database, general modeling workflow, paper translation/analysis, and planning research next steps from the local vault. For specialized plasmonics, nanophotonics, SPP/DLSPP/LR-DLSPP, PCM photonics, EIM/ЭДП, optical antennas, or photonic COMSOL/FEM/CST mode-analysis tasks, use `plasmonics-photonics`.
---

# Scientific Work (Claude Code adapter)

Shared base skill: ../../../_base/skills/scientific-work/SKILL.md.

When this skill triggers, read that base SKILL.md completely and follow it together with any references/, scripts/, and assets/ next to the base file. Resolve relative resource paths from the shared base skill directory.

Keep this file as a Claude-specific thin adapter: frontmatter and Claude-only trigger wording belong here; durable domain rules, reusable workflows, scripts, references, and lessons belong in the shared base skill.

Notes:
- Ignore agents/openai.yaml; it is Codex-only metadata in the Codex adapter.
- Update the shared base first for behavior changes, then adjust Codex/Claude adapters only when their platform-specific pointers or trigger descriptions need to change.
