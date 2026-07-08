# Bug Detection Checklist (Phase 3)

Hunt by defect class — each class has a place it hides and a question that flushes it out. For every suspected bug, verify by tracing the path (principle 1), then report: location · severity · what happens · why it happens · fix.

## Logic errors
- **Boundary conditions:** off-by-one in loops/slices/pagination; `<` vs `<=` at limits; inclusive/exclusive date ranges (the classic: end-of-day excluded); fencepost errors in batching.
- **Boolean logic:** De Morgan slips (`!(a && b)` vs `!a && !b`); conditions that can never be true/false (check each branch's reachability); precedence without parentheses (`a || b && c`).
- **Inverted or misplaced conditions:** early returns that skip required side effects; `if (err)` branches that fall through to the success path.
- **Wrong variable:** copy-paste rows using `a` where `b` was meant — scan any repeated similar blocks character-by-character; it's the highest-yield 30 seconds in review.
- **Unit/precision mistakes:** seconds vs milliseconds (`Date.now()` mixing with unix seconds), cents vs dollars, float equality/accumulation on money (`0.1 + 0.2`), timezone-naive date math, string comparison of numbers (`"10" < "9"`).

## Null / absent / edge inputs
For every input and every external call result, ask: what happens when it's **null/undefined, empty (`""`, `[]`, `{}`), whitespace, zero, negative, huge, duplicated, or malformed**?
- Property chains on possibly-absent data (`user.profile.name`) where the guard is missing or the optional chain silently produces `undefined` that flows onward.
- "Can't happen" defaults (`?? 0`, `|| {}`) that convert absence into a *valid-looking wrong value* — often worse than crashing.
- Collection assumptions: first/last element of possibly-empty arrays; `find()` result used without a miss check; division by possibly-zero counts.

## Race conditions & concurrency
- **Check-then-act on shared state:** exists-check then create; balance-check then debit; read-modify-write without atomicity. Two concurrent requests both pass the check. Fix: DB constraint + handle violation, atomic update (`UPDATE ... WHERE balance >= x`), or locking. Anything involving money, quotas, or uniqueness gets this scrutiny.
- **Non-atomic multi-step updates:** two writes that must both happen, without a transaction (see transactions below).
- **Shared mutable state across requests:** module-level variables mutated per request in server code; caches without concurrency control; singletons holding request data (leaks across users!).
- **TOCTOU on files** and duplicate-delivery on queue consumers (are handlers idempotent?).

## Async mistakes
- **Unawaited promises:** fire-and-forget calls whose failures vanish; missing `await` making code proceed before completion (an `async` call inside `forEach` never awaits — classic); functions returning a promise where a value is expected (`if (isValid(x))` where `isValid` is async — always truthy).
- **Parallel mutation:** `Promise.all` over handlers that write shared structures or the same rows.
- **Sequential awaits that should be parallel** are a performance finding; **parallel awaits that should be sequential** (B needs A's result or A's lock) are a correctness finding.
- **Error handling across async boundaries:** try/catch that can't catch (wraps the call but not the await; callback errors thrown outside the try); rejected promises in event handlers/timers with no `.catch` — process-level crash or silent failure by runtime.
- **Cancellation/unmount:** state updates after component unmount or request abort; stale-response races (two in-flight fetches resolving out of order — last-write-wins by luck). Look for missing abort/ignore-stale guards in UI data fetching.

## State bugs
- Stale reads: value captured at closure creation used after it changed (React stale-closure in callbacks/intervals is the canonical case — see `frameworks.md`).
- Derived state stored instead of computed — then not updated when the source changes.
- Initialization order: config/connections read before ready; module-import side effects depending on import order.
- State machines with unreachable/undefined transitions: what happens on "cancel" while "processing"? Enumerate the state × event grid for anything with a status field.

## Transactions & consistency
- **Multi-write invariants without a transaction:** order + order_items; debit + credit; create + audit-log. Ask: if the process dies between line X and X+1, is stored data valid?
- **Transaction scope wrong:** external calls (HTTP, email) *inside* a DB transaction (locks held across network latency; commit doesn't retract the email); or the transaction committed before the message/event is enqueued (use outbox) — dual-write inconsistency both ways.
- Missing rollback on error paths; connections/transactions leaked on exceptions (no finally/context manager).
- Retries around non-idempotent operations — retry + no idempotency key = duplicate side effects.

## Resource & memory issues
- Unclosed resources on error paths: files, DB connections, cursors — anything acquired needs try/finally or language equivalent (context manager, `using`, defer).
- Unbounded growth: caches without eviction, arrays that only append across requests, listeners/subscriptions added but never removed (the SPA memory leak), timers never cleared.
- Loading unbounded data: whole tables/files into memory where the size is user-controlled.

## Error-handling failures
- **Swallowed errors:** empty catch; catch-log-continue where the caller then proceeds on garbage; `.catch(() => {})`. Ask of every catch block: *can the code after this legitimately run if the try failed?*
- **Over-broad catch** hiding programming errors (catching `Exception`/bare `except` around 40 lines to guard one call).
- **Error → wrong signal:** returning `null`/`-1`/empty on failure where callers can't distinguish it from a real value; HTTP 200 with an error body; exceptions replaced by console.log.
- **Partial-failure handling in batches:** one bad item aborts the whole batch (or worse — is silently skipped with no report). What's the contract?
- Error messages leaking internals (stack traces, SQL, paths) to clients — cross-file with `security.md`.

## Reporting discipline

A bug report that will be acted on reads like: **"`orders.ts:41` (HIGH): concurrent checkouts can oversell — the stock check at :38 and decrement at :41 aren't atomic, so two requests can both pass with stock=1. Fix: make the decrement conditional (`UPDATE stock SET qty = qty-1 WHERE id=? AND qty >= 1`) and treat 0 rows affected as sold-out."** Location, consequence, mechanism, fix — in that shape, every time.
