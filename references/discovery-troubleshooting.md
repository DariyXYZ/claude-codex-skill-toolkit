# Discovery Troubleshooting

## Symptom: skill exists on disk but does not appear in `Available skills`

Check:
- wrong installation directory
- missing `SKILL.md`
- malformed frontmatter
- UTF-8 BOM at file start
- duplicate copies causing you to inspect the wrong folder

## Symptom: skill appears but is rarely selected

Check:
- `description` is too generic
- the skill name is too abstract
- trigger phrases are missing
- the user request wording and the skill description do not overlap enough

## Symptom: repo looked installable but turned out to be a catalog

Check:
- whether there is any real skill folder with `SKILL.md`
- whether the repo only points to external skills

Response pattern:
- explain that the repo is an index, not a directly installable skill
- recommend concrete sub-skills or linked repos

## Symptom: plugin packaging exists but Codex still does not discover the skill

Check:
- whether the current Codex build indexes plugin-provided skills
- whether the canonical `.codex/skills/<name>` copy exists

## Symptom: Windows install keeps failing around Python

Check:
- whether `python` resolves to the Windows Store stub
- whether a real interpreter path is available

Response pattern:
- pick one working interpreter
- avoid bouncing between launchers
- continue with the helper script using the explicit interpreter path
