from __future__ import annotations

import argparse
from pathlib import Path

from classify_install_hint import classify
from inspect_skill_repo import inspect


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown install report for a Claude-to-Codex skill install scenario."
    )
    parser.add_argument("--hint", required=True, help="User request, tutorial snippet, or install hint")
    parser.add_argument(
        "--target-path",
        help="Optional local repo/skill path to inspect alongside the install hint",
    )
    parser.add_argument(
        "--out",
        help="Optional output path for the Markdown report. Prints to stdout if omitted.",
    )
    return parser.parse_args()


def render_candidate_section(report: dict) -> list[str]:
    lines = ["## Candidates", ""]
    candidates = report.get("candidate_skills") or []
    if not candidates:
        lines.append("No installable candidate skill folders were detected.")
        lines.append("")
        return lines

    for candidate in candidates:
        trigger = candidate.get("trigger_profile") or {}
        deps = candidate.get("dependency_profile") or {}
        lines.append(f"### `{candidate.get('folder')}`")
        lines.append(f"- Declared name: `{candidate.get('name')}`")
        lines.append(f"- Compatibility score: `{candidate.get('compatibility_score')}`")
        lines.append(f"- Trigger quality: `{trigger.get('trigger_quality_score')}` ({trigger.get('trigger_quality_label')})")
        lines.append(f"- Dependency risk: `{deps.get('risk_band')}`")
        if candidate.get("compatibility_notes"):
            lines.append(f"- Compatibility notes: {'; '.join(candidate['compatibility_notes'])}")
        if trigger.get("prompt_matches"):
            best = trigger["prompt_matches"][0]
            lines.append(f"- Best prompt overlap: `{best['prompt']}` -> {', '.join(best['overlap'])}")
        lines.append("")
    return lines


def render_markdown(hint: str, classification: dict, repo_report: dict | None) -> str:
    lines = [
        "# Install Report",
        "",
        "## Input",
        "",
        f"```text\n{hint}\n```",
        "",
        "## Install Hint Classification",
        "",
        f"- Scenario: `{classification.get('scenario')}`",
        f"- Codex route: `{classification.get('codex_route')}`",
    ]

    extracted = classification.get("extracted") or {}
    if extracted:
        lines.append(f"- Extracted values: `{extracted}`")
    notes = classification.get("notes") or []
    if notes:
        lines.append(f"- Notes: {'; '.join(notes)}")

    if repo_report:
        lines.extend(
            [
                "",
                "## Repository Analysis",
                "",
                f"- Repo kind: `{repo_report.get('repo_kind')}`",
                f"- Recommended route: `{repo_report.get('recommended_route')}`",
                f"- Compatibility score: `{repo_report.get('compatibility_score')}`",
                f"- Install tier: `{repo_report.get('install_recommendation_tier')}`",
                f"- Candidate count: `{len(repo_report.get('candidate_skill_dirs') or [])}`",
                f"- Conflict count: `{len(repo_report.get('conflicts_with_installed') or [])}`",
            ]
        )
        if repo_report.get("notes"):
            lines.append(f"- Repo notes: {'; '.join(repo_report['notes'])}")
        lines.append("")
        lines.extend(render_candidate_section(repo_report))

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    classification = classify(args.hint)
    repo_report = inspect(Path(args.target_path)) if args.target_path else None
    markdown = render_markdown(args.hint, classification, repo_report)

    if args.out:
        Path(args.out).write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
