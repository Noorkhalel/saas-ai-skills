# Architecture Styles and the Style Decision

How to choose the overall shape of the system (Phase 2, decision 1) and organize its insides (decision 2). The style decision is the most expensive one to reverse — spend real analysis here, and record it as an ADR (template at the end).

## The decision framework

Start from the default and let requirements push you off it:

**Default: modular monolith.** One deployable, strict internal module boundaries (each module: public interface, private internals, own tables). It gives you 80% of microservices' structure benefits — clear ownership, testable seams, future extraction points — at roughly zero operational cost. Almost every system under ~20 engineers and without extreme scale asymmetry should start here.

Move to **microservices** only when concrete forces demand it, and only for the modules that feel the force:

| Force | Evidence that it's real (not speculative) |
|-------|-------------------------------------------|
| Independent scaling | One workload's load profile is measured (or reliably known) to be 10×+ different from the rest — e.g., ingest pipeline vs. admin UI |
| Independent deployment by teams | Multiple teams are *actually* blocked on each other's release cycles today |
| Hard isolation | A component needs a different security/compliance boundary, runtime, or failure blast radius (e.g., untrusted-code execution, PCI scope) |
| Different tech constraints | A module genuinely needs a different language/runtime (ML inference, real-time media) |

If none of these hold, microservices buy you: network calls where function calls were, distributed transactions, eventual consistency, N deploy pipelines, observability sprawl, and integration testing pain — for nothing. Say so in the plan. A useful rule: **you need roughly one team per service you run**; a 4-person team proposing 8 services has designed an org chart they don't have. Extracting a service *later* from a well-modularized monolith is a known, bounded operation; merging a distributed mess back is not.

**Serverless functions** fit when load is spiky/bursty or near-zero at rest, work is event-shaped (file uploaded → process; webhook → handle), and per-request state is small. Costs: cold starts on latency-sensitive paths, execution time limits, harder local dev, and vendor coupling. A common winning hybrid: monolith for the product, functions for the spiky edges (media processing, scheduled jobs, webhook fan-out).

**Event-driven backbone** (broker, async messaging as the primary integration) fits when the domain is genuinely reactive — many consumers reacting to a stream of facts, integrations that must be decoupled in time, audit/event-log requirements. Costs: ordering, idempotency, retries, debugging across hops, and eventual consistency everywhere. Most systems need *some* async (jobs, webhooks, notifications) — that's a queue inside a monolith, not an event-driven architecture. Don't confuse the two in the plan.

**Choosing for an existing system (review engagements):** the current architecture is a sunk fact with migration cost attached. Recommend the *incremental path* — usually: enforce module boundaries inside the monolith first, then extract only the module(s) under real force, via the Strangler Fig pattern (route traffic through a facade, move one capability at a time). Big-bang rewrites are almost always the wrong recommendation; if you recommend one anyway, the plan must say why incremental is impossible.

## Internal organization

Whatever the deployment shape, the inside follows the same rules:

**Dependency rule (Clean/Hexagonal).** Dependencies point inward: infrastructure → application → domain. The domain (business rules, entities) imports nothing about HTTP, SQL, or vendors. The application layer orchestrates use cases. Adapters at the edge translate between the outside world and the core, through interfaces the core owns (ports). Practical payoff to state in the plan: the domain is testable without infrastructure, and vendors/frameworks are swappable at known cost.

**Layers to name in the plan** (one line each): edge (routing, auth, rate limiting, validation) → application/use-cases → domain → infrastructure adapters (DB, queue, email, third parties). Collapse layers that would only forward — a CRUD-heavy app doesn't need four ceremonial layers around every table (KISS); say which layers you collapsed and why.

**Module boundaries: use DDD bounded contexts.** The best module seams follow the business's language: where the same word changes meaning ("order" to sales vs. fulfillment) or a cluster of concepts changes together, that's a boundary. For each module the plan states: name, one-sentence responsibility, the data it owns, its public interface, and what it may call. Within a module, apply DDD tactically where the domain is rich: entities, value objects, aggregates as consistency boundaries (one transaction = one aggregate). Skip the ceremony for genuinely CRUD modules — DDD is for complex domains, not a tax on simple ones.

**Communication defaults.** Within a monolith: in-process interface calls between modules (not HTTP to yourself). Module → module data access goes through the owning module's interface, never its tables. Async (queue/events) where decoupling in time is a requirement: outbound webhooks, long-running jobs, notification fan-out, retryable integrations. Between services (if any): prefer a small number of coarse, versioned contracts; avoid chatty sync chains (a request fanning into 6 sequential service calls is a distributed monolith).

**CQRS, applied honestly.** Splitting read and write *models* is cheap and often right (queries bypass domain machinery and read straight from the DB, shaped for the screen). Separate read *stores* with projections is heavy machinery — recommend only with demonstrated read/write asymmetry that caching and replicas can't cover.

## Style cheat sheet

| Style | Best for | Avoid when | First bottleneck to watch |
|-------|----------|-----------|---------------------------|
| Modular monolith | Almost everything at the start; teams < ~20 | Genuine independent-scaling/team-autonomy forces exist now | DB write contention; deploy queue as team grows |
| Microservices | Multiple autonomous teams; measured scale asymmetry; hard isolation | Small team, unproven boundaries, no platform/ops maturity | Cross-service consistency; operational load |
| Serverless | Spiky/event-shaped work; near-zero baseline load | Latency-sensitive hot paths; long-running work; heavy local dev needs | Cold starts; per-invocation cost at sustained load |
| Event-driven | Many consumers of a fact stream; time-decoupled integrations | The workflow is really a sequence needing an orchestrator | Debugging/tracing; poison messages; ordering |
| Layered monolith (no module seams) | Prototypes, tiny scope, disposable tools | Anything expected to grow | Big ball of mud by accretion |

## Architecture Decision Records

Document every significant decision (style, tenancy model, database, API style, hosting) as a short ADR — in the plan itself or the repo's `docs/adr/`:

```markdown
# ADR-003: Modular monolith over microservices
Status: accepted · Date: 2026-07-07
Context: 4 engineers, B2B SaaS, ~200 tenants year one, no scale asymmetry between modules.
Decision: Single deployable with enforced module boundaries (billing, accounts, projects, notifications).
Alternatives: Microservices (rejected: operational cost exceeds team capacity; no isolating force);
  plain monolith without module seams (rejected: forecloses cheap extraction later).
Consequences: One deploy pipeline; module discipline must be enforced by lint/arch tests;
  notifications module is the most likely future extraction (async, spiky).
Revisit when: any module needs independent scaling, or team exceeds ~3 squads.
```

The "Revisit when" line is what makes an ADR a living decision instead of archaeology — every major decision in the plan should carry its trigger.
