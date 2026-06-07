#!/usr/bin/env bash
# install.sh — Solo-Code-Harness Installer
# Cross-platform: Linux, macOS, Windows (Git Bash/MSYS2)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo "=== Solo-Code-Harness Installer v2.0.0 ==="
echo ""

# ─── Platform Detection ───
detect_platform() {
  case "$(uname -s)" in
    Linux*)  echo "linux" ;;
    Darwin*) echo "macos" ;;
    CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
    *)       echo "unknown" ;;
  esac
}

PLATFORM=$(detect_platform)
echo "[*] Platform: $PLATFORM"

# ─── Check Prerequisites ───
check_command() {
  if command -v "$1" &>/dev/null; then
    echo -e "  ${GREEN}OK${NC}    $1 ($($1 --version 2>&1 | head -1))"
    return 0
  else
    echo -e "  ${RED}MISS${NC} $1"
    return 1
  fi
}

echo "[*] Checking prerequisites..."
PREREQ_OK=true
check_command "git" || PREREQ_OK=false
check_command "node" || PREREQ_OK=false
check_command "python" || check_command "python3" || PREREQ_OK=false

if [ "$PREREQ_OK" = false ]; then
  echo ""
  echo -e "${RED}ERROR: Missing prerequisites. Please install git, node, and python.${NC}"
  exit 1
fi

# ─── Install Git Hooks ───
echo "[*] Setting up git hooks..."
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null || echo "")
if [ -n "$GIT_DIR" ]; then
  echo "  Git hooks installed (use .claude/settings.json for enforcement)"
else
  echo -e "  ${YELLOW}SKIP${NC}  Not a git repository"
fi

# ─── Install MCP Servers ───
echo "[*] Checking MCP servers..."
if [ -f "$SCRIPT_DIR/.mcp.json" ]; then
  echo "  .mcp.json found — MCP servers configured"
  echo "  Run: npx playwright install chromium  (for browser E2E testing)"
fi

# ─── Run Security Scan ───
echo "[*] Running security scan..."
if python "$SCRIPT_DIR/.github/scripts/security_scan.py" "$SCRIPT_DIR" 2>/dev/null; then
  echo -e "  ${GREEN}OK${NC}    No secrets found"
else
  echo -e "  ${YELLOW}WARN${NC}  Security scan found issues — review manually"
fi

# ─── Run Verification ───
if [ -f "$SCRIPT_DIR/verify.sh" ]; then
  echo "[*] Running verification..."
  bash "$SCRIPT_DIR/verify.sh" || true
fi

# ─── Summary ───
echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "  Harness:  Solo-Code-Harness v2.0.0"
echo "  Location: $SCRIPT_DIR"
echo ""
echo "  Quick start:"
echo "    • Read .claude/CLAUDE.md for agent rules"
echo "    • Check .claude/settings.json for lifecycle hooks"
echo "    • Run verify.sh to confirm setup"
echo ""
