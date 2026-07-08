# Testing Review Checklist (Phase 8)

Review the tests as seriously as the code — they're the spec, the safety net, and often where the real gaps hide. Two questions drive the phase: **what behavior in this code is unpinned by any test?** and **do the existing tests actually fail when the code breaks?**

## Missing tests

Map code → coverage by *behavior*, not by line metric:

- Every branch of business logic: does some test force each side of each meaningful conditional? (Coverage tools help but 100% line coverage with assertion-free tests is worth zero.)
- **Error paths:** the least-tested, most production-relevant code — what test exercises the catch block, the failed external call, the invalid input rejection, the transaction rollback?
- **Edge inputs** derived systematically (same grid as `bugs.md`): empty/null/absent, boundaries (at/below/above every limit), duplicates & idempotency (run it twice), zero/negative/huge numbers, unicode/whitespace/long strings, concurrent invocation where state is shared.
- **Security-relevant behavior as tests:** authz denials (the 403/404 paths), tenant isolation (user A requesting tenant B's resource — for SaaS code this test is as important as any feature test), validation rejections. If the review found security issues (Phase 4), each fix needs a pinning test — name it.
- For a PR: does the diff include tests *for the change*? New behavior without tests = the default regression risk finding; a bugfix without a test reproducing the bug will regress.

## Weak tests — the trust audit

Tests that pass without protecting anything:

- **Assertion-free or tautological:** "doesn't throw" as the only claim; asserting the mock returned what you told the mock to return; snapshot tests nobody reads (giant snapshots = auto-approved churn).
- **Mock choreography instead of behavior:** asserting `service.method` was called with exact args, while the actual *outcome* (state change, return value, emitted event) goes unasserted — these tests break on every refactor and catch no bugs; the inverted cost profile.
- **Over-mocking:** mocking the thing under test's collaborators so deeply that the test exercises the mocks; mocking the DB in "repository tests" (testing nothing); mock drift — mocks encoding behavior the real dependency no longer has (verify mock shape against the real contract where visible).
- **Interdependent or flaky-by-design:** shared mutable fixtures, order-dependent tests, real time/sleeps (`setTimeout` in tests), unseeded randomness, real network calls in "unit" tests.
- **Weakened assertions in diffs:** PR-mode red flag — assertions loosened (`toEqual` → `toBeTruthy`, exact → `objectContaining`, deleted cases) to make the diff green. Treat as a potential hidden behavior change, HIGH until explained.

## Test-shape recommendations

Recommend by what each level uniquely catches — and name concrete tests (scenario + assertion), never "add more tests":

- **Unit** — business rules, calculations, branching: fast, per-behavior, named for the behavior (`rejects_expired_coupon`). The default recommendation for domain logic the review found untested.
- **Integration** — where fakes lie: real queries against a real (test) DB (the N+1 and the missing-filter *show up here*), HTTP contract shapes, serialization round-trips, transaction/rollback behavior, RLS policies (integration-test tenant isolation against the actual policy, not a mock).
- **E2E** — the 2–5 flows the product dies without (signup, checkout, the money path), through the real stack. Recommend *few*; E2E suites that mirror every unit test become a flake-farm that teams stop trusting.

The recommendation format that gets acted on: *"`applyDiscount` has no test for stacked coupons (the bug in Phase 3 lives there). Add: unit — `applies_only_best_coupon_when_stacking_disabled`, asserting total = 90.00 for fixtures X; integration — POST /checkout with two coupons returns 422."*

## Regression risk (PR mode)

For a diff, state the risk profile explicitly: which existing behaviors does this change touch that *no test currently pins*? That list — "callers of `formatPrice` rely on locale behavior this PR changes; nothing tests it" — is the single most useful testing output of a PR review, because it tells the author exactly where the silent breakage will come from.
