---
name: skill-management
description: Create and update the user's shared skill base and AI-specific thin adapters for Codex, Claude, and other agents. Use when the user asks to add, edit, persist, synchronize, relocate, or organize skills, especially when deciding where skills should live across PCs and Google Drive.
---

# Skill Management

## Canonical Location

Create and update user-owned shared skills and AI-specific thin adapters in the Google Drive synced Obsidian vault by default:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills
```

This synced folder is the canonical repository for the user's personal skill system. Durable behavior lives in the shared base layer so Codex, Claude, and future AI-specific adapters can all use the same rules through Google Drive and Git synchronization.

## Shared Base And Thin Adapters

Use a two-layer skill architecture:

- Shared base skills live under `_base/skills/<skill-name>/`. Put durable domain rules, reusable workflows, references, scripts, assets, lessons, and self-improvement policy there.
- Codex adapters live at `<skill-name>/SKILL.md`, with Codex-only `agents/openai.yaml` next to them. Keep these files thin: frontmatter, trigger wording, and a pointer to the shared base.
- Claude adapters live at `.claude/skills/<skill-name>/SKILL.md`. Keep these files thin: Claude trigger wording and a pointer to the same shared base.
- Other AI-specific adapters should follow the same pattern: a minimal platform-specific wrapper that points to `_base/skills/<skill-name>/`.
- Keep adapter folders thin too. A Codex adapter folder should contain only `SKILL.md` plus platform metadata such as `agents/openai.yaml`; a Claude adapter folder should contain only its `SKILL.md` unless Claude-specific metadata becomes necessary. Do not keep `references/`, `scripts/`, `assets/`, `secrets/`, caches, generated logs, or durable workflow files inside adapter folders.
- Store synced local credentials outside adapter folders, for example under `.codex/secrets/<skill-name>/`, and document the path from the shared base when a script needs it. Keep legacy adapter-local secret paths only as temporary migration fallbacks.

When changing skill behavior, edit the shared base first. Edit Codex, Claude, or other adapters only when platform-specific trigger text, metadata, or pointer paths need to change. Do not copy durable rules into more than one adapter.

## GitHub Mirror

The Google Drive skill folder is also mirrored to GitHub:

```text
https://github.com/fufellen/LLM-skills
```

Local git repository path:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills
```

After materially creating or updating user-owned skills, commit and publish the skill changes to this repository by default unless the user explicitly says not to. For `fufellen/LLM-skills`, follow the root `README.md` contribution workflow. An authenticated repository owner or administrator with a confirmed active bypass may push directly to `origin/main`; a branch and pull request are optional for that account. The branch protection on `main` exists for outside contributors, not for the owner: the repository is published for shared use, but the owner is its sole maintainer and does not open pull requests against their own work. Consequently a successful owner push prints a remote notice of this shape, and it is the EXPECTED outcome, not a defect:

```text
remote: Bypassed rule violations for refs/heads/main:
remote: - Changes must be made through a pull request.
remote: - Cannot update this protected ref.
```

Do not report that notice as a problem, do not ask whether to switch to pull requests, and do not propose relaxing the protection rule (user clarification, 2026-08-18). Report the pushed commit range and continue. Every other account must use `main_<github-login>` and a pull request: push the branch to the source repository when write access exists, or create a fork and push it there when write access is absent or unknown. If administrator bypass cannot be confirmed, do not push to `main`. GitHub CLI is not required for plain Git operations when a configured credential helper can authenticate the push; create any required pull request through an available connector, REST API, website, or `gh`. Before committing:

Before choosing among those workflows, run `_base/skills/skill-management/scripts/Get-GitHubContributionMode.ps1` from the repository root. Use its machine-readable `AccessClass`, `DirectMainAllowed`, `RequiresFork`, `RequiresPullRequest`, and `WorkingBranch` fields. The script checks the authenticated GitHub account, effective repository permissions, active default-branch rulesets, and the administrator bypass without printing the credential. Do not infer access from a clone, login name, or public read access. If the check cannot authenticate or complete, fail closed: do not push to `main` and treat source-repository write access as unconfirmed.

