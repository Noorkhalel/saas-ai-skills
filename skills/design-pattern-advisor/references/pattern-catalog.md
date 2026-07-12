# Pattern selection catalog

## Creational

| Pattern | Consider when | Prefer simpler option when |
|---|---|---|
| Factory Method / Abstract Factory | creation selects implementations or coherent families; caller must not know concrete lifecycle | construction is direct or existing DI already composes it |
| Builder | many optional/ordered construction steps, immutable validation-heavy object | named parameters/object literal/functional options are clear |
| Prototype | copying configured objects is meaningful and controlled | ordinary construction is cheaper/clearer |
| Singleton / Object Pool | one controlled process-local lifetime or expensive scarce resources need pooling | module/DI-managed lifetime or ordinary allocation works |

## Structural

| Pattern | Consider when | Avoid when |
|---|---|---|
| Adapter | external/legacy contract must translate into an internal contract; isolate failure/semantics | only cosmetic renaming occurs |
| Facade | consumers need stable simpler subsystem access | it becomes a god service or hides required controls |
| Decorator | optional composable behavior causes subclass explosion | middleware/functions/framework facilities are clearer |
| Proxy | access, caching, lazy loading, logging, authorization need controlled mediation | latency/control flow becomes surprising |
| Composite | clients should treat hierarchical leaves/groups uniformly | a plain tree/data traversal is clearer |
| Bridge / Flyweight | independent dimensions of variation or large shared intrinsic state are proven | variation/memory pressure is speculative |

## Behavioral

| Pattern | Consider when | Avoid when |
|---|---|---|
| Strategy | multiple interchangeable algorithms implement one operation and variation recurs | a closed simple map/conditional/callback is clearer |
| State | behavior and transitions vary materially by state across methods | a small enum/table/state machine is enough |
| Command | operations need queueing, logging, retry, audit, undo, schedule | direct call is sufficient |
| Observer / Pub-Sub | multiple independent consumers react, eventual consistency is acceptable | direct synchronous ordering/traceability is required |
| Chain of Responsibility | ordered handlers process/forward request | order must remain obvious or framework middleware exists |
| Mediator | peer coordination is dominant and can be owned centrally | it becomes a god coordinator |
| Template Method | stable workflow with limited inherited variation and inheritance is already justified | composition/Strategy enables safer independent replacement |
| Visitor | operations change often while element structure is stable | ordinary application conditional/visitor complexity exceeds benefit |
| Memento / Iterator / Interpreter | snapshot/undo, collection traversal, or formal language need is concrete | plain data/history/iteration/parser works |

## Enterprise and DDD

Repository, Unit of Work, Data Mapper, Service Layer, Specification, Domain Model, Aggregate, Entity, Value Object, Domain/Application Service, Domain Event, Anti-Corruption Layer, and Bounded Context are patterns around persistence/domain/integration boundaries. Use them for demonstrated ownership, invariants, query/persistence translation, or foreign-model translation. Do not wrap an ORM with a pass-through repository or force an aggregate/domain model on simple CRUD.
