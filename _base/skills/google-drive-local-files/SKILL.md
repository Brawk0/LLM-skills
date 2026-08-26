---
name: google-drive-local-files
description: Work with the user's Google Drive through the local synced filesystem rooted at `C:\Users\User\Мой диск`, not through the native Google Drive/Docs/Sheets/Slides connector. Use when the user asks to inspect, search, clean, organize, audit, delete, move, deduplicate, inventory, or find junk in Google Drive, My Drive, `Мой диск`, `гугл диск`, or `гугл хранилище`, especially when they say to work through files on the PC.
---

# Google Drive Local Files

## Operating Rule

Use the local Google Drive Desktop sync folder as the default source of truth:

```text
C:\Users\User\Мой диск
```

Do not use the native Google Drive, Docs, Sheets, or Slides connector by default for this user's Drive file work. Use those connectors only when the user explicitly asks for native Google Drive access, when Drive-only metadata is required, or when a Google-native file has no useful local content and the user accepts that limitation.

Important local roots:

- `C:\Users\User\Мой диск` - synced My Drive root.
- `C:\Users\User\Мой диск\Obsidian` - synced Obsidian vault.
- `C:\Users\User\Мой диск\Obsidian\.codex\skills` - synced user-owned skill repository.

For shell work on this Windows machine, prefer PowerShell with `-LiteralPath` for paths under `Мой диск`. Prefer `rg` / `rg --files` for text and filename search; use `Get-ChildItem` for metadata, size, time, and recursive filesystem inspection.

If a file is cloud-only, locked, partially synced, or represented locally only as a Google shortcut/placeholder, report that local access is limited instead of silently switching to a native connector.

## Safety

Start read-only for audits, cleanup planning, duplicate checks, and "what is junk?" requests.

Before deleting, moving, or bulk-renaming Drive-synced files:

1. Present exact candidate paths with size, last write time, reason, and confidence.
2. Separate "obvious trash" from "probably redundant" and "needs human review".
3. Wait for explicit user approval for the destructive action.
4. Use exact `Remove-Item -LiteralPath` or `Move-Item -LiteralPath` targets. Before recursive operations, verify resolved absolute paths stay under `C:\Users\User\Мой диск` or another explicitly named target.
5. Verify the result afterward.

Treat these cases carefully:

- `.tmp.drivedownload` and `.tmp.driveupload` are Google Drive Desktop temporary folders. They may be junk only when sync is idle/stale; do not delete recently modified contents while Drive may still be syncing.
- `desktop.ini` files in Drive-synced folders are usually harmless Windows/Drive folder metadata and may be regenerated.
- Obsidian `.trash` contains user-deleted notes and attachments; it is a cleanup candidate, not an automatic deletion target.
- Conflict copies from Google Drive, Obsidian Sync, or other sync tools may contain edits that exist nowhere else. Never delete conflict files in bulk by name or size heuristic alone.
- Google-native `.gdoc`, `.gsheet`, `.gslides`, or shortcut-like files may not contain document content locally.

## Junk Audit Workflow

For "junk", "trash", "мусор", "почистить диск", "что удалить", and similar requests, scan for candidates in groups:

- **Obvious temporary/system files:** `~$*`, `*.tmp`, `*.temp`, `*.part`, `*.crdownload`, `Thumbs.db`, `.DS_Store`, stale Drive temp folders.
- **Generated caches/build outputs:** `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.ipynb_checkpoints`, `dist`, `build`, local virtual environments, and package-manager caches inside Drive.
- **Duplicates and copies:** names containing `copy`, `копия`, `duplicate`, `(1)`, `(2)`, ` - Copy`, `_copy`, or repeated imported folder names. Confirm duplicates by size and hash before recommending deletion with high confidence.
- **Large low-value payloads:** installers, old archives, downloaded toolchains, ISO images, zipped backups, and duplicated exported media. Large files are not automatically junk; explain why each looks disposable or ask for review.
- **Empty or near-empty artifacts:** zero-byte Office lock files, logs, old backups, placeholder exports, and abandoned generated files.
- **Existing trash folders:** `.trash`, `Trash`, `Корзина`, and app-specific trash folders.

Report results as a practical cleanup list: path, size, last modified date, reason, and recommendation. Avoid calling something "safe to delete" unless the evidence is strong and the file is not user content.

## Skill Files

When the task is about the user's skills, work with the synced skill repository under:

```text
C:\Users\User\Мой диск\Obsidian\.codex\skills
```

Do not treat plugin caches under `C:\Users\User\.codex\plugins\cache` or system skills under `C:\Users\User\.codex\skills\.system` as the durable source for user-owned skill behavior. Use local cache/system copies only as references when explicitly needed.

For creating, updating, validating, committing, and pushing skills, use `skill-authoring`, `skill-management`, and `skill-learning` as applicable.

## Self-Improvement And Publishing

When local Google Drive filesystem work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact domain rules, command patterns, validation checks, reusable examples, or tooling notes in this shared-base skill or a focused shared-base reference file. Do not store secrets, credentials, private content, copyrighted source text, generated logs, raw project/customer material, or one-off facts in the skill.

Before materially editing this skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check: fetch `origin main`, compare local `HEAD` with `origin/main`, fast-forward if local is behind and the relevant working tree is clean, and inspect dirty/ahead/diverged states before continuing.

After materially updating this skill, validate the shared base and adapters when feasible, then commit and push the relevant skill changes to the owning repository by default unless the user explicitly says not to. Stage only relevant skill files and repository metadata.

If publishing encounters remote changes or merge conflicts, resolve them autonomously when the intended final meaning can be determined from the files, commit history, nearby rules, and the user's instruction. Preserve compatible rules from both sides, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