1. Check `git status --short`.
2. Make sure `secrets/`, API keys, tokens, local credentials, caches, and generated logs are not staged.
3. Stage only relevant skill files and repo metadata.
4. Split commits by semantic block when the update contains independent concerns; avoid vague rollups such as "skill update" when separate commits like "document commit policy" and "refresh skill inventory" would be clearer.
5. Use concise commit messages that briefly describe the concrete change.
6. Keep `origin` pointed at the canonical repository, including when a separate `fork` remote is needed.
7. Run `scripts/Get-GitHubContributionMode.ps1`; if it reports `administrator` with `DirectMainAllowed = True`, the account may push directly to `origin/main`.
8. Otherwise push only `main_<github-login>` to `origin` when write access exists, or to `fork` when it does not.
9. For non-administrator contributions, open a pull request to `main` and do not merge it unless the owner explicitly asks. An administrator may use a pull request voluntarily.

If push fails because credentials, network, or remote permissions are unavailable, keep the local commit if it was created and report the exact blocker.

Before materially editing a user-owned skill, applying self-learning updates, or publishing changes, run a lightweight freshness check modeled on `nto-formatting`:

1. Fetch remote state with `git fetch origin main`.
2. Compare local `HEAD` with `origin/main`.
3. If they match, continue.
4. If local `HEAD` is behind and the relevant working tree is clean, fast-forward with `git merge --ff-only origin/main`.
5. If the repository is dirty, ahead, or diverged, inspect and report the state before editing or publishing. Continue autonomously only when dirty changes are unrelated to the target skill and can be left unstaged, or when the intended integration can be determined safely.

If remote changes, divergence, or merge conflicts occur while publishing user-owned skill changes, resolve them autonomously when the intended final meaning can be determined from the files, commit history, and the user's current instruction. Preserve compatible rules from both sides, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.

## Corporate Skills Submodule

The corporate skills repository is stored as a Git submodule inside the personal skills repository. Its root is the `nto-formatting` skill, and separately requested corporate skills may live as top-level skill folders inside that same checkout.

```text
Corporate source of truth: https://github.com/ak-tech-electronics/codex-skills
Personal repo with submodule: https://github.com/fufellen/LLM-skills
Submodule path in personal repo: nto-formatting
```

The corporate repo root is the skill folder itself: it must contain `SKILL.md` at repo root, plus optional `agents/`, `references/`, `scripts/`, and `assets/` folders. Do not nest it as `nto-formatting/SKILL.md` inside the corporate repo.

Keep personal-repo details out of the corporate `nto-formatting` skill. The personal repository knows that it consumes the corporate repo as a submodule; the corporate repo should only describe itself as the NTO skill source of truth and may refer generically to downstream mirrors or submodules.

Use corporate skills in-place from the Git checkout where they were cloned. Do not copy corporate skill folders into a system skills directory as independent duplicates. If a system-level skills repository, registry, bootstrap folder, or local Codex configuration needs to expose a corporate skill, store only a lightweight pointer to the checked-out skill path, such as a path entry, manifest entry, symlink, or submodule pointer. Edit, validate, commit, and push the corporate checkout itself.

Do not pull the NTO submodule on every ordinary skill use. Use this freshness model instead:

- For normal NTO drafting or review, use the local submodule checkout as-is.
- Before editing the NTO skill, applying self-learning updates, or publishing changes, run `git -C nto-formatting fetch origin main`.
- Compare `git -C nto-formatting rev-parse HEAD` with `git -C nto-formatting rev-parse origin/main`.
- If the submodule is behind and clean, fast-forward it with `git -C nto-formatting merge --ff-only origin/main`.
- If the submodule is dirty, ahead, or diverged, stop and report the state before editing.
- Use `git submodule update --remote nto-formatting` only when the user explicitly asks to sync to the latest corporate version without making a skill edit.

If a merge conflict occurs while updating or publishing the corporate `nto-formatting` skill, resolve it autonomously when the intended result can be determined from the files, commit history, and the user's current instruction. Validate the corporate skill, then commit and push the corporate repo. Commit and push the updated submodule pointer only when the current workspace is a parent repository that actually consumes the corporate repo as a submodule. If the current workspace contains only the standalone corporate repo, no parent pointer exists and no pointer commit is needed. Stop only when the conflict requires guessing unavailable technical meaning, choosing between incompatible user instructions, exposing confidential data, or using unavailable repository permissions.

When `nto-formatting` is materially updated:

