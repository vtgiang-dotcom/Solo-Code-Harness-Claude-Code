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

# Path validation patterns
PATH_WARN = [
    (r"\b/tmp/", "Writing to /tmp — data lost on reboot. Use persistent path."),
    (r"\b~/", "Tilde ~ in script — may not expand as expected. Use $HOME."),
    (r"(?<!\w)\.\.\/\.\.\/",
     "Deep relative path — fragile. Use absolute or project-relative."),
]

# Mode/permission validation patterns
MODE_WARN = [
    (r"chmod\s+.*777", "chmod 777 — world-writable. Use 755 or 644 instead."),
    (r"chmod\s+.*\+x\s+(?!.*\.sh)", "chmod +x on non-script file — verify intent."),
    (r"chown\s+.*:.*", "chown in script — may require sudo. Verify ownership intent."),
]

# Sed/syntax validation patterns
SED_WARN = [
    (r"sed\s+.*\|.*sed", "Piped sed commands — fragile. Use single sed with -e."),
    (r"sed\s+-i\s+(?!.*\.bak)", "sed -i without .bak — no backup. Use sed -i.bak."),
    (r"grep\s+(?:(?!!).)*$", "grep without --line-buffered in pipe — output delayed."),
]

# Command semantics validation
SEMANTIC_WARN = [
    (r"kill\s+-9", "kill -9 is SIGKILL — no cleanup. Try kill -15 first."),
    (r"docker\s+rm\s+-f", "docker rm -f — force remove. May orphan resources."),
    (r"npm\s+audit\s+fix\s+--force",
     "npm audit fix --force — may break deps. Review first."),
    (r"git\s+stash\s+drop", "git stash drop — irreversible. Use git stash pop first."),
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
            break

    # Check path validation
    for pattern, message in PATH_WARN:
        if re.search(pattern, command):
            print(f"PATH: {message}", file=sys.stderr)
            break

    # Check mode/permission validation
    for pattern, message in MODE_WARN:
        if re.search(pattern, command):
            print(f"MODE: {message}", file=sys.stderr)
            break

    # Check sed/syntax validation
    for pattern, message in SED_WARN:
        if re.search(pattern, command):
            print(f"SED: {message}", file=sys.stderr)
            break

    # Check command semantics
    for pattern, message in SEMANTIC_WARN:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"SEMANTIC: {message}", file=sys.stderr)
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
