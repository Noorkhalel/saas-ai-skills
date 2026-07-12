# Language, framework, frontend, and distributed guidance

## Language and framework adaptation

- **TypeScript/JavaScript:** use functions, closures, object literals, modules, maps, structural types, and callbacks before class hierarchy. React custom hooks, reducers, controlled/compound components, provider, render props, or HOCs may fit UI concerns.
- **Python:** prefer protocols, duck typing, callables, dataclasses, decorators, context managers, and explicit modules where they clarify responsibility.
- **Java/C#:** interfaces, records, delegates, and DI can express patterns, but existing Spring/ASP.NET composition may already manage factories/strategies/lifetimes.
- **Go:** use small consumer interfaces, explicit constructors, composition, and functional options rather than Builder class hierarchies.
- **Rust:** use traits, enums, ownership, and type-state; an enum plus explicit transition function often beats State classes.
- **PHP/Laravel:** use contracts, container, middleware, and framework lifecycle rather than rebuilding them.

Middleware commonly already is Chain of Responsibility; DI containers may compose factories/lifetimes; Redux/reducers can model state transitions; Nest providers may be adapters/strategies; Django ORM is Active Record-like; FastAPI dependencies can inject boundaries. Review whether a native mechanism is already sufficient before introducing a duplicate pattern.

## Integration and distributed patterns

Use API Gateway/BFF for distinct client composition/governance needs; Saga only for a multi-service transaction with explicit compensation; Outbox for atomic local state plus reliable event publication; Inbox/idempotent consumer for at-least-once delivery; circuit breaker/retry/bulkhead for measured dependency failure/capacity behavior; DLQ for controlled terminal event failure; competing consumers for measured queue throughput; strangler fig for incremental legacy replacement. CQRS needs a justified read/write model difference and projection/rebuild/freshness ownership. Event sourcing needs audit/temporal reconstruction worth version/replay/privacy/operations cost.

For any event/distributed recommendation, state source of truth, delivery guarantee, ordering scope, idempotency, retry/backoff, duplicate handling, timeout, compensation, observability, DLQ/replay, security/tenant scope, and incident recovery. Do not apply a distributed pattern to a local in-process problem.
