#!/usr/bin/env python3
"""
Generate global Claude Code settings for DeepSeek.

Creates or updates ~/.claude/settings.json with the env section
needed to route Claude Code through the DeepSeek API. After running
this, both `claude` CLI and VSCode Extension work without the launcher.

Usage:
    python tools/setup-global-config.py
    python tools/setup-global-config.py --dry-run
"""

import argparse
import json
import sys
from pathlib import Path


def settings_path() -> Path:
    home = Path.home()
    return home / ".claude" / "settings.json"


def deepseek_env(api_key: str) -> dict:
    return {
        "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
        "ANTHROPIC_AUTH_TOKEN": api_key,
        "ANTHROPIC_MODEL": "deepseek-v4-pro[1m]",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro[1m]",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-pro[1m]",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-v4-flash[1m]",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        "CLAUDE_CODE_EFFORT_LEVEL": "max",
    }


def load_api_key() -> str:
    """Try to read DEEPSEEK_API_KEY from project .env file."""
    env_file = Path(__file__).resolve().parents[1] / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split("=", 1)
                if len(parts) == 2 and parts[0].strip() == "DEEPSEEK_API_KEY":
                    val = parts[1].strip().strip('"').strip("'")
                    if val and val != "YOUR_DEEPSEEK_API_KEY_HERE":
                        return val
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate ~/.claude/settings.json for DeepSeek"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be written without writing")
    args = parser.parse_args()

    path = settings_path()
    api_key = load_api_key()

    if not api_key:
        print("WARNING: DEEPSEEK_API_KEY not found in .env")
        print(f"You can edit {path} manually to add ANTHROPIC_AUTH_TOKEN later.")
        api_key = "<your DeepSeek API Key>"

    # Read existing config if any
    existing = {}
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"WARNING: {path} exists but is not valid JSON. Overwriting.")

    # Merge env section
    if "env" not in existing:
        existing["env"] = {}
    existing["env"].update(deepseek_env(api_key))

    if args.dry_run:
        print(f"Would write to {path}:")
        print(json.dumps(existing, indent=2))
        return 0

    # Write
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")

    print(f"  Global config written: {path}")
    print(f"  Model: {existing['env']['ANTHROPIC_MODEL']}")
    print("  VSCode: search 'claudeCode.disableLoginPrompt' and enable it")
    print("  Ready: run 'claude' directly in any project directory")
    return 0


if __name__ == "__main__":
    sys.exit(main())
