---
name: harness-design-intent
description: Why this harness exists — compensating for DeepSeek weaknesses in Claude Code
metadata:
  type: project
---

# Design Intent — DO NOT REMOVE

This harness is built **specifically to optimize Claude Code for DeepSeek.** It is NOT a general-purpose Claude Code harness.

## Why

DeepSeek v4-pro is ~5-10x cheaper than Claude Opus but weaker at:
- Instruction-following
- Hallucination resistance (invents APIs, libraries, params)
- Code consistency (different patterns on every call)
- AI-tell prose ("leverage", "paradigm shift", 40-word sentences)

## How

Every rule, skill, and gate compensates for a specific DeepSeek weakness observed in real usage:
- **CLAUDE.md: 251 lines** — intentional, not bloat
- **Anti-hallucination rules (A1-A5)** — DeepSeek hallucinates more
- **Prose quality rules (8-15)** — DeepSeek produces more AI-tell patterns
- **10 skills with protocols** — step-by-step, not generic advice
- **7 verification gates** — catch errors a cheaper model makes more often
- **Smart launcher** — routes complex tasks to pro, simple to flash

## Critical Constraint

**DO NOT shorten rules to "optimize."** Cheaper models need longer, more explicit rules. If you remove a rule without understanding which DeepSeek failure mode it prevents, you reintroduce that failure mode.

**Why:** Each rule exists because DeepSeek made that specific mistake before. Removing it means waiting for the mistake to happen again.

**How to apply:** Before modifying any rule, skill, or gate, ask: "Which DeepSeek failure mode does this prevent?" If you cannot answer, do not modify it. Run `python .github/scripts/checklist.py .` after any change — all 7 gates must stay green.
