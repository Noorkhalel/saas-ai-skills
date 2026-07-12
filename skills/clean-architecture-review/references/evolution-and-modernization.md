# Incremental modernization and production architecture

## Prioritization

Prioritize in this order: data/security/correctness boundary failure; inability to safely change/test a critical workflow; repeated delivery/incident cost; then structural cleanliness. Quantify or state uncertainty: incidents, lead time, test duration/flakiness, change failure rate, cycle count, module churn/co-change, latency/error/saturation, or team ownership conflicts.

## Safe evolution sequence

1. Map behavior and add characterization/contract tests plus observability.
2. Establish dependency rules/lints and a composition-root seam for one critical path.
3. Extract one use case or module API while preserving callers.
4. Put a port around one external/database/integration dependency owned by the policy.
5. Migrate callers incrementally; run old/new paths or adapters if semantic risk warrants it.
6. Delete legacy paths only after usage, correctness, performance, and rollback windows permit.

For a strangler-style extraction, retain a source of truth and clear routing/contract ownership. Do not dual-write without idempotency, reconciliation, monitoring, and a retirement plan. For service extraction, define data ownership, synchronous/async contract, authentication, error/retry/timeout, deployment/observability, incident ownership, and rollback before code movement.

## Production and team scale

Review configuration/secrets per environment, immutable deploy artifact, migration/version control, health/readiness, metrics/logs/traces/correlation, rate/concurrency limits, failure isolation, SLO/error budgets, backup/restore/data retention, security threat boundaries, and dependency ownership/on-call. Module boundaries should align enough with teams and capability ownership to avoid serial coordination; do not reorganize solely around a future team chart.

## Rewrite decision record

Recommend a rewrite only with evidence that incremental seams cannot meet a required correctness/security/operability or economic constraint. State scope, retained behavior/data, cutover strategy, parallel-run/reconciliation, consumer migration, staffing/time/cost, failure plan, and success/exit criteria. A rewrite is a portfolio decision, not a code-cleanliness fix.
