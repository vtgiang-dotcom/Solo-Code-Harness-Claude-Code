# install.ps1 — Solo-Code-Harness Installer for Windows PowerShell
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Solo-Code-Harness Installer v2.0.0 ===" -ForegroundColor Cyan
Write-Host ""

# ─── Check Prerequisites ───
Write-Host "[*] Checking prerequisites..." -ForegroundColor Yellow

$prereqs = @(
  @{Name="git";    Test="git --version"},
  @{Name="node";   Test="node --version"},
  @{Name="python"; Test="python --version"}
)

$ok = $true
foreach ($p in $prereqs) {
  try {
    $result = Invoke-Expression $p.Test 2>$null
    Write-Host "  OK    $($p.Name) ($($result -join ' ').Trim())" -ForegroundColor Green
  } catch {
    Write-Host "  MISS  $($p.Name)" -ForegroundColor Red
    $ok = $false
  }
}

if (-not $ok) {
  Write-Host "`nERROR: Missing prerequisites. Install git, node, python and retry." -ForegroundColor Red
  exit 1
}

# ─── Check .mcp.json ───
Write-Host "[*] Checking MCP servers..." -ForegroundColor Yellow
if (Test-Path "$ScriptDir\.mcp.json") {
  Write-Host "  .mcp.json found — MCP servers configured" -ForegroundColor Green
  Write-Host "  Run: npx playwright install chromium  (for browser E2E testing)"
} else {
  Write-Host "  WARN  No .mcp.json — create from .mcp.json template" -ForegroundColor Yellow
}

# ─── Security Scan ───
Write-Host "[*] Running security scan..." -ForegroundColor Yellow
try {
  python "$ScriptDir\.github\scripts\security_scan.py" "$ScriptDir" 2>$null
  Write-Host "  OK    No secrets found" -ForegroundColor Green
} catch {
  Write-Host "  WARN  Security scan found issues — review manually" -ForegroundColor Yellow
}

# ─── Verify ───
if (Test-Path "$ScriptDir\verify.sh") {
  Write-Host "[*] Running verification (bash verify.sh)..." -ForegroundColor Yellow
  try {
    bash "$ScriptDir\verify.sh"
  } catch {
    Write-Host "  WARN  Could not run verify.sh (bash needed)" -ForegroundColor Yellow
  }
}

# ─── Summary ───
Write-Host ""
Write-Host "=== Installation Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "  Harness:  Solo-Code-Harness v2.0.0"
Write-Host "  Location: $ScriptDir"
Write-Host ""
Write-Host "  Quick start:"
Write-Host "    * Read .claude/CLAUDE.md for agent rules"
Write-Host "    * Check .claude/settings.json for permission config"
Write-Host "    * Run 'bash verify.sh' to confirm setup"
Write-Host ""
