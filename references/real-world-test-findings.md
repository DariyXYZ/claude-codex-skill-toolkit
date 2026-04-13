# Real-world Test Findings

These findings came from testing the toolkit against real public repositories.

## Tested repositories

### 1. `anthropics/skills`

Observed shape:
- `skills/<name>/SKILL.md`
- many installable child skill folders

Toolkit outcome:
- correctly classified as `multi-skill-repo`
- recommended route: `install-exact-skill-folder`

Takeaway:
- the current direct-install path works well for standard skill repositories

### 2. `nextlevelbuilder/ui-ux-pro-max-skill`

Observed shape:
- `.claude/skills/<name>/SKILL.md`
- `.claude-plugin/plugin.json`
- root `skill.json`
- multi-platform CLI installation instructions, including Codex

Original toolkit behavior:
- misclassified as `catalog-or-non-skill`

Improved toolkit behavior:
- should classify as `platform-installer-repo`
- should recommend `extract-platform-skill-folder`

Takeaways:
- Claude/platform-specific repos often hide real skill folders under `.claude/skills/`
- `skill.json` and plugin manifests are strong signals that the repo is installable, just not in the default `skills/` layout
- at least some child skills from this repo can be copied into Codex and are successfully discovered

Live Codex discovery result:
- `.claude/skills/ui-styling` discovered in Codex as `ckm:ui-styling`
- `.claude/skills/design-system` discovered in Codex as `ckm:design-system`

Important nuance:
- these skills still may deserve optional migration for naming polish and trigger tuning, even when raw discovery works

### 3. `travisvn/awesome-claude-skills`

Observed shape:
- documentation and links only
- no installable `SKILL.md` folder

Toolkit outcome:
- correctly classified as `catalog-or-docs`
- recommended route: do not install directly

Takeaway:
- catalog repos should be treated as indexes, not install targets

## Main product improvements derived from testing

1. Detect `.claude/skills` as a first-class layout.
2. Surface `skill.json` and `.claude-plugin/plugin.json` as installability signals.
3. Distinguish platform-installer repos from true catalogs.
4. Keep direct-install guidance for standard `skills/` repos.
5. Preserve a separate route for docs-only catalogs.
