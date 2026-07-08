# Architecture Review

Read this when an engagement touches module boundaries, when the user asks about design, or at step 8 of every non-trivial workflow. Two jobs: **evaluate** the architecture the code has, and **guide migration** toward a better one — always incrementally.

An architecture review during refactoring answers three questions:

1. **Which direction do dependencies point?** (the single most important architectural fact)
2. **Do the boundaries match the reasons things change?**
3. **Is the architecture's ceremony proportional to the system's actual complexity?**

## Contents

- [Principles](#principles) — SOLID, DRY, KISS, YAGNI
- [Dependency rules](#dependency-rules) — DIP, DI, ISP in practice
- [Architectural styles](#architectural-styles) — recognizing, evaluating, and refactoring toward each
- [Running the review](#running-the-review)
- [Incremental migration strategies](#incremental-migration-strategies)

---

## Principles

Principles are diagnostic lenses, not laws. Each names a specific failure mode; cite the principle *and* the concrete harm.

**S — Single Responsibility.** A unit should have one reason to change. Violation shows up as Divergent Change and Mixed Responsibilities; the test is the one-sentence description ("this exists to ___" without "and"). Fix: Extract Class/Module along the axes of change.

**O — Open/Closed.** Adding a variant shouldn't require editing every existing operation. Violation shows up as parallel switch statements — each new case edits N files. Fix: Replace Conditional with Polymorphism, Extract Strategy. Don't inverse-overapply: code that never grows variants doesn't need extension points (YAGNI).

**L — Liskov Substitution.** A subtype must be usable anywhere its supertype is. Violations: subclasses throwing `NotSupported` on inherited methods, callers type-checking before calling, overrides that weaken guarantees or strengthen requirements. Fix: Composition over Inheritance, or split the interface (ISP) so the subtype only promises what it delivers.

**I — Interface Segregation.** Consumers shouldn't depend on members they don't use. Violation: implementing a 20-method interface with 17 stubs; a change to any member recompiles/retests every consumer. Fix: Extract Interface per consumer role.

**D — Dependency Inversion.** High-level policy must not depend on low-level detail; both depend on abstractions. Violation: domain code importing database drivers, HTTP clients, or vendor SDKs directly. Fix: Extract Interface owned by the high-level side + Introduce Dependency Injection.

**DRY.** Every piece of *knowledge* has one authoritative home. DRY is about knowledge, not text: two identical-looking blocks that will evolve independently are not duplication, and merging them creates false coupling — the worst outcome. Conversely, one business rule expressed in three places (frontend validation, backend validation, DB constraint) may be deliberate defense-in-depth; ensure a single source generates or documents the rule.

**KISS.** Prefer the simplest structure that meets *current* requirements. In refactoring: when two transformations fix the smell, apply the smaller; when a review can't justify a layer's existence, recommend collapsing it.

**YAGNI.** Don't build for speculative futures. In refactoring this cuts both ways: remove Speculative Generality you find, and don't *introduce* it — the moment to add flexibility is when the second real use case arrives, shaped by facts.

## Dependency rules

The rules that make everything else checkable:

- **Dependencies point from volatile toward stable, from detail toward policy.** Business rules are the most stable, most valuable code; I/O mechanisms are detail. If changing your database vendor would touch domain files, the arrows point the wrong way.
- **Inject collaborators; construct at the composition root.** Objects receive dependencies (constructor injection first choice); `new` for collaborators appears only at the edge (`main`, container config, request setup). This is what makes units testable and implementations swappable. A DI *framework* is optional; the discipline isn't.
- **Interfaces belong to their consumers.** Define the port where it's used, named for the need (`OrderNotifier`), not where it's implemented (`SmtpClient`). This is what actually inverts the dependency.
- **Keep interfaces role-sized** (ISP). One consumer role per interface; compose roles where a class serves several.
- **No cycles between modules.** A cycle is one module wearing two names. Break with DIP, an extracted shared module, or events (see Circular Dependencies in the smell catalog).

## Architectural styles

For each style: what it is, the signal that a codebase *wants* it, and the refactoring path toward it. Evaluate fit — the right architecture is the cheapest one the system's real complexity can afford. Ceremony beyond need is Speculative Generality at architecture scale.

### Layered Architecture
Horizontal layers (presentation → application → domain → data), each depending only downward (or inward). The baseline style; most codebases claim it.
**Wants it:** Mixed Responsibilities everywhere — SQL in handlers, business rules in UI callbacks.
**Refactor toward:** Extract Method to separate layer concerns within units, Extract Class/Module per layer, Introduce Repository for the data edge. **Watch for:** skip-layer imports and "anemic" pass-through layers (Lazy Class at scale); business logic pooling in a fat "service" layer while the domain model is just data bags.

### Hexagonal (Ports & Adapters)
The domain core defines interfaces (ports) for everything it needs from the outside; adapters implement them for concrete tech. Direction: everything points inward at the core.
**Wants it:** Layered code where swapping/faking infrastructure is still hard; tests that need real databases.
**Refactor toward:** for each infrastructure touchpoint in domain code: Extract Interface (port, consumer-owned) → Introduce Adapter (move the tech-specific code behind it) → Introduce Dependency Injection. One port at a time, highest-pain first (usually persistence).

### Clean Architecture
Concentric layers (entities ← use cases ← interface adapters ← frameworks) with a strict inward dependency rule. Practically: hexagonal plus an explicit application/use-case layer.
**Wants it:** Business workflows tangled through controllers; the same use case duplicated across entry points (HTTP + CLI + queue).
**Refactor toward:** Extract Class per use case (one orchestrating class per workflow), entities free of framework imports, controllers reduced to translation. Don't cargo-cult four layers into a CRUD app — collapse layers that would only forward (KISS).

### Domain-Driven Design (DDD)
Model the business domain explicitly: entities (identity), value objects (immutable values), aggregates (consistency boundaries), repositories, domain services and events, a ubiquitous language shared with domain experts, and bounded contexts that let the same word mean different things in different subdomains.
**Wants it:** Primitive Obsession at scale; business rules scattered and disputed; "what does *order* actually mean here" arguments; one `User`/`Product` class serving five departments' conflicting needs (that's a missing bounded context).
**Refactor toward:** start tactical and cheap — Introduce Value Object for domain concepts, gather rules onto entities (Move Method cures anemic models), Rename toward the domain experts' vocabulary. Aggregate boundaries and bounded contexts are bigger moves: draw them along transactional-consistency needs and language boundaries respectively, then enforce with module boundaries (see Modular Monolith).

### CQRS
Separate the write model (commands, invariant-enforcing) from the read model (queries, shaped for display).
**Wants it:** One model tortured in two directions — aggregates loading half the database to render a list; read-side joins corrupting write-side design; wildly asymmetric read/write load.
**Refactor toward:** lightweight first — split repository interfaces into reads and writes (ISP), let queries bypass the domain model and read straight from the data source. Separate storage/projections and event sourcing are heavy machinery; recommend only with demonstrated need.

### Event-Driven Architecture
Components communicate via events; producers don't know consumers.
**Wants it:** One action hard-wired to a growing list of reactions (Introduce Observer's smell, at system scale); Shotgun Surgery every time a new reaction is added; temporal coupling where independent work is forced sequential.
**Refactor toward:** Introduce Observer/domain events in-process first; a broker only when process boundaries demand it. **Honest costs to state in any recommendation:** ordering, retries, idempotency, and debugging all get harder; an event chain that must complete in sequence is a workflow wearing a disguise — an explicit orchestrator is better.

### Modular Monolith
One deployable, internally partitioned into modules with enforced boundaries: each module has a public API, private internals, and no reaching into another's tables or internals.
**Wants it:** A monolith turning into a big ball of mud, or a team eyeing microservices without operational readiness. This is the default recommendation between "layered monolith" and "microservices" — most of the coupling benefits, none of the distributed-systems tax.
**Refactor toward:** choose module boundaries (bounded contexts are the best guide) → move code into modules (Extract Module) → define each module's public interface and migrate cross-module calls onto it → enforce (visibility rules, lint/arch tests, separate schemas). Cross-module transactions and joins are where this gets hard; resolve them *before* claiming the boundary exists.

### Microservices
Modules become independently deployed services communicating over the network.
**Wants it:** genuinely independent scaling/deployment/team-autonomy needs, *proven* module boundaries, and the operational maturity to pay for distribution (observability, resilience patterns, data consistency strategies).
**Refactor toward:** modular monolith first — a service split along a wrong boundary is catastrophically expensive to fix. Then Strangler Fig per module (see below), starting with the module with the fewest synchronous cross-module calls. **Review duty:** when you see a "distributed monolith" (services that must deploy together, chatty synchronous chains, shared databases), say so plainly and recommend consolidation or boundary repair — more services is not more architecture.

## Running the review

Concrete procedure for step 8 of the workflow:

1. **Map the dependency graph** at module level (imports, or build-level deps). Flag: cycles, domain→infrastructure arrows, everything-depends-on-it hubs (God Object at module scale), skip-layer shortcuts.
2. **Test boundaries against change scenarios.** Pick 2–3 realistic changes ("add a payment provider", "change the DB", "new notification channel") and trace what would need editing. Many-file answers reveal boundary misplacement (Shotgun Surgery at architecture scale).
3. **Check the principles** where evidence appeared during phases A–C; cite violations with location and concrete harm, not just the acronym.
4. **Judge proportionality.** Ceremony with no current payoff → recommend collapsing (YAGNI); missing structure with recurring pain → recommend the *lightest* style that fixes it.
5. **Verdict in the report:** what the architecture is (named style, honestly assessed), the top 2–3 structural risks, and the recommended direction with its first incremental step.

## Incremental migration strategies

Architecture migrations must ship value continuously — a six-month "big rewrite branch" is how migrations die. All three strategies are Parallel Change (expand → migrate → contract) at different scales:

- **Strangler Fig** — stand up the new structure alongside the old; route one slice of traffic/callers at a time to it; the old path shrinks until deletion. Works for extracting services, replacing subsystems, framework migrations. Key: a routing seam (facade, proxy, feature flag) in front of both.
- **Branch by Abstraction** — for in-process replacements when you can't run both paths side by side externally: insert an abstraction over the old implementation (Extract Interface + migrate callers), build the new implementation behind it, switch (flag or config), remove the old. The codebase stays green and shippable throughout — no long-lived VCS branch.
- **Anti-Corruption Layer** — when new clean code must coexist with a legacy model for a long time: a translation layer (Adapter + Facade) that converts between the legacy model and the new one, so legacy concepts don't leak in. Often the first thing to build in a DDD migration.

Sequence any migration so that **every merged step leaves the system better and deployable**, and abandonment at any point is safe. If a proposed plan lacks that property, redesign the plan.
