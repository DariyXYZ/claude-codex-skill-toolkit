---
name: claude-codex-skill-toolkit
description: Convert, install, audit, package, and troubleshoot Claude Code skills for Codex. Use when the user asks to install a Claude skill in Codex, migrate a Claude-oriented skill, adapt a GitHub skill repo, fix Codex skill discovery, package a migrated skill for sharing, or review whether a Claude skill will work well in Codex.
---

# Claude to Codex Skill Toolkit

## Purpose

Handle the full Claude-to-Codex skill lifecycle:
- inspect a GitHub repo or local skill folder
- choose the shortest safe route: direct install or migration
- classify the install hint the user found in a Claude tutorial
- score compatibility, dependency risk, and install tier before acting
- rewrite discovery-critical metadata when needed
- validate that Codex can actually discover the result
- package the finished skill for reuse or GitHub publishing

Use this skill for both one-off installs and building a reusable, polished Codex-native port.

## Auto Trigger

Activate when the request includes ideas like:
- install this Claude skill in Codex
- migrate this Claude Code skill
- port this skill to Codex
- adapt this skill for Codex
- why is this installed skill not showing up
- package this migrated skill for GitHub
- review whether this Claude skill will work in Codex

## Quick Route Selection

Choose the shortest route that is still reliable.

1. If the repo already contains a clean `SKILL.md` and the folder layout is obvious, install the exact skill folder first, then validate discovery.
2. If the repo contains platform-specific layouts such as `.claude/skills`, `.claude-plugin`, or `skill.json`, inspect those signals before deciding it is non-installable.
3. If the repo is Claude-specific, ambiguous, multi-skill, or still uses Claude-only assumptions, migrate before claiming success.
4. If the task is only evaluation, inspect the repo and explain compatibility without installing anything.
5. If the user wants a shareable artifact, build a clean Codex-native package with minimal structure and validation notes.

Use `scripts/inspect_skill_repo.py` when a local folder is available and the repo layout is not obvious.
Use `scripts/check_skill_md.py` when you need a deterministic check of frontmatter or BOM issues.
Use `scripts/classify_install_hint.py` when the user pastes a Claude tutorial command or install snippet and you need to map it to a Codex route.
Use `scripts/trigger_score.py` when installability looks fine but you need to know whether the skill will actually match real user prompts well.
Use `scripts/generate_install_report.py` to leave behind a readable Markdown analysis after each install review.
Use `scripts/install_skill_flow.py` when you want a semi-automatic route selector that can also copy a chosen local skill into Codex.

## Core Workflow

1. Inspect the source.
Read the repo layout, locate `skills/`, `SKILL.md`, helper scripts, and any Claude-only packaging assumptions.

2. Decide the route.
Use `references/compatibility-matrix.md` to decide between direct install, light adaptation, or full migration.
If the user copied a tutorial command, normalize it first with `references/install-route-adaptation.md`.

3. Perform the smallest viable change.
- Direct install if the source is already Codex-friendly.
- Rewrite `SKILL.md` and supporting files if discovery or trigger quality is weak.
- Split long guidance into `references/` when building a durable Codex port.
- Use compatibility score and install tier to explain why a route is safe or risky.
- Generate an install report whenever the result will be reviewed later, shared, or used as a migration record.

4. Validate, do not assume.
Always verify:
- the skill folder exists where intended
- `SKILL.md` is parser-friendly
- the file is UTF-8 without BOM
- `codex debug prompt-input` exposes the skill when the target is a live Codex install

5. Package cleanly when asked.
For GitHub or sharing, keep one canonical skill folder with:
- `SKILL.md`
- `agents/openai.yaml` when useful
- `references/` only for material worth loading on demand
- `scripts/` only for deterministic helpers

## Fast Path For GitHub Skill Repos

When the user provides a GitHub repo or skill URL:

1. Inspect the repo root and `skills/` first.
2. Also inspect `.claude/skills`, root `skill.json`, and `.claude-plugin/plugin.json` before deciding the repo is only docs or a catalog.
3. Install the exact skill folder, not the whole repository, when the target path is clear.
4. Read the installed `SKILL.md` immediately after install.
5. Stop if discovery is already clean.
6. Switch to migration if the installed skill is invisible, vaguely named, malformed, or still Claude-only.

Bias toward exact `--repo` plus `--path` installs when you can infer the path confidently.

## Migration Rules

When migration is required:

1. Preserve behavior, not original packaging.
2. Rewrite the frontmatter so `name` and `description` clearly express both function and trigger phrases.
3. Keep the body concise and operational.
4. Move long playbooks, mappings, and troubleshooting into `references/`.
5. Avoid duplicate aliases unless there is a real discovery reason.

For the full sequence, read `references/migration-playbook.md`.

## Discovery Rules

- Treat "installed on disk but missing from `codex debug prompt-input`" as a failed install.
- Save `SKILL.md` as UTF-8 without BOM.
- Prefer one canonical folder per skill.
- Keep frontmatter simple.
- Make the `description` trigger-rich enough that Codex can match real user phrasing.

If discovery is broken, use `references/discovery-troubleshooting.md`.

## Packaging Rules

When building a shareable Codex-native port:

- publish the canonical skill folder itself
- avoid extra documentation files unless the user explicitly wants repo-facing docs
- keep helper scripts generic and deterministic
- do not ship duplicate migrated variants of the same skill
- if a repo contains multiple skills, package each one as a distinct skill folder

## Required Validation

Before calling the migration finished, verify:
- `scripts/check_skill_md.py <path-to-skill-md>` reports no blocking issues
- `scripts/inspect_skill_repo.py <path-to-skill-folder>` shows the expected structure
- compatibility score, dependency profile, and install tier are sensible for the chosen route
- trigger quality is good enough for realistic prompts, or the report clearly explains why migration polish is still needed
- `codex debug prompt-input` shows the skill when installed into a live Codex skills directory

## Reference Guide

Read only what is needed:
- `references/migration-playbook.md` for the end-to-end migration sequence
- `references/compatibility-matrix.md` for route selection
- `references/install-route-adaptation.md` for translating Claude install tutorials into Codex actions
- `references/install-workflow.md` for the semi-automatic installer pattern
- `references/discovery-troubleshooting.md` for failure analysis
