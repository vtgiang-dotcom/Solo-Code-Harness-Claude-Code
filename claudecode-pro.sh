#!/usr/bin/env bash
# Shortcut: Claude Code with DeepSeek v4 Pro
# Equivalent: ./claudecode.sh -Model pro
# Use when you know the task needs maximum power (large refactor, complex debug, architecture design)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/claudecode.sh" -Model pro "$@"
