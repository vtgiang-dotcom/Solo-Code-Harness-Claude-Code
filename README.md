# Solo-Code Harness — Claude Code Agent Layer

> **Mission:** The lightest, safest harness that transforms Claude Code into a disciplined Solo-Code Engineer.
> <sub>1 developer + Claude Code + DeepSeek = a team. The harness is your engineering process.</sub>

<p align="center"><b>Claude Code</b> + <b>DeepSeek API</b> (flash + pro)</p>

---

## Philosophy

**Solo development with AI is about discipline, not speed.** Without guardrails, AI agents cut corners. Solo-Code Harness enforces the process:

| Principle | Without | With | Mechanism |
|-----------|:---:|:---:|-----------|
| Plan before code | Occasional | **Always** | CLAUDE.md rulebook |
| Ask before destructive ops | Rare | **Always** | settings.json deny rules |
| Read before edit | Sometimes | **Always** | CLAUDE.md rulebook |
| Scan secrets before commit | Rare | **Always** | security_scan.py |
| Prose quality (no AI-tells) | Drifts | **Guided** | CLAUDE.md prose rules |
| Model selection | Manual | **Auto** | claudecode.ps1 smart detect |

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
