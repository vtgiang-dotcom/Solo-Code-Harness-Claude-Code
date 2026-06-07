# Claude Code + DeepSeek API — Smart Launcher
#
# Default: deepseek-v4-pro (best quality, still cheaper than Claude)
# Override: -Model flash (fast/cheap for simple tasks)
# Auto-detect: -p "refactor X" scans prompt to pick model
#
# Usage:
#   .\solocode.ps1                  # pro (default — best quality)
#   .\solocode.ps1 -Model flash      # force flash
#   .\solocode.ps1 -Model pro        # force pro
#   .\solocode.ps1 -p "refactor X"   # auto-detect from prompt text
#   .\solocode-pro.ps1               # shortcut for -Model pro

param(
    [ValidateSet("auto", "flash", "pro")]
    [string]$Model = "pro"
)

$envFile = Join-Path $PSScriptRoot ".env"
$deepseekApiKey = ""

if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            $parts = $line.Split('=', 2)
            if ($parts.Length -eq 2) {
                if ($parts[0].Trim() -eq "DEEPSEEK_API_KEY") {
                    $deepseekApiKey = $parts[1].Trim()
                }
            }
        }
    }
} else {
    Write-Error ".env not found at $envFile"
    exit 1
}

if (-not $deepseekApiKey -or $deepseekApiKey -eq "YOUR_DEEPSEEK_API_KEY_HERE") {
    Write-Host "ERROR: DEEPSEEK_API_KEY not configured in .env" -ForegroundColor Red
    exit 1
}

# --- Resolve model ---
$autoDetected = $false

function Test-IsComplex {
    param([string]$Text)
    $kw = @("refactor","debug","bug","build","create","analyze","audit","architect",
        "design","migrate","implement","security","optimize","performance","fix",
        "error","crash","restructure","review")
    ($kw | Where-Object { $Text.ToLower() -match $_ }).Count -gt 0
}

if ($Model -eq "auto") {
    # Try to detect from -p flag or piped args
    $promptText = ""
    $pIdx = [Array]::IndexOf($args, "-p")
    if ($pIdx -ge 0 -and $pIdx + 1 -lt $args.Count) {
        $promptText = $args[$pIdx + 1]
    } elseif ($args.Count -gt 0) {
        $promptText = $args -join " "
    }
    if ($promptText -and (Test-IsComplex $promptText)) {
        $Model = "pro"
        $autoDetected = $true
    } else {
        $Model = "flash"
    }
}

$modelName  = if ($Model -eq "pro") { "deepseek-v4-pro[1m]" } else { "deepseek-v4-flash[1m]" }
$modelLabel = if ($Model -eq "pro") { "PRO" } else { "FLASH" }
$detectNote = if ($autoDetected) { " (auto)" } else { "" }

# --- Launch ---
$env:ANTHROPIC_BASE_URL = "https://api.deepseek.com/anthropic"
$env:ANTHROPIC_API_KEY = $deepseekApiKey
$env:ANTHROPIC_AUTH_TOKEN = $deepseekApiKey          # Claude Code reads both
$env:ANTHROPIC_MODEL = $modelName
# Map Claude model names to DeepSeek (prevent routing errors)
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = "deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = "deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL = "deepseek-v4-flash[1m]"
# Prevent Claude Code from phoning home to Anthropic
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
# Max effort — DeepSeek needs explicit instruction
$env:CLAUDE_CODE_EFFORT_LEVEL = "max"

$logDir = Join-Path $PSScriptRoot ".claude"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
$logFile = Join-Path $logDir "usage.log"
$sessionStart = Get-Date

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " Claude Code + DeepSeek API" -ForegroundColor Green
Write-Host " Model : $modelName ($modelLabel)$detectNote" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host " Switch: .\solocode.ps1 -Model flash  (tiet kiem token)" -ForegroundColor DarkGray
Write-Host "         .\solocode.ps1 -p ""refactor""  (auto-detect)" -ForegroundColor DarkGray
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

& claude $args

$sessionEnd = Get-Date
$duration = [math]::Round(($sessionEnd - $sessionStart).TotalMinutes, 1)

try {
    $logEntry = [PSCustomObject]@{
        timestamp    = $sessionStart.ToString("o")
        model        = $modelName
        mode         = if ($autoDetected) { "auto" } else { "manual" }
        duration_min = $duration
        exit_code    = $LASTEXITCODE
    }
    $logEntry | ConvertTo-Json -Compress | Add-Content -Path $logFile -Encoding UTF8
} catch { }

Write-Host "--- Session: ${duration}min | Model: $modelName ---" -ForegroundColor DarkGray
