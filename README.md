# Solo-Code Harness — Claude Code + DeepSeek

> **Mission:** Claude Code experience at DeepSeek price. A disciplined engineering harness that compensates for model gaps so you ship quality code at ~5-10x lower cost.
> <sub>1 developer + Claude Code CLI + DeepSeek API + this harness = a team.</sub>

<p align="center">
  <b>Claude Code</b> (harness, skills, MCP) ───▶ <b>DeepSeek API</b> (thinking, coding)<br>
  <sub>Experience of Claude • Price of DeepSeek</sub>
</p>

---

## Why This Exists

**DeepSeek v4-pro is ~5-10x cheaper than Claude Opus, but weaker at:** instruction-following, hallucination resistance, and consistent code quality. The harness compensates for each gap.

| DeepSeek Weakness | Harness Compensation |
|---|---|
| Higher hallucination rate — invents APIs, libraries, params | Anti-hallucination rules (A1-A5): verify before generating |
| Unstable code quality — inconsistent patterns across calls | 10 structured skills with step-by-step protocols, not generic advice |
| More AI-tell prose — "leverage", "paradigm shift", 40-word sentences | Prose quality rules (8-15) enforced in every output |
| No built-in guardrails for destructive ops | 29 deny patterns in settings.json, guard.test.js 29/29 |
| No commit discipline | Conventional commits enforced, `--no-verify` blocked |

> **Key insight:** With cheaper models, rules must be *longer and more explicit* — not shorter. CLAUDE.md at 251 lines is intentional compensation, not bloat.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  claudecode.ps1 │────▶│  Claude Code CLI  │────▶│  DeepSeek   │
│  smart launcher │     │  + harness        │     │  API        │
│                 │     │  + 10 skills      │     │  v4-pro     │
│  model: auto    │     │  + 4 MCP servers  │     │  v4-flash   │
└─────────────────┘     └──────────────────┘     └─────────────┘
        │                        │                       │
        │  ANTHROPIC_BASE_URL = api.deepseek.com/anthropic
        │  ANTHROPIC_MODEL   = deepseek-v4-pro
        │  ANTHROPIC_API_KEY = $DEEPSEEK_API_KEY
        │
        │  Claude Code thinks it talks to Anthropic.
        │  DeepSeek responds in Anthropic-compatible format.
        │  Cost: ~$0.3/M tokens vs Claude's ~$3/M.
```

### Smart Launcher — Auto Model Selection

`claudecode.ps1` scans your prompt for 20 complexity keywords. Complex tasks get `v4-pro`; quick reads get `v4-flash`. No manual switching.

```
.\claudecode.ps1                  # pro default — best quality
.\claudecode.ps1 -Model flash     # flash — read-only, simple Q&A
.\claudecode.ps1 -p "refactor X"  # auto-detect from prompt text
.\claudecode-pro.ps1              # pro shortcut
```

| Trigger keywords → pro | Everything else → flash |
|---|---|
| refactor, debug, bug, build, create, analyze, audit, architect, design, migrate, implement, security, optimize, fix, error, crash, restructure, review | Read files, explain code, search, ask questions |

---

## Philosophy

**Solo development with AI is about discipline, not speed.** Without guardrails, AI agents cut corners. This harness enforces the process:

| Principle | Without | With | Mechanism |
|-----------|:---:|:---:|-----------|
| Plan before code | Occasional | **Always** | CLAUDE.md rulebook |
| Ask before destructive ops | Rare | **Always** | settings.json deny rules |
| Read before edit | Sometimes | **Always** | CLAUDE.md rulebook |
| Scan secrets before commit | Rare | **Always** | security_scan.py |
| Prose quality (no AI-tells) | Drifts | **Guided** | CLAUDE.md prose rules |
| Cost-optimized model routing | Manual | **Auto** | claudecode.ps1 smart detect |

---

## Quick Start

```bash
git clone <your-repo-url>
cd Solo-Code-Harness

# Smart launcher — auto-detect flash vs pro
.\claudecode.ps1

# Force model
.\claudecode.ps1 -Model pro     # DeepSeek v4 Pro
.\claudecode.ps1 -Model flash   # DeepSeek v4 Flash
.\claudecode-pro.ps1            # Pro shortcut
```

---

## Structure

```
.claude/                    # Claude Code harness
  CLAUDE.md                 # Master rulebook (247 lines)
  settings.json             # Permission allow/deny rules
  skills/                   # 10 validated skills
  memory/                   # Cross-session persistent memory
  usage.log                 # Session telemetry (local)

.github/scripts/            # security_scan.py, checklist.py
.github/hooks/scripts/      # guard.js, guard.test.js (29/29)

tools/                      # Quality gates
  garden.py                 # Drift detection
  test_harness.py           # 25 unit tests
  test_integration.py       # 46 integration tests
  eval_harness.py           # Behavioral scoring

claudecode.ps1              # Smart launcher (flash/pro auto-detect)
claudecode-pro.ps1          # Pro shortcut
.mcp.json                   # 4 MCP servers
Makefile                    # garden, test, check
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

---

## Model Selection

`claudecode.ps1` auto-detects task complexity or asks interactively:

```
.\claudecode.ps1                  # Asks [F/p] before launch
.\claudecode.ps1 -Model pro       # Force deepseek-v4-pro
.\claudecode.ps1 -Model flash     # Force deepseek-v4-flash
.\claudecode.ps1 -p "refactor X"  # Auto-detect from prompt
```

Uses DeepSeek API at `https://api.deepseek.com/anthropic` with `DEEPSEEK_API_KEY` from `.env`.

---

## MCP Servers

| Server | Purpose |
|--------|---------|
| `sequential-thinking` | Chain-of-thought reasoning |
| `memory` | Persistent knowledge graph |
| `context7` | Live documentation lookup |
| `playwright` | Browser E2E testing |

---

## License

MIT — See [LICENSE](LICENSE)
