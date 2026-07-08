# Refactoring Pattern Catalog

Mechanics, risk, and selection guidance for every transformation this skill supports. Patterns are grouped by intent. Each entry: **When** (the smell/situation that justifies it), **Mechanics** (safe step order), **Risk** (per the SKILL.md risk model) and, where the shape matters, a compact before/after.

**Selection principle:** pick the smallest transformation that fixes the named smell. Extraction before moving; moving before splitting; splitting before introducing a design pattern. A design pattern is justified only by an *observed* smell that is exactly the problem the pattern solves — introducing patterns speculatively is itself a smell (Speculative Generality). Examples use TypeScript-flavored pseudocode; the mechanics are language-agnostic.

## Contents

- [Extraction](#extraction) — Extract Method/Function, Variable, Constant, Class, Module, Interface
- [Moving and consolidating](#moving-and-consolidating) — Move Method, Move Field, Split Class, Merge Duplicate Logic
- [Simplifying conditionals](#simplifying-conditionals) — Guard Clauses, Replace Switch, Replace Conditional with Polymorphism, Replace Temp with Query
- [Data and encapsulation](#data-and-encapsulation) — Replace Primitive with Object, Introduce Value Object, Encapsulate Field, Encapsulate Collection
- [Introducing design patterns](#introducing-design-patterns) — Strategy, Repository, Factory, Builder, Adapter, Facade, Decorator, Observer, State, Command, Mediator
- [Structural](#structural) — Introduce Dependency Injection, Composition over Inheritance, Remove Dead Code

---

## Extraction

### Extract Method / Extract Function
**When:** Long Method; a block needs a comment to explain *what* it does; the same fragment appears more than once; mixed abstraction levels.
**Mechanics:** (1) Identify a coherent fragment with one purpose. (2) Name it after the purpose — the would-be comment is the name. (3) Pass in what it reads; return what it produces; if it needs many locals, extract a smaller piece or see Replace Temp with Query. (4) Replace the fragment with the call; verify. Watch for: fragments that mutate more than one local (return an object or split the fragment) and fragments containing early `return`/`continue` (preserve control flow explicitly).
**Risk:** Low (no shared mutable state) / Medium (mutations, exceptions, or async inside).

```ts
// Before                                  // After
function printInvoice(inv) {               function printInvoice(inv) {
  // calc totals                             const totals = calculateTotals(inv);
  let sub = 0;                               render(inv, totals);
  for (const l of inv.lines)               }
    sub += l.qty * l.price;
  const tax = sub * TAX_RATE;
  // ...30 lines of rendering
}
```

### Extract Variable
**When:** An expression is hard to read inline — compound conditions, nested calls, repeated sub-expressions.
**Mechanics:** Introduce a well-named local for the sub-expression; substitute. `const isEligible = age >= 18 && country in SERVED_REGIONS` turns a puzzle into a sentence. Confirm the expression has no side effects before deduplicating repeated occurrences.
**Risk:** Low.

### Extract Constant
**When:** Magic Numbers, Magic Strings.
**Mechanics:** Define a named constant at the narrowest scope that covers all uses; replace each occurrence *after confirming it means the same thing* — two `0.0825`s may be different concepts (tax rate vs. some ratio) that must not share a name. Prefer enums/union types for closed sets of strings.
**Risk:** Low.

### Extract Class
**When:** God Object, Long Class, Divergent Change, Temporary Fields, a Data Clump with behavior.
**Mechanics:** (1) Identify the responsibility cluster (fields + methods that use them). (2) Create the new class; Move Field then Move Method one member at a time, keeping tests green after each. (3) Decide the relationship: the old class holds an instance (usual), or callers use the new class directly. (4) Rename the old class if its meaning narrowed.
**Risk:** Medium.

### Extract Module
**When:** A file/module hosts multiple unrelated concerns; Low Cohesion grab-bags; a concern needs to be depended on separately (e.g., to break a Circular Dependency).
**Mechanics:** Same as Extract Class at file level: create the module, move one export at a time, update imports (tool-assisted), re-export temporarily from the old location if the import fan-in is large, then migrate importers incrementally (Parallel Change) and remove the re-export.
**Risk:** Medium; watch for import cycles created by the split and for side effects that ran at old-module import time.

### Extract Interface
**When:** Tight Coupling to a concrete class; a consumer uses only a slice of a large class (Interface Segregation); you need a test double; breaking a Circular Dependency via Dependency Inversion.
**Mechanics:** (1) List only the members the *consumer* actually uses — the interface belongs to the consumer's needs, not the implementation's shape. (2) Define it, have the concrete class implement it. (3) Retype the consumer's dependency to the interface. Keep interfaces small; several narrow interfaces beat one wide one.
**Risk:** Low–Medium.

## Moving and consolidating

### Move Method
**When:** Feature Envy — the method uses another class's data more than its own; consolidating Shotgun Surgery.
**Mechanics:** (1) Check what the method uses from its current home; if some, extract that part first. (2) Copy to the target class, adapt references (`customer.x` becomes `this.x`; pass the old host as a parameter if still needed). (3) Delegate from the old location; verify; then migrate callers and delete the delegate (or keep it if the old location is a published API — note the compat decision).
**Risk:** Medium; polymorphic methods (overridden anywhere?) upgrade to High.

### Move Field
**When:** A field is used more by another class than its own; reuniting a field with the methods that govern it; usually a step inside Extract Class.
**Mechanics:** (1) Encapsulate the field first if it's publicly accessed. (2) Create it in the target; update the accessors on the source to read through to the target. (3) Migrate accesses; remove the source field. Watch for: serialization (persisted field names!), ORM mappings, and reflective access — each makes this High risk.
**Risk:** Medium–High.

### Split Class
**When:** God Object / Divergent Change where *multiple* responsibility clusters exist — Extract Class repeated until each class has one reason to change.
**Mechanics:** Identify all clusters up front and plan the target shape; then execute as a sequence of Extract Class steps, largest/most-independent cluster first. Keep the original name on the cluster that best matches the class's published meaning; consumers of other clusters migrate to the new classes (Parallel Change if fan-in is large).
**Risk:** Medium–High depending on fan-in.

### Merge Duplicate Logic
**When:** Duplicate Code — identical or near-identical blocks in 2+ places.
**Mechanics:** (1) Diff the copies *carefully*; near-duplicates often hide an intentional divergence (a bug fix applied to one copy). If they differ, surface the difference to the user before merging — deciding which behavior is "correct" is a behavior change. (2) For identical copies: Extract Method/Function into the nearest common scope; replace each copy one at a time, verifying after each. (3) For structural duplicates that vary in a value → parameterize; vary in behavior → Extract Strategy or pass a function.
**Risk:** Low (identical, same file) → High (near-duplicates across modules).

## Simplifying conditionals

### Replace Nested If with Guard Clauses
**When:** Deep Nesting where the nesting handles special cases and the happy path is buried.
**Mechanics:** For each special case: invert the condition, handle it immediately (`return`/`throw`/`continue`), un-indent the remainder. Repeat until the main path reads top-to-bottom flat. Requires the branches to be exits — if both branches carry real logic, use Decompose Conditional (extract condition and branches into named methods) instead.
**Risk:** Low, but preserve evaluation order of conditions that have side effects or guard each other (`x != null` before `x.value`).

```ts
// Before                            // After
if (user) {                          if (!user) throw new NotFound();
  if (user.active) {                 if (!user.active) throw new Inactive();
    if (quota.ok(user)) {            if (!quota.ok(user)) throw new QuotaExceeded();
      /* real work */                /* real work — at top level */
    } else throw new QuotaExceeded();
  } else throw new Inactive();
} else throw new NotFound();
```

### Replace Switch
**When:** The same `switch`/`if-else` chain over a type code appears in more than one place, or grows a case per feature.
**Mechanics — pick the lightest sufficient form:** (1) A single switch in one place is often *fine* — leave it. (2) Data-driven: replace with a lookup table/map when cases differ only in values. (3) Behavior-driven: replace with a map of functions/handlers keyed by the case. (4) Full polymorphism (below) when cases carry state or multiple operations vary together. Ensure exhaustiveness stays checked — a compiler-verified switch replaced by a map can silently miss a case; keep a "no handler" failure path.
**Risk:** Low (table) → Medium (polymorphism).

### Replace Conditional with Polymorphism
**When:** Multiple operations branch on the *same* type discriminator — parallel switches over `shape.kind` in `area()`, `perimeter()`, `draw()`.
**Mechanics:** (1) Create the class/subtype hierarchy (or discriminated-union handlers) for the variants. (2) One operation at a time: push each branch body into its variant as an override; the original method delegates. (3) When all operations are pushed, the discriminator field and switches disappear. (4) Creation sites now need a Factory — see Introduce Factory.
**Risk:** Medium. Only worth it for *parallel* conditionals; a single switch does not justify a hierarchy.

### Replace Temp with Query
**When:** A local computed once then read in several places blocks Extract Method; or the same computation is duplicated as temps across methods.
**Mechanics:** (1) Confirm the computation is pure and its inputs don't change between the original computation point and the reads — otherwise extracting changes *when* it's evaluated, which is a behavior change. (2) Extract the expression into a method/getter; replace reads with calls. Note performance: re-evaluating an expensive query per call may need memoization — see `references/performance.md`.
**Risk:** Low (pure) / High (impure or time-sensitive).

## Data and encapsulation

### Replace Primitive with Object
**When:** Primitive Obsession — a bare primitive carries domain meaning, rules, or units.
**Mechanics:** (1) Create the type wrapping the primitive; validate in the constructor so invalid instances can't exist. (2) Parallel Change: accept/return both forms at the boundary while migrating; convert at the edges (parse, don't validate). (3) Migrate behavior that operated on the primitive into the type (Move Method). Keep value semantics: immutable, equality by value.
**Risk:** Medium; serialization boundaries (JSON, DB columns) need explicit conversion — keep the wire format identical.

### Introduce Value Object
**When:** Data Clumps; a group of values with joint invariants (`startDate ≤ endDate`); money, ranges, addresses, identifiers.
**Mechanics:** Same as Replace Primitive with Object but for a group: immutable class/record, constructor enforces cross-field invariants, equality by value, no identity. Then shrink signatures: `(startDate, endDate)` → `DateRange`, and move clump-related behavior (`overlaps`, `contains`) onto it.
**Risk:** Medium.

### Encapsulate Field
**When:** Missing Encapsulation — public mutable fields; invariants maintained by caller convention.
**Mechanics:** (1) Make the field private; add accessor(s) — but prefer intention-revealing operations over a bare setter (`deactivate()` over `setActive(false)`). (2) Migrate accesses (tool-assisted). (3) Move invariant maintenance into the mutators.
**Risk:** Low–Medium.

### Encapsulate Collection
**When:** A getter returns an internal mutable collection and callers mutate it directly.
**Mechanics:** (1) Add intention-revealing mutators (`addItem`, `removeItem`) that maintain invariants. (2) Migrate mutating call sites to them. (3) Change the getter to return a read-only view/copy. Do step 3 *last* — doing it first breaks every mutating caller at once. Decide view vs. copy consciously: a live read-only view changes under the caller's feet; a copy has cost and staleness. Match whichever matches current observable behavior.
**Risk:** Medium.

## Introducing design patterns

A pattern introduction is a *refactoring* only when it restructures existing behavior; each entry names the smell that earns it. If the smell isn't present, don't introduce the pattern.

### Extract Strategy
**When:** Divergent Change / Duplicate Code where variants of one algorithm are selected by conditionals or copy-pasted-with-edits; you need to add variants without touching existing ones.
**Mechanics:** (1) Define the strategy interface from what varies (one method is common). (2) Extract each variant branch into an implementation. (3) The host receives the strategy (parameter or injected) and delegates; the selection conditional collapses to choosing a strategy — often a lookup map or Factory.
**Risk:** Medium.

### Introduce Repository
**When:** Data-access code (SQL/ORM calls) scattered through business logic (Mixed Responsibilities); business rules untestable without a database.
**Mechanics:** (1) Define an interface named for the *domain* need (`OrderRepository.findOpenOrders()`, not `runQuery(sql)`). (2) Move existing queries behind it verbatim — do not "improve" the SQL while moving (two hats). (3) Inject the repository; business logic now tests against a fake. Keep queries parameterized when moving them — see `references/security.md`.
**Risk:** Medium.

### Introduce Factory
**When:** Complex construction logic duplicated at call sites; construction branching on type codes (often follows Replace Conditional with Polymorphism); constructors doing real work.
**Mechanics:** (1) Extract the construction snippet into a factory function/method (Extract Method applied to `new`). (2) Migrate creation sites. (3) If creation needs dependencies, make it a class and inject it. Prefer plain factory functions over Abstract Factory ceremony unless families of related objects genuinely vary together.
**Risk:** Low–Medium.

### Introduce Builder
**When:** Large Constructors — telescoping overloads, many optional parameters, callers passing `null`s.
**Mechanics:** In languages with named/default arguments or object literals, use those instead — Builder is often unnecessary ceremony. Otherwise: builder collects parameters via chained setters; `build()` validates completeness and constructs. Migrate the worst call sites first.
**Risk:** Low–Medium.

### Introduce Adapter
**When:** Tight Coupling to a third-party or legacy interface that leaks its types everywhere; consolidating two different interfaces for the same concept.
**Mechanics:** (1) Define the interface *your* code wants. (2) Implement it wrapping the foreign API; move all direct usages behind it one call site at a time. Your domain types stop importing theirs — which also creates the seam for testing and future replacement.
**Risk:** Medium.

### Introduce Facade
**When:** Every consumer of a subsystem repeats the same multi-call choreography ("configure, connect, begin, do, commit"); Message Chains into subsystem internals.
**Mechanics:** Extract the choreography (it already exists at call sites — this is Merge Duplicate Logic at a boundary) into one entry point with a use-case-shaped method. Migrate consumers; then you may tighten the subsystem's internal visibility.
**Risk:** Low–Medium.

### Introduce Decorator
**When:** Cross-cutting behavior (caching, retry, logging, metrics) interleaved with core logic in many methods, or bolted on via inheritance (`CachedRetryingHttpClient` class explosion).
**Mechanics:** Requires an interface (Extract Interface first). Implement the cross-cutting concern as a wrapper implementing the same interface, delegating to the wrapped instance. Strip the concern out of the core; compose at construction/DI time. Order of stacked decorators is behavior — document it.
**Risk:** Medium.

### Introduce Observer
**When:** A module directly calls back into modules that depend on it (Circular Dependency), or one action fans out into unrelated reactions hard-wired inline (order placement directly calling email, analytics, inventory...).
**Mechanics:** (1) Define the event and a subscribe mechanism on the producer. (2) Move each hard-wired reaction into a subscriber, one at a time, keeping order if reactions are order-sensitive — order sensitivity is observable behavior and a caution flag: observers make ordering implicit and error handling per-subscriber; if the reactions form a required sequence, an explicit orchestrator is more honest than events.
**Risk:** Medium–High.

### Introduce State
**When:** An object's behavior branches on a status field in many methods, with transition rules scattered and invalid transitions possible.
**Mechanics:** Replace Conditional with Polymorphism where the discriminator is the mutable status: one class per state implementing the operations, the host delegates to a current-state object, transitions return/set the next state. Centralizes the transition table; invalid transitions become unrepresentable or fail fast.
**Risk:** Medium–High (state machines are usually load-bearing; characterization-test the transitions first).

### Introduce Command
**When:** Operations need to be queued, undone, logged, or retried, and are currently inline method calls entangled with their invocation context.
**Mechanics:** Reify each operation as an object/closure carrying its parameters with an `execute()` (and `undo()` if needed). Extract the inline logic into commands one operation at a time; the invoker becomes generic.
**Risk:** Medium.

### Introduce Mediator
**When:** A cluster of components all reference each other pairwise (N² coupling) — classic in UI forms and multi-service orchestration.
**Mechanics:** (1) Create the mediator owning the interaction rules. (2) Reroute one pairwise interaction at a time through it; components end up knowing only the mediator. Watch that the mediator doesn't become a God Object — it should hold *interaction* logic only, not the components' own behavior.
**Risk:** Medium.

## Structural

### Introduce Dependency Injection
**When:** Tight Coupling via internal `new` of collaborators; hidden global/singleton access; untestable units.
**Mechanics:** (1) Extract Interface for the dependency if consumers should be isolated from the implementation. (2) Move construction out: accept the collaborator via constructor (default it to the old `new` temporarily to keep callers compiling — Parallel Change). (3) Push construction up the call graph to the composition root (`main`, container config, request setup). (4) Remove the temporary defaults. Constructor injection first; a DI *framework* is optional and a separate decision — manual wiring at the root is fine and often clearer.
**Risk:** Medium.

### Composition over Inheritance
**When:** Inheritance used for code reuse rather than true substitutability: subclasses overriding fragments of parent behavior, "base classes" that are really utility grab-bags, LSP violations (subclass throws on inherited method), deep fragile hierarchies.
**Mechanics:** (1) Identify what the subclass actually reuses. (2) Extract that into a component (Extract Class). (3) The former subclass holds the component and delegates; implements a shared interface (Extract Interface) if callers need polymorphism. (4) Dismantle the hierarchy one leaf at a time. High-value but wide-reaching — Parallel Change and strong tests.
**Risk:** High.

### Remove Dead Code
**When:** Dead Code — but only after *proving* deadness.
**Mechanics:** (1) Search all reference forms: direct calls, re-exports, reflection/metaprogramming, DI/container registration, route tables, config files, templates, serialized names, scheduled jobs, *other repositories* if the code is published. (2) Check whether it's a public API — external callers you can't see make removal a breaking change requiring deprecation instead. (3) Delete whole units (function + its tests + its now-unused helpers), not just bodies. (4) One deletion per commit for easy restore. Commented-out code and unreachable branches delete without ceremony.
**Risk:** Low (private, provably unreferenced) → High (published API).
