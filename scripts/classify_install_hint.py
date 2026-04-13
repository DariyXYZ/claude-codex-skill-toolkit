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
CLAUDE_LOCAL_SKILL_SNIPPET_RE = re.compile(r"\.claude/skills/([^/\s]+)", re.IGNORECASE)
LOCAL_SCAFFOLD_COMMAND_RE = re.compile(r"\b(mkdir|touch|printf|cat|echo|cp|copy)\b", re.IGNORECASE)
CLAUDE_TEXT_RE = re.compile(r"\b(claude|claude code|anthropic|anthropics)\b", re.IGNORECASE)
CLAUDE_GITHUB_OWNER_RE = re.compile(r"github\.com/anthropics/|^anthropics/", re.IGNORECASE)
CLAUDE_DOCS_RE = re.compile(r"(docs\.anthropic\.com|anthropic\.com)", re.IGNORECASE)


def detect_claude_signals(text: str) -> list[str]:
    signals: list[str] = []
    normalized = text.strip()

    if CLAUDE_TEXT_RE.search(normalized):
        signals.append("mentions-claude-or-anthropic")
    if CLAUDE_GITHUB_OWNER_RE.search(normalized):
        signals.append("anthropics-github-source")
    if ".claude/" in normalized.lower() or "\\.claude\\" in normalized.lower():
        signals.append("claude-local-path")
    if PLUGIN_MARKETPLACE_ADD_RE.search(normalized):
        signals.append("claude-plugin-marketplace-command")
    if PLUGIN_INSTALL_RE.search(normalized) or PLUGIN_ADD_RE.search(normalized):
        signals.append("claude-plugin-command")
    if API_SKILLS_RE.search(normalized):
        signals.append("claude-skills-api")
    if ZIP_RE.search(normalized):
        signals.append("claude-zip-or-upload-flow")
    if CLAUDE_DOCS_RE.search(normalized):
        signals.append("anthropic-docs-or-domain")

    github_match = GITHUB_URL_RE.search(normalized)
    if github_match:
        github_url = github_match.group(0).lower()
        if "/blob/" in github_url or "/tree/" in github_url:
            signals.append("github-path-link")
        if "/skills/" in github_url:
            signals.append("github-skills-path")
        if "claude" in github_url:
            signals.append("claude-in-github-url")

    short_match = GITHUB_SHORT_RE.search(normalized)
    if short_match and "claude" in short_match.group(1).lower():
        signals.append("claude-in-repo-name")

    # Preserve order but avoid duplicates.
    return list(dict.fromkeys(signals))


def has_strong_claude_signal(signals: list[str]) -> bool:
    strong_signals = {
        "mentions-claude-or-anthropic",
        "anthropics-github-source",
        "claude-local-path",
        "claude-plugin-marketplace-command",
        "claude-plugin-command",
        "claude-skills-api",
        "claude-zip-or-upload-flow",
        "anthropic-docs-or-domain",
        "claude-in-github-url",
        "claude-in-repo-name",
    }
    return any(signal in strong_signals for signal in signals)


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
    claude_signals = detect_claude_signals(text)
    should_use_toolkit = has_strong_claude_signal(claude_signals)

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
            "claude_signals": claude_signals,
            "should_use_claude_codex_skill_toolkit": should_use_toolkit,
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
            "claude_signals": claude_signals,
            "should_use_claude_codex_skill_toolkit": should_use_toolkit,
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
            "claude_signals": claude_signals,
            "should_use_claude_codex_skill_toolkit": should_use_toolkit,
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
            "claude_signals": claude_signals,
            "should_use_claude_codex_skill_toolkit": should_use_toolkit,
        }

    local_scaffold = CLAUDE_LOCAL_SKILL_SNIPPET_RE.search(text)
    if local_scaffold and LOCAL_SCAFFOLD_COMMAND_RE.search(text):
        scenario = "claude-local-skill-scaffold"
        extracted["skill_folder"] = local_scaffold.group(1)
        extracted["skill_path"] = f".claude/skills/{local_scaffold.group(1)}"
        codex_route = "normalize-local-claude-skill-scaffold"
        notes.append(
            "This pattern usually scaffolds a local Claude skill folder rather than installing a published skill from a marketplace or repo."
        )
        if "skill.md" in text and "SKILL.md" not in text and "Skill.md" not in text:
            notes.append(
                "The snippet uses lowercase skill.md; inspect and normalize the filename before treating it as Codex-ready."
            )
        if "## Metadata" in text or "**Description**" in text:
            notes.append(
                "The snippet appears to use markdown metadata sections instead of Codex-style YAML frontmatter, so migration polish is likely needed."
            )
        return {
            "scenario": scenario,
            "extracted": extracted,
            "codex_route": codex_route,
            "notes": notes,
            "claude_signals": claude_signals,
            "should_use_claude_codex_skill_toolkit": should_use_toolkit,
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
            "claude_signals": claude_signals,
            "should_use_claude_codex_skill_toolkit": should_use_toolkit,
        }

    github_url = GITHUB_URL_RE.search(text)
    if github_url:
        if CLAUDE_GITHUB_OWNER_RE.search(github_url.group(0)) or "claude" in github_url.group(0).lower():
            scenario = "claude-github-repo-or-tree-url"
            codex_route = "run-claude-to-codex-skill-flow"
            notes.append(
                "This GitHub source carries Claude-oriented signals, so the Claude-to-Codex toolkit should inspect and validate it before relying on direct install."
            )
        else:
            scenario = "github-repo-or-tree-url"
            codex_route = "inspect-github-repo-and-install-exact-skill-folder"
            notes.append(
                "A GitHub URL is the cleanest path for Codex: inspect the repo layout, then install or migrate the exact skill folder."
            )
        extracted["github_url"] = github_url.group(0)
        return {
            "scenario": scenario,
            "extracted": extracted,
            "codex_route": codex_route,
            "notes": notes,
            "claude_signals": claude_signals,
            "should_use_claude_codex_skill_toolkit": should_use_toolkit,
        }

    github_short = GITHUB_SHORT_RE.search(text)
    if github_short:
        if github_short.group(1).lower().startswith("anthropics/") or "claude" in github_short.group(1).lower():
            scenario = "claude-github-owner-repo-ref"
            codex_route = "run-claude-to-codex-skill-flow"
            notes.append(
                "This owner/repo reference looks Claude-oriented, so it should first go through the Claude-to-Codex toolkit."
            )
        else:
            scenario = "github-owner-repo-ref"
            codex_route = "inspect-github-repo-and-install-exact-skill-folder"
            notes.append(
                "A short owner/repo reference usually maps to the same repo inspection flow as a full GitHub URL."
            )
        extracted["repo_ref"] = github_short.group(1)
        return {
            "scenario": scenario,
            "extracted": extracted,
            "codex_route": codex_route,
            "notes": notes,
            "claude_signals": claude_signals,
            "should_use_claude_codex_skill_toolkit": should_use_toolkit,
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
        "claude_signals": claude_signals,
        "should_use_claude_codex_skill_toolkit": should_use_toolkit,
    }


def main() -> int:
    args = parse_args()
    print(json.dumps(classify(args.text), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
