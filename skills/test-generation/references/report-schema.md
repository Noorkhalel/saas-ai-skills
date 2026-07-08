# Test Generation Report Schema

This is the complete annotated template for the skill's output. Every activation must produce a report following this structure.

## Template

```markdown
# Test Generation Report

## Code Summary

Purpose, inputs/outputs, dependencies, side effects, error conditions, external services, state management — derived from Phase 1 analysis only. Never include information not evidenced in the analyzed code.

## Behaviors Identified

Numbered list of every observable behavior. Each behavior cites its source:

1. [Behavior description] — *Source: code (line N)* | *docs (section X)* | *existing tests (file:line)* | *user statement* | *ASSUMPTION: [reason]*

Behaviors without a traceable source must be labeled ASSUMPTION and surfaced in the Risks section.

## Test Plan

### Unit Tests
<!-- Include when unit-testable behaviors exist -->

| Behavior | Category | Rationale |
|----------|----------|-----------|
| [What is being tested] | happy-path / edge / boundary / ... | [Why this test matters] |

### Integration Tests
<!-- Include when code interacts with databases, APIs, external services -->

### End-to-End Tests
<!-- Include when full user flows are in scope -->

### Edge Cases
<!-- Include when boundary/edge behaviors are identified -->

### Boundary Tests
<!-- Include when threshold/limit behaviors exist -->

### Negative Tests
<!-- Include when invalid input / error handling behaviors exist -->

### Authentication Tests
<!-- Include when authn logic is present -->

### Authorization Tests
<!-- Include when authz / RBAC / permission logic is present -->

### Regression Tests
<!-- Include when known bug history exists -->

**Conditional section rules**: Omit a subsection entirely or mark it "Not applicable — [reason]" when the analyzed code has no behaviors in that category. Never fabricate tests for an inapplicable category.

## Generated Test Code

Complete, runnable test files with suggested file paths. Each file:
- Uses the detected framework's native patterns
- Names tests by behavior, not by method
- Follows Arrange-Act-Assert structure
- Contains no placeholder assertions or TODO comments
- Is syntactically valid and runnable given documented setup

## Fixtures
<!-- Conditional: Only when fixtures are generated -->
Shared test data, factories, or builders. Each describes its purpose.

## Mocks
<!-- Conditional: Only when mocks are generated -->
Each mock states the isolation need justifying it (see references/mocks-fixtures.md).

## Test Data
<!-- Conditional: Only when test data builders/datasets are generated -->
Data factories, seed data, or representative datasets.

## Coverage Estimate

Qualitative assessment of behavior coverage. This is explicitly NOT a line/branch coverage percentage from instrumentation. It states:
- What behaviors are covered by the generated tests
- What behaviors are NOT covered and why (out of scope, untestable, requires refactoring)
- Confidence level in the coverage assessment

## Untestable Areas
<!-- Conditional: Only when hard-to-test code is found -->
Each area identifies: what makes it untestable, the specific code pattern, and what tests become possible after refactoring.

## Refactoring Recommendations
<!-- Conditional: Only when untestable areas or design issues are found -->
Behavior-preserving suggestions only. Each recommendation:
- Names the current pattern and its testing obstacle
- Proposes a specific refactoring (extract interface, inject dependency, etc.)
- Describes what tests become possible after the change

## Risks

Always present. Includes:
- Every `ASSUMPTION:` made during generation (labeled clearly)
- Flakiness risks (if any patterns couldn't be fully eliminated)
- Environment dependencies (if tests need specific setup)
- Coverage gaps (what's not tested and why)

## Final Recommendations

Always present. Includes:
- Missing tests the user should add (beyond current scope)
- Validation gaps in the codebase
- Testing infrastructure recommendations
- Prioritized next steps
```

## Invariants

These five invariants must hold for every report:

1. **Traceability**: Every expected value in generated tests traces to a cited behavior source. Zero invented requirements.
2. **Determinism**: No generated test contains fixed sleeps, wall-clock/timezone dependence, test-order dependence, unseeded randomness, or live external-service calls.
3. **Runnability**: Generated test code is syntactically valid for its declared framework and runnable given documented setup.
4. **Independence**: Each test can run alone and in any order. No shared mutable state.
5. **Honest gaps**: Inapplicable sections are omitted or marked, never fabricated. Untestable code yields recommendations, not brittle tests.
