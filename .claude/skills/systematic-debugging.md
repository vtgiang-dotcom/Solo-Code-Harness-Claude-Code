---
name: debug
description: "Systematic debugging — reproduce, isolate, identify root cause, test the fix. Use whenever the user reports a bug, error, crash, test failure, unexpected behavior, or anything 'not working'. Trigger on: bug, error, crash, fix, debug, broken, fails, stack trace, exception, investigate, why isn't, what's wrong. Apply before attempting ANY fix — no fixes without root cause first."
license: MIT
allowed-tools: "Read, Grep, Glob, Bash"
---

# Systematic Debugging

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

## Decision Tree: Which Phase Are You In?

```
User reports an issue →
├── Error message with stack trace?
│   ├── Yes → Phase 1: Read errors, reproduce, check recent changes
│   │         Then → Phase 2: Find working examples, compare
│   └── No → Gather more data: add logging, ask for exact steps
│
├── Can reproduce consistently?
│   ├── Yes → Phase 3: Form hypothesis, test minimally
│   │         Worked? → Phase 4: Create test, fix, verify
│   │         Failed? → New hypothesis (if <3 attempts: back to Phase 1)
│   │         Failed 3+ times? → Question the architecture
│   └── No → Phase 1: Add diagnostic logging at each boundary
│             Run once → which component fails? Trace data flow up
│
├── Working example exists in codebase?
│   ├── Yes → Phase 2: Compare against reference, list all differences
│   └── No → Search for similar patterns in adjacent code
│
└── Fix applied but new problems appear?
    └── STOP. Architectural issue. Don't keep patching.
```

## The Iron Law

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.** If you haven't completed Phase 1, you cannot propose fixes. Symptom fixes are failure.

---

## Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully** — Don't skip warnings. Note line numbers, file paths, stack traces.
2. **Reproduce Consistently** — Exact steps. Every time? If not → gather more data, don't guess.
3. **Check Recent Changes** — Git diff, commits, new dependencies, config changes, environment differences.
4. **Multi-Component Evidence Gathering** — When system has multiple components (API → service → DB), add diagnostic logging at EACH boundary. Log what data enters/exits each component. Run once to isolate WHERE it breaks.
5. **Trace Data Flow** — Where does the bad value originate? What called this with the bad value? Keep tracing up. Fix at source, not at symptom.

---

## Phase 2: Pattern Analysis

1. **Find Working Examples** — Locate similar working code in the same codebase.
2. **Compare Against References** — Read reference implementation completely, understand pattern before applying.
3. **Identify Differences** — What's different between working and broken? List every difference, don't assume it "can't matter."
4. **Understand Dependencies** — What components, settings, config, environment does this need?

---

## Phase 3: Hypothesis and Testing

1. **Form Single Hypothesis** — State clearly: "X is the root cause because Y." Be specific.
2. **Test Minimally** — SMALLEST possible change, one variable at a time.
3. **Verify Before Continuing** — Did it work? Yes → Phase 4. No → Form NEW hypothesis. Don't add more fixes.
4. **When You Don't Know** — Say "I don't understand X." Don't pretend. Ask for help.

---

## Phase 4: Implementation

1. **Create Failing Test Case** — Simplest reproduction. MUST have before fixing.
2. **Implement Single Fix** — ONE change at a time. No "while I'm here" improvements.
3. **Verify Fix** — Test passes? No other tests broken? Issue actually resolved?
4. **If Fix Doesn't Work** — Count attempts. If < 3: return to Phase 1. **If ≥ 3: STOP. Question the architecture.** Each fix revealing new problems in different places = architectural problem, not a bug.

---

## Red Flags — STOP and Return to Phase 1

If you catch yourself thinking any of these, you're guessing, not debugging:

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Skip the test, I'll manually verify"
- "Add multiple changes, run tests"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)
- Each fix reveals new problem in different place

**3+ failed fixes = Question the architecture, not the fix.**

---

## Quick Reference

| Phase             | Key Activities                                         | Success Criteria            |
| ----------------- | ------------------------------------------------------ | --------------------------- |
| 1. Root Cause     | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY     |
| 2. Pattern        | Find working examples, compare                         | Identify differences        |
| 3. Hypothesis     | Form theory, test minimally                            | Confirmed or new hypothesis |
| 4. Implementation | Create test, fix, verify                               | Bug resolved, tests pass    |
