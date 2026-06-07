---
allowed-tools: Bash(python .github/scripts/security_scan.py:*), Bash(python .github/scripts/checklist.py:*), Bash(python tools/garden.py:*), Bash(python -m pytest:*), Bash(ruff check:*), Bash(python tools/eval_harness.py:*)
description: Run all 7 Solo-Code verification gates
---

## Context

- Current branch: !`git branch --show-current`
- Last commit: !`git log --oneline -1`

## Task

Run all 7 verification gates in order. Stop at the first failure.

### Gate 1: Security Scan
```bash
python .github/scripts/security_scan.py . --strict
```
Expected: exit 0, "No issues found."

### Gate 2: Lint
```bash
ruff check .
```
Expected: exit 0, no errors.

### Gate 3: Garden (Drift Detection)
```bash
python tools/garden.py
```
Expected: "0 errors, 0 warnings"

### Gate 4: Integration Tests
```bash
python tools/test_integration.py
```
Expected: all gates green.

### Gate 5: Harness Tests
```bash
python -m pytest tools/test_harness.py -q
```
Expected: all tests pass.

### Gate 6: Eval Score
```bash
python tools/eval_harness.py --min-score 60
```
Expected: score ≥ 60.

### Gate 7: No Debug Artifacts
```bash
grep -rE '(console\.log|console\.debug|print\(.*debug|pdb\.set_trace|debugger)' --include='*.py' --include='*.ts' --include='*.js' . | grep -v node_modules | grep -v '.venv' | grep -v '.git'
```
Expected: no output (no debug statements found).

## Report Format

```
SOLO-CODE GATE CHECK
====================
Branch: <branch>
Commit: <hash>

[✓] Gate 1: Security Scan   — PASS
[✓] Gate 2: Lint            — PASS
[✓] Gate 3: Garden          — PASS
[✓] Gate 4: Integration     — PASS
[✓] Gate 5: Harness Tests   — PASS
[✓] Gate 6: Eval Score      — PASS (<score>/100)
[✓] Gate 7: Debug Artifacts — PASS

VERDICT: ALL GATES PASSED / GATE <N> FAILED
```

If any gate fails, explain the failure and suggest fixes. Do NOT proceed with commit/push until all gates pass.
