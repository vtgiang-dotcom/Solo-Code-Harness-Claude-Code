# Solo-Code Harness — Optimizing Claude Code for DeepSeek

> **Purpose:** Make DeepSeek work as a disciplined Claude Code engineer. This harness compensates for every weakness DeepSeek has — so Claude Code + DeepSeek matches Claude Opus quality at ~5-10x lower cost.
> <sub>Claude Code CLI (interface) + DeepSeek API (engine) + This Harness (discipline) = a one-person team.</sub>

<p align="center">
  <b>Claude Code</b> ──▶ <b>Harness</b> (rules, skills, MCP, gates) ──▶ <b>DeepSeek API</b><br>
  <sub>This is NOT a general-purpose harness. It is built specifically to optimize Claude Code for DeepSeek.</sub>
</p>

---

## Problem & Solution

**DeepSeek is ~5-10x cheaper than Claude Opus, but measurably weaker.** Running Claude Code on DeepSeek without this harness gives you: hallucinated code, inconsistent style, AI-tell prose, and zero engineering discipline. This harness exists to fix each of those.

| DeepSeek Weakness | How This Harness Compensates |
|---|---|
| **High hallucination** — invents libraries, APIs, parameter names | Anti-hallucination rules (A1-A5): verify imports and APIs before generating |
| **Unstable code quality** — different patterns on every call | 10 skills with step-by-step protocols, not generic advice |
| **AI-tell prose** — "leverage", "paradigm shift", 40-word sentences | Prose quality rules (8-15) enforced on every output |
| **No guardrails** — happily runs `rm -rf`, `DROP TABLE` | 29 deny patterns in settings.json, guard.test.js 29/29 |
| **No commit discipline** — sloppy messages | Conventional commits enforced, `--no-verify` blocked |

> **Design principle:** Cheaper models need *longer, more explicit* rules — not shorter. CLAUDE.md at 251 lines is intentional compensation for DeepSeek. Every line is a mistake DeepSeek once made and can no longer repeat.

---

## How It Works

```
┌──────────────────┐     ┌──────────────────────┐     ┌─────────────┐
│  solocode.ps1    │────▶│  Claude Code CLI      │────▶│  DeepSeek   │
│  Smart launcher  │     │  + CLAUDE.md (rules)  │     │  API        │
│  Auto model pick │     │  + 10 skills          │     │  v4-pro     │
│  flash vs pro    │     │  + 4 MCP servers      │     │  v4-flash   │
└──────────────────┘     └──────────────────────┘     └─────────────┘
        │                         │                         │
        │  ANTHROPIC_BASE_URL  = https://api.deepseek.com/anthropic
        │  ANTHROPIC_MODEL     = deepseek-v4-pro
        │  ANTHROPIC_API_KEY   = $DEEPSEEK_API_KEY (from .env)
        │
        │  Claude Code thinks it's talking to Anthropic.
        │  DeepSeek responds in Anthropic-compatible format.
        │  The harness intercepts every bad habit before it reaches you.
        │
        │  Pricing (per 1M tokens):
        │    pro:   $0.435 input / $0.87 output / $0.003625 cache hit
        │    flash: $0.14 input  / $0.28 output / $0.0028 cache hit
        │  Harness maximizes cache hits → most input at ~$0.003/M
        │  Cost: ~$0.3/M tokens vs Claude's ~$3/M.
```

### Smart Launcher — Auto Model Selection

`solocode.ps1` scans your prompt against 20 complexity keywords. Complex tasks get `v4-pro`; file reads and quick questions get `v4-flash`. No manual switching.

```
.\solocode.ps1                  # pro default — best quality
.\solocode.ps1 -Model flash     # flash — read files, simple Q&A
.\solocode.ps1 -p "refactor X"  # auto-detect from prompt text
.\solocode-pro.ps1              # pro shortcut
```

| Keywords → pro | Everything else → flash |
|---|---|
| refactor, debug, bug, build, create, analyze, audit, architect, design, migrate, implement, security, optimize, fix, error, crash, restructure, review | Read files, explain code, search, ask questions |

---

## Design Philosophy

**Claude Code is the best interface. DeepSeek is the cheapest engine. But connecting them requires a discipline layer.** This harness is that layer — it forces DeepSeek to follow the engineering process Claude Code expects.

| Discipline | Without Harness | With Harness | Mechanism |
|------------|:---:|:---:|-----------|
| Plan before coding | Sometimes | **Always** | CLAUDE.md rulebook |
| Confirm destructive ops | Rarely | **Always** | settings.json deny rules |
| Read file before editing | Sometimes | **Always** | CLAUDE.md rulebook |
| Scan secrets before commit | Rarely | **Always** | security_scan.py |
| No AI-tell prose | Drifts | **Controlled** | CLAUDE.md prose rules |
| Task-appropriate model | Manual | **Automatic** | solocode.ps1 smart detect |
| Cache-optimized prompts | No | **Designed-in** | Stable CLAUDE.md = max cache hits |

> **Cache economics:** DeepSeek charges ~$0.003/M tokens for cache hits (vs $0.435/M for uncached input). The harness's long, stable system prompt is a feature, not a bug — every cached token saves ~99% in input cost. A 251-line CLAUDE.md that hits cache costs less than a 50-line one that misses.

---

## Quick Start

### New project (empty directory)

