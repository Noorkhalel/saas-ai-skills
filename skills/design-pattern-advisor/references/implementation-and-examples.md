# Adoption and worked examples

## Adoption protocol

Characterize behavior and public contracts; add regression tests; identify stable and variable behavior; introduce the smallest seam; migrate one implementation; validate behavior, error/side-effect ordering, and metrics; migrate remaining implementations; remove obsolete branch/duplication after rollback window. Use contract/selection tests for Strategy, mapping/lifecycle tests for Factory, translation/failure tests for Adapter, ordering/duplicate/failure-isolation tests for Observer, transition tests for State, and duplicate/retry/compensation tests for distributed patterns.

## Required examples

1. **Strategy recommended:** repeated Stripe/PayPal/bank behavior in capture/refund/status has growing variants. Compare a provider map; choose Strategy/adapter only if shared operations and testing benefit justify it.
2. **Strategy rejected:** a two-code lookup uses a small immutable map; keep map/function because a strategy hierarchy costs more.
3. **Factory recommended:** provider documents require credentials, feature configuration, lifecycle/validation, and consistent related clients; factory centralizes valid creation.
4. **Factory rejected:** one object literal with three inputs; direct construction is clearer than a wrapper factory.
5. **Adapter:** isolate third-party payment SDK behind internal payment contract; translate requests/errors/webhooks and contract-test it.
6. **Observer recommended:** independent audit, notification, and analytics consumers react to a domain event; document at-least-once/idempotency/failure isolation.
7. **Observer rejected:** payment must synchronously reserve stock before completion; direct call makes order/failure visible.
8. **State:** complex order lifecycle has transition guards, side effects, and state-specific behavior; use explicit state machine or State only if enum/table is insufficient.
9. **Singleton harmful:** database/config/logger/current-user singleton mixes lifetimes and global mutable user state; use explicit application/request lifetimes and injection.
10. **Repository review:** ORM already provides cohesive query/persistence semantics; reject pass-through repository unless domain boundary, test seam, or query translation exists.
11. **Outbox:** DB update plus event publish can split on crash; transactionally store outbox, relay idempotently, and handle duplicate consumers.
12. **CQRS rejected:** small CRUD has no divergent read/write model or projection need; keep modular service/ORM.
13. **React:** repeated fetch/state logic becomes a custom hook plus API function where reuse/test complexity is real; avoid GoF class patterns.
14. **Go:** functional options make optional construction readable; avoid Builder classes.
15. **Rust:** enum plus transition function models finite states; avoid State trait hierarchy unless runtime extensibility is needed.

For each case, the input/problem, forces, candidates, recommendation, trade-offs, and expected output are the stated decision; adapt to actual code rather than copying a pattern.
