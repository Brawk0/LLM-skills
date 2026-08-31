---
name: schematic-bom-export
description: Build the assembly Markdown BOM note and the matching print-ready PDF from a DipTrace BoM.csv export. Use when asked to make, refresh, or check a board BOM for an Obsidian assembly folder, to add batch quantity columns, to exclude non-purchasable mechanical placements, or to sanity-check a BOM export for duplicate part numbers, footprint/part-number mismatches and wrong resistor codes.
---

# Schematic BOM Export (Claude adapter)

Shared base skill: ../../../_base/skills/schematic-bom-export/SKILL.md.

When this skill triggers, read that base `SKILL.md` completely and follow it together with the necessary files under its `references/` and `scripts/` directories. Resolve relative resource paths from the shared-base skill directory.

Keep this adapter thin. Claude-specific trigger wording belongs here; durable BOM rules, layout constants, scripts, and reusable lessons belong in the shared base.
