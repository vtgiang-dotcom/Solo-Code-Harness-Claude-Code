# Solo-Code Harness — Tối ưu Claude Code cho DeepSeek

> **Mục đích:** Biến DeepSeek thành Claude Code engineer đáng tin cậy. Harness này bù đắp mọi điểm yếu của DeepSeek — để Claude Code làm việc với DeepSeek tốt như với Claude Opus, với chi phí thấp hơn ~5-10x.
> <sub>Claude Code CLI (giao diện) + DeepSeek API (engine) + Harness này (kỷ luật) = đội ngũ 1 người.</sub>

<p align="center">
  <b>Claude Code</b> ──▶ <b>Harness</b> (rules, skills, MCP, gates) ──▶ <b>DeepSeek API</b><br>
  <sub>Dự án này KHÔNG phải harness tổng quát. Nó được thiết kế riêng để tối ưu Claude Code cho DeepSeek.</sub>
</p>

---

## Vấn đề & Giải pháp

**DeepSeek rẻ hơn Claude Opus ~5-10x, nhưng yếu hơn rõ rệt.** Nếu dùng Claude Code với DeepSeek mà không có harness, bạn gặp: code ảo giác, style không nhất quán, văn phong AI, thiếu kỷ luật kỹ thuật. Harness này tồn tại để giải quyết từng vấn đề.

| DeepSeek yếu ở đâu | Harness bù bằng gì |
|---|---|
| **Ảo giác cao** — bịa thư viện, API, tham số không tồn tại | Anti-hallucination rules (A1-A5): verify trước khi generate |
| **Code không ổn định** — pattern khác nhau mỗi lần gọi | 10 skills với protocol từng bước, không phải lời khuyên chung chung |
| **Văn AI** — "leverage", "paradigm shift", câu 40 từ | Prose quality rules (8-15) enforced trong mọi output |
| **Không guardrail** — sẵn sàng rm -rf, drop table | 29 deny patterns trong settings.json, guard.test.js 29/29 |
| **Không kỷ luật commit** — message tùy tiện | Conventional commits, block `--no-verify` |

> **Nguyên tắc thiết kế:** Model càng rẻ → rule càng phải *dài và chi tiết*. CLAUDE.md 251 dòng không phải bloat — đó là compensation có chủ đích cho DeepSeek. Mỗi dòng là một lỗi DeepSeek từng mắc phải và đã được ngăn chặn.

---

## Cách nó hoạt động

```
┌──────────────────┐     ┌──────────────────────┐     ┌─────────────┐
│  claudecode.ps1  │────▶│  Claude Code CLI      │────▶│  DeepSeek   │
│  Smart launcher  │     │  + CLAUDE.md (rules)  │     │  API        │
│  Auto model pick │     │  + 10 skills          │     │  v4-pro     │
│  flash vs pro    │     │  + 4 MCP servers      │     │  v4-flash   │
└──────────────────┘     └──────────────────────┘     └─────────────┘
        │                         │                         │
        │  ANTHROPIC_BASE_URL  = https://api.deepseek.com/anthropic
        │  ANTHROPIC_MODEL     = deepseek-v4-pro
        │  ANTHROPIC_API_KEY   = $DEEPSEEK_API_KEY (từ .env)
        │
        │  Claude Code nghĩ nó đang nói chuyện với Anthropic.
        │  DeepSeek phản hồi đúng format Anthropic.
        │  Harness chặn mọi thói xấu của DeepSeek trước khi đến tay bạn.
        │  Chi phí: ~$0.3/M tokens thay vì ~$3/M của Claude.
```

### Smart Launcher — Tự động chọn model DeepSeek

`claudecode.ps1` quét prompt của bạn với 20 keyword. Task phức tạp → `v4-pro`; đọc file, hỏi nhanh → `v4-flash`. Không cần chuyển thủ công.

```
.\claudecode.ps1                  # pro mặc định — chất lượng tốt nhất
.\claudecode.ps1 -Model flash     # flash — đọc file, hỏi đáp đơn giản
.\claudecode.ps1 -p "refactor X"  # auto-detect từ nội dung prompt
.\claudecode-pro.ps1              # shortcut pro
```

| Keyword → pro | Còn lại → flash |
|---|---|
| refactor, debug, bug, build, create, analyze, audit, architect, design, migrate, implement, security, optimize, fix, error, crash, restructure, review | Đọc file, giải thích code, tìm kiếm, hỏi đáp |

---

## Triết lý thiết kế

**Claude Code là giao diện tốt nhất. DeepSeek là engine rẻ nhất. Nhưng ghép chúng với nhau cần một lớp trung gian.** Harness này là lớp đó — nó ép DeepSeek tuân thủ kỷ luật mà Claude Code đòi hỏi.

| Kỷ luật | Không có harness | Có harness | Cơ chế |
|---------|:---:|:---:|--------|
| Lên kế hoạch trước khi code | Thỉnh thoảng | **Luôn luôn** | CLAUDE.md rulebook |
| Hỏi trước thao tác destructive | Hiếm | **Luôn luôn** | settings.json deny rules |
| Đọc file trước khi sửa | Đôi khi | **Luôn luôn** | CLAUDE.md rulebook |
| Quét secrets trước commit | Hiếm | **Luôn luôn** | security_scan.py |
| Văn phong không AI-tell | Bị trôi | **Kiểm soát** | CLAUDE.md prose rules |
| Chọn model theo task | Thủ công | **Tự động** | claudecode.ps1 smart detect |

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
