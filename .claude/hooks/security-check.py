#!/usr/bin/env python3
"""
Security Check Hook — Real-time security warnings for sensitive operations.

Events:
  - preEdit      → Warn when editing .env, auth, config, or credential files
  - postCommit   → Scan git diff for secrets after a commit
  - postPush     → Scan unpushed commits for secrets before/after push

Uses the existing security_scan.py patterns for consistency.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


# ── Sensitive File Patterns ────────────────────────────────────────────────

SENSITIVE_FILE_PATTERNS = [
    r'\.env(\..*)?$',           # .env, .env.local, .env.production
    r'credentials',              # credentials, credentials.json
    r'secret',                   # secret, secrets, client_secret
    r'\.pem$',                  # Private key files
    r'\.key$',                  # Key files
    r'\.pfx$',                  # Certificate files
    r'\.p12$',                  # PKCS12 files
    r'\.token$',                # Token files
    r'settings\.json$',         # Settings with potential secrets
    r'\.mcp\.json$',            # MCP config with API keys
    r'config/auth',             # Auth config
    r'config/credentials',      # Credentials config
    r'\.htpasswd',              # Apache htpasswd
    r'\.netrc',                 # Netrc file
    r'\.ssh/',                  # SSH directory
]

HIGH_SENSITIVITY_SECRETS = [
    (r"sk-[a-zA-Z0-9]{20,}", "Anthropic/OpenAI API key"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"gh[pousr]_[A-Za-z0-9_]{36,}", "GitHub Personal Access Token"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API Key"),
    (r"xox[bpras]-[0-9a-zA-Z]{10,}", "Slack Token"),
    (r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private Key"),
    (r"(?:password|passwd|pwd)\s*[:=]\s*[\"'][^\"']{8,}[\"']", "Hardcoded password"),
    (r"(?:api_key|apikey|api-key|secret_key)\s*[:=]\s*[\"'][\w\-]{20,}[\"']", "Hardcoded API key/secret"),
    (r"eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+", "JWT Token (possible hardcoded)"),
    (r"(?:mongodb|postgres|mysql|redis)://[^\"'\s]+@", "Database connection string with credentials"),
]


def is_sensitive_file(file_path: str) -> tuple[bool, str]:
    """Check if a file path matches sensitive file patterns."""
    path_lower = file_path.lower()
    for pattern in SENSITIVE_FILE_PATTERNS:
        if re.search(pattern, path_lower):
            return True, pattern
    return False, ""


def scan_diff_for_secrets() -> list[str]:
    """Scan staged + unstaged diff for high-sensitivity secrets."""
    try:
        # Get diff content
        result = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True, text=True, timeout=30,
            cwd=Path.cwd(),
        )
        if result.returncode != 0:
            return []

        diff_content = result.stdout
        if not diff_content.strip():
            return []

        findings = []
        for line_no, line in enumerate(diff_content.splitlines(), 1):
            # Only scan added lines (lines starting with +)
            if not line.startswith("+") or line.startswith("+++"):
                continue
            for pattern, description in HIGH_SENSITIVITY_SECRETS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Sanitize the finding — don't show the actual secret
                    sanitized = re.sub(pattern, "[REDACTED]", line[1:].strip(), count=1)
                    findings.append(
                        f"  [{description}] line {line_no}: {sanitized[:120]}"
                    )
        return findings
    except Exception:
        return []


# ── Event Handlers ─────────────────────────────────────────────────────────

def on_pre_edit() -> None:
    """Warn before editing sensitive files."""
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    tool_input = input_data.get("toolInput", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("filePath", "")

    if not file_path:
        return

    is_sensitive, pattern = is_sensitive_file(file_path)
    if is_sensitive:
        warning = (
            f"SECURITY: Editing sensitive file ({pattern}): {file_path}\n"
            f"  Ensure no credentials, tokens, or secrets are committed.\n"
            f"  Use environment variables or secret management instead of hardcoding."
        )
        print(f"\n{warning}\n", file=sys.stderr)
        emit_result("sensitive_file_warning", {
            "file": file_path,
            "pattern": pattern,
            "warning": warning,
        })


def on_post_commit() -> None:
    """Scan git diff for secrets after a commit."""
    findings = scan_diff_for_secrets()

    if findings:
        warning = "SECURITY ALERT: Potential secrets detected in git diff:\n" + "\n".join(findings)
        print(f"\n{warning}\n", file=sys.stderr)
        emit_result("secrets_detected", {
            "count": len(findings),
            "findings": findings,
        })
    else:
        emit_result("security_clean", {"status": "no secrets detected"})


def on_post_push() -> None:
    """Check recent commits for security issues."""
    findings = scan_diff_for_secrets()

    if findings:
        warning = "SECURITY ALERT: Check unpushed/pushed commits:\n" + "\n".join(findings)
        print(f"\n{warning}\n", file=sys.stderr)
        emit_result("secrets_in_push", {
            "count": len(findings),
            "findings": findings,
        })
    else:
        emit_result("push_clean", {"status": "no secrets in recent commits"})


def emit_result(status: str, data: dict) -> None:
    """Emit structured result for Claude Code to parse."""
    output = {
        "hook": "security-check",
        "status": status,
        "data": data,
    }
    print(json.dumps(output, ensure_ascii=False, default=str))


# ── Dispatch ───────────────────────────────────────────────────────────────

def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else ""

    handlers = {
        "preEdit": on_pre_edit,
        "postCommit": on_post_commit,
        "postPush": on_post_push,
    }

    handler = handlers.get(event)
    if handler:
        handler()
    else:
        print(f"Usage: security-check.py <preEdit|postCommit|postPush>", file=sys.stderr)
        print(f"Unknown event: {event}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