1. Work inside the submodule path or a fresh corporate repo clone.
2. Validate the skill in the corporate repo root.
3. Commit and push the corporate repo first.
4. If working inside a parent repo with `nto-formatting` as a submodule, return to that parent repo and verify that `nto-formatting` points at the new corporate commit.
5. Commit and push the updated submodule pointer only when such a parent repo exists.
6. Report the corporate commit hash and, when applicable, the parent repo pointer commit hash.

Do not duplicate the corporate NTO skill as ordinary tracked files in the personal repo. On a fresh clone of the personal repo, initialize submodules with `git submodule update --init --recursive`; when updating from the corporate `main` branch, use `git submodule update --remote nto-formatting`.

## Corporate LTspice Skill

The `ltspice-simulation` skill is corporate-primary and lives inside the corporate checkout at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\nto-formatting\ltspice-simulation
```

Do not keep an independent top-level duplicate at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\ltspice-simulation
```

For LTspice skill reads, edits, validation, commits, and pushes, work in the corporate checkout path. After publishing corporate changes, commit and push only the updated submodule pointer in the personal repository.

## Default Rule

- When creating a new user skill, place it under the Google Drive synced skill folder above unless the user explicitly asks for another location.
- When updating an existing user skill, prefer the Google Drive copy if one exists.
- Never store durable user-owned skills only in local non-synced skill folders such as `C:\Users\User\.codex\skills`.
- Durable skills belong either in the Google Drive synced skill repository or in the Git repository of the project they serve.
- Treat local non-synced skill folders as temporary bootstrap pointers, thin adapters to the durable source, cache, or system-managed content, not as the durable home for user preferences.
- Do not commit or push synced secrets; keep `secrets/` folders and local credential files ignored.
- If a user gives a durable preference about how skills should be created, updated, named, synced, or used, add it to the shared base for this skill or the relevant domain skill without waiting for another reminder.
- When creating or materially updating user-owned skills, use `skill-authoring` as the personal default workflow, alongside the system `skill-creator` mechanics.
- Work through the AI-specific thin adapter that triggered, but persist reusable changes in `_base/skills/<skill-name>/`. The adapter should remain a pointer, not the source of durable behavior.
- When a new or existing skill needs self-learning, reusable lessons, or durable preference persistence, use the `skill-learning` skill instead of copying the full learning policy into every domain skill.
- Material self-learning updates to user-owned skills should be validated, committed, and pushed by default unless the user explicitly says not to. Future skill creation should include a compact domain-specific self-improvement section that points to `skill-learning` and this publishing/merge-conflict policy.
- Future skill creation should include an NTO-style freshness check before material edits, self-learning updates, and publishing.
- When a personal skill is mirrored to a corporate repository, keep the personal repository copy as the safety copy unless the user explicitly asks to remove it. Corporate publishing, permissions, sync, or merge failures must not cause loss of the user's personal skill work.

## Existing Google Drive Skills

- `scientific-work` (personal source of truth, now also mirrored into the corporate checkout at `.codex/skills/nto-formatting/scientific-work` so the corporate `scientific-article-writing` resolves its reference) currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\scientific-work
```

- `plasmonics-photonics` currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\plasmonics-photonics
```

- `knowledge-refactoring` currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\knowledge-refactoring
```

- `nto-formatting` currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\nto-formatting
```

- `ltspice-simulation` currently lives inside the corporate checkout at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\nto-formatting\ltspice-simulation
```

- `pdf-textbook-to-markdown` currently lives in the personal skills repository as the safety copy at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\pdf-textbook-to-markdown
```

It is also mirrored in the corporate checkout at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\nto-formatting\pdf-textbook-to-markdown
```

- `skill-learning` currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\skill-learning
```

- `skill-authoring` currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\skill-authoring
```

- `google-drive-local-files` currently lives at:

```text
C:\Users\User\Мой диск\Obsidian\.codex\skills\google-drive-local-files
```

- `obsidian-canvas` currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\obsidian-canvas
```

- `phd-lerer-repo` currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\phd-lerer-repo
```

- `markdown-to-docx` (personal source of truth, now also mirrored into the corporate checkout at `.codex/skills/nto-formatting/markdown-to-docx` so the corporate `scientific-article-writing` resolves its reference) currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\markdown-to-docx
```

- `optics-spectroscopy-article` currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\optics-spectroscopy-article
```

- `christian-presentations` currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\christian-presentations
```

