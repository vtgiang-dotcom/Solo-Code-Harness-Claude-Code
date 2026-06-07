---
allowed-tools: Bash(python .github/scripts/security_scan.py:*), Bash(git diff:*), Bash(git log:*), Read, Grep
description: Run a full security review of the codebase or current diff
---

## Context

- Current branch: !`git branch --show-current`
- Recent commits (last 5): !`git log --oneline -5`
- Uncommitted changes: !`git diff --stat HEAD`

## Task

Run a comprehensive security review in this order:

### 1. Secret Scan
```bash
python .github/scripts/security_scan.py . --strict
```

### 2. Git Diff Review
Review the current diff for:
- Hardcoded credentials (API keys, tokens, passwords)
- Unsafe patterns (eval, exec, os.system, shell=True)
- XSS risks (innerHTML, dangerouslySetInnerHTML)
- Unvalidated user input in SQL queries
- Missing input validation on API endpoints

### 3. Sensitive Files Check
Verify no sensitive files are staged:
```bash
git diff --cached --name-only | grep -E '(\.env|\.pem|\.key|credentials|secret|\.token)'
```

### 4. Report
Summarize findings in this format:
```
SECURITY REVIEW REPORT
======================
Branch: <branch>
Files reviewed: <count>
Secrets found: <count>
Unsafe patterns: <count>
Sensitive files staged: <count>

Findings:
[Detailed list with file paths and line numbers]

Verdict: PASS / NEEDS FIXES
```

If any secrets are found, **BLOCK** the commit until resolved.
