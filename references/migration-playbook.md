# Migration Playbook

## Goal

Turn a Claude-oriented skill into a Codex-native skill that installs cleanly, triggers reliably, and can be shared without confusing duplicates.

## Standard Sequence

1. Inspect source layout.
Look for:
- root `SKILL.md`
- `skills/` directory
- helper scripts
- Claude-only instructions
- plugin-only packaging

2. Identify the canonical unit.
Decide whether the repo contains:
- one installable skill folder
- a catalog of many skills
- only guidance, not a real skill

3. Choose a route.
- Direct install: source is already clean and Codex-friendly
- Light adaptation: install first, then improve frontmatter or wording
- Full migration: rewrite packaging and split references

4. Rewrite for Codex if needed.
Focus on:
- clear `name`
- trigger-rich `description`
- concise workflow body
- optional `agents/openai.yaml`
- references only where they reduce noise

5. Validate.
Check file structure, BOM, frontmatter, and discovery.

6. Package.
Keep one canonical folder that can be copied into `.codex/skills` or published directly.

## Heuristics

### Direct install is usually enough when

- the repo already has a clear `skills/<name>/SKILL.md`
- the frontmatter is simple
- the description already says what the skill does and when to use it
- the body is operational rather than Claude-marketing-heavy

### Full migration is usually needed when

- there is no usable `SKILL.md`
- the description is too vague to trigger well in Codex
- the file begins with BOM
- the repo depends on Claude-only plugin commands or marketplace behavior
- the repo mixes multiple aliases and duplicate directories

## Strong Description Pattern

Use a description that answers both:
- what the skill does
- when it should be used

Good pattern:

`Convert, install, audit, and package Claude Code skills for Codex. Use when the user asks to port a Claude skill to Codex, install a GitHub skill repo, fix discovery, or package a migrated skill for sharing.`

## Packaging Pattern

Prefer this shape:

```text
skill-name/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── migration-playbook.md
│   └── discovery-troubleshooting.md
└── scripts/
    ├── inspect_skill_repo.py
    └── check_skill_md.py
```

## Final Rule

If the user asks whether the migration is done, and the skill is not discoverable in the target Codex environment, the answer is still no.
