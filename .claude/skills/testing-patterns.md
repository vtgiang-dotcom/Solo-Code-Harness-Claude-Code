---
name: test
description: "Write tests, improve coverage, apply TDD. Use when adding features or fixing bugs."
license: MIT
allowed-tools: "Read, Write, Edit, Bash, Grep"
---

# Testing Patterns

## TDD Philosophy

1. **Write failing test FIRST** → 2. Implement minimal code to pass → 3. Refactor after green
2. Never write production code without a failing test

## Behavior-Driven Testing

- Test behavior, not implementation details
- Focus on public APIs and business requirements
- Use descriptive test names: `should [behavior] when [condition]`

## Factory Pattern (DRY Test Data)

Create reusable factory functions with sensible defaults:

```
function getMockX(overrides?: Partial<X>): X {
  return { /* sensible defaults */ ...overrides };
}
```

- Override only what differs per test
- Keeps tests DRY and maintainable
- Avoid duplicating test data across test cases

## Test Structure (AAA Pattern)

```
describe('Component/Module', () => {
  it('should [expected behavior] when [condition]', () => {
    // Arrange — set up test data and mocks
    // Act — call the function under test
    // Assert — verify the result
  })
})
```

## Test Cases to Cover

- **Happy path** — Normal usage with valid inputs
- **Error cases** — Invalid inputs, missing data, failures
- **Edge cases** — Empty, null, zero, negative, max values
- **Boundary conditions** — At limits, just above, just below

## Mocking Principles

- Mock external dependencies (APIs, databases, file system)
- Don't mock the code under test — mock its collaborators
- Use factory functions for mock data, not inline objects

## Anti-Patterns

- Testing mocks instead of real behavior
- Not using factory functions → duplicated test data
- Testing implementation details instead of behavior
- Multiple logical assertions in one test
- Fixing a bug without adding a regression test
