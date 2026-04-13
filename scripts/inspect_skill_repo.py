from __future__ import annotations

import argparse
import json
import re
from os import environ
from pathlib import Path
from trigger_score import score_skill_dir


SKILL_LAYOUTS = (
    ("root", ""),
    ("skills-dir", "skills"),
    ("claude-skills-dir", ".claude/skills"),
)

NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
DESCRIPTION_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)
COMMAND_HINT_RE = re.compile(
    r"\b(npm|pnpm|bun|bunx|npx|python|python3|pip|uv|node|cargo|go|gh)\b"
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


def parse_skill_metadata(skill_dir: Path) -> dict:
    skill_md = skill_dir / "SKILL.md"
    result = {
        "folder": skill_dir.name,
        "path": str(skill_dir.resolve()),
        "name": None,
        "description": None,
    }

    if not skill_md.exists():
        return result

    try:
        text = skill_md.read_text(encoding="utf-8-sig")
    except Exception:
        return result

    name_match = NAME_RE.search(text)
    desc_match = DESCRIPTION_RE.search(text)
    if name_match:
        result["name"] = name_match.group(1).strip().strip('"').strip("'")
    if desc_match:
        result["description"] = desc_match.group(1).strip().strip('"').strip("'")
    return result


def audit_candidate_dependencies(skill_dir: Path) -> dict:
    files = list(skill_dir.rglob("*"))
    file_names = {path.name.lower() for path in files if path.is_file()}
    suffixes = [path.suffix.lower() for path in files if path.is_file()]

    has_scripts_dir = (skill_dir / "scripts").exists()
    has_python = any(suffix == ".py" for suffix in suffixes)
    has_node = any(suffix in {".js", ".cjs", ".mjs", ".ts"} for suffix in suffixes)
    has_shell = any(suffix in {".sh", ".ps1", ".bash"} for suffix in suffixes)
    has_requirements = "requirements.txt" in file_names
    has_pyproject = "pyproject.toml" in file_names
    has_package_json = "package.json" in file_names
    has_lockfiles = any(
        name in file_names
        for name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb"}
    )

    command_hints = set()
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        try:
            text = skill_md.read_text(encoding="utf-8-sig")
            command_hints = set(COMMAND_HINT_RE.findall(text))
        except Exception:
            command_hints = set()

    risk_score = 0
    notes = []
    if has_scripts_dir:
        risk_score += 1
        notes.append("Contains scripts directory.")
    if has_python:
        risk_score += 1
        notes.append("Contains Python files.")
    if has_node:
        risk_score += 1
        notes.append("Contains Node/JS files.")
    if has_shell:
        risk_score += 2
        notes.append("Contains shell or PowerShell scripts.")
    if has_requirements or has_pyproject:
        risk_score += 1
        notes.append("Declares Python dependency metadata.")
    if has_package_json or has_lockfiles:
        risk_score += 1
        notes.append("Declares Node dependency metadata.")
    if len(command_hints) >= 3:
        risk_score += 1
        notes.append("SKILL.md references multiple external CLIs.")

    if risk_score <= 1:
        risk_band = "low"
    elif risk_score <= 3:
        risk_band = "medium"
    else:
        risk_band = "high"

    return {
        "has_scripts_dir": has_scripts_dir,
        "has_python": has_python,
        "has_node": has_node,
        "has_shell": has_shell,
        "has_requirements": has_requirements,
        "has_pyproject": has_pyproject,
        "has_package_json": has_package_json,
        "has_lockfiles": has_lockfiles,
        "command_hints": sorted(command_hints),
        "risk_band": risk_band,
        "notes": notes,
    }


def score_candidate(candidate: dict, conflicts: dict[str, list[str]]) -> tuple[int, list[str]]:
    score = 90
    reasons = []

    candidate_name = candidate.get("name")
    if not candidate_name:
        score -= 20
        reasons.append("Missing parsed skill name.")
    if not candidate.get("description"):
        score -= 10
        reasons.append("Missing parsed description.")

    dependency_profile = candidate.get("dependency_profile") or {}
    risk_band = dependency_profile.get("risk_band")
    if risk_band == "medium":
        score -= 8
        reasons.append("Medium dependency/runtime complexity.")
    elif risk_band == "high":
        score -= 18
        reasons.append("High dependency/runtime complexity.")

    if candidate_name and candidate_name in conflicts:
        score -= 20
        reasons.append("Conflicts with an already installed skill name.")

    if candidate_name and ":" in candidate_name:
        score -= 4
        reasons.append("Namespaced skill name may merit migration polish.")

    trigger_profile = candidate.get("trigger_profile") or {}
    trigger_score = trigger_profile.get("trigger_quality_score")
    if isinstance(trigger_score, int):
        if trigger_score >= 85:
            score += 5
            reasons.append("Strong trigger quality.")
        elif trigger_score >= 65:
            score += 2
            reasons.append("Good trigger quality.")
        elif trigger_score < 45:
            score -= 10
            reasons.append("Weak trigger quality.")

    score = max(0, min(100, score))
    return score, reasons


def score_repo(report: dict) -> tuple[int, str]:
    base_by_kind = {
        "single-skill-repo": 92,
        "multi-skill-repo": 86,
        "platform-installer-repo": 72,
        "installer-or-plugin-repo": 52,
        "catalog-or-docs": 8,
    }
    score = base_by_kind.get(report.get("repo_kind"), 40)

    if not report.get("candidate_skill_dirs"):
        score -= 25
    if report.get("conflicts_with_installed"):
        score -= 10
    if report.get("has_skill_json") and "codex" in (report.get("skill_json_platforms") or []):
        score += 6

    candidate_scores = [
        candidate.get("compatibility_score")
        for candidate in report.get("candidate_skills", [])
        if candidate.get("compatibility_score") is not None
    ]
    if candidate_scores:
        average_candidate = sum(candidate_scores) / len(candidate_scores)
        score = round((score * 0.55) + (average_candidate * 0.45))

    score = max(0, min(100, int(score)))

    if score >= 85:
        tier = "tier_1_direct_install"
    elif score >= 70:
        tier = "tier_2_direct_install_with_review"
    elif score >= 50:
        tier = "tier_3_migrate_after_inspection"
    elif score >= 30:
        tier = "tier_4_extract_and_migrate"
    else:
        tier = "tier_5_not_recommended"

    return score, tier


def get_codex_skills_root() -> Path | None:
    codex_home = environ.get("CODEX_HOME")
    if codex_home:
        root = Path(codex_home) / "skills"
        return root if root.exists() else root

    user_profile = environ.get("USERPROFILE")
    if not user_profile:
        return None
    return Path(user_profile) / ".codex" / "skills"


def get_installed_skill_names(skills_root: Path | None) -> dict[str, list[str]]:
    if not skills_root or not skills_root.exists():
        return {}

    installed: dict[str, list[str]] = {}
    for child in skills_root.iterdir():
        if not child.is_dir():
            continue
        metadata = parse_skill_metadata(child)
        if metadata["name"]:
            installed.setdefault(metadata["name"], []).append(str(child.resolve()))
    return installed


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
        "candidate_skills": [],
        "conflicts_with_installed": [],
        "candidate_skill_dirs": [],
        "repo_kind": "",
        "compatibility_score": None,
        "install_recommendation_tier": "",
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
    report["candidate_skills"] = [parse_skill_metadata(skill_dir) for skill_dir in skill_dirs]

    installed_skill_names = get_installed_skill_names(get_codex_skills_root())
    conflicts = []
    for candidate in report["candidate_skills"]:
        candidate["dependency_profile"] = audit_candidate_dependencies(Path(candidate["path"]))
        candidate["trigger_profile"] = score_skill_dir(Path(candidate["path"]))
        candidate_name = candidate.get("name")
        if candidate_name and candidate_name in installed_skill_names:
            conflicts.append(
                {
                    "candidate_name": candidate_name,
                    "candidate_path": candidate["path"],
                    "installed_paths": installed_skill_names[candidate_name],
                }
            )
    report["conflicts_with_installed"] = conflicts

    conflict_lookup = {
        item["candidate_name"]: item["installed_paths"]
        for item in conflicts
        if item.get("candidate_name")
    }
    for candidate in report["candidate_skills"]:
        score, reasons = score_candidate(candidate, conflict_lookup)
        candidate["compatibility_score"] = score
        candidate["compatibility_notes"] = reasons

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

    if conflicts:
        report["notes"].append(
            "One or more candidate skills have the same frontmatter name as already-installed Codex skills. Review for collisions before installing."
        )

    compatibility_score, install_tier = score_repo(report)
    report["compatibility_score"] = compatibility_score
    report["install_recommendation_tier"] = install_tier

    return report


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    report = inspect(path)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
