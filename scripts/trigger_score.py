from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
DESCRIPTION_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+./:-]*", re.IGNORECASE)
STOPWORDS = {
    "a",
    "an",
    "and",
    "any",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "not",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "up",
    "use",
    "well",
    "when",
    "why",
    "will",
    "with",
}

GENERIC_TERMS = {
    "help",
    "works",
    "tasks",
    "general",
    "various",
    "misc",
    "tool",
    "skill",
    "stuff",
}

TRIGGER_PHRASE_MARKERS = (
    "use when",
    "triggers on",
    "when the user asks",
    "applies when",
)


def parse_skill_frontmatter(skill_md: Path) -> dict:
    result = {"name": None, "description": None}
    if not skill_md.exists():
        return result

    text = skill_md.read_text(encoding="utf-8-sig")
    name_match = NAME_RE.search(text)
    desc_match = DESCRIPTION_RE.search(text)
    if name_match:
        result["name"] = name_match.group(1).strip().strip('"').strip("'")
    if desc_match:
        result["description"] = desc_match.group(1).strip().strip('"').strip("'")
    return result


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text) if token.lower() not in STOPWORDS]


def default_prompt_suite() -> list[str]:
    return [
        "build a responsive web interface",
        "audit accessibility problems in this UI",
        "create a design system with tokens and components",
        "improve motion performance in this app",
        "test a local web application",
        "create a presentation deck",
        "edit a word document",
        "analyze a spreadsheet file",
    ]


def score_trigger_quality(name: str | None, description: str | None, prompts: list[str] | None = None) -> dict:
    prompts = prompts or default_prompt_suite()
    score = 50
    notes = []

    if not name:
        return {
            "trigger_quality_score": 0,
            "notes": ["Missing skill name."],
            "prompt_matches": [],
        }

    name_tokens = tokenize(name.replace("-", " "))
    desc_tokens = tokenize(description or "")
    combined_tokens = set(name_tokens + desc_tokens)

    if description:
        score += 10
        notes.append("Has description.")
    else:
        score -= 20
        notes.append("Missing description.")

    desc_length = len(description or "")
    if 60 <= desc_length <= 320:
        score += 10
        notes.append("Description length is in a strong trigger range.")
    elif desc_length < 35:
        score -= 12
        notes.append("Description is too short for strong trigger matching.")
    elif desc_length > 420:
        score -= 6
        notes.append("Description may be too long or diffuse for crisp triggering.")

    description_lower = (description or "").lower()
    if any(marker in description_lower for marker in TRIGGER_PHRASE_MARKERS):
        score += 12
        notes.append("Description includes explicit trigger phrasing.")
    else:
        score -= 6
        notes.append("Description lacks explicit trigger phrasing.")

    unique_name_tokens = [token for token in name_tokens if token not in GENERIC_TERMS]
    if len(unique_name_tokens) >= 2:
        score += 8
        notes.append("Skill name contains specific tokens.")
    else:
        score -= 6
        notes.append("Skill name is too generic or too short.")

    prompt_matches = []
    for prompt in prompts:
        prompt_tokens = set(tokenize(prompt))
        overlap = sorted(prompt_tokens & combined_tokens)
        if overlap:
            prompt_matches.append({"prompt": prompt, "overlap": overlap, "count": len(overlap)})

    if prompt_matches:
        max_match = max(match["count"] for match in prompt_matches)
        score += min(15, max_match * 3)
        notes.append("Description/name overlaps with realistic user prompts.")
    else:
        score -= 10
        notes.append("Weak overlap with realistic user prompts.")

    if ":" in name:
        score -= 3
        notes.append("Namespaced skill name may be less intuitive in user phrasing.")

    score = max(0, min(100, score))
    prompt_matches = sorted(prompt_matches, key=lambda item: item["count"], reverse=True)

    if score >= 85:
        label = "strong"
    elif score >= 65:
        label = "good"
    elif score >= 45:
        label = "weak"
    else:
        label = "poor"

    return {
        "trigger_quality_score": score,
        "trigger_quality_label": label,
        "notes": notes,
        "prompt_matches": prompt_matches[:5],
    }


def score_skill_dir(skill_dir: Path, prompts: list[str] | None = None) -> dict:
    metadata = parse_skill_frontmatter(skill_dir / "SKILL.md")
    result = score_trigger_quality(metadata["name"], metadata["description"], prompts)
    result["name"] = metadata["name"]
    result["description"] = metadata["description"]
    result["path"] = str(skill_dir.resolve())
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score trigger quality for a skill based on its name/description and prompt overlap."
    )
    parser.add_argument("path", help="Path to a skill directory or SKILL.md file")
    parser.add_argument(
        "--prompt",
        action="append",
        default=[],
        help="Custom prompt to test against. Repeat to provide multiple prompts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    prompts = args.prompt or None

    skill_dir = path.parent if path.is_file() else path
    print(json.dumps(score_skill_dir(skill_dir, prompts), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
