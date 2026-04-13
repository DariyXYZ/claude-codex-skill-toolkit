# Compatibility Matrix

Use this matrix to choose the route quickly.

## Case: repo contains `skills/<name>/SKILL.md`

Recommended route:
- install that exact folder first
- read the installed `SKILL.md`
- validate discovery

Risk level:
- low to medium

Migration needed when:
- the description is weak
- the name is misleading
- discovery fails

## Case: repo contains `.claude/skills/<name>/SKILL.md`

Recommended route:
- treat the repo as a platform-specific skill source
- inspect `.claude/skills/` child folders directly
- install or migrate the exact child skill folder you need

Risk level:
- medium

Migration needed when:
- the repo only documents Claude marketplace install paths
- there is no obvious Codex-native packaging
- the skill name or description needs cleanup for Codex triggering

Extra signals:
- `skill.json`
- `.claude-plugin/plugin.json`
- multi-platform CLI install instructions in `README.md`

## Case: repo contains only a root `README.md` and links to other skills

Recommended route:
- do not install the repo as a skill
- treat it as a catalog
- select concrete downstream skill repos instead

Risk level:
- high for direct install

Migration needed when:
- the user wants a Codex-native curated package derived from that catalog

## Case: repo contains a skill, but instructions are Claude-marketplace-specific

Recommended route:
- inspect the real skill content
- preserve logic, not installation wrapper
- migrate to Codex-native packaging

Risk level:
- medium to high

Migration needed when:
- the workflow depends on Claude-only marketplace or plugin behavior

## Case: skill installs but does not appear in `codex debug prompt-input`

Recommended route:
- treat as failure
- inspect BOM, frontmatter, description quality, and installation path

Risk level:
- high

Migration needed when:
- frontmatter or discovery wording is poor

## Case: skill appears in Codex but triggers unreliably

Recommended route:
- strengthen the `description`
- add clearer trigger phrases
- remove vague wording

Risk level:
- medium

Migration needed when:
- the original wording was written for Claude-specific invocation behavior
