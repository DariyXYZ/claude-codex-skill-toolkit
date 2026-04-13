from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from classify_install_hint import classify
from generate_install_report import render_markdown
from inspect_skill_repo import get_codex_skills_root, inspect


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Semi-automatic Claude-to-Codex skill install flow."
    )
    parser.add_argument("--hint", required=True, help="User request, tutorial snippet, or install hint")
    parser.add_argument(
        "--target-path",
        help="Optional local repo or skill path to inspect and act on",
    )
    parser.add_argument(
        "--candidate-folder",
        help="Optional candidate folder name to choose from a multi-skill repo",
    )
    parser.add_argument(
        "--report-out",
        help="Optional path to write a Markdown install report",
    )
    parser.add_argument(
        "--execute-copy",
        action="store_true",
        help="Copy the chosen local skill folder into the local Codex skills directory.",
    )
    return parser.parse_args()


GITHUB_SKILL_PATH_RE = re.compile(r"/skills/([^/\s]+)")


def infer_candidate_from_classification(classification: dict, repo_report: dict) -> str | None:
    extracted = classification.get("extracted") or {}

    github_url = extracted.get("github_url")
    if github_url:
        match = GITHUB_SKILL_PATH_RE.search(github_url)
        if match:
            return match.group(1)

    plugin_ref = extracted.get("plugin_ref")
    if plugin_ref and "@" in plugin_ref:
        return plugin_ref.split("@", 1)[0]

    return None


def choose_candidate(classification: dict, repo_report: dict, candidate_folder: str | None) -> dict | None:
    candidates = repo_report.get("candidate_skills") or []
    if not candidates:
        return None

    desired_folder = candidate_folder or infer_candidate_from_classification(classification, repo_report)
    if desired_folder:
        for candidate in candidates:
            if candidate["folder"] == desired_folder:
                return candidate
        return None

    if len(candidates) == 1:
        return candidates[0]

    return None


def copy_to_codex_skills(skill_source: Path) -> Path:
    skills_root = get_codex_skills_root()
    if not skills_root:
        raise RuntimeError("Could not determine Codex skills root.")
    skills_root.mkdir(parents=True, exist_ok=True)

    destination = skills_root / skill_source.name
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(skill_source, destination)
    return destination


def main() -> int:
    args = parse_args()
    classification = classify(args.hint)
    repo_report = inspect(Path(args.target_path)) if args.target_path else None
    chosen_candidate = (
        choose_candidate(classification, repo_report, args.candidate_folder)
        if repo_report
        else None
    )

    result = {
        "classification": classification,
        "repo_report": repo_report,
        "chosen_candidate": chosen_candidate,
        "executed_copy_destination": None,
        "next_action": "",
    }

    if chosen_candidate:
        result["next_action"] = (
            f"Inspect or install candidate folder '{chosen_candidate['folder']}' "
            f"with tier {repo_report.get('install_recommendation_tier')}."
        )
    elif repo_report and len(repo_report.get("candidate_skills") or []) > 1:
        result["next_action"] = (
            "Multiple candidate skill folders were found. Choose one with "
            "--candidate-folder or use the generated report to review them."
        )
    else:
        result["next_action"] = f"Follow route: {classification.get('codex_route')}."

    if args.execute_copy:
        if not chosen_candidate:
            raise RuntimeError(
                "No candidate skill was selected. Provide --target-path and optionally --candidate-folder."
            )
        destination = copy_to_codex_skills(Path(chosen_candidate["path"]))
        result["executed_copy_destination"] = str(destination.resolve())

    if args.report_out:
        report_markdown = render_markdown(args.hint, classification, repo_report)
        Path(args.report_out).write_text(report_markdown, encoding="utf-8")

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
