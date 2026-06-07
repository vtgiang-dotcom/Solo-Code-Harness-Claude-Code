#!/usr/bin/env python3
"""
Stop hook — runs before Claude Code ends the session.

Verifies the verification gates have been checked before stopping.
DeepSeek-tuned: DeepSeek is more likely to forget verification steps.
"""

import json
import sys


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Don't block the stop — just remind
    transcript = input_data.get("transcript", "")

    checks = [
        ("secret", "security_scan.py", "Secret scan not detected this session"),
        ("ruff check", "lint", "Ruff lint not detected this session"),
        ("checklist.py", "gates", "Checklist not run this session"),
    ]

    missing = []
    for keyword, _name, msg in checks:
        if keyword not in transcript.lower():
            missing.append(msg)

    if missing:
        print(
            "REMINDER: No verification checks detected in this session:",
            file=sys.stderr,
        )
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        print("  Run: python .github/scripts/checklist.py .", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
