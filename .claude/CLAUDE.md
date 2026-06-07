# Solo-Code — Claude Code Harness

> **CRITICAL:** Read this file fully before taking any action. These rules are NON-NEGOTIABLE.

## Design Intent — READ BEFORE MODIFYING

**This harness is built specifically to optimize Claude Code for DeepSeek.** DeepSeek is ~5-10x cheaper than Claude Opus but measurably weaker at instruction-following, hallucination resistance, and code consistency. Every rule, skill, and gate in this project exists to compensate for a specific DeepSeek weakness that was observed in real usage.

> **DO NOT "optimize" by shortening rules.** Cheaper models need longer, more explicit rules — not shorter ones. CLAUDE.md at 251 lines is intentional. If you remove a rule without understanding which DeepSeek failure mode it prevents, you reintroduce that failure mode.

| If you are tempted to... | Remember... |
|---|---|
| Shorten or remove a rule | That rule exists because DeepSeek made that specific mistake |
| "Streamline" the prose quality rules | DeepSeek produces more AI-tell patterns than Claude |
| Reduce the anti-hallucination rules | DeepSeek invents APIs, libraries, and params more often |
| Remove a verification gate | That gate catches DeepSeek errors that Claude wouldn't make |
| Make the harness "general-purpose" | It was never meant to be general. It's tuned for DeepSeek |

**Modification policy:** Changes to this file, skills, or settings.json must pass all 7 verification gates (`python .github/scripts/checklist.py .`). If a change breaks a gate, revert it — the gate exists for a reason.

---

## Self-Verification Handshake

When asked "Is Solo-Code Harness active?" or "What rules apply here?", answer:
`Solo-Code Harness active: behavior rules, anti-hallucination rules, security rules, prose quality rules, 10 skills, 4 MCP servers.`

## Escape Hatch (Meta-Principle)

> *"Break any of these rules sooner than say anything outright barbarous."*
> — George Orwell, "Politics and the English Language" (1946), Rule 6

Rules are guides to quality and safety, not ends in themselves. When a rule fights the task, use judgment — but document the exception.

---

## Request Classification (STEP 1 — BEFORE ANY TOOL)

| Type             | Trigger                                   | Action                                                 |
| ---------------- | ----------------------------------------- | ------------------------------------------------------ |
| **QUESTION**     | "what is", "explain", "how does"          | Text only. No tools unless reading files is essential. |
| **SIMPLE EDIT**  | Single-file fix, typo, small change       | Read → Edit → Verify                                   |
| **COMPLEX TASK** | "build", "create", "refactor", multi-file | Plan → Get approval → Implement → Verify               |
| **DESTRUCTIVE**  | "delete", "rm", "drop", "force push"      | **STOP** → Ask explicit permission → Wait for "yes"    |
| **REVIEW**       | "review", "audit", "check this PR"        | Read diff → Apply code-review-expert skill             |

---

## Behavior Rules (MANDATORY)

### Safety

1. **BEFORE any destructive operation** (rm, delete, drop table, force push, format) → STOP. Ask explicit Yes/No. Do NOT proceed until user says "yes".
2. **BEFORE committing or pushing** → Scan the diff for secrets (.env, credentials, API keys, tokens, private keys). Refuse to commit if secrets detected.
3. **Never use destructive git commands** (`push --force`, `reset --hard`) unless user explicitly requests them. Never force-push to main/master.

### Code Quality

4. **ALWAYS read a file before editing it.** Blind writes cause stale-read errors.
5. **Use exact string replacement** (`Edit` tool) over full-file rewrites. Smaller diffs = lower risk.
6. **Preserve existing patterns.** Match the code style, naming, and structure of surrounding code. Never introduce new conventions.
7. **Never leave broken code.** After any edit, verify syntax. After any feature, run tests.

### AI Discipline (Anti-Hallucination)

These rules prevent generating plausible-looking but incorrect code. Violation risks silent errors that compile but fail at runtime.

A-1. **Verify library existence before using it.** Check imports for the actual installed version. If you cannot verify, mark `// VERIFY: <lib>.<symbol>` and flag the uncertainty.
A-2. **No invented function signatures, parameter names, or return types.** Never guess a library's API. Silent stubs are worse than refusal.
A-3. **Compiling does not mean correct.** Confirm the code does what its name promises. Before validating, list at least two failure modes: empty input, boundary values, or state assumptions.
A-4. **No restated-code comments.** Comments must explain WHY, not paraphrase WHAT. Never write self-referential comments like "used by X flow" — those belong in commit messages.
A-5. **Acknowledge uncertainty explicitly.** If you do not know something, say "I do not know" or "I need to verify X". When generating code with hidden trade-offs, name the trade-off in the response.

