from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a local repo or skill folder for Claude-to-Codex migration triage."
    )
    parser.add_argument("path", help="Path to a local repo or skill folder")
    return parser.parse_args()


def find_skill_dirs(root: Path) -> list[Path]:
    results: list[Path] = []
    if (root / "SKILL.md").exists():
        results.append(root)
    skills_dir = root / "skills"
    if skills_dir.exists() and skills_dir.is_dir():
        for child in skills_dir.iterdir():
            if child.is_dir() and (child / "SKILL.md").exists():
                results.append(child)
    return sorted(set(results))


def inspect(path: Path) -> dict:
    report = {
        "root": str(path.resolve()),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "has_root_skill_md": (path / "SKILL.md").exists(),
        "has_skills_dir": (path / "skills").exists(),
        "candidate_skill_dirs": [],
        "recommended_route": "",
        "notes": [],
    }

    if not path.exists():
        report["recommended_route"] = "missing"
        report["notes"].append("Path does not exist.")
        return report

    if not path.is_dir():
        report["recommended_route"] = "invalid"
        report["notes"].append("Path is not a directory.")
        return report

    skill_dirs = find_skill_dirs(path)
    report["candidate_skill_dirs"] = [str(p.resolve()) for p in skill_dirs]

    if (path / "skills").exists() and skill_dirs:
        report["recommended_route"] = "install-exact-skill-folder"
        report["notes"].append(
            "Repo contains a skills/ directory. Install a concrete child skill folder, not the whole repo."
        )
    elif (path / "SKILL.md").exists():
        report["recommended_route"] = "inspect-root-skill"
        report["notes"].append(
            "Repo root itself looks like a skill. Check SKILL.md quality, then install or migrate."
        )
    else:
        report["recommended_route"] = "catalog-or-non-skill"
        report["notes"].append(
            "No installable skill folder detected. This may be a catalog, docs repo, or unsupported layout."
        )

    readme = path / "README.md"
    if readme.exists() and not skill_dirs:
        report["notes"].append(
            "README exists without a detected skill folder; inspect whether the repo is only an index of external skills."
        )

    return report


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    report = inspect(path)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
