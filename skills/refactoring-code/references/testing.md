# Testing: Safety Nets and Test Impact

Tests are the operational definition of "behavior preserved" — without them, that claim is an opinion. Read this before refactoring untested code, when a test blocks a refactoring, and when writing the Testing Impact section of a report.

## The rules

1. **Never remove or weaken a test to make a refactoring pass.** A red test after a structural change means the change wasn't behavior-preserving — the test just did its job. Revert the step, don't adjust the assertion.
2. **The exception that needs a conversation:** tests welded to internals (asserting private state, mock-call choreography, exact internal call order) legitimately break under pure structural change. Don't delete these quietly. Surface it: propose a behavior-level replacement test, get agreement, add the replacement *first*, then retire the internal-coupled test. Net coverage of behavior must never decrease.
3. **Mechanical test updates are expected and fine:** renames, moved imports, changed constructor signatures flowing into test setup. The distinction is *what the test asserts* — assertions are behavior; setup and names are structure.
4. **Green before, green after, every step.** If the suite is red before you start, stop and report — you cannot detect your own breakage on a red baseline.

## Building a safety net for untested code

When the code in scope has no meaningful coverage, build the net before restructuring (this is the workflow's step-4 risk mitigation):

**Characterization tests** — tests that pin down what the code *does* (not what it should do):

1. Identify the unit's observable outputs: return values, state changes, calls to collaborators, thrown errors, emitted events.
2. Write a test invoking the code with a representative input; assert something trivially false; run it; copy the *actual* value into the assertion. The current behavior — bugs included — is the spec. If output looks like a bug, add a comment and report it; don't fix it (fixing is a behavior change to propose separately).
3. Cover the input classes that hit different code paths: typical cases, each branch of major conditionals, boundary values, error paths. Coverage tooling shows what the characterization suite still misses.
4. For code with complex output (reports, rendered documents, serialized structures), use **golden-master/snapshot testing**: capture entire outputs for a battery of inputs, diff against them after every step. Crude but extremely effective for legacy refactoring; retire in favor of focused tests once the structure improves.

**Finding a seam** — untestable code (hard-wired DB/network/clock/randomness) needs a minimal seam first. Bootstrap carefully: apply only the lowest-risk, compiler-verifiable transformations needed to inject or intercept the dependency (extract-and-parameterize, constructor default that preserves old wiring), then write tests, then do the real refactoring. Keep the bootstrap steps microscopic — you're refactoring without a net for exactly those steps.

**If no net can be built** (no test infra, no time, hostile environment): say so explicitly in the report; restrict yourself to tool-assisted and type-checker-verifiable transformations; downgrade the engagement's ambition rather than gamble.

## Recommending tests

When coverage is missing, generate concrete recommendations (or the tests themselves if asked) — never generic advice. Every recommendation names the unit, the scenario, and the assertion.

**Unit tests** — for each nontrivial unit in scope: one test per behavior (not per method), named for the behavior (`applies_bulk_discount_over_100_units`). Prioritize: business rules and calculations, branching logic, anything you're about to restructure.

**Integration tests** — where units meet the things fakes lie about: real queries against a real (test) database, actual HTTP contract shapes, serialization round-trips, transaction boundaries. Prioritize the paths your refactoring crosses — moving data access behind a Repository deserves an integration test proving the queries still return the same shapes.

**Edge cases** — derive systematically rather than brainstorming: empty/null/absent for every input; boundaries of every explicit limit (at, one-below, one-above); duplicates and already-processed inputs (idempotency); unicode/whitespace/very-long strings; zero/negative/overflow numbers; concurrent access where state is shared; each declared error path actually erroring.

**Regression tests** — pin anything that has bitten before or will: every bug found during the engagement (report → test reproducing it → then it may be fixed with approval); quirks discovered during Phase A that callers depend on (pin them so the *next* refactorer doesn't "fix" them); characterization tests promoted into named, documented behavior tests.

## Testing Impact section of the report

State, concretely:

```markdown
## Testing Impact
- Coverage before: <what was pinned — suites, roughly what they cover, gaps relevant to this change>
- Safety net added: <characterization/golden-master tests written, what they pin>
- Tests updated mechanically: <renames/setup changes, with confirmation no assertions changed>
- Tests flagged: <internal-coupled tests needing replacement, with proposed behavior-level substitutes>
- Recommended (not yet written): <prioritized list — unit / integration / edge / regression, each naming unit + scenario + assertion>
- Verification run: <suites run at final state and their results>
```

A refactoring engagement should leave the code *easier* to test than it found it — count the newly-testable units (post-DI, post-extraction) as part of the value delivered, and say so in the report.
