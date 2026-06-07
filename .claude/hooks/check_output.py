#!/usr/bin/env python3
"""
PostToolUse hook — checks command output for error patterns.

Catches common DeepSeek mistakes visible in command output:
syntax errors, missing dependencies, failed tests.
"""

import json
import re
import sys

ERROR_PATTERNS = [
    (r"ModuleNotFoundError|ImportError", "Python import error — missing dependency?"),
    (r"cannot find module", "Node module not found — run npm install?"),
    (r"command not found", "Command not found — install the tool first?"),
    (r"Permission denied", "Permission denied — check file permissions"),
    (r"fatal: not a git repository", "Not a git repo — cd to correct directory?"),
    (r"npm ERR!", "npm error — check package.json"),
    (r"SyntaxError", "Syntax error in code"),
    (r"EACCES", "Access denied — check permissions or use sudo"),
    (r"No such file or directory", "File not found — verify the path"),
]


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    stderr = input_data.get("tool_output", {}).get("stderr", "")
    if not stderr:
        sys.exit(0)

    for pattern, message in ERROR_PATTERNS:
        if re.search(pattern, stderr, re.IGNORECASE):
            print(f"ISSUE: {message}", file=sys.stderr)
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
