# Solo-Code Harness — Makefile
# ==============================
# All tooling runs through `python`. No external dependencies needed.

PY := python

.PHONY: help generate garden test test-integration check deploy

help:
	@echo "Solo-Code Harness — Claude Code Quality Gates"
	@echo "============================================="
	@echo ""
	@echo "  make garden             Drift detection (structure, skills, rulebook)"
	@echo "  make test               Run harness test suite"
	@echo "  make test-integration   Run integration tests"
	@echo "  make check              Full gate: ruff + garden + test + integration"
	@echo "  make deploy TARGET=..   Deploy harness to another project"
	@echo "  make cost               Estimate session costs from usage.log"
	@echo ""
	@echo "Security:"
	@echo "  make security-scan      Scan for hardcoded secrets"
	@echo "  make gitleaks           Scan with gitleaks"

garden:
	$(PY) tools/garden.py

test:
	$(PY) -m pytest tools/test_harness.py -v

test-integration:
	$(PY) tools/test_integration.py

check:
	@echo "=== Lint (ruff) ==="
	ruff check . || exit 1
	@echo ""
	@echo "=== Garden ==="
	$(PY) tools/garden.py || exit 1
	@echo ""
	@echo "=== Harness Tests ==="
	$(PY) -m pytest tools/test_harness.py -q || exit 1
	@echo ""
	@echo "=== Integration Tests ==="
	$(PY) tools/test_integration.py || exit 1
	@echo ""
	@echo "  All gates passed."

security-scan:
	$(PY) .github/scripts/security_scan.py .

gitleaks:
	gitleaks dir . --no-banner -c .gitleaks.toml

deploy:
	$(PY) tools/deploy.py $(TARGET)

cost:
	$(PY) tools/cost.py $(ARGS)
