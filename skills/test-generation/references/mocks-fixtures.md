# Mocks, Fixtures, and Test Data Patterns

## When to Mock

Mock only when you have a concrete isolation need. Before reaching for a mock, ask: "Can I use the real thing?" If the answer is yes, use the real thing.

**Justified mock reasons** (each mock in generated tests must cite one):

| Reason | Example |
|--------|---------|
| **Non-deterministic** | System clock, random number generator, UUIDs |
| **Slow** | Network calls, disk I/O in unit tests |
| **Expensive** | Third-party API with rate limits or costs |
| **Hard-to-trigger errors** | Network timeout, disk full, connection refused |
| **External trust boundary** | Code you don't own and shouldn't verify |
| **Unavailable in CI** | Database that doesn't exist in test environment |

**Not valid reasons to mock**:
- "It's best practice" — mocking without a reason tests your mocks
- "It's simpler" — simplicity that hides bugs is a liability
- "I can't be bothered to set up the real dependency" — set it up
- "It makes the test faster" — only valid if measurably slow

## Over-Mocking: The #1 Test-Generation Failure Mode

Over-mocking is when you mock so much that your test verifies the mock setup, not the code. Signs:

1. **More mock setup than assertions** — the test is a mock specification, not a behavior test
2. **Testing that method X calls method Y** — implementation coupling; any refactor breaks the test
3. **Mock returning mock returning mock** — you've lost contact with reality
4. **Every dependency is mocked** — you're testing in a vacuum; integration bugs go undetected

**Recovery**: Replace mocks with real implementations from the bottom up. Start with data layers (in-memory database), then services. Keep mocks only at the edges (HTTP clients, message queues, external APIs).

## Test Doubles Taxonomy

Use the right type of test double for the situation:

| Type | What it does | When to use |
|------|-------------|-------------|
| **Stub** | Returns canned responses | Need to supply indirect input (e.g., config values) |
| **Mock** | Verifies interactions | Need to verify side effects (e.g., email was sent) |
| **Fake** | Working implementation (simplified) | Need realistic behavior without infrastructure (e.g., in-memory DB) |
| **Spy** | Records calls for later assertion | Need to verify calls without changing behavior |
| **Dummy** | Satisfies parameter requirements | Need to fill a required parameter that isn't used |

**Prefer fakes over mocks** for data stores. An in-memory implementation of your repository interface exercises the real query logic; a mock just returns what you told it to.

## Fixture Patterns

### Test Data Builders

Builders create test objects with sensible defaults and chainable overrides:

```typescript
// Builder with sensible defaults — override only what matters for each test
const userBuilder = () => ({
  id: 'user-1',
  name: 'Test User',
  email: 'test@example.com',
  role: 'member',
  createdAt: new Date('2024-01-01'),
  // Override specific fields
  with: (overrides) => ({ ...userBuilder(), ...overrides }),
});

// Usage: only the relevant field is explicit
const admin = userBuilder().with({ role: 'admin' });
const newUser = userBuilder().with({ createdAt: new Date('2024-06-01') });
```

```python
# Python equivalent using dataclass + factory
@dataclass
class UserFactory:
    id: str = "user-1"
    name: str = "Test User"
    email: str = "test@example.com"
    role: str = "member"

    def build(self, **overrides):
        return replace(self, **overrides)

# Usage
admin = UserFactory().build(role="admin")
```

### Shared Fixtures vs. Per-Test Setup

**Shared fixtures** (e.g., pytest fixtures, beforeEach/beforeAll):
- Use for expensive, read-only setup (database schema, server startup)
- Never for mutable state — each test must get a clean copy

**Per-test setup** (inline in test body):
- Use for test-specific data that makes the test's intent clear
- Prefer this for simple setup — locality beats DRY in tests

### Database Test Fixtures

- **Transaction rollback**: Wrap each test in a transaction, rollback after — fastest isolation
- **Truncate + seed**: Clear tables and insert known data — works when transactions don't (multi-connection tests)
- **Containerized database**: Spin up a real database per test suite (TestContainers, pg_tmp) — most realistic

## Anti-Patterns

### Brittle assertion ordering

```typescript
// BAD: Breaks if implementation changes sort order
expect(result).toEqual(['apple', 'banana', 'cherry']);

// GOOD: When order doesn't matter
expect(result).toEqual(expect.arrayContaining(['apple', 'banana', 'cherry']));
expect(result).toHaveLength(3);
```

### Testing internal state

```typescript
// BAD: Reaches into private state
expect(service._cache.size).toBe(3);

// GOOD: Test observable behavior
expect(service.get('key')).toBe('cached-value');
```

### Excessive setup for trivial assertions

If your test needs 30 lines of setup for a 1-line assertion, either:
1. The code under test does too much (refactoring opportunity)
2. You're testing at the wrong level (go higher: integration; or lower: unit)
3. You need a builder/fixture to hide the ceremony
