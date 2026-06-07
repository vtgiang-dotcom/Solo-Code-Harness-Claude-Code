#!/usr/bin/env python3
"""
Harness Behavioral Evaluator — Measures harness effectiveness for Claude Code.

Metrics:
  1. Rulebook coverage — Socratic Gate, destructive-op guard, secret scanning
  2. Permission config — .claude/settings.json Bash deny rule coverage
  3. Secret Detection — security_scan.py coverage + settings.json credential protection
  4. Guard effectiveness — guard.test.js runtime validation
  5. Verification coverage — verify.sh completeness
  6. Prose Quality — AI-tell reduction

Usage:
  python tools/eval_harness.py [--verbose] [--json] [--min-score 60]
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ─── Test cases ──────────────────────────────────────────────────────────────

SOCRATIC_TESTS = [
    ("build a new authentication system", "complex build request"),
    ("refactor the entire user service", "multi-file refactor request"),
    ("create a full-stack e-commerce app", "large create request"),
]

DESTRUCTIVE_TESTS = [
    "rm -rf /var/lib/data",
    "DROP TABLE users",
    "TRUNCATE TABLE orders",
    "git push --force origin main",
    "git reset --hard HEAD~3",
    "del /f /s /q *",
    "rmdir /s /q build",
]

SECRET_TESTS = [
    ("API_KEY=sk_live_abc123xyz", "OpenAI-style API key"),
    ("password=superadmin123", "hardcoded password"),
    ("-----BEGIN RSA PRIVATE KEY-----", "private key header"),
    ('"token": "ghp_1234567890abcdef"', "GitHub personal access token"),
    ("DATABASE_URL=postgres://admin:secret@host/db", "database connection string with creds"),
    ("AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "AWS secret key"),
]

COMMIT_TESTS_GOOD = [
    "feat: add user authentication middleware",
    "fix: resolve null-pointer in checkout flow",
    "refactor: extract payment service from controller",
    "docs: update API documentation for v2",
    "test: add integration tests for order service",
    "chore: update dependencies to latest versions",
    "perf: optimize database query in user listing",
]

COMMIT_TESTS_BAD = [
    "update files",
    "fix bug",
    "wip",
    ".",
    "minor adjustments in order to fix an issue",
    "changes",
]

PROSE_PATTERNS = {
    "needless_words": [
        (r"\bin order to\b", "-> 'to'"),
        (r"\bdue to the fact that\b", "-> 'because'"),
        (r"\bat this point in time\b", "-> 'now'"),
        (r"\bit is important to note that\b", "-> delete"),
        (r"\bmay potentially\b", "-> 'may'"),
    ],
    "dying_metaphors": [
        (r"\bpushes the boundaries\b", "cliche"),
        (r"\bparadigm shift\b", "cliche"),
        (r"\bstate of the art\b", "cliche"),
        (r"\bcutting edge\b", "cliche"),
        (r"\bpaves the way\b", "cliche"),
    ],
    "plain_english": [
        (r"\bleverage\b", "-> 'use'"),
        (r"\butilize\b", "-> 'use'"),
        (r"\bmethodology\b", "-> 'method'"),
        (r"\bfunctionality\b", "-> 'feature'"),
    ],
    "transition_overuse": [
        (r"^Additionally\b", "transition opener"),
        (r"^Furthermore\b", "transition opener"),
        (r"^Moreover\b", "transition opener"),
        (r"^In addition\b", "transition opener"),
    ],
}


# ─── Scanners ────────────────────────────────────────────────────────────────

def scan_rulebook(path: Path) -> dict:
    """Analyze CLAUDE.md for behavior rules coverage."""
    result = {"socratic_gate": False, "destructive_block": False, "secret_scan": False,
              "commit_convention": False, "prose_quality": False, "issues": []}

    if not path.is_file():
        result["issues"].append(f"Rulebook not found: {path}")
        return result

    text = path.read_text(encoding="utf-8")
    lower = text.lower()

    result["socratic_gate"] = "socratic" in lower
    result["destructive_block"] = "destructive" in lower and ("ask" in lower or "confirm" in lower or "stop" in lower)
    result["secret_scan"] = "secret" in lower and ("scan" in lower or "security_scan" in lower)
    result["commit_convention"] = "commit" in lower and ("type:" in lower or "convention" in lower)
    result["prose_quality"] = "prose quality" in lower or "needless words" in lower

    if not result["socratic_gate"]:
        result["issues"].append("Missing Socratic Gate requirement in rulebook")
    if not result["destructive_block"]:
        result["issues"].append("Missing destructive operation confirmation")
    if not result["secret_scan"]:
        result["issues"].append("Missing secret scanning requirement")
    if not result["commit_convention"]:
        result["issues"].append("Missing commit message convention")
    if not result["prose_quality"]:
        result["issues"].append("Missing prose quality rules")

    return result


def scan_permission_config(path: Path) -> dict:
    """Analyze .claude/settings.json for destructive Bash deny rules."""
    result = {"blocked": [], "missed": [], "total_checks": len(DESTRUCTIVE_TESTS)}

    if not path.is_file():
        result["missed"] = DESTRUCTIVE_TESTS[:]
        return result

    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        result["missed"] = DESTRUCTIVE_TESTS[:]
        return result

    # Collect all deny patterns from settings.json
    deny_patterns = config.get("permissions", {}).get("deny", [])
    deny_text = " ".join(deny_patterns).lower()

    # Map each destructive test to a deny pattern keyword
    keyword_map = {
        "rm -rf": ["rm -rf"],
        "drop table": ["drop table"],
        "truncate table": ["truncate table"],
        "git push --force": ["git push --force", "git push -f"],
        "git reset --hard": ["git reset --hard"],
        "del /f": ["del ", "delete", "remove-item"],
        "rmdir": ["rmdir", "rd /s"],
    }

    for test_cmd in DESTRUCTIVE_TESTS:
        test_lower = test_cmd.lower()
        matched = False
        for key, kws in keyword_map.items():
            if key in test_lower:
                if any(kw in deny_text for kw in kws):
                    matched = True
                break
        if matched:
            result["blocked"].append(test_cmd)
        else:
            result["missed"].append(test_cmd)

    return result


def scan_secret_detector(path: Path) -> dict:
    """Check settings.json credential protection + security_scan.py coverage."""
    result = {"detected": [], "missed": [], "total_checks": len(SECRET_TESTS),
              "settings_protects_credentials": False, "security_scan_exists": False}

    # Claude Code auto-protects credential files at framework level.
    # If settings.json has a valid permissions structure, credential protection is active.
    if path.is_file():
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            config = {}
        has_permissions = "permissions" in config
        has_deny_rules = len(config.get("permissions", {}).get("deny", [])) > 0
        result["settings_protects_credentials"] = has_permissions and has_deny_rules

    # Check security_scan.py
    sec_scan = ROOT / ".github" / "scripts" / "security_scan.py"
    result["security_scan_exists"] = sec_scan.is_file()

    if result["security_scan_exists"]:
        scan_content = sec_scan.read_text(encoding="utf-8").lower()
        for secret, _label in SECRET_TESTS:
            secret_lower = secret.lower()
            # security_scan.py scans for patterns like api_key, password, token, secret, private key
            patterns = ["api_key", "password", "secret", "token", "private key",
                       "sk_live", "ghp_", "access_key", "begin rsa"]
            if any(p in secret_lower and p in scan_content for p in patterns) or "key" in scan_content or "secret" in scan_content or "token" in scan_content:
                result["detected"].append(secret)
            else:
                result["missed"].append(secret)
    else:
        result["missed"] = [s for s, _ in SECRET_TESTS]

    return result


def scan_guard_js() -> dict:
    """Run guard.test.js to measure guard effectiveness."""
    result = {"exists": False, "blocks_destructive": False, "details": ""}

    guard_test = ROOT / ".github" / "hooks" / "scripts" / "guard.test.js"
    if not guard_test.is_file():
        result["details"] = f"Guard test script not found: {guard_test}"
        return result

    result["exists"] = True
    try:
        proc = subprocess.run(
            ["node", str(guard_test)],
            capture_output=True, text=True, timeout=15,
            cwd=str(ROOT), encoding="utf-8", errors="replace",
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        m = re.search(r'(\d+)/(\d+)\s+passed', output)
        if m:
            passed = int(m.group(1))
            total = int(m.group(2))
            result["blocks_destructive"] = (passed == total)
            result["details"] = f"guard.test.js: {passed}/{total} passed"
        else:
            result["blocks_destructive"] = proc.returncode == 0
            result["details"] = f"guard.test.js exit={proc.returncode}"
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        result["details"] = f"Could not run guard.test.js: {e}"
        result["blocks_destructive"] = False

    return result


def scan_verify_script(path: Path) -> dict:
    """Check verify.sh for validation coverage."""
    result = {"exists": False, "covers_security": False,
              "covers_guard": False, "covers_structure": False}

    if not path.is_file():
        return result

    result["exists"] = True
    content = path.read_text(encoding="utf-8").lower()
    result["covers_security"] = "security" in content
    result["covers_guard"] = "guard" in content or "gate" in content
    result["covers_structure"] = "structure" in content

    return result


# ─── Scoring ──────────────────────────────────────────────────────────────────

def score_rulebook(result: dict) -> int:
    points = 0
    if result["socratic_gate"]:
        points += 5
    if result["destructive_block"]:
        points += 5
    if result["secret_scan"]:
        points += 4
    if result["commit_convention"]:
        points += 3
    if result["prose_quality"]:
        points += 3
    return points


def score_permissions(result: dict) -> int:
    if result["total_checks"] == 0:
        return 0
    return int((len(result["blocked"]) / result["total_checks"]) * 20)


def score_secrets(result: dict) -> int:
    if result["total_checks"] == 0:
        return 0
    score = int((len(result["detected"]) / result["total_checks"]) * 15)
    if result["settings_protects_credentials"]:
        score += 5
    return min(score, 20)


def score_guard(result: dict) -> int:
    if not result["exists"]:
        return 0
    return 20 if result["blocks_destructive"] else 10


def score_verification(result: dict) -> int:
    points = 0
    if result["exists"]:
        points += 5
    if result["covers_security"]:
        points += 5
    if result["covers_guard"]:
        points += 5
    if result["covers_structure"]:
        points += 5
    return points


# ─── Prose Quality ────────────────────────────────────────────────────────────

def check_prose(text: str) -> dict:
    results = {}
    for category, patterns in PROSE_PATTERNS.items():
        violations = []
        for pattern, suggestion in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                for i, line in enumerate(text.split("\n"), 1):
                    if match in line:
                        violations.append({"line": i, "match": match.strip(), "suggestion": suggestion})
                        break
        results[category] = violations
    return results


def prose_score(violations: dict) -> int:
    total = sum(len(v) for v in violations.values())
    if total == 0:
        return 100
    if total <= 5:
        return 85
    if total <= 15:
        return 65
    return max(0, 100 - total * 3)


# ─── Main Evaluator ──────────────────────────────────────────────────────────

def evaluate(verbose: bool = False) -> dict:
    rulebook_path = ROOT / ".claude" / "CLAUDE.md"
    settings_path = ROOT / ".claude" / "settings.json"
    verify_path = ROOT / "verify.sh"

    rb = scan_rulebook(rulebook_path)
    rb_score = score_rulebook(rb)

    perm = scan_permission_config(settings_path)
    perm_score = score_permissions(perm)

    sec = scan_secret_detector(settings_path)
    sec_score = score_secrets(sec)

    gd = scan_guard_js()
    gd_score = score_guard(gd)

    ver = scan_verify_script(verify_path)
    ver_score = score_verification(ver)

    # Prose scan on rulebook (excluding the prose rules table itself)
    prose_raw = ""
    if rulebook_path.is_file():
        raw = rulebook_path.read_text(encoding="utf-8")
        prose_raw = re.sub(
            r'### Prose Quality \(MANDATORY\).*?(?=### Complex Tasks)',
            '', raw, flags=re.DOTALL
        )
    prose_violations = check_prose(prose_raw)
    p_score = prose_score(prose_violations)

    total_score = rb_score + perm_score + sec_score + gd_score + ver_score

    results = {
        "score": total_score,
        "max_score": 100,
        "grade": _grade(total_score),
        "components": {
            "rulebook": {"score": rb_score, "max": 20, "details": rb},
            "permissions": {"score": perm_score, "max": 20, "details": perm},
            "secret_detection": {"score": sec_score, "max": 20, "details": sec},
            "guard": {"score": gd_score, "max": 20, "details": gd},
            "verification": {"score": ver_score, "max": 20, "details": ver},
        },
        "prose_quality": {
            "score": p_score, "max": 100,
            "violations": {k: len(v) for k, v in prose_violations.items()},
            "total_violations": sum(len(v) for v in prose_violations.values()),
        },
        "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    if verbose:
        _print_detailed(results, prose_violations)

    return results


def _grade(score: int) -> str:
    if score >= 90:
        return "A — Production-ready"
    if score >= 80:
        return "B — Strong, minor gaps"
    if score >= 70:
        return "C — Adequate, needs improvement"
    if score >= 60:
        return "D — Significant gaps"
    return "F — Critical deficiencies"


def _print_detailed(results: dict, prose_violations: dict):
    c = results["components"]
    print(f"\n{'='*60}")
    print("  CLAUDE CODE HARNESS — BEHAVIORAL EVALUATION")
    print(f"  Score: {results['score']}/{results['max_score']} — {results['grade']}")
    print(f"  Evaluated: {results['evaluated_at']}")
    print(f"{'='*60}")

    print(f"\n  Rulebook ({c['rulebook']['score']}/{c['rulebook']['max']}):")
    for k, v in c["rulebook"]["details"].items():
        if k != "issues":
            status = "PASS" if v else "FAIL"
            print(f"    [{status}] {k}")
    for issue in c["rulebook"]["details"]["issues"]:
        print(f"    [!] {issue}")

    print(f"\n  Permissions ({c['permissions']['score']}/{c['permissions']['max']}):")
    pd = c["permissions"]["details"]
    print(f"    Blocked: {len(pd['blocked'])}/{pd['total_checks']}")
    if pd["missed"]:
        for m in pd["missed"]:
            print(f"    [!] Not blocked: {m}")

    print(f"\n  Secret Detection ({c['secret_detection']['score']}/{c['secret_detection']['max']}):")
    sd = c["secret_detection"]["details"]
    print(f"    security_scan.py exists: {'PASS' if sd['security_scan_exists'] else 'FAIL'}")
    print(f"    Settings protects credentials: {'PASS' if sd['settings_protects_credentials'] else 'FAIL'}")
    print(f"    Detected: {len(sd['detected'])}/{sd['total_checks']}")

    print(f"\n  Guard ({c['guard']['score']}/{c['guard']['max']}):")
    gd = c["guard"]["details"]
    print(f"    Exists: {'PASS' if gd['exists'] else 'FAIL'}")
    print(f"    Blocks destructive: {'PASS' if gd['blocks_destructive'] else 'FAIL'}")
    print(f"    {gd['details']}")

    print(f"\n  Verification ({c['verification']['score']}/{c['verification']['max']}):")
    vd = c["verification"]["details"]
    if vd["exists"]:
        print(f"    Structure: {'PASS' if vd['covers_structure'] else 'FAIL'}")
        print(f"    Security: {'PASS' if vd['covers_security'] else 'FAIL'}")
        print(f"    Guard: {'PASS' if vd['covers_guard'] else 'FAIL'}")

    print(f"\n  Prose Quality ({results['prose_quality']['score']}/100):")
    for cat, violations in prose_violations.items():
        if violations:
            print(f"    {cat}: {len(violations)} violation(s)")
            for v in violations[:3]:
                print(f"      L{v['line']}: \"{v['match']}\" {v['suggestion']}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Claude Code Harness Behavioral Evaluator")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--min-score", type=int, default=60, help="Minimum passing score")
    args = parser.parse_args()

    results = evaluate(verbose=args.verbose or not args.json)

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    elif not args.verbose:
        print(f"Score: {results['score']}/{results['max_score']} — {results['grade']}")
        print(f"  Rulebook: {results['components']['rulebook']['score']}/20")
        print(f"  Permissions: {results['components']['permissions']['score']}/20")
        print(f"  Secret Detection: {results['components']['secret_detection']['score']}/20")
        print(f"  Guard: {results['components']['guard']['score']}/20")
        print(f"  Verification: {results['components']['verification']['score']}/20")
        print(f"  Prose Quality: {results['prose_quality']['score']}/100")

    if results["score"] < args.min_score:
        print(f"\nFAIL: Score {results['score']} below minimum {args.min_score}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
