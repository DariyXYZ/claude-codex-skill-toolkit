from __future__ import annotations

import argparse
import json
from pathlib import Path

from inspect_skill_repo import inspect


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a smoke-test matrix against local skill repositories."
    )
    parser.add_argument("paths", nargs="+", help="One or more local repo paths to inspect")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format",
    )
    return parser.parse_args()


def render_markdown(reports: list[dict]) -> str:
    lines = [
        "# Smoke Test Matrix",
        "",
        "| Repo | Kind | Route | Candidates | Conflicts | Notes |",
        "|---|---|---|---:|---:|---|",
    ]
    for report in reports:
        repo = Path(report["root"]).name
        kind = report.get("repo_kind") or "-"
        route = report.get("recommended_route") or "-"
        candidates = len(report.get("candidate_skill_dirs") or [])
        conflicts = len(report.get("conflicts_with_installed") or [])
        notes = "; ".join(report.get("notes") or [])
        lines.append(f"| `{repo}` | `{kind}` | `{route}` | {candidates} | {conflicts} | {notes} |")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    reports = [inspect(Path(path)) for path in args.paths]

    if args.format == "markdown":
        print(render_markdown(reports))
    else:
        print(json.dumps(reports, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
