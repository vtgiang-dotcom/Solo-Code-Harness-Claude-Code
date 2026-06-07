#!/usr/bin/env python3
"""
Deploy Solo-Code Harness to a target project.

Copies the harness layer (rules, skills, permissions, launcher, guard)
without the harness self-tests or docs.

Usage:
    python tools/deploy.py /path/to/target-project
    python tools/deploy.py /path/to/target-project --dry-run
"""

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Files and directories to deploy (relative to harness root)
DEPLOY = [
    # ── Core harness ──
    ".claude/",                         # CLAUDE.md, settings.json, skills/, memory/
    ".mcp.json",                        # MCP server config
    # ── Launcher scripts ──
    "claudecode.ps1",                   # Smart launcher — Windows PowerShell
    "claudecode-pro.ps1",               # Pro shortcut — Windows
    "claudecode.sh",                    # Smart launcher — Linux/Mac bash
    "claudecode-pro.sh",                # Pro shortcut — Linux/Mac
    # ── Security & quality gates ──
    ".github/scripts/security_scan.py", # Secret scanner
    ".github/scripts/checklist.py",     # Master validation checklist
    ".github/hooks/scripts/guard.js",   # Permission guard
    ".github/hooks/scripts/guard.test.js", # Guard tests
    # ── Linter config ──
    ".ruff.toml",                       # Python linter
    # ── Makefile ──
    "Makefile",                         # Quality gate targets
]

# Specifically excluded (these stay with the harness repo)
EXCLUDE = [
    "README.md",
    "tools/",
    ".git/",
    ".env",
    ".venv/",
    "__pycache__/",
    "*.pyc",
]


def deploy(target: Path, dry_run: bool = False) -> int:
    if not target.exists():
        print(f"ERROR: Target directory does not exist: {target}")
        return 1

    copied = 0
    skipped = 0

    for item in DEPLOY:
        src = ROOT / item
        dst = target / item

        if not src.exists():
            print(f"  SKIP: {item} (not found at source)")
            skipped += 1
            continue

        if dry_run:
            kind = "DIR" if src.is_dir() else "FILE"
            print(f"  [{kind}] {item} -> {dst}")
            copied += 1
            continue

        try:
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", ".DS_Store"
                ))
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            print(f"  COPY: {item}")
            copied += 1
        except OSError as e:
            print(f"  FAIL: {item} - {e}")
            return 1

    print(f"\n  Done: {copied} deployed, {skipped} skipped")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deploy Solo-Code Harness to a target project"
    )
    parser.add_argument("target", type=Path, help="Path to target project")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be copied without actually copying"
    )
    args = parser.parse_args()

    target = args.target.resolve()

    print(f"  Solo-Code Harness -> {target}")
    if args.dry_run:
        print("  (dry run - no files copied)\n")
    else:
        print()

    return deploy(target, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
