# Install Workflow

This note describes the semi-automatic install workflow layered on top of repo inspection and install-hint classification.

## Goal

Take a user-provided install hint and move from "tutorial syntax" to "Codex action plan" with minimal manual reasoning.

## Inputs

- install hint text
- optional local repo path
- optional chosen candidate folder

## Outputs

- normalized install scenario
- Codex route
- repo compatibility score
- install recommendation tier
- candidate skill shortlist
- optional Markdown report
- optional local copy into `.codex/skills`

## Script roles

### `classify_install_hint.py`

Normalizes tutorial syntax into a Codex route.

### `inspect_skill_repo.py`

Evaluates repo structure, dependency risk, trigger quality, conflicts, and install tier.

### `generate_install_report.py`

Produces a Markdown record of the analysis.

### `install_skill_flow.py`

Combines the previous scripts into a semi-automatic installer flow.

## Recommended usage pattern

1. Classify the install hint.
2. Inspect the repo or local extracted package.
3. Review score, tier, conflicts, and trigger quality.
4. Generate a report.
5. If the path is local and safe, copy the chosen skill into `.codex/skills`.
