#!/usr/bin/env python3
"""
PreToolUse hook — validates file edits before they happen.

Catches patterns DeepSeek is prone to: hardcoded secrets,
unsafe patterns, missing validation.
Adapted from Claude Code official security-guidance plugin patterns.
"""

import json
import re
import sys

# Patterns to WARN about
SECRET_PATTERNS = [
    (r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][A-Za-z0-9_-]{16,}['\"]",
     "Hardcoded API key detected"),
    (r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]+['\"]",
     "Hardcoded password detected"),
    (r"(?i)(secret|token)\s*[:=]\s*['\"][A-Za-z0-9_-]{16,}['\"]",
     "Hardcoded secret/token detected"),
    (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
     "Private key detected — never commit this"),
    (r"sk-[a-zA-Z0-9]{32,}",
     "OpenAI/Anthropic API key pattern detected"),
    (r"gh[pousr]_[A-Za-z0-9]{36,}",
     "GitHub token detected"),
    (r"AKIA[0-9A-Z]{16}",
     "AWS Access Key ID detected"),
]

UNSAFE_PATTERNS = [
    (r"\.innerHTML\s*=", "innerHTML — XSS risk. Use textContent"),
    (r"dangerouslySetInnerHTML", "dangerouslySetInnerHTML — XSS risk"),
    (r"(eval|exec)\s*\(.*\$", "eval/exec with var input — injection risk"),
    (r"os\.system\s*\(.*\$", "os.system() with variable input"),
    (r"subprocess\.call\(.*shell\s*=\s*True",
     "subprocess with shell=True — injection risk"),
    (r"pickle\.load", "pickle.load — unsafe. Use json"),
    (r"yaml\.load\s*\((?!\s*SafeLoader)",
     "yaml.load — use yaml.safe_load()"),
    (r"(?i)INSERT\s+INTO.*VALUES.*\$\{",
     "SQL injection risk — use parameterized queries"),
    (r"\.execute\s*\(\s*['\"].*%\s*",
     "SQL string formatting — use parameterized queries"),
]


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    new_text = (
        tool_input.get("new_string", "")
        or tool_input.get("new_text", "")
    )
    content = tool_input.get("content", "")
    text_to_check = new_text or content

    if not text_to_check:
        sys.exit(0)

    # Skip known-safe files
    safe_ext = {".lock", ".json", ".svg", ".png", ".jpg", ".gif", ".ico"}
    if any(file_path.endswith(ext) for ext in safe_ext):
        sys.exit(0)

    # Check secrets
    for pattern, message in SECRET_PATTERNS:
        if re.search(pattern, text_to_check):
            if file_path.endswith((".env", ".env.local")):
                sys.exit(0)
            print(f"SECURITY: {message} in {file_path}", file=sys.stderr)
            break

    # Check unsafe patterns
    for pattern, message in UNSAFE_PATTERNS:
        if re.search(pattern, text_to_check, re.IGNORECASE):
            print(f"WARNING: {message} in {file_path}", file=sys.stderr)
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