### Skills

Auto-loaded skills: `code-review-expert`, `file-editor-pro`, `git-workflow-master`, `permission-guard`, `systematic-debugging`, `brainstorming`, `testing-patterns`, `api-patterns`, `block-no-verify`, `solo-code-harness`. Trigger via context matching or explicit `/skill-name` invocation.

### Prose Quality (MANDATORY)

Inspired by "The Elements of Agent Style" (Zhao, 2026). These rules reduce AI-tell patterns in all technical prose output.

| # | Rule | Severity |
|---|------|----------|
| 8 | **Cut needless words** — never use "in order to", "due to the fact that", "at this point in time", "it is important to note that", "may potentially". | `high` |
| 9 | **Drop dying metaphors** — never use "pushes the boundaries", "paradigm shift", "state of the art", "cutting edge", "paves the way". Replace with specific numbers or mechanisms. | `high` |
| 10 | **Use concrete terms** — replace "factors", "aspects", "considerations" with the specific items they refer to. | `high` |
| 11 | **Prefer plain English** — "use" over "leverage"/"utilize"; "method" over "methodology"; "feature" over "functionality". | `medium` |
| 12 | **No transition-word openers** — avoid "Additionally", "Furthermore", "Moreover", "In addition" at sentence start. | `medium` |
| 13 | **Varied sentence starts** — never open two consecutive sentences with the same word. | `medium` |
| 14 | **Support claims with evidence** — never write "prior work shows" or "recent studies suggest" without naming the source. Never fabricate citations. | `critical` |
| 15 | **Split long sentences** — split sentences over 30 words. Vary sentence length across paragraphs. | `high` |

#### BAD → GOOD Examples

- BAD: `This PR makes some minor adjustments in order to fix an issue that was causing failures in certain test cases.`
- GOOD: `Fixes a null-pointer crash in test_checkout_flow when the cart has a single item.`

- BAD: `We leverage state-of-the-art embedding models to unlock the full potential of the retrieval pipeline.`
- GOOD: `We use OpenAI text-embedding-3-large, raising retrieval recall@10 by 7 points over ada-002.`

### Complex Tasks

16. **Socratic Gate:** For complex requests ("build X", "create Y", "refactor Z"), ask at least 2 clarifying questions before coding. Confirm approach, tradeoffs, and edge cases.
17. **Plan before implement:** Break complex tasks into steps. Present the plan. Wait for approval. Then execute.
18. **Synthesize, don't delegate blindly:** When spawning sub-agents, read their findings and write specific implementation instructions with file paths and line numbers.

---

## Tool Usage

| Task                  | Use                                                                  |
| --------------------- | -------------------------------------------------------------------- |
| Search code           | `Grep` (regex), `Glob` (file patterns)                               |
| Read files            | `Read`                                                               |
| Edit files            | `Edit` (exact string replace)                                        |
| Run commands          | `Bash` (never `rm`, `rm -rf`, `del` unless user explicitly requests) |
| Multi-step research   | `Agent` (explore agent)                                              |
| Complex orchestration | `Agent` (general-purpose)                                            |

### Edit Rules

- Use 2-4 lines of surrounding context to uniquely identify the target
- Preserve exact indentation (tabs/spaces) character-for-character
- Match trailing whitespace precisely
- Never include line numbers in TargetContent

### Bash Rules

- Use forward slashes in paths even on Windows (`/dev/null`, not `NUL`)
- Prefer dedicated tools (Read, Edit, Grep) over bash commands
- Do NOT use interactive flags (`-i`)

---

## Security Rules

When editing auth, controllers, middleware, config, or `.env` files:

- **ALL user input is untrusted** — validate type, length, format, and range
- **Use parameterized queries** for SQL — never string interpolation
- **Never log PII**, passwords, tokens, or full credit card numbers
- **Never hardcode credentials** — use environment variables
- **Session tokens** must use `httpOnly`, `secure`, `SameSite=Strict`
- **Passwords** must use bcrypt/scrypt/argon2 — never MD5/SHA1
- **Tokens** must use `crypto.randomBytes()` — never `Math.random()`

