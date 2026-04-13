from __future__ import annotations

import argparse
import json
from pathlib import Path


SKILL_LAYOUTS = (
    ("root", ""),
    ("skills-dir", "skills"),
    ("claude-skills-dir", ".claude/skills"),
)


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


def find_layout_candidates(root: Path) -> dict[str, list[Path]]:
    candidates: dict[str, list[Path]] = {}

    for layout_name, relative_path in SKILL_LAYOUTS:
        if layout_name == "root":
            if (root / "SKILL.md").exists():
                candidates[layout_name] = [root]
            continue

        base_dir = root / relative_path
        if not base_dir.exists() or not base_dir.is_dir():
            continue

        children = []
        for child in base_dir.iterdir():
            if child.is_dir() and (child / "SKILL.md").exists():
                children.append(child)
        if children:
            candidates[layout_name] = sorted(children)

    return candidates


def load_skill_json(root: Path) -> dict | None:
    skill_json = root / "skill.json"
    if not skill_json.exists():
        return None
    try:
        return json.loads(skill_json.read_text(encoding="utf-8"))
    except Exception:
        return {"_parse_error": True}


def inspect(path: Path) -> dict:
    skill_json = load_skill_json(path) if path.exists() and path.is_dir() else None
    layout_candidates = (
        find_layout_candidates(path) if path.exists() and path.is_dir() else {}
    )
    flattened_candidates = sorted(
        {
            candidate
            for paths in layout_candidates.values()
            for candidate in paths
        }
    )

    report = {
        "root": str(path.resolve()),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "has_root_skill_md": (path / "SKILL.md").exists(),
        "has_skills_dir": (path / "skills").exists(),
        "has_claude_skills_dir": (path / ".claude" / "skills").exists(),
        "has_claude_plugin": (path / ".claude-plugin" / "plugin.json").exists(),
        "has_skill_json": (path / "skill.json").exists(),
        "skill_json_name": skill_json.get("name") if isinstance(skill_json, dict) and "_parse_error" not in skill_json else None,
        "skill_json_platforms": skill_json.get("platforms") if isinstance(skill_json, dict) and "_parse_error" not in skill_json else [],
        "layout_candidates": {
            key: [str(p.resolve()) for p in value]
            for key, value in layout_candidates.items()
        },
        "candidate_skill_dirs": [],
        "repo_kind": "",
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

    skill_dirs = flattened_candidates or find_skill_dirs(path)
    report["candidate_skill_dirs"] = [str(p.resolve()) for p in skill_dirs]

    if "claude-skills-dir" in layout_candidates:
        report["repo_kind"] = "platform-installer-repo"
        report["recommended_route"] = "extract-platform-skill-folder"
        report["notes"].append(
            "Repo contains .claude/skills. Treat it as a platform-specific skill source and install or migrate individual child skill folders."
        )
        if report["has_skill_json"]:
            report["notes"].append(
                "Root skill.json suggests this repo may support multi-platform installation workflows."
            )
        if "codex" in (report["skill_json_platforms"] or []):
            report["notes"].append(
                "skill.json explicitly lists codex support; check whether the repo ships a Codex-native install path before migrating manually."
            )
    elif (path / "skills").exists() and skill_dirs:
        report["repo_kind"] = "multi-skill-repo"
        report["recommended_route"] = "install-exact-skill-folder"
        report["notes"].append(
            "Repo contains a skills/ directory. Install a concrete child skill folder, not the whole repo."
        )
    elif (path / "SKILL.md").exists():
        report["repo_kind"] = "single-skill-repo"
        report["recommended_route"] = "inspect-root-skill"
        report["notes"].append(
            "Repo root itself looks like a skill. Check SKILL.md quality, then install or migrate."
        )
    elif report["has_skill_json"] or report["has_claude_plugin"]:
        report["repo_kind"] = "installer-or-plugin-repo"
        report["recommended_route"] = "inspect-platform-packaging"
        report["notes"].append(
            "Repo exposes installer/plugin metadata but no direct root SKILL.md. Inspect platform packaging and extract the real skill folders before migration."
        )
    else:
        report["repo_kind"] = "catalog-or-docs"
        report["recommended_route"] = "catalog-or-non-skill"
        report["notes"].append(
            "No installable skill folder detected. This may be a catalog, docs repo, or unsupported layout."
        )

    readme = path / "README.md"
    if readme.exists() and not skill_dirs and not report["has_skill_json"] and not report["has_claude_plugin"]:
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
