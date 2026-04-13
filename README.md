# Claude to Codex Skill Toolkit

Convert, install, audit, package, and troubleshoot Claude Code skills for Codex.

This repository contains a Codex-native skill that helps with:
- installing Claude-oriented skills into Codex
- deciding when direct install is enough
- migrating Claude-only skills into Codex-friendly structure
- validating discovery issues such as weak frontmatter or UTF-8 BOM
- packaging migrated skills for sharing or publishing

## What is inside

- `SKILL.md`: the main Codex skill
- `agents/openai.yaml`: Codex UI metadata
- `references/`: migration playbook, compatibility matrix, troubleshooting notes
- `scripts/check_skill_md.py`: lint-like checker for discovery-critical `SKILL.md` issues
- `scripts/inspect_skill_repo.py`: quick repo triage for migration planning

## Install in Codex

Copy or clone this folder into your local Codex skills directory:

- Windows: `C:\Users\<you>\.codex\skills\claude-codex-skill-toolkit`
- Or any Codex-indexed skills path used by your environment

Then restart Codex.

## Typical use cases

- "Install this Claude skill in Codex"
- "Will this GitHub skill repo work well in Codex?"
- "Migrate this Claude Code skill to Codex"
- "Why is this skill on disk but not visible in Codex?"
- "Package this migrated skill for GitHub"

## Local checks

```powershell
python scripts/check_skill_md.py SKILL.md
python scripts/inspect_skill_repo.py .
```

## License

MIT. See `LICENSE.txt`.
