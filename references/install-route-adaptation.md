# Install Route Adaptation

This guide translates common Claude skill installation patterns into Codex-friendly actions.

## Why this matters

Users often discover skills through tutorials written for Claude, not Codex. The toolkit should recognize the installation style in the user's request and choose the correct adaptation path.

## Common Claude installation patterns

### 1. GitHub repo or repo path

Examples:
- `https://github.com/owner/repo`
- `owner/repo`
- `https://github.com/owner/repo/tree/main/skills/skill-name`
- `https://github.com/anthropics/skills/blob/main/skills/theme-factory/SKILL.md`

Claude context:
- often documented as a plugin marketplace repo
- may also be a direct skill repo

Codex adaptation:
- if the owner, URL, repo name, or surrounding text signals Claude or Anthropic, route through `claude-codex-skill-toolkit` first instead of treating it as a plain direct-install request
- inspect the repo
- locate `skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md`, or root `SKILL.md`
- install the exact skill folder
- migrate only if discovery or naming quality is weak

### 2. Claude marketplace add

Examples:
- `/plugin marketplace add owner/repo`
- `/plugin marketplace add https://gitlab.com/company/plugins.git`
- `/plugin marketplace add ./my-marketplace`

Claude context:
- adds a marketplace source containing `.claude-plugin/marketplace.json`

Codex adaptation:
- inspect the referenced repo or local directory
- do not assume the marketplace itself is the skill
- extract the real skill folders behind the marketplace metadata
- if only plugin wrappers exist, inspect platform packaging before install

### 3. Claude plugin install

Examples:
- `/plugin install ui-ux-pro-max@ui-ux-pro-max-skill`

Claude context:
- installs a plugin from a known marketplace

Codex adaptation:
- resolve the marketplace repo first
- inspect `.claude/skills/` or other packaged skill locations
- install or migrate the underlying skill folder, not the Claude plugin wrapper

### 4. Local plugin add

Examples:
- `/plugin add /path/to/skill-directory`
- `/plugin add ./path/to/marketplace.json`

Claude context:
- local plugin or marketplace install

Codex adaptation:
- inspect the local path directly
- if it points to a skill folder, evaluate `SKILL.md`
- if it points to marketplace/plugin metadata, locate the real child skill folders

### 5. Web upload as ZIP

Examples:
- "Upload a ZIP file containing your skill folder"
- "Package your skill folder as a ZIP file"

Claude context:
- Claude web UI supports skill ZIP uploads

Codex adaptation:
- unzip the package
- inspect the extracted folder
- install the contained skill folder into `.codex/skills`
- migrate only if discovery quality is poor

### 6. Skills API

Examples:
- `POST /v1/skills`
- "Create and manage custom agent skills"

Claude context:
- hosted API-managed skill lifecycle

Codex adaptation:
- local Codex installation still requires the actual filesystem skill package
- if the user only has a hosted `skill_id`, ask for the exported source files or ZIP
- if the repo/files are available, inspect them normally

### 7. Local Claude shell scaffold

Examples:
- `mkdir -p .claude/skills/ux-copy && touch .claude/skills/ux-copy/skill.md`
- `mkdir -p .claude/skills/ux-copy && printf "...markdown..." > .claude/skills/ux-copy/skill.md`
- `cp -R my-skill ~/.claude/skills/my-skill`

Claude context:
- common in tutorials, gists, or AI-generated shell snippets
- usually creates a local skill scaffold instead of installing a published skill from a registry

Codex adaptation:
- treat this as a local bootstrap flow, not as proof that a real published skill was installed
- inspect the generated folder directly
- normalize `skill.md` or `Skill.md` to `SKILL.md`
- convert markdown metadata sections into YAML frontmatter when needed
- only then install or copy the normalized skill into `.codex/skills`

## Recommended adaptive logic

1. Detect the install hint type from the user request.
2. Normalize it into a Codex route.
3. Inspect the underlying repo, folder, or ZIP.
4. Choose one of:
- direct install
- direct install with review
- migrate after inspection
- extract and migrate
- not recommended

## Official and ecosystem signals

Official patterns currently visible in Claude materials include:
- custom skill ZIP upload in Claude web settings
- Skills API creation and management for hosted skills
- plugin marketplace commands in Claude Code docs and ecosystem repos

Community repositories often document:
- `/plugin marketplace add ...`
- `/plugin install ...`
- GitHub repo URLs
- CLI installers that generate `.claude/skills/` or platform-specific files
- shell snippets that manually create `.claude/skills/<name>/skill.md` as a local bootstrap

## High-confidence Claude markers

Treat these as direct signals to use the Claude-to-Codex toolkit:
- `anthropics/` GitHub owner or `github.com/anthropics/...`
- any request text containing `Claude`, `Claude Code`, `Anthropic`, or `anthropics`
- `.claude/skills`, `.claude-plugin`, `skill.json`, `marketplace.json`
- `/plugin marketplace add`, `/plugin install`, `/plugin add`
- Claude ZIP upload and Skills API references

Treat these as softer signals that still deserve review:
- repo names containing `claude`
- docs or blog pages on `anthropic.com` or `docs.anthropic.com`
- mixed installer repos that mention both Codex and Claude in the same setup instructions
