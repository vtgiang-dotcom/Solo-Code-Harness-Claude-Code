#!/usr/bin/env python3
"""Solo-Code Harness — Garden (Drift Detection) for Claude Code.

Checks .claude/ directory structure, skill integrity, and boundary compliance.

Usage:
  python tools/garden.py
  python tools/garden.py --strict
  python tools/garden.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent

SKILL_CAP_BYTES = 12288
SKILLS_DIR = ROOT / ".claude" / "skills"
CLAUDE_MD = ROOT / ".claude" / "CLAUDE.md"
SETTINGS_JSON = ROOT / ".claude" / "settings.json"

REQUIRED_SKILLS = [
    "code-review-expert", "brainstorming", "systematic-debugging",
    "testing-patterns", "file-editor-pro", "git-workflow-master",
    "api-patterns", "permission-guard", "solo-code-harness", "block-no-verify",
]

REQUIRED_FRONTMATTER = ["name", "description", "allowed-tools"]


class Finding(NamedTuple):
    severity: str
    category: str
    message: str
    path: str = ""


def check_structure() -> list[Finding]:
    findings = []
    for d in [".claude", ".github"]:
        if not (ROOT / d).is_dir():
            findings.append(Finding("ERROR", "structure", f"Missing directory: {d}/"))
    for f in [CLAUDE_MD, SETTINGS_JSON]:
        if not f.is_file():
            findings.append(Finding("ERROR", "structure", f"Missing file: {f.name}"))
    return findings


def check_skills() -> list[Finding]:
    findings = []
    if not SKILLS_DIR.is_dir():
        return [Finding("ERROR", "skills", "Missing .claude/skills/")]

    existing = {f.stem for f in SKILLS_DIR.glob("*.md")}

    # Missing skills
    for s in REQUIRED_SKILLS:
        if s not in existing:
            findings.append(Finding("ERROR", "skills", f"Missing skill: {s}.md"))

    # Stale skills
    for name in existing:
        if name not in REQUIRED_SKILLS:
            findings.append(Finding("WARNING", "stale", f"Unexpected skill: {name}.md",
                                     f".claude/skills/{name}.md"))

    # Frontmatter + size checks
    for f in sorted(SKILLS_DIR.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        size = f.stat().st_size

        if size > SKILL_CAP_BYTES:
            findings.append(Finding("WARNING", "size", f"Skill {f.stem} is {size}B (cap: {SKILL_CAP_BYTES}B)",
                                     str(f.relative_to(ROOT))))

        if not content.startswith("---"):
            findings.append(Finding("ERROR", "frontmatter", f"Skill {f.stem} missing frontmatter",
                                     str(f.relative_to(ROOT))))
            continue

        for key in REQUIRED_FRONTMATTER:
            if key not in content.split("---")[1]:
                findings.append(Finding("WARNING", "frontmatter",
                                         f"Skill {f.stem} missing '{key}' in frontmatter",
                                         str(f.relative_to(ROOT))))

    return findings


def check_rulebook() -> list[Finding]:
    findings = []
    if not CLAUDE_MD.is_file():
        return [Finding("ERROR", "rulebook", "Missing CLAUDE.md")]

    content = CLAUDE_MD.read_text(encoding="utf-8")
    lower = content.lower()
    lines = content.count("\n") + 1

    if lines > 300:
        findings.append(Finding("WARNING", "size", f"CLAUDE.md is {lines} lines (cap 300)"))

    required = {
        "destructive": "destructive operation guard",
        "socratic": "socratic gate",
        "commit": "commit convention",
        "DeepSeek": "model selection",
    }
    for keyword, label in required.items():
        if keyword.lower() not in lower:
            findings.append(Finding("WARNING", "rulebook", f"CLAUDE.md missing: {label}"))

    return findings


def print_findings(findings: list[Finding], json_output: bool = False) -> int:
    if json_output:
        print(json.dumps([{"severity": f.severity, "category": f.category,
                           "message": f.message, "path": f.path} for f in findings], indent=2))
        return sum(1 for f in findings if f.severity == "ERROR")

    if not findings:
        print("  No issues found. Harness garden is clean.\n")
        return 0

    errors = [f for f in findings if f.severity == "ERROR"]
    warnings = [f for f in findings if f.severity == "WARNING"]
    infos = [f for f in findings if f.severity == "INFO"]

    by_category: dict[str, list[Finding]] = {}
    for f in findings:
        by_category.setdefault(f.category, []).append(f)

    for category, items in sorted(by_category.items()):
        print(f"\n  [{category.upper()}] — {len(items)} finding(s)")
        for f in items:
            tag = {"ERROR": "  [ERROR]", "WARNING": "  [WARN]", "INFO": "  [INFO]"}.get(f.severity, "  -")
            print(f"{tag} {f.message}")
            if f.path:
                print(f"      Path: {f.path}")

    print(f"\n  Summary: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")
    return len(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Solo-Code Harness — Garden drift detection")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    print("\n  Garden: scanning .claude/ directory...\n")

    all_findings = check_structure() + check_skills() + check_rulebook()

    error_count = print_findings(all_findings, args.json)

    if args.strict:
        return 1 if all_findings else 0
    return 1 if error_count else 0


if __name__ == "__main__":
    sys.exit(main())
