from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check a SKILL.md file for common Codex discovery issues."
    )
    parser.add_argument("path", help="Path to SKILL.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.path)

    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 1

    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")

    issues: list[str] = []
    warnings: list[str] = []

    if raw.startswith(b"\xef\xbb\xbf"):
        issues.append("File starts with UTF-8 BOM; save as UTF-8 without BOM.")

    if not text.startswith("---"):
        issues.append("File does not start with YAML frontmatter marker '---'.")
    else:
        match = FRONTMATTER_RE.match(text)
        if not match:
            issues.append("Frontmatter block is malformed or not closed properly.")
        else:
            frontmatter = match.group(1)
            lines = [line for line in frontmatter.splitlines() if line.strip()]
            keys = []
            for line in lines:
                if ":" not in line:
                    warnings.append(f"Frontmatter line may be invalid: {line}")
                    continue
                keys.append(line.split(":", 1)[0].strip())

            if "name" not in keys:
                issues.append("Frontmatter is missing required 'name' field.")
            if "description" not in keys:
                issues.append("Frontmatter is missing required 'description' field.")

            if "description" in keys:
                desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
                if desc_match:
                    desc_value = desc_match.group(1).strip().strip('"').strip("'")
                    if len(desc_value) < 25:
                        warnings.append("Description looks very short and may trigger poorly.")
                else:
                    warnings.append(
                        "Description may be multiline or malformed; check trigger wording manually."
                    )

    print(f"Checked: {path}")
    print(f"Issues: {len(issues)}")
    print(f"Warnings: {len(warnings)}")

    if issues:
        print("\nBlocking issues:")
        for issue in issues:
            print(f"- {issue}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

    if not issues and not warnings:
        print("\nNo obvious discovery issues found.")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