```bash
# Clone harness as template
git clone https://github.com/vtgiang-dotcom/Solo-Code-Harness-Claude-Code.git my-project
cd my-project

# Remove harness self-tests and docs — keep the harness layer only
rm -rf .git tools/ README.md
git init
git add -A && git commit -m "init: Solo-Code Harness + DeepSeek"

# Create .env with your DeepSeek API key
echo "DEEPSEEK_API_KEY=sk-your-key-here" > .env

# Ready
.\solocode.ps1
```

### Existing project (add harness to current codebase)

```bash
# Clone harness to temp, copy harness layer only
git clone https://github.com/vtgiang-dotcom/Solo-Code-Harness-Claude-Code.git /tmp/harness
cp -r /tmp/harness/.claude /tmp/harness/.mcp.json \
      /tmp/harness/solocode* /tmp/harness/.github \
      /tmp/harness/.ruff.toml /tmp/harness/Makefile .
rm -rf /tmp/harness
echo "DEEPSEEK_API_KEY=sk-your-key-here" > .env

# Or use the deploy script (dry-run first)
python tools/deploy.py . --dry-run
python tools/deploy.py .
```

### VSCode Extension (alternative to CLI)

```bash
# 1. Install Claude Code VSCode Extension
#    https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code

# 2. Disable login prompt (required for DeepSeek)
#    VSCode Settings → search "claudeCode.disableLoginPrompt" → enable

# 3. Generate global config so VSCode Extension reads DeepSeek settings
python tools/setup-global-config.py
```

### Force model

```bash
# Windows (PowerShell)
.\solocode.ps1                  # pro[1m] default — best quality
.\solocode.ps1 -Model flash     # flash[1m] — read files, simple Q&A
.\solocode.ps1 -p "refactor X"  # auto-detect from prompt text
.\solocode-pro.ps1              # pro shortcut

# Linux / Mac (bash)
chmod +x solocode.sh solocode-pro.sh
./solocode.sh                   # pro[1m] default — best quality
./solocode.sh -Model flash      # flash[1m] — read files, simple Q&A
./solocode.sh -p "refactor X"   # auto-detect from prompt text
./solocode-pro.sh               # pro shortcut
```

### What gets deployed

| Copied | Not copied |
|--------|-----------|
| `.claude/` (rules, skills, memory) | `tools/` (harness self-tests) |
| `.mcp.json` (4 MCP servers) | `README.md` |
| `solocode.ps1` (smart launcher) | `.git/` |
| `.github/` (security gates) | `.env` (create your own) |
| `.ruff.toml`, `Makefile` | |

---

## Structure

```
.claude/                    # Claude Code harness
  CLAUDE.md                 # Master rulebook (251 lines)
  settings.json             # Permission allow/deny rules
  skills/                   # 10 validated skills
  memory/                   # Cross-session persistent memory
  usage.log                 # Session telemetry (local)

.github/scripts/            # security_scan.py, checklist.py
.github/hooks/scripts/      # guard.js, guard.test.js (29/29)

tools/                      # Quality gates
  garden.py                 # Drift detection
  test_harness.py           # 18 unit tests
  test_integration.py       # 46 integration tests
  eval_harness.py           # Behavioral scoring (100/100)

solocode.ps1                # Smart launcher — Windows
solocode-pro.ps1            # Pro shortcut — Windows
solocode.sh                 # Smart launcher — Linux/Mac
solocode-pro.sh             # Pro shortcut — Linux/Mac
.mcp.json                   # 4 MCP servers
```

---

## Skills (10)

| Skill | Tools | Purpose |
|-------|-------|---------|
| `code-review-expert` | Read, Grep, Glob, Bash | Code review, PR audit |
| `file-editor-pro` | Read, Edit, Grep, Glob | Precise file editing |
| `systematic-debugging` | Read, Grep, Glob, Bash | Root cause analysis |
| `brainstorming` | Read, Grep, Glob | Feature design, architecture |
| `testing-patterns` | Read, Write, Edit, Bash, Grep | Test writing, TDD |
| `git-workflow-master` | Bash | Safe commits, conventional format |
| `api-patterns` | Read, Grep, Glob | API design (REST/GraphQL/tRPC) |
| `permission-guard` | Read, AskUserQuestion | Destructive op confirmation |
| `block-no-verify` | Bash, Read | Block `git commit --no-verify` |
| `solo-code-harness` | Read, Edit, Bash, Agent, Skill | Harness deployment |

---

## Quality Gates

```bash
make check              # Full gate: ruff + garden + test + integration
make garden             # Drift detection
make test               # Unit tests (pytest)
make test-integration   # Integration tests
make security-scan      # Secret scan
```

| Gate | Result |
|------|--------|
| `ruff check .` | All passed |
| `python tools/garden.py` | 0 errors, 0 warnings |
| `python tools/test_integration.py` | 46 passed, 0 failed |
| `python -m pytest tools/test_harness.py -q` | 18 passed |
| `python tools/eval_harness.py` | 100/100 — A (Production-ready) |
| `python .github/scripts/security_scan.py .` | Clean |
| `python .github/scripts/checklist.py .` | 4/4 passed |

---

## MCP Servers

| Server | Purpose |
|--------|---------|
| `sequential-thinking` | Chain-of-thought reasoning for complex problems |
| `memory` | Persistent knowledge graph across sessions |
| `context7` | Live documentation lookup for libraries and frameworks |
| `playwright` | Browser automation for E2E testing and web scraping |

---

## License

MIT — See [LICENSE](LICENSE)
