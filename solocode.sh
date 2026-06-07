#!/usr/bin/env bash
# Claude Code + DeepSeek API — Smart Launcher (Linux/Mac)
#
# Default: deepseek-v4-pro (best quality, still cheaper than Claude)
# Override: -Model flash (fast/cheap for simple tasks)
# Auto-detect: -p "refactor X" scans prompt to pick model
#
# Usage:
#   ./solocode.sh                  # pro (default — best quality)
#   ./solocode.sh -Model flash      # force flash
#   ./solocode.sh -Model pro        # force pro
#   ./solocode.sh -p "refactor X"   # auto-detect from prompt text
#   ./solocode-pro.sh               # shortcut for -Model pro

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

# ── Read DEEPSEEK_API_KEY from .env ──────────────────────────────
if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: .env not found at $ENV_FILE" >&2
    exit 1
fi

DEEPSEEK_API_KEY=""
while IFS='=' read -r key value; do
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs | sed 's/^"//;s/"$//;s/^'\''//;s/'\''$//')
    if [[ "$key" == "DEEPSEEK_API_KEY" && -n "$value" ]]; then
        DEEPSEEK_API_KEY="$value"
    fi
done < <(grep -v '^#' "$ENV_FILE" | grep -v '^$')

if [[ -z "$DEEPSEEK_API_KEY" || "$DEEPSEEK_API_KEY" == "YOUR_DEEPSEEK_API_KEY_HERE" ]]; then
    echo "ERROR: DEEPSEEK_API_KEY not configured in .env" >&2
    exit 1
fi

# ── Resolve model ────────────────────────────────────────────────
MODEL="pro"
AUTO_DETECTED=false
MODEL_ARG=""

# Parse -Model flag
for i in "$@"; do
    if [[ "$i" == "-Model" ]]; then
        # next arg should be the value — handled below
        MODEL_ARG="pending"
    elif [[ "$MODEL_ARG" == "pending" ]]; then
        case "$i" in
            pro|flash|auto) MODEL="$i" ;;
            *) echo "ERROR: Unknown model '$i'. Use: pro, flash, auto" >&2; exit 1 ;;
        esac
        MODEL_ARG=""
    fi
done

# Auto-detect if model is auto
if [[ "$MODEL" == "auto" ]]; then
    PROMPT_TEXT=""
    # Try -p flag
    for j in "$@"; do
        if [[ "$P_COLLECT" == "1" ]]; then
            PROMPT_TEXT="$j"
            P_COLLECT=0
        fi
        if [[ "$j" == "-p" ]]; then
            P_COLLECT=1
        fi
    done
    # If no -p, use all args as prompt
    if [[ -z "$PROMPT_TEXT" ]]; then
        PROMPT_TEXT="$*"
    fi

    # Check for complexity keywords
    COMPLEX_KW="refactor|debug|bug|build|create|analyze|audit|architect|design|migrate|implement|security|optimize|performance|fix|error|crash|restructure|review"
    if echo "$PROMPT_TEXT" | grep -iqE "$COMPLEX_KW"; then
        MODEL="pro"
        AUTO_DETECTED=true
    else
        MODEL="flash"
    fi
fi

# Resolve model name
if [[ "$MODEL" == "pro" ]]; then
    MODEL_NAME="deepseek-v4-pro[1m]"
    MODEL_LABEL="PRO"
else
    MODEL_NAME="deepseek-v4-flash[1m]"
    MODEL_LABEL="FLASH"
fi

DETECT_NOTE=""
if [[ "$AUTO_DETECTED" == true ]]; then
    DETECT_NOTE=" (auto)"
fi

# ── Set environment variables ────────────────────────────────────
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_API_KEY="$DEEPSEEK_API_KEY"
export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY"
export ANTHROPIC_MODEL="$MODEL_NAME"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro[1m]"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro[1m]"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash[1m]"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"
export CLAUDE_CODE_EFFORT_LEVEL="max"

# ── Ensure log directory exists ──────────────────────────────────
LOG_DIR="$SCRIPT_DIR/.claude"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/usage.log"

# ── Banner ───────────────────────────────────────────────────────
echo ""
echo -e "\033[32m============================================================\033[0m"
echo -e "\033[32m Claude Code + DeepSeek API\033[0m"
echo -e "\033[36m Model : $MODEL_NAME ($MODEL_LABEL)$DETECT_NOTE\033[0m"
echo -e "\033[90m------------------------------------------------------------\033[0m"
echo -e "\033[90m Switch: ./solocode.sh -Model flash  (save tokens)\033[0m"
echo -e "\033[90m         ./solocode.sh -p \"refactor\"  (auto-detect)\033[0m"
echo -e "\033[32m============================================================\033[0m"
echo ""

# ── Launch ───────────────────────────────────────────────────────
SESSION_START=$(date -u +%Y-%m-%dT%H:%M:%S)
START_EPOCH=$(date +%s)

claude "$@"
EXIT_CODE=$?

SESSION_END=$(date -u +%Y-%m-%dT%H:%M:%S)
END_EPOCH=$(date +%s)
DURATION_MIN=$(echo "scale=1; ($END_EPOCH - $START_EPOCH) / 60" | bc 2>/dev/null || echo "0")

# ── Log session ──────────────────────────────────────────────────
MODE="manual"
if [[ "$AUTO_DETECTED" == true ]]; then MODE="auto"; fi

cat >> "$LOG_FILE" << EOF
{"timestamp":"$SESSION_START","model":"$MODEL_NAME","mode":"$MODE","duration_min":$DURATION_MIN,"exit_code":$EXIT_CODE}
EOF

echo -e "\033[90m--- Session: ${DURATION_MIN}min | Model: $MODEL_NAME ---\033[0m"
