# Default Skill Pattern

Use this reference when creating or updating user-owned shared-base skills and AI-specific thin adapters.

## Minimal Structure

Every durable user-owned skill should have:

- `_base/skills/<skill-name>/SKILL.md` as the shared source of durable behavior;
- optional shared-base `references/` for detailed guidance that should load only when relevant;
- optional shared-base `scripts/` only for repeatable deterministic utilities;
- optional shared-base `assets/` only for reusable output resources;
- `<skill-name>/SKILL.md` as a thin Codex adapter pointing to the shared base;
- Codex `agents/openai.yaml` with `display_name`, `short_description`, and `default_prompt`;
- `.claude/skills/<skill-name>/SKILL.md` as a thin Claude adapter when Claude should expose the same skill.

Durable skills should live in the synced Google Drive skill repository or in a project Git repository. Local-only skill folders should contain only thin pointers/adapters, caches, or system-managed skills; do not put durable behavior there.

Avoid extra README, changelog, installation, or quick-reference files unless the user explicitly asks for them. Do not duplicate durable rules across Codex and Claude adapters.

## Default Self-Improvement Section

Adapt this section for non-static user-owned domain skills:

```markdown
## Self-Improvement And Publishing

When <domain> work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact domain rules, command patterns, parser improvements, validation checks, reusable examples, or tooling notes in this shared-base skill or a focused shared-base `references/<topic>.md` file. Do not store secrets, credentials, private content, copyrighted source text, generated logs, raw project/customer material, or one-off facts in the skill.

Before materially editing this skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check: fetch `origin main`, compare local `HEAD` with `origin/main`, fast-forward if local is behind and the relevant working tree is clean, and inspect dirty/ahead/diverged states before continuing.

After materially updating this skill, validate the shared base and adapters when feasible, then commit and push the relevant skill changes to the owning repository by default unless the user explicitly says not to. Stage only relevant skill files and repository metadata. Split commits by semantic block when the update contains independent concerns; avoid vague rollups such as "skill update".

If publishing encounters remote changes or merge conflicts, resolve them autonomously when the intended final meaning can be determined from the files, commit history, nearby rules, and the user's instruction. Preserve compatible rules from both sides, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.
```

For skills mirrored from the personal repository to a corporate repository, add that the personal repository copy is the safety copy and should not be deleted unless the user explicitly asks. If corporate publishing, permissions, sync, or merge resolution fails, preserve and report the personal copy or personal commit.

## Publishing Checklist

Use this checklist before committing user-owned skill changes:

1. Run the freshness check.
2. Validate changed shared-base skills and AI-specific adapters with the system `quick_validate.py` when feasible.
3. Test added or changed scripts.
4. Run `git status --short`.
5. Confirm unrelated user changes remain unstaged.
6. Confirm `secrets/`, credentials, caches, generated logs, and protected source material are not staged.
7. Stage only relevant skill files.
8. Run `git diff --cached --check`.
9. Commit with concise messages that each describe one semantic block.
10. Follow the owning repository's contribution policy. For `fufellen/LLM-skills`, first run `_base/skills/skill-management/scripts/Get-GitHubContributionMode.ps1`. An authenticated owner or administrator for which it returns `DirectMainAllowed = True` may push directly to `main`. Every other account must push `main_<github-login>` to the source repository when write access exists or to the user's fork otherwise, then open a pull request to `main`.

## Useful Commands

```powershell
git -C "C:\Users\User\Мой диск\Obsidian\.codex\skills" fetch origin main
git -C "C:\Users\User\Мой диск\Obsidian\.codex\skills" rev-parse HEAD
git -C "C:\Users\User\Мой диск\Obsidian\.codex\skills" rev-parse origin/main
git -C "C:\Users\User\Мой диск\Obsidian\.codex\skills" status --short
# quick_validate.py reads SKILL.md with the locale codec, so a Cyrillic
# description crashes it with UnicodeDecodeError on Windows. Force UTF-8:
$env:PYTHONUTF8 = "1"
python "C:\Users\User\.codex\skills\.system\skill-creator\scripts\quick_validate.py" "C:\Users\User\Мой диск\Obsidian\.codex\skills\<skill-name>"
git -C "C:\Users\User\Мой диск\Obsidian\.codex\skills" diff --cached --check
$access = powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\User\Мой диск\Obsidian\.codex\skills\_base\skills\skill-management\scripts\Get-GitHubContributionMode.ps1" -AsJson | ConvertFrom-Json
$access | Format-List
# Owner or administrator with a confirmed active bypass:
git -C "C:\Users\User\Мой диск\Obsidian\.codex\skills" push origin main
# Every other account:
$githubLogin = 'replace-with-login'
$branch = "main_$githubLogin"
git -C "C:\Users\User\Мой диск\Obsidian\.codex\skills" switch -c $branch origin/main
git -C "C:\Users\User\Мой диск\Obsidian\.codex\skills" push -u origin $branch
```

Use `git merge --ff-only origin/main` only after confirming local `HEAD` is behind and the relevant working tree is clean. If administrator bypass cannot be confirmed, do not use the direct-main command. When the account has no source-repository write access, add its fork as the `fork` remote and replace the branch push destination with `fork`; keep `origin` pointed at `fufellen/LLM-skills`. GitHub CLI is optional when plain Git can authenticate through a configured credential helper.

## Frontmatter Description Rule

Put triggering information in `description`, not only in the body. Include the task types, file types, tools, or phrases that should activate the skill. Keep it specific enough to beat generic skills but broad enough for natural requests.
