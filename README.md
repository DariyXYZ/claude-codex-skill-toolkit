# Claude to Codex Skill Toolkit

Convert, install, audit, package, and troubleshoot Claude Code skills for Codex.

This repository contains a Codex-native skill for people who need to move skills from Claude-oriented ecosystems into Codex without guessing what will actually work.

![Validate Skill](https://github.com/DariyXYZ/claude-codex-skill-toolkit/actions/workflows/validate.yml/badge.svg)

It helps with:

- installing Claude-oriented skills into Codex
- deciding when direct install is enough
- migrating Claude-only skills into Codex-friendly structure
- handling Claude- or platform-specific layouts such as `.claude/skills`, `.claude-plugin`, and `skill.json`
- handling shell snippets that manually create `.claude/skills/<name>/skill.md`
- detecting skill-name collisions against already installed Codex skills
- scoring compatibility and install risk before install
- adapting Claude tutorial install styles into Codex-friendly routes
- validating discovery issues such as weak frontmatter or UTF-8 BOM
- packaging migrated skills for sharing or publishing

## Who this is for

- Codex users installing skills from Claude- or Anthropic-oriented repos
- people adapting multi-platform skill repos into Codex-friendly layouts
- maintainers who want a repeatable migration and validation workflow

## Why this repo exists

Installing a skill from GitHub is often not enough when the source repo uses Claude-specific packaging such as `.claude/skills`, `.claude-plugin`, `skill.json`, or marketplace-style install instructions.

This toolkit exists to:

- distinguish direct-install cases from migration cases
- validate discovery-critical details before calling the install done
- reduce broken installs caused by weak metadata, wrong folder choice, or platform assumptions

## Quick install

Copy or clone this folder into your local Codex skills directory:

- Windows: `C:\Users\<you>\.codex\skills\claude-codex-skill-toolkit`
- or any Codex-indexed skills path used by your environment

Then restart Codex.

## Quick use

Typical prompts:

- "Install this Claude skill in Codex"
- "Will this GitHub skill repo work well in Codex?"
- "Migrate this Claude Code skill to Codex"
- "Why is this skill on disk but not visible in Codex?"
- "Package this migrated skill for GitHub"

## Automatic Claude markers

This toolkit should be used automatically when a user asks to install a skill and the request contains Claude-oriented signals, even if they do not explicitly say "use claude-codex-skill-toolkit".

Strong markers include:

- GitHub URLs or `owner/repo` references under `anthropics/`, especially `anthropics/skills`
- text containing `Claude`, `Claude Code`, `Anthropic`, or `anthropics`
- `.claude/skills`, `.claude-plugin`, `skill.json`, or `marketplace.json`
- `/plugin marketplace add`, `/plugin install`, and `/plugin add`
- Claude ZIP upload instructions and Skills API references

Expected behavior:

- detect the Claude marker first
- run the toolkit flow
- inspect the real skill layout
- choose direct install, install-with-review, migration, or extract-and-migrate
- validate Codex discovery before calling the install done

## What is inside

- `SKILL.md`: the main Codex skill
- `agents/openai.yaml`: Codex UI metadata
- `references/`: migration playbook, compatibility matrix, troubleshooting notes
- `scripts/check_skill_md.py`: lint-like checker for discovery-critical `SKILL.md` issues
- `scripts/inspect_skill_repo.py`: quick repo triage for migration planning
- `scripts/run_smoke_matrix.py`: smoke-test matrix for multiple local skill repos
- `scripts/classify_install_hint.py`: translates Claude-oriented install hints into Codex install routes
- `scripts/trigger_score.py`: estimates how well a skill will match realistic user phrasing
- `scripts/generate_install_report.py`: creates a Markdown install report after analysis
- `scripts/install_skill_flow.py`: semi-automatic install workflow for local repo or skill paths

## Typical use cases

- "Install this Claude skill in Codex"
- "Install this skill: https://github.com/anthropics/skills/blob/main/skills/theme-factory/SKILL.md"
- "Поставь скилл https://github.com/anthropics/skills/blob/main/skills/theme-factory/SKILL.md"
- "Will this GitHub skill repo work well in Codex?"
- "Migrate this Claude Code skill to Codex"
- "Will this mkdir/printf .claude/skills command really install a Claude skill?"
- "Why is this skill on disk but not visible in Codex?"
- "Package this migrated skill for GitHub"

## Local checks

```powershell
python scripts/check_skill_md.py SKILL.md
python scripts/inspect_skill_repo.py .
python scripts/run_smoke_matrix.py C:\path\to\repo1 C:\path\to\repo2 --format markdown
python scripts/classify_install_hint.py "/plugin marketplace add owner/repo"
python scripts/classify_install_hint.py "mkdir -p .claude/skills/ux-copy && printf \"...\" > .claude/skills/ux-copy/skill.md"
python scripts/trigger_score.py C:\path\to\skill-folder
python scripts/generate_install_report.py --hint "https://github.com/owner/repo" --target-path C:\path\to\repo
```

## Semi-automatic install flow

Example:

```powershell
python scripts/install_skill_flow.py `
  --hint "/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill" `
  --target-path C:\path\to\ui-ux-pro-max-skill `
  --report-out install-report.md
```

If the target path is local and you already know the chosen candidate folder, you can also copy it into Codex:

```powershell
python scripts/install_skill_flow.py `
  --hint "https://github.com/anthropics/skills/tree/main/skills/frontend-design" `
  --target-path C:\path\to\repo `
  --candidate-folder frontend-design `
  --execute-copy
```

## Real-world findings

This toolkit has been smoke-tested against:

- `anthropics/skills` as a standard `skills/<name>/SKILL.md` multi-skill repo
- `nextlevelbuilder/ui-ux-pro-max-skill` as a multi-platform installer repo with `.claude/skills`, `.claude-plugin`, and `skill.json`
- `travisvn/awesome-claude-skills` as a catalog repo that should not be installed directly
- manual `.claude/skills/<name>/skill.md` shell scaffolds that need filename and metadata normalization before Codex install

See `references/real-world-test-findings.md`.
See `references/install-route-adaptation.md`.
See `references/claude-install-patterns-research.md`.

## Scope boundary

This repository focuses on Claude-to-Codex skill compatibility, migration, validation, and packaging. It is not a general-purpose plugin manager for arbitrary development tools.

## License

MIT. See `LICENSE.txt`.
