from __future__ import annotations

import argparse
import json
import re


GITHUB_URL_RE = re.compile(r"https?://github\.com/[^/\s]+/[^)\s]+")
GITHUB_SHORT_RE = re.compile(r"\b([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\b")
ZIP_RE = re.compile(r"\b(zip|upload a skill|upload.*zip|zip file)\b", re.IGNORECASE)
PLUGIN_MARKETPLACE_ADD_RE = re.compile(r"/plugin\s+marketplace\s+add\s+([^\s]+)")
PLUGIN_INSTALL_RE = re.compile(r"/plugin\s+install\s+([^\s]+)")
PLUGIN_ADD_RE = re.compile(r"/plugin\s+add\s+([^\s]+)")
API_SKILLS_RE = re.compile(r"(/v1/skills|POST\s+/v1/skills|Skills API)", re.IGNORECASE)
LOCAL_PATH_RE = re.compile(r"([A-Za-z]:\\[^\n\r]+|\.{0,2}/[^\s]+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify a Claude skill installation hint and map it to a Codex-compatible route."
    )
    parser.add_argument("text", help="User request, tutorial snippet, or install hint text")
    return parser.parse_args()


def classify(text: str) -> dict:
    text = text.strip()

    scenario = "unknown"
    extracted = {}
    codex_route = "inspect-manually"
    notes = []

    match = PLUGIN_MARKETPLACE_ADD_RE.search(text)
    if match:
        scenario = "claude-plugin-marketplace-add"
        extracted["marketplace_ref"] = match.group(1)
        codex_route = "inspect-marketplace-repo-and-extract-skill"
        notes.append(
            "Claude marketplace syntax usually points to a repo with .claude-plugin metadata, not a Codex-ready skill folder."
        )
        return {
            "scenario": scenario,
            "extracted": extracted,
            "codex_route": codex_route,
            "notes": notes,
        }

    match = PLUGIN_INSTALL_RE.search(text)
    if match:
        scenario = "claude-plugin-install"
        extracted["plugin_ref"] = match.group(1)
        codex_route = "resolve-plugin-source-then-extract-real-skill"
        notes.append(
            "Claude plugin install syntax needs the marketplace or source repo to determine the underlying skill files."
        )
        return {
            "scenario": scenario,
            "extracted": extracted,
            "codex_route": codex_route,
            "notes": notes,
        }

    match = PLUGIN_ADD_RE.search(text)
    if match:
        scenario = "claude-plugin-add-local-or-remote"
        extracted["path_or_url"] = match.group(1)
        codex_route = "inspect-local-or-remote-plugin-path"
        notes.append(
            "Claude /plugin add commonly targets a local directory or a remote marketplace/plugin descriptor."
        )
        return {
            "scenario": scenario,
            "extracted": extracted,
            "codex_route": codex_route,
            "notes": notes,
        }

    if API_SKILLS_RE.search(text):
        scenario = "claude-skills-api"
        codex_route = "needs-exported-files-or-zip"
        notes.append(
            "The Skills API manages hosted skills. Codex local installation still needs the underlying skill folder or ZIP."
        )
        return {
            "scenario": scenario,
            "extracted": extracted,
            "codex_route": codex_route,
            "notes": notes,
        }

    if ZIP_RE.search(text):
        scenario = "claude-zip-upload"
        codex_route = "unzip-and-inspect-skill-folder"
        notes.append(
            "Claude web upload flows typically use a ZIP package; for Codex, extract it and inspect the contained skill folder."
        )
        return {
            "scenario": scenario,
            "extracted": extracted,
            "codex_route": codex_route,
            "notes": notes,
        }

    github_url = GITHUB_URL_RE.search(text)
    if github_url:
        scenario = "github-repo-or-tree-url"
        extracted["github_url"] = github_url.group(0)
        codex_route = "inspect-github-repo-and-install-exact-skill-folder"
        notes.append(
            "A GitHub URL is the cleanest path for Codex: inspect the repo layout, then install or migrate the exact skill folder."
        )
        return {
            "scenario": scenario,
            "extracted": extracted,
            "codex_route": codex_route,
            "notes": notes,
        }

    github_short = GITHUB_SHORT_RE.search(text)
    if github_short:
        scenario = "github-owner-repo-ref"
        extracted["repo_ref"] = github_short.group(1)
        codex_route = "inspect-github-repo-and-install-exact-skill-folder"
        notes.append(
            "A short owner/repo reference usually maps to the same repo inspection flow as a full GitHub URL."
        )
        return {
            "scenario": scenario,
            "extracted": extracted,
            "codex_route": codex_route,
            "notes": notes,
        }

    local_path = LOCAL_PATH_RE.search(text)
    if local_path:
        scenario = "local-path"
        extracted["path"] = local_path.group(1)
        codex_route = "inspect-local-folder-or-zip"
        notes.append(
            "Local install hints should be inspected directly for SKILL.md, skills/, .claude/skills, or plugin metadata."
        )

    return {
        "scenario": scenario,
        "extracted": extracted,
        "codex_route": codex_route,
        "notes": notes,
    }


def main() -> int:
    args = parse_args()
    print(json.dumps(classify(args.text), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
