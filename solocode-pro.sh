#!/usr/bin/env bash
# Shortcut: Claude Code with DeepSeek v4 Pro
# Equivalent: ./solocode.sh -Model pro
# Use when you know the task needs maximum power (large refactor, complex debug, architecture design)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/solocode.sh" -Model pro "$@"
