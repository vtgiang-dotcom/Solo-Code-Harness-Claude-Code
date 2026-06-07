"""Integration tests for Claude Code harness — skills, structure, frontmatter.

Run: python tools/test_integration.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKILLS_DIR = ROOT / ".claude" / "skills"
CLAUDE_MD = ROOT / ".claude" / "CLAUDE.md"
SKILL_CAP_BYTES = 12288

REQUIRED_SKILLS = [
    "code-review-expert", "brainstorming", "systematic-debugging",
    "testing-patterns", "file-editor-pro", "git-workflow-master",
    "api-patterns", "permission-guard", "solo-code-harness", "block-no-verify",
]

pass_count = 0
fail_count = 0


def ok(msg: str) -> None:
    global pass_count
    pass_count += 1
    print(f"  [PASS] {msg}")


def fail(msg: str) -> None:
    global fail_count
    fail_count += 1
    print(f"  [FAIL] {msg}")


def header(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def _parse_fm(raw: str) -> tuple[dict | None, str]:
    raw = raw.lstrip()
    if not raw.startswith("---"):
        return None, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return None, raw
    body = parts[2].lstrip()
    fm = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return (fm if fm else None), body


def test_structure() -> None:
    header("Test 1: Directory structure")
    if (ROOT / ".claude").is_dir():
        ok(".claude/ exists")
    else:
        fail(".claude/ missing")
    if CLAUDE_MD.is_file():
        ok("CLAUDE.md exists")
    else:
        fail("CLAUDE.md missing")
    if SKILLS_DIR.is_dir():
        ok(".claude/skills/ exists")
    else:
        fail(".claude/skills/ missing")


def test_skill_counts() -> None:
    header("Test 2: Skill counts")
    existing = {f.stem for f in SKILLS_DIR.glob("*.md")} if SKILLS_DIR.is_dir() else set()
    if len(existing) == 10:
        ok("10 skills found")
    else:
        fail(f"Expected 10 skills, found {len(existing)}")

    for s in REQUIRED_SKILLS:
        if s in existing:
            ok(f"  {s}")
        else:
            fail(f"  {s} missing")


def test_frontmatter() -> None:
    header("Test 3: Skill frontmatter validity")
    if not SKILLS_DIR.is_dir():
        fail("Skills dir missing")
        return

    for f in sorted(SKILLS_DIR.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        fm, _ = _parse_fm(content)
        if fm and "name" in fm and "description" in fm and "allowed-tools" in fm:
            ok(f"{f.stem}: frontmatter valid ({fm['allowed-tools']})")
        elif fm:
            missing = [k for k in ["name", "description", "allowed-tools"] if k not in fm]
            fail(f"{f.stem}: missing {missing}")
        else:
            fail(f"{f.stem}: no frontmatter")


def test_file_sizes() -> None:
    header("Test 4: File size boundaries")

    if CLAUDE_MD.is_file():
        lines = CLAUDE_MD.read_text(encoding="utf-8").count("\n") + 1
        if lines <= 300:
            ok(f"CLAUDE.md: {lines} lines (cap 300)")
        else:
            fail(f"CLAUDE.md: {lines} lines (cap 300)")

    if SKILLS_DIR.is_dir():
        for f in sorted(SKILLS_DIR.glob("*.md")):
            size = f.stat().st_size
            if size <= SKILL_CAP_BYTES:
                ok(f"{f.stem}: {size}B ok")
            else:
                fail(f"{f.stem}: {size}B exceeds {SKILL_CAP_BYTES}B")


def test_allowed_tools_valid() -> None:
    header("Test 5: allowed-tools reference real Claude Code tools")
    valid_tools = {"Read", "Edit", "Write", "Bash", "Grep", "Glob",
                   "Agent", "Skill", "AskUserQuestion", "WebFetch", "WebSearch",
                   "TaskCreate", "TaskUpdate", "TaskGet", "TaskList",
                   "EnterPlanMode", "ExitPlanMode"}
    issues = 0
    for f in sorted(SKILLS_DIR.glob("*.md")):
        fm, _ = _parse_fm(f.read_text(encoding="utf-8"))
        if not fm or "allowed-tools" not in fm:
            continue
        tools = [t.strip() for t in fm["allowed-tools"].split(",")]
        bad = [t for t in tools if t not in valid_tools]
        if bad:
            fail(f"{f.stem}: invalid tools: {bad}")
            issues += 1
        else:
            ok(f"{f.stem}: all tools valid")
    if issues == 0:
        ok("All skills reference valid Claude Code tools")


def main() -> int:
    global pass_count, fail_count
    print(f"\n{'#'*60}")
    print("  Solo-Code Harness — Integration Test Suite")
    print(f"{'#'*60}")

    test_structure()
    test_skill_counts()
    test_frontmatter()
    test_file_sizes()
    test_allowed_tools_valid()

    print(f"\n{'#'*60}")
    print(f"  Results: {pass_count} passed, {fail_count} failed")
    print(f"{'#'*60}\n")
    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())
