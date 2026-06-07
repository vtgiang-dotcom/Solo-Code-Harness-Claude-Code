"""Tests for Claude Code harness — YAML serialization, frontmatter parsing, skills.

Run: python -m pytest tools/test_harness.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SKILLS_DIR = ROOT / ".claude" / "skills"
REQUIRED_SKILLS = [
    "code-review-expert", "brainstorming", "systematic-debugging",
    "testing-patterns", "file-editor-pro", "git-workflow-master",
    "api-patterns", "permission-guard", "solo-code-harness", "block-no-verify",
]


# ─── YAML Serializer ────────────────────────────────────────────────────────

def _yaml_scalar(value: str | bool | int | float) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    need_quote = any(c in s for c in ':#{}[]&*!|>%@`"\',')
    if need_quote or s.startswith(" ") or s.endswith(" "):
        return f'"{s.replace(chr(34), chr(92)+chr(34))}"'
    return s


def _yaml_node(val: object, indent: int = 0) -> str:
    pre = "  " * indent
    if isinstance(val, dict):
        lines = []
        for k, v in val.items():
            key = _yaml_scalar(k)
            if isinstance(v, dict):
                lines.append(f"{pre}{key}:")
                lines.append(_yaml_node(v, indent + 1))
            elif isinstance(v, list):
                lines.append(f"{pre}{key}:")
                for item in v:
                    lines.append(f"{pre}  - {_yaml_scalar(item)}")
            else:
                lines.append(f"{pre}{key}: {_yaml_scalar(v)}")
        return "\n".join(lines)
    return _yaml_scalar(val)


def _yaml_fm(data: dict) -> str:
    if not data:
        return ""
    lines = _yaml_node(data)
    return f"---\n{lines}\n---\n"


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


# ─── YAML Serializer Tests ──────────────────────────────────────────────────

class TestYamlSerializer:
    def test_scalar_string(self):
        assert _yaml_scalar("hello") == "hello"

    def test_scalar_quoted(self):
        assert '"' in _yaml_scalar("hello: world")

    def test_scalar_bool(self):
        assert _yaml_scalar(True) == "true"
        assert _yaml_scalar(False) == "false"

    def test_flat_dict(self):
        result = _yaml_node({"name": "test", "mode": "primary"})
        assert "name: test" in result
        assert "mode: primary" in result

    def test_nested_dict(self):
        result = _yaml_node({"name": "c", "permission": {"read": "allow", "edit": "deny"}})
        assert "name: c" in result
        assert "  read: allow" in result
        assert "  edit: deny" in result

    def test_list(self):
        result = _yaml_node({"tools": ["Read", "Grep", "Glob"]})
        assert "- Read" in result

    def test_frontmatter_wrapping(self):
        result = _yaml_fm({"name": "test"})
        assert result.startswith("---\n")
        assert result.rstrip().endswith("\n---")

    def test_empty_frontmatter(self):
        assert _yaml_fm({}) == ""


# ─── Frontmatter Parse Tests ────────────────────────────────────────────────

class TestFrontmatterParse:
    def test_parses_valid(self):
        fm, body = _parse_fm("---\nname: hello\ndescription: Test.\n---\n\n# Title\n\nBody.")
        assert fm == {"name": "hello", "description": "Test."}
        assert body.startswith("# Title")

    def test_no_fm_returns_none(self):
        fm, body = _parse_fm("# Just a title")
        assert fm is None
        assert body == "# Just a title"

    def test_empty_string(self):
        fm, body = _parse_fm("")
        assert fm is None
        assert body == ""


# ─── Skills Tests ───────────────────────────────────────────────────────────

class TestSkills:
    def test_all_skills_exist(self):
        existing = {f.stem for f in SKILLS_DIR.glob("*.md")}
        for s in REQUIRED_SKILLS:
            assert s in existing, f"Missing skill: {s}"

    def test_expected_count(self):
        assert len(list(SKILLS_DIR.glob("*.md"))) == 10

    def test_all_have_frontmatter(self):
        for f in SKILLS_DIR.glob("*.md"):
            content = f.read_text(encoding="utf-8")
            assert content.startswith("---"), f"{f.stem}: missing frontmatter"
            fm, _ = _parse_fm(content)
            assert fm is not None, f"{f.stem}: failed to parse frontmatter"
            assert "name" in fm, f"{f.stem}: missing name"
            assert "description" in fm, f"{f.stem}: missing description"
            assert "allowed-tools" in fm, f"{f.stem}: missing allowed-tools"

    def test_all_have_body_content(self):
        for f in SKILLS_DIR.glob("*.md"):
            _, body = _parse_fm(f.read_text(encoding="utf-8"))
            assert body, f"{f.stem}: empty body"
            assert len(body.strip()) >= 50, f"{f.stem}: body too short ({len(body.strip())} chars)"


# ─── Claude Tools Validity ──────────────────────────────────────────────────

VALID_CLAUDE_TOOLS = {"Read", "Edit", "Write", "Bash", "Grep", "Glob",
                      "Agent", "Skill", "AskUserQuestion", "WebFetch", "WebSearch",
                      "TaskCreate", "TaskUpdate", "TaskGet", "TaskList",
                      "EnterPlanMode", "ExitPlanMode"}


class TestAllowedTools:
    def test_all_tools_valid(self):
        for f in SKILLS_DIR.glob("*.md"):
            fm, _ = _parse_fm(f.read_text(encoding="utf-8"))
            if not fm or "allowed-tools" not in fm:
                pytest.fail(f"{f.stem}: missing allowed-tools")
            tools = [t.strip() for t in fm["allowed-tools"].split(",")]
            for t in tools:
                assert t in VALID_CLAUDE_TOOLS, f"{f.stem}: invalid tool '{t}'"


# ─── Rulebook Tests ─────────────────────────────────────────────────────────

class TestRulebook:
    def test_claude_md_exists(self):
        assert (ROOT / ".claude" / "CLAUDE.md").is_file()

    def test_contains_required_sections(self):
        content = (ROOT / ".claude" / "CLAUDE.md").read_text(encoding="utf-8").lower()
        for section in ["destructive", "socratic", "commit", "security", "deepseek"]:
            assert section in content, f"CLAUDE.md missing: {section}"
