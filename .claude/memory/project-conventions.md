---
type: project
created: 2026-05-29
updated: 2026-05-29
---

# Project Conventions

## Git Workflow
- Always create a new dedicated branch for major code changes.
- Branch name format: `feature/[task-slug]` or `fix/[bug-slug]`.
- Never force-push to `main`/`master`.

## Code Style
- Follow existing patterns in the codebase exactly.
- Prefer named exports over default exports.
- Comment WHY, not WHAT.
- No emojis in code or commit messages unless user requests.

## Security
- Never commit `.env` files, credentials, or API keys.
- Use environment variables for all secrets.
- Run `python .github/scripts/security_scan.py .` before deployment.

**Why:** Consistent conventions prevent drift and reduce cognitive load.
**How to apply:** Check these conventions at the start of every task. When in doubt, follow what the existing code does.