- `presentation-creation` currently lives at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\presentation-creation
```

- `conference-paper-formatting` is the personal shared skill for compact conference-proceedings manuscripts that start directly with the introduction, omit the title and author block, use the stored two-column CJE_KB_CMP visual baseline, and end with the reference list. It lives at:

```text
C:\Users\User\Мой диск\Obsidian\.codex\skills\conference-paper-formatting
```

- Presentation workflow rules for scientific/popular-science decks currently live at:

```text
C:\Users\User\РњРѕР№ РґРёСЃРє\Obsidian\.codex\skills\scientific-work\references\presentation-workflow.md
```

- `scientific-article-writing` (universal venue-agnostic manuscript base) lives in the personal skills repository at `.codex/skills/scientific-article-writing` (shared base `_base/skills/scientific-article-writing/`) and is now also mirrored into the corporate checkout at `.codex/skills/nto-formatting/scientific-article-writing`. Keep the personal copy as the safety copy.

- `ru-language-purity` is the shared source of truth for де-кальке (RU/EN language purity: English calques, false friends, суржик, invented compounds, plus the mirror EN-from-RU check). Personal safety copy at `.codex/skills/ru-language-purity` (shared base `_base/skills/ru-language-purity/`, checklist in `references/decalque-ru-en.md`), mirrored into the corporate checkout at `.codex/skills/nto-formatting/ru-language-purity`. Referenced by `scientific-article-writing`, `nto-formatting`, `optics-spectroscopy-article`, and `apede-ieee-conference-article` instead of each embedding its own copy.

- `database-development` (design, specify, build, and deploy databases plus their server deployment and client apps) lives in the personal skills repository: shared base `_base/skills/database-development/`, Codex adapter `.codex/skills/database-development`, Claude adapter `.claude/skills/database-development`.

- `vps-server-management` (rent, secure, set up, and operate Linux VPS servers; SSH keys, ufw, swap, HTTPS reverse proxy, systemd services, backups; encodes the user's Windows+VPN connection quirks — native OpenSSH, not plink) lives in the personal skills repository: shared base `_base/skills/vps-server-management/` (with `references/connection-lessons.md`), Codex adapter `.codex/skills/vps-server-management`, Claude adapter `.claude/skills/vps-server-management`.

- `engineering-simulator-development` (source-faithful engineering simulators and digital twins; physical models, FPGA/firmware arithmetic, protocol/client reconstruction, calibration tables, engineering GUI, and Windows EXE delivery) lives in the personal skills repository: shared base `_base/skills/engineering-simulator-development/`, Codex adapter `.codex/skills/engineering-simulator-development`, Claude adapter `.claude/skills/engineering-simulator-development`.

- `diptrace-ascii` (structure-aware inspection, electrical audit, encoding-safe editing, and validation of DipTrace Schematic ASCII `.asc` files) lives in the personal skills repository: shared base `_base/skills/diptrace-ascii/`, Codex adapter `diptrace-ascii/`, Claude adapter `.claude/skills/diptrace-ascii/`.

- `jlink-mcp-runtime` is the Google Drive safety mirror of the complete portable J-Link Codex plugin from `C:\workspace\ToF-LIDAR-R\.codex\jlink-mcp-runtime`. Its thin Codex adapter lives at `.codex/skills/jlink-mcp-runtime`, while the shared workflow and full runnable plugin snapshot live at `_base/skills/jlink-mcp-runtime/`.

## Creating New Skills

When creating a new skill from scratch:

1. Use the personal `skill-authoring` workflow for user defaults and the system `skill-creator` guidance for generator/validation mechanics.
2. Use `skill-learning` when the skill should persist reusable lessons, failure modes, commands, durable user preferences, or self-improvement behavior.
3. Initialize the shared base in `_base/skills/<skill-name>/`.
4. Add a Codex adapter at `<skill-name>/SKILL.md` and, when Claude should use the skill, a Claude adapter at `.claude/skills/<skill-name>/SKILL.md`; both should point to the shared base.
5. Keep the adapter `SKILL.md` files concise and platform-specific only.
6. Put detailed workflows in shared-base `references/`.
7. Put deterministic utilities in shared-base `scripts/`.
8. Put templates and reusable media in shared-base `assets/`.
9. Validate the shared base and adapters with the skill-creator validation script when feasible.
10. Include a compact self-improvement section in the shared base that says durable lessons should be saved through `skill-learning`, validated, committed, pushed, and semantically merge-resolved when safe.

## Updating Existing Skills

Before editing a skill:

1. Check whether a Google Drive version exists.
2. Edit the Google Drive version first.
3. If the change affects durable behavior, edit `_base/skills/<skill-name>/`, not the Codex/Claude adapter.
4. Edit adapters only for platform-specific frontmatter descriptions, UI metadata, or pointer paths.
5. Avoid editing system skills under `.system` unless the user explicitly asks and the file is intended to be user-modifiable.
6. After updating, tell the user exactly which shared base and adapter files changed.

## Cross-PC Expectations

For a skill to be useful on another PC:

- its folder should be inside the synced Google Drive skill root;
- scripts and references should use relative paths where possible;
- absolute paths may mention the expected vault root, but should explain that Google Drive sync must place the vault at the same or adapted path;
- secrets should not be duplicated unless the user explicitly requests synced secrets for convenience;
- if a local connector or plugin is required, document how to test it from the synced skill.

## Relationship To Domain Skills

Use this skill for general rules about skill storage and synchronization. Use domain skills for domain behavior:

- general scientific notes, papers, PhD work, Obsidian research workflows: `scientific-work`;
- plasmonics, nanophotonics, SPP/DLSPP/LR-DLSPP, PCM photonics, optical antennas, EIM/Р­Р”Рџ, and photonic COMSOL/FEM/CST mode-analysis workflows: `plasmonics-photonics`;
- scientific and technical report / NTO formatting: `nto-formatting`;
- natural Russian scientific language and the shared RU/EN де-кальке checklist (English calques, false friends, суржик, invented compounds) used across the manuscript/report skills: `ru-language-purity`;
- LTspice schematic and netlist simulation workflows: `nto-formatting/ltspice-simulation`;
- PDF textbook to Markdown workflows: `pdf-textbook-to-markdown` in the personal repo, mirrored to `nto-formatting/pdf-textbook-to-markdown` in the corporate repo when requested;
- shared self-learning and reusable-lesson policy for skills: `skill-learning`;
- user-owned skill creation/update workflow and default self-improvement/publishing policy: `skill-authoring`;
- local synced Google Drive filesystem search, cleanup, storage audit, and Drive-backed skill/file access: `google-drive-local-files`;
- Obsidian `.canvas` creation, validation, and visual tree layout: `obsidian-canvas`;
- reproducible PhD/Lerer calculation-code repository work: `phd-lerer-repo`;
- database design, ТЗ, SQL schemas, server deployment, and client apps over a database: `database-development`;
- renting, securing, configuring, and operating Linux VPS servers, and deploying apps onto them (SSH, ufw, swap, HTTPS, systemd, backups): `vps-server-management`;
- source-faithful engineering simulators and digital twins that must reproduce mechanics, FPGA/firmware arithmetic, device protocols, production-client reconstruction, calibration tables, GUI behavior, and Windows EXE releases: `engineering-simulator-development`;
- DipTrace Schematic ASCII inspection, net/pin/pad reconstruction, datasheet-backed electrical and component-height audits, Cyrillic normalization, and encoding-safe `.asc` edits: `diptrace-ascii`;
- journal-article formatting and submission packaging for «Оптика и спектроскопия» / Ioffe journals: `optics-spectroscopy-article`;
- general slide deck creation, review, regeneration, and `.pptx` handling: `presentation-creation`;
- compact conference-proceedings manuscript formatting based on the user's stored two-column example: `conference-paper-formatting`;
- efficient ModelSim (Intel FPGA Starter Edition 10.5b) simulation workflows — vsim/vlog/.do automation, batch runs, WLF/dataset comparison, modelsim.ini tuning, error diagnosis: `modelsim` (project-specific ModelSim facts for `C:\workspace\verilog` stay in `fpga-dev`);
- Christian, church, Bible, Sunday school, youth, sermon, camp, and devotional deck content rules: `christian-presentations`, used alongside `presentation-creation`;
- presentation-specific behavior for research talks: `scientific-work/references/presentation-workflow.md`, used alongside `presentation-creation` when relevant;
- Obsidian REST/MCP bridge details: `scientific-work/references/obsidian-ai-integration.md`.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
