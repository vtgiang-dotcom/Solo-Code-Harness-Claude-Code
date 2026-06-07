---
name: solo-code-harness
description: "Deploy, configure, and maintain the Solo-Code Claude Code harness. Use when: deploy harness, setup claude, configure AI agents, install AI harness, solo-code setup, initialize project."
license: MIT
allowed-tools: "Read, Edit, Bash, Agent, Skill"
---

# Solo-Code Harness — Optimizing Claude Code for DeepSeek

You are an expert on the Solo-Code Harness framework — a discipline layer built **specifically to make DeepSeek work reliably through Claude Code.**

> **Design Intent:** This harness compensates for DeepSeek's weaknesses (hallucination, inconsistency, AI-tell prose, missing guardrails). Every rule is intentionally long — cheaper models need more explicit guidance. Do NOT shorten rules without understanding which DeepSeek failure mode they prevent. See `.claude/CLAUDE.md` § Design Intent.

---

## Architecture

| Component | Location | Purpose |
|-----------|----------|---------|
| Rulebook | `.claude/CLAUDE.md` | Behavior rules, anti-hallucination, prose quality, model selection |
| Permissions | `.claude/settings.json` | Bash allow/deny rules |
| Skills | `.claude/skills/` | 10 context-triggered skills |
| Memory | `.claude/memory/` | Cross-session persistent memory |
| MCP | `.mcp.json` | sequential-thinking, memory, context7, playwright |
| Launcher | `solocode.ps1` | Smart model selection (DeepSeek flash/pro) |

---

## Deployment

Copy these files to the target project:

```
.claude/                    # Full harness
.mcp.json                   # MCP server config
.github/scripts/            # security_scan.py, checklist.py
.github/hooks/scripts/      # guard.js, guard.test.js
.gitleaks.toml              # Secret scanner config
.ruff.toml                  # Python linter config
solocode.ps1              # Smart launcher
solocode-pro.ps1          # Pro shortcut
```

Claude Code auto-discovers `.claude/CLAUDE.md` and `.claude/settings.json` at repo root.

---

## Skills Reference

| Skill | Tools | Triggers |
|-------|-------|----------|
| `code-review-expert` | Read, Grep, Glob, Bash | PR review, code audit, security |
| `file-editor-pro` | Read, Edit, Grep, Glob | File editing, refactoring |
| `systematic-debugging` | Read, Grep, Glob, Bash | Bug, error, test failure |
| `brainstorming` | Read, Grep, Glob | Design, architecture, ideation |
| `testing-patterns` | Read, Write, Edit, Bash, Grep | Test writing, TDD |
| `git-workflow-master` | Bash | Commit, push, PR |
| `api-patterns` | Read, Grep, Glob | API design (REST/GraphQL/tRPC) |
| `permission-guard` | Read, AskUserQuestion | rm, delete, credentials, config |
| `block-no-verify` | Bash, Read | `git commit --no-verify` |
| `solo-code-harness` | Read, Edit, Bash, Agent, Skill | Harness setup, deploy |

---

## Security Model

1. **Permission layer** (`.claude/settings.json`) — deny rules block rm -rf, DROP TABLE, git push --force, del, rmdir, Remove-Item
2. **Behavioral layer** (`CLAUDE.md`) — destructive-op confirmation, secret scan before commit
3. **Enforcement layer** (scripts) — `security_scan.py` + `guard.test.js` (29/29)

---

## Customization

### For a new project
1. Copy harness files to project root
2. Customize `.claude/CLAUDE.md` with tech stack and conventions
3. Update `.claude/memory/project-conventions.md`
4. Adjust `.claude/settings.json` permissions

### Adding a new skill
Create `.claude/skills/<name>.md`:

```yaml
---
name: my-skill
description: "When to use this skill. Use when: keyword1, keyword2."
allowed-tools: "Read, Grep, Bash"
---

# Skill content
```

### Verification
```bash
make check              # Full gate
python tools/garden.py  # Drift detection
```
