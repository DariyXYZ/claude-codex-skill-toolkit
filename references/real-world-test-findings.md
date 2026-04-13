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
- should also be treated as Claude-oriented because the GitHub owner itself is `anthropics`

Takeaway:
- the current direct-install path works well for standard skill repositories
- `anthropics/...` is a first-class activation marker for the Claude-to-Codex toolkit, even when the repo layout is already Codex-friendly

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

### 4. `ehmo/platform-design-skills`

Observed shape:
- `skills/<platform>/SKILL.md`
- product-design-oriented platform skills for web, iOS, Android, and more

Toolkit outcome:
- correctly classified as `multi-skill-repo`
- revealed a practical naming collision with an already installed local skill

Important finding:
- `skills/web/SKILL.md` declares `name: web-design-guidelines`
- this collides with the already installed Vercel skill of the same frontmatter name

Takeaway:
- repo structure alone is not enough
- a migration toolkit should detect name collisions before install, not after

### 5. `ibelick/ui-skills`

Observed shape:
- `skills/` repo with focused UI review and repair skills

Toolkit outcome:
- correctly classified as `multi-skill-repo`

Takeaway:
- these repos are good candidates for raw install
- next-order evaluation should focus on trigger quality and dependency/risk, not just structure

### 6. `shadcn-ui/ui`

Observed shape:
- monorepo with a `skills/shadcn/SKILL.md`
- strong component and CLI-oriented guidance

Toolkit outcome:
- correctly classified as `multi-skill-repo`

Takeaway:
- very large monorepos can still expose a clean skill path
- the toolkit should help users locate the exact child skill rather than misclassifying the whole repo

## Main product improvements derived from testing

1. Detect `.claude/skills` as a first-class layout.
2. Surface `skill.json` and `.claude-plugin/plugin.json` as installability signals.
3. Distinguish platform-installer repos from true catalogs.
4. Treat `anthropics/...`, `Claude`, and `Anthropic` references as first-class toolkit triggers, not just normal GitHub installs.
5. Preserve a separate route for docs-only catalogs.
6. Detect frontmatter-name collisions against already installed Codex skills.
