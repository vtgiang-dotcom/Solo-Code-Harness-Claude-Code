---
name: block-no-verify
description: "Block commits that skip pre-commit hooks (--no-verify, -n). Auto-triggers on: git commit --no-verify, git commit -n, git push --no-verify, git am --no-verify. Use whenever git operations with bypass flags are detected. Enforces security scan + lint + tests before every commit."
license: MIT
allowed-tools: "Bash, Read"
---

# Block No-Verify

Prevent `git commit --no-verify` which bypasses security scanning, lint, and pre-commit hooks.

## Detection Patterns

Block any of these patterns:
- `git commit --no-verify`
- `git commit -n`
- `git push --no-verify`
- `git am --no-verify`

## Response

When detected, respond with:

```
BLOCKED: git commit with --no-verify detected.

Pre-commit hooks exist for a reason — they run:
  - Secret scanning (python .github/scripts/security_scan.py .)
  - Linting (ruff check .)
  - Guard tests (node .github/hooks/scripts/guard.test.js)

Run without --no-verify to pass all gates, OR
explain why you need to bypass (e.g., emergency hotfix with documented reason).

If you have a valid reason, run:
  git commit -m "message" --no-verify
  (will be logged for audit)
```

## Governance

If bypass is accepted, document the reason and approval in the commit message body:
- Date and time
- Reason for bypass
- Files changed
- Who approved
