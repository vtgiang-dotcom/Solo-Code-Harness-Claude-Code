#!/usr/bin/env python3
"""
DeepSeek cost estimator for Claude Code sessions.

Reads .claude/usage.log and estimates cost per session.
Token counts are estimates based on typical Claude Code usage rates —
for exact counts, use `/status` inside Claude Code.

DeepSeek pricing (June 2026):
  pro:   $0.435/M input (cache miss) / $0.003625/M input (cache hit) / $0.87/M output
  flash: $0.14/M  input (cache miss) / $0.0028/M   input (cache hit) / $0.28/M output

Usage:
    python tools/cost.py                 # Show last 10 sessions
    python tools/cost.py --all           # Show all sessions
    python tools/cost.py --summary       # Summary only
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / ".claude" / "usage.log"

# DeepSeek pricing per 1M tokens
PRICING = {
    "deepseek-v4-pro[1m]":    {"input": 0.435, "cache": 0.003625, "output": 0.87},
    "deepseek-v4-flash[1m]":  {"input": 0.14,  "cache": 0.0028,   "output": 0.28},
    # Legacy names (without [1m] suffix)
    "deepseek-v4-pro":        {"input": 0.435, "cache": 0.003625, "output": 0.87},
    "deepseek-v4-flash":      {"input": 0.14,  "cache": 0.0028,   "output": 0.28},
}

# Rough token consumption rates for Claude Code (tokens per minute)
# Conservative estimates — actual usage varies by context size and task
# ~3K input/min (system prompt amortized + user), ~800 output/min
TOKENS_PER_MINUTE = {
    "input_estimate":  3000,
    "output_estimate": 800,
    "cache_hit_ratio": 0.7,    # ~70% hits cache (CLAUDE.md is stable)
}


def load_sessions() -> list[dict]:
    if not LOG_PATH.is_file():
        return []
    sessions = []
    for line in LOG_PATH.read_text(encoding="utf-8").strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            sessions.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return sessions


def estimate_cost(session: dict) -> dict | None:
    model = session.get("model", "")
    pricing = PRICING.get(model)
    if not pricing:
        return None

    duration_min = session.get("duration_min", 0)
    if duration_min <= 0:
        return None

    # Estimate tokens
    input_tokens = int(duration_min * TOKENS_PER_MINUTE["input_estimate"])
    output_tokens = int(duration_min * TOKENS_PER_MINUTE["output_estimate"])
    cache_ratio = TOKENS_PER_MINUTE["cache_hit_ratio"]

    cache_tokens = int(input_tokens * cache_ratio)
    miss_tokens = input_tokens - cache_tokens

    # Calculate cost
    cache_cost = (cache_tokens / 1_000_000) * pricing["cache"]
    miss_cost = (miss_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total = cache_cost + miss_cost + output_cost

    return {
        "model": model,
        "duration_min": duration_min,
        "input_tokens_est": input_tokens,
        "output_tokens_est": output_tokens,
        "cache_hit_est": cache_tokens,
        "cache_miss_est": miss_tokens,
        "cost_est": round(total, 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="DeepSeek cost estimator")
    parser.add_argument("--all", action="store_true", help="Show all sessions")
    parser.add_argument("--summary", action="store_true", help="Summary only")
    args = parser.parse_args()

    sessions = load_sessions()
    if not sessions:
        print("No sessions logged yet. Run .\\claudecode.ps1 first.")
        print("Tip: use /status inside Claude Code for exact token counts.")
        return 0

    limit = len(sessions) if args.all else 10
    recent = sessions[-limit:]

    total_cost = 0.0
    total_min = 0.0

    if not args.summary:
        print(f"{'Timestamp':<22} {'Model':<25} {'Dur':>6} {'Cost(est)':>10}")
        print("-" * 67)

    for s in recent:
        est = estimate_cost(s)
        if est:
            ts = s.get("timestamp", "?")[:19].replace("T", " ")
            print(
                f"{ts:<22} {est['model']:<25}"
                f" {est['duration_min']:>5.0f}m"
                f"  ${est['cost_est']:>8.4f}"
            )
            total_cost += est["cost_est"]
            total_min += est["duration_min"]

    print("-" * 67)

    if len(sessions) > limit and not args.all:
        remaining = len(sessions) - limit
        print(f"(+{remaining} more sessions. Use --all for full history)")
        print()

    print(f"  Total sessions shown: {len(recent)}")
    print(f"  Total duration:       {total_min:.0f} minutes")
    print(f"  Estimated total cost: ${total_cost:.4f}")
    print()
    p = PRICING["deepseek-v4-pro[1m]"]
    f = PRICING["deepseek-v4-flash[1m]"]
    print("  Note: Costs are ESTIMATES based on typical token rates.")
    print("  For exact counts: /status inside Claude Code.")
    print(f"  Pricing: pro ${p['input']}/M in, ${p['output']}/M out")
    print(f"           flash ${f['input']}/M in, ${f['output']}/M out")
    return 0


if __name__ == "__main__":
    sys.exit(main())
