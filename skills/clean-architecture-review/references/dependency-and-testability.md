# Dependencies, smells, and testability

## Dependency review

Start at composition roots, entry points, and representative use cases. Build a directed import/module graph and find strongly connected components. Check whether domain/application code imports framework, HTTP, ORM, SQL, queue, cloud SDK, configuration, logging, or concrete adapter types. Also inspect runtime-only coupling via service locators, global state, environment/config reads, reflection, database schema, shared queues, and synchronous calls.

Interpret metrics, do not worship them: high fan-in can mean a useful stable abstraction; high fan-out can indicate orchestration or a god service; a cycle matters when it forces release/test/change together. Couple evidence to a scenario: "Adding billing rule X requires editing controller, repository, webhook handler, and UI because policy is duplicated." 

## Common smells and responses

| Smell | Mechanism to verify | Incremental response |
|---|---|---|
| Fat controller | validation, policy, orchestration, persistence mixed | extract one use case; keep transport mapping thin |
| Fat repository | business decisions/query orchestration mixed with persistence | move policy to use case/domain; keep persistence contract focused |
| God service/class | unrelated workflows/state change together | split by capability after characterization tests |
| Framework leakage | core types import ORM/HTTP/framework | introduce DTO mapping/port at edge of one workflow |
| Circular modules | modules cannot change/release independently | invert a dependency, extract contract, or merge falsely split modules |
| Shared mutable state | hidden order/concurrency dependency | encapsulate owner, inject state, make transition explicit |
| Anemic model | invariants duplicated across callers | move behavior near data if it reduces inconsistency |
| Generic common module | unrelated features depend on unstable utilities | narrow, govern, relocate, or duplicate small code |

## Testability

Unit-test deterministic domain/use-case policy without booting a server/framework/real DB where this yields fast trusted feedback. Contract/integration-test adapters against actual database/API/broker semantics. Test seams should reflect failures that matter: persistence conflict, timeout, retry/idempotency, authorization, serialization, event delivery, and migrations. Avoid mock-heavy tests that merely verify implementation calls; favor behavior and contracts.

Dependency injection should make collaborators explicit at a composition root. Service locators, static globals, ambient transaction/user context, and hidden clocks/randomness reduce test isolation unless carefully wrapped. A test pyramid is not a target ratio; use the cheapest test that proves the risk.