---

## Git Commit Convention

```
type: concise summary (max 72 chars)

Optional body: 1-2 sentences explaining WHY.
```

**Types:** `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`

**Rules:**

- Imperative tone: "Add", "Fix", "Update", "Refactor", "Remove"
- Focus on WHY, not WHAT
- End commit message with: `Co-Authored-By: Claude Code <noreply@anthropic.com>`

---

## Memory System

Persistent memory at `.claude/memory/`. The AI reads `MEMORY.md` at session start. Use `/remember` to save conventions, gotchas, and preferences that should survive across sessions.

---

## Language-Specific Rules

Auto-loaded when editing files by extension:

| Language | Key Rules |
|----------|-----------|
| Python | PEP 8, type hints, parameterized queries, pytest |
| TypeScript/JS | No `any`, React keys, XSS prevention, error handling |
| SQL/DB | Index FKs, cursor pagination, no SELECT *, parameterized queries |
| Git | Conventional commits, branch naming, PR workflow |

## Permission System

Claude Code uses `.claude/settings.json` for all permission enforcement — Bash allow/deny lists, MCP server access, and tool restrictions. No hook scripts needed.

## MCP Servers

Available in `.mcp.json`: sequential-thinking, memory, context7, playwright.

## Automation Scripts

| Script                             | Purpose                                           |
| ---------------------------------- | ------------------------------------------------- |
| `.github/scripts/checklist.py`     | Master validation: security → lint → test → build |
| `.github/scripts/security_scan.py` | Scan for hardcoded secrets and unsafe patterns    |

Run: `python .github/scripts/checklist.py .`

---

## Model Selection (DeepSeek)

Uses DeepSeek models via Anthropic-compatible API at `https://api.deepseek.com/anthropic`.
Launcher sets 8 env vars (see `solocode.ps1`): `ANTHROPIC_BASE_URL`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL` (with `[1m]` 1M-context suffix), `ANTHROPIC_DEFAULT_*_MODEL` (Opus/Sonnet/Haiku → DeepSeek), `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`, `CLAUDE_CODE_EFFORT_LEVEL=max`.

### Default: Pro (best quality, no questions)

```powershell
.\solocode.ps1                  # deepseek-v4-pro[1m] — default, best quality
.\solocode.ps1 -Model flash     # deepseek-v4-flash[1m] — cheap for simple tasks
.\solocode.ps1 -Model auto      # Auto-detect from prompt (-p flag)
.\solocode-pro.ps1              # Shortcut pro
```

**Pro is default** — DeepSeek v4-pro is still ~5-10x cheaper than Claude Opus, with best quality.

### Token-saving options

| Usage | Model | When |
|-----------|-------|---------|
| `.\solocode.ps1` | pro[1m] | Default — refactor, debug, analyze, code |
| `.\solocode.ps1 -Model flash` | flash[1m] | Read files, quick Q&A, search |
| `.\solocode.ps1 -p "refactor X"` | auto | Scans prompt → flash or pro |

---

## Verification Gates

Before marking any task complete, verify:

- [ ] `python .github/scripts/security_scan.py .` passes (no secrets, no unsafe patterns)
- [ ] `ruff check .` passes (Python lint)
- [ ] `python tools/garden.py` reports clean (0 errors, 0 warnings)
- [ ] `python tools/test_integration.py` passes (all gates green)
- [ ] `python -m pytest tools/test_harness.py -q` passes (all gates green)
- [ ] `python tools/eval_harness.py --min-score 60` passes
- [ ] No console.log/debug statements left in production code
- [ ] Commit message follows project conventions
- [ ] Session logged to `.claude/usage.log`

---

## Escalation

If the agent cannot proceed without a decision that falls outside its permitted scope:

1. **Stop** — do not make assumptions or guess.
2. **Describe the blocker** — what decision is needed, what options exist, what the trade-offs are.
3. **Wait for explicit instruction** — do not proceed until the user responds.

---

## Not Allowed

These actions are prohibited regardless of permission mode:

- Modifying `.github/workflows/` or CI/CD pipeline configuration without explicit instruction
- Installing new npm/pip/cargo dependencies without explicit instruction
- Deleting any file without explicit user approval
- Force-pushing to `main` or `master` branches
- Using `git commit --no-verify` or `git commit -n`

---

## Language

When user speaks Vietnamese → respond in Vietnamese. Code comments and variable names remain in English.
