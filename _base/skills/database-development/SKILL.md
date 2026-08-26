---
name: database-development
description: Design, specify, build, and deploy databases and the applications around them. Use for база данных, БД, ТЗ на базу данных, SQL schema design, ER diagrams, PostgreSQL/SQLite/MySQL, CRUD record-keeping apps (students, teachers, lessons, payments, inventory, clients), server deployment of a database on a rented VPS, backups, migrations, and PC/mobile/web client apps over a database.
---

# Database Development

## Core Goal

Take a database project from an idea to a working system in controlled stages: requirements captured as files, a reviewed data model, SQL schema, a prototype, server deployment, and client applications. Project documents live in the user's Obsidian vault; code lives in a Git repository for that project.

## Workflow

1. **Requirements first.** Before any SQL, capture requirements in the project folder as separate notes: техническое задание (ТЗ), development plan, open questions for the stakeholder. Mine any existing materials (spreadsheets, Obsidian cards, paper forms) for real field names and workflows — they beat invented ones.
2. **Data model.** Turn entities into a Mermaid `erDiagram` inside a vault note, then into SQL DDL in the same note. Get the model reviewed against the ТЗ before writing application code.
3. **Prototype.** Validate the schema and core workflows with the smallest possible setup (SQLite or a local PostgreSQL plus a minimal UI) and realistic sample data before renting servers.
4. **Deployment.** Move to the production DBMS on the server, set up backups and access control, then build the real clients.
5. **Data migration.** Plan how existing records (e.g., Obsidian cards, Excel) get imported; write a one-off import script rather than retyping.

## Document Set

Each database project keeps these notes in its vault project folder, cross-linked with `[[wiki links]]`:

- `Техническое задание.md` — цель, роли, сущности, функции, отчёты, платформы, безопасность; keep it the single source of truth for scope.
- `Схема базы данных.md` — Mermaid ER diagram + SQL DDL, updated together; the DDL in the note must match the migrations in the code repo.
- `План разработки.md` — numbered phases with acceptance criteria ("этап готов, когда…").
- `Вопросы к заказчику.md` — open questions with answers filled in as they arrive; move settled answers into the ТЗ.

## Data Modeling Rules

- Money is `NUMERIC(10,2)` (or integer kopecks/cents), never float.
- Transactional rows snapshot their price: a lesson stores the price charged at that date, even though the current rate lives on the enrollment/rate table. Balances are computed from history, not stored as an editable field.
- People and other master-data rows get a `status` (active/archived) instead of hard deletes; history tables (lessons, payments) are append-only with corrections as new rows or an explicit `status`.
- Use snake_case names, surrogate `id` primary keys, explicit foreign keys with sensible `ON DELETE` behavior (usually `RESTRICT` for history, `CASCADE` only for pure child rows).
- A person who plays several roles (e.g., both administrator and teacher) is one `users`/`people` row with roles, not duplicate rows.
- Every table gets `created_at`; mutable tables also `updated_at`. Store timestamps in UTC (`timestamptz`) and convert in the UI.
- Schema changes ship as numbered migration files (`001_init.sql`, `002_...sql`) applied in order; never edit an applied migration.

## Default Stack

Options are ordered; take the first unless the project dictates otherwise:

1. **Server DB:** PostgreSQL on a rented VPS; SQLite for prototypes and single-user tools.
2. **Backend:** Python + FastAPI + SQLAlchemy/Alembic exposing a REST API; the DB port itself is never exposed to the internet.
3. **Client for ПК + телефон:** one responsive web app (server-rendered or SPA) behind HTTPS — covers desktop and phone with one codebase; wrap as PWA if an "app icon" is wanted. Native/Flutter apps only if offline work or device APIs are truly required.

For a FastAPI + Jinja2 + PostgreSQL admin app specifically, read [references/fastapi-jinja-web-patterns.md](references/fastapi-jinja-web-patterns.md) once at the start of the session — it collects the recurring traps (TemplateResponse signature, `body > nav` selector, `.box.stack` vertical forms, PWA/Web-Push setup, per-enrollment pricing, role ≠ job title, time-sheet-as-a-query, `TRUNCATE … RESTART IDENTITY CASCADE`, deploy-script env loading) so you don't rediscover them on every rebuild.

## Deployment And Operations

- VPS hardening basics: SSH keys only, firewall allowing SSH+HTTPS, DBMS listening on localhost/private network only, application connects via a least-privilege DB user.
- Backups from day one: nightly `pg_dump` to a dated file plus a copy off the server (object storage or synced drive); test a restore before declaring backups done.
- HTTPS via a reverse proxy (Caddy or nginx + certbot); no plain-HTTP logins.
- Keep server setup reproducible: a `deploy/` folder in the project repo with the compose file / service units and a short runbook note in the vault.

## Learning

When database work reveals a durable, reusable lesson (schema pattern, migration pitfall, DBMS quirk, deployment recipe, client-stack verdict), use the `skill-learning` policy. Save only the domain-specific rule, example, command, script, or reference here; do not store secrets, connection strings, dumps with real personal data, or one-off project facts.

## Self-Improvement And Publishing

When database-development work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact domain rules, command patterns, validation checks, reusable examples, or tooling notes in this shared-base skill or a focused shared-base `references/<topic>.md` file. Do not store secrets, credentials, private content, real personal data from project databases, generated logs, raw project/customer material, or one-off facts in the skill.

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
