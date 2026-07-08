# Concurrency, Races & Distributed Bugs (Phase 5)

Read when the bug is **intermittent, "random," "only under load," "can't reproduce," or "works with a breakpoint."** Those words are the signature of concurrency, ordering, or external-state bugs — suspect these *before* re-reading logic that looks correct, because it probably is correct, just not under interleaving.

## Recognizing a concurrency bug

Tells: fails intermittently with no input change; frequency rises with load/parallelism; disappears when you add logging or a debugger (timing shifted); data is "sometimes" wrong/duplicated/missing; the same code is correct single-threaded. If you see these, stop looking for a logic error and start looking at *shared mutable state under concurrent access*.

## Race conditions

- **Check-then-act on shared state** — the archetype. Read a value, decide, act, but another actor changed it in between: exists-check then insert (duplicate), balance-check then debit (overspend/oversell), read-modify-write of a counter (lost update). Two requests both pass the check.
  - **Verify:** is the read and the dependent write atomic? If there's any gap — including an `await`/I/O between them — it's racy.
  - **Fix direction:** make it atomic — a DB unique constraint + handle the violation, a conditional write (`UPDATE ... SET x=x-1 WHERE id=? AND x>=1`, act on 0-rows-affected), `SELECT ... FOR UPDATE`, an atomic counter, or a lock. "Wrap in a transaction" alone does *not* fix it under default isolation — the check still races unless the write is conditional or the rows are locked.
- **Shared mutable state across requests:** module/global variables, singletons, or caches mutated per-request in a concurrent server → one user's data bleeds into another's, or corrupts. Request-scope the state.
- **Non-atomic multi-step updates** that must all-or-nothing without a transaction (`references/data.md`).
- **Async interleaving in one process** counts even without threads: between `await`s, other tasks run — shared state you read before an `await` may be stale after it. Single-threaded event loops still race across `await` boundaries.

## Deadlocks

- Two actors each holding a resource the other needs. In DBs: transactions locking rows in *different orders* (T1 locks A then B, T2 locks B then A) — the DB kills one victim; the log names both. In code: nested locks acquired in inconsistent order; sync-over-async (`.Result`/`.get()` on the same executor) starving its own thread pool.
- **Verify:** enumerate what locks are held and in what order across paths. **Fix:** a global lock-ordering discipline (always A before B), shorter critical sections, timeouts that fail rather than hang, or removing the second lock.
- Connection-pool "deadlock": every pool connection is held by a request waiting for a *new* connection (e.g., a transaction that makes a nested call needing its own connection) → total stall. Tell: everything hangs at high concurrency, resolves on restart.

## Making an intermittent bug deterministic

You cannot fix what you can't trigger — force the condition:
- **Inject the interleaving:** add a delay/breakpoint at the suspected gap (between check and act) and drive two concurrent requests — a real race becomes 100% reproducible. Concurrency test harnesses and thread-sanitizers help.
- **Amplify:** run the operation from many workers in a tight loop; raise parallelism until it surfaces.
- **Pin the nondeterminism:** fix the clock/timezone, seed the RNG, replay the exact payload/order — to rule *out* time/randomness or confirm it.
- The endpoint is a test that reproduces the race (e.g., fires N concurrent requests and asserts the invariant holds) — the only credible proof a concurrency fix works.

## Distributed-systems failures

When the bug spans services/network, extra failure modes:
- **Partial failure:** a call that neither clearly succeeds nor fails (timeout) — did the work happen? Non-idempotent operations + client retries = duplicates (double charge, double send). Fix: idempotency keys, dedup, exactly-once-effect design. This is the most common distributed bug in payment/order/messaging code.
- **Eventual consistency / read-after-write:** reading a replica right after writing the primary returns stale data; a cache not yet invalidated; an event not yet processed. "The update didn't save" that's actually "the read was too fast."
- **Ordering & duplication in queues/events:** messages arrive out of order or more than once — handlers must be idempotent and order-independent, or the design must guarantee ordering. Poison messages retrying forever; missing/oversized dead-letter handling.
- **Dual-write inconsistency:** writing to DB then publishing an event (or two stores) without atomicity — a crash between them leaves them disagreeing. Fix: outbox pattern, or make one the source of truth.
- **Clock skew** across nodes breaking time-based logic (token expiry, ordering by timestamp, TTLs) — never assume synchronized clocks for correctness.
- **Cascading failure / thundering herd:** one slow dependency exhausts caller threads/connections, which fails *their* callers; retries amplify the load. Tells in the timeline: failures spreading outward from one origin. Fix: timeouts everywhere, circuit breakers, backoff+jitter, bulkheads.

## Reporting

Name the exact shared resource and the interleaving that corrupts it ("two concurrent `POST /reserve` both read stock=1 at line 40 before either decrements at line 43"), the confidence, and the atomicity-restoring fix — plus the concurrent test that reproduces it. A concurrency finding without the specific interleaving is a guess; make the race concrete.
