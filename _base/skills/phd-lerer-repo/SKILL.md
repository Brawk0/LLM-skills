---
name: phd-lerer-repo
description: Maintain the user's `fufellen/phd_lerer` GitHub repository for PhD/Lerer calculation programs. Use when Codex needs to move, add, validate, document, commit, or push C, Python, COMSOL Java, EDP/EIM, plasmonic-waveguide, or other reproducible scientific calculation code into `phd_lerer`, keep README files current, or decide which generated artifacts belong in Git.
---

# PhD Lerer Repo

## Purpose

Use this skill for the dedicated calculation-code repository:

```text
GitHub: https://github.com/fufellen/phd_lerer
Local checkout (machine-dependent): C:\Users\mrfuf\source\phd_lerer or C:\Users\User\source\phd_lerer
Default branch: master
```

The checkout path differs per PC (for example `mrfuf` on one machine, `User` on another), so absolute paths written inside Obsidian notes may point at another machine's copy - resolve `phd_lerer` on the current PC instead of trusting a note's hardcoded path.

This repository is the durable home for reproducible calculation sources from the Lerer/PhD workflow. Obsidian notes may explain results, but source code, small deterministic inputs, and small reference outputs should live here when they are useful beyond one note.

## Checkout Freshness (before computing)

Before running repo scripts or trusting their numbers, confirm the local checkout is not behind `origin/master`: `git fetch origin`, then compare `HEAD` with `origin/master`. A stale checkout can carry outdated material tables (for example `composite_ema` `eps_au`/`eps_ag`/`eps_cu`) that silently change numeric results - a cross-check that should read 0.80 read 1.76 purely because the local `eps_au(532)` was an older table revision, and only matched the source note after a fast-forward. If the checkout is behind with a clean tree, fast-forward (`git merge --ff-only origin/master`) before computing; if it has diverged or the tree is dirty, resolve that first. After syncing, re-run the script's self-test and confirm anchor values match the source note before building anything on top.

## Repository Rules

- Put reusable calculation code in `phd_lerer`, not only in `CODEX/` folders inside Obsidian.
- Keep C sources, Python scripts, COMSOL Java model generators, small material tables, small CSV exports, and PNG comparison plots when they help reproduce or validate a result.
- Do not commit bulky or machine-local solver artifacts by default: `.mph`, `.class`, `.log`, `.status`, `.recovery`, build folders, caches, and virtual environments.
- Keep root `README.md` current whenever the repository structure changes.
- Add or update a local README in the scientific subfolder when usage needs commands, dependencies, expected outputs, or caveats.
- Stage only relevant files. Preserve unrelated dirty work in the repository or skill repo.

## EDP/COMSOL Layout

For the Ag strip EDP/FEM work, use:

```text
edp/
  Ag_.c
  metal_strip_w800/
    README.md
    requirements.txt
    scripts/
    comsol_exports/
    results/
```

Use `edp/Ag_.c` as the shared silver optical-constants source. If Python replaces direct C execution for analysis, put the Python scripts in `scripts/` and make README commands explicit.

## Validation Workflow

Before committing scientific code:

1. Run `git status --short --branch` and inspect the intended diff.
2. Run the smallest reproducibility checks available, for example:

```powershell
python .\edp\metal_strip_w800\scripts\repeat_lerer_metal_strip.py
python .\edp\metal_strip_w800\scripts\width_sweep_ag_strip.py
python .\edp\metal_strip_w800\scripts\compare_comsol_width_sweep_500nm.py
python .\edp\metal_strip_w800\scripts\compare_comsol_lambda_sweep_w800.py
```

3. Check that generated results land in the documented `results/` folder and that COMSOL postprocessors read from `comsol_exports/`.
4. If COMSOL itself is run, inspect the batch log and expected CSV files. Do not treat only the process exit code as success.
5. Record whether the result is `validated`, `diagnostic`, `discrepant`, or `unverified` in README text, a summary file, or the commit message.

## Publishing

For repository changes requested by the user, commit and push to `origin/master` when validation passes and no unrelated changes are staged. Use concise scientific commit messages, for example:

```text
Add EDP Ag strip validation scripts
Update COMSOL branch-selection diagnostics
Document phd_lerer EDP workflow
```

If push fails because of credentials, remote permissions, or network issues, keep the local commit and report the exact blocker.

## Skill Learning

When work with `phd_lerer` reveals a reusable repository convention, use the `skill-learning` policy and update this skill or the relevant domain skill. Do not store secrets, credentials, private raw datasets, unpublished full measurements, bulky generated solver files, or one-off project facts in the skill.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
