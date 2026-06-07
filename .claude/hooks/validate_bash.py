#!/usr/bin/env python3
"""
PreToolUse hook — validates bash commands before execution.

Blocks destructive patterns and suggests safer alternatives.
Adapted from Claude Code official hook examples.
DeepSeek-tuned: catches patterns DeepSeek is more likely to generate.
"""

import json
import re
import sys

# Patterns that should be BLOCKED (exit code 2)
BLOCK_PATTERNS = [
    (r"rm\s+-rf\s+/", "rm -rf / — absolute path deletion blocked"),
    (r"rm\s+-rf\s+~", "rm -rf ~ — home directory deletion blocked"),
    (r"rm\s+-rf\s+\*", "rm -rf * — wildcard deletion blocked"),
    (r"git\s+push\s+.*(--force|-f)\s+.*(main|master)",
     "Force push to main/master blocked"),
    (r"git\s+reset\s+--hard", "git reset --hard blocked — use --soft or --mixed"),
    (r"DROP\s+(TABLE|DATABASE)", "DROP TABLE/DATABASE blocked"),
    (r"TRUNCATE\s+TABLE", "TRUNCATE TABLE blocked"),
    (r"dd\s+if=", "dd if= blocked — raw disk write risk"),
    (r"mkfs\.", "mkfs blocked — filesystem format risk"),
    (r"(chmod|chown)\s+.*777", "chmod/chown 777 blocked — world-writable"),
    (r">\s*/dev/sd[a-z]", "Direct write to /dev/sd* blocked"),
    (r"shred\s+", "shred blocked — irreversible deletion"),
    (r"del\s+/f\s+/s", "del /f /s blocked — recursive force delete on Windows"),
    (r"Remove-Item\s+.*-Recurse.*-Force", "Remove-Item -Recurse -Force blocked"),
]

# Patterns that generate WARNINGS (exit code 0, stderr message)
WARN_PATTERNS = [
    (r"npm\s+install\s+-g",
     "npm install -g: global install — prefer local or npx"),
    (r"pip\s+install\s+(?!-r|\.)",
     "pip install: consider adding to requirements.txt"),
    (r"git\s+commit\s+.*(--no-verify|-n)",
     "git commit --no-verify bypasses pre-commit hooks"),
    (r"curl\s+.*\|\s*(ba)?sh",
     "curl | sh: piping to shell is unsafe. Review script first"),
    (r"(eval|exec)\(.*\$", "eval/exec with variable input — code injection risk"),
    (r"console\.log\(|debugger;", "Debug code detected — remove before committing"),
    (r"print\(.*\)\s*#.*debug", "Debug print detected — remove before committing"),
]


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # Silent pass on invalid input

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    command = input_data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    # Check block patterns first
    for pattern, message in BLOCK_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"BLOCKED: {message}", file=sys.stderr)
            sys.exit(2)  # Block the tool call

    # Check warning patterns
    for pattern, message in WARN_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"WARNING: {message}", file=sys.stderr)
            break  # Only show first warning

    sys.exit(0)


if __name__ == "__main__":
    main()
