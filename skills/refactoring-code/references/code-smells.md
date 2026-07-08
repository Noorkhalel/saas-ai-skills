# Code Smell Catalog

A smell is not a bug — it is evidence that the structure will make the next change slower, riskier, or more error-prone. For each smell: how to detect it, why it hurts, and the fix (pattern names refer to `references/patterns.md`).

Use catalog names in reports. "Feature Envy at `order.ts:141`" points at a known fix; "this looks messy" points nowhere. Report the *evidence* alongside the name, and rate severity by how often the code changes and how many things depend on it — a God Object nobody touches is lower priority than a Long Method edited weekly.

## Contents

- [Bloaters](#bloaters) — God Object, Long Method, Long Class, Large Constructors, Deep Nesting, Data Clumps, Primitive Obsession
- [Couplers](#couplers) — Feature Envy, Tight Coupling, Circular Dependencies, Missing Encapsulation
- [Change preventers](#change-preventers) — Shotgun Surgery, Divergent Change, Mixed Responsibilities, Low Cohesion
- [Dispensables](#dispensables) — Duplicate Code, Dead Code, Lazy Class, Speculative Generality, Magic Numbers, Magic Strings
- [Clarity and correctness hazards](#clarity-and-correctness-hazards) — Poor Naming, Hidden Side Effects, Temporary Fields, Improper Error Handling

---

## Bloaters

### God Object
**Detect:** One class that knows or does too much: hundreds of lines, many unrelated fields, imported by everything, edited in most PRs regardless of feature. Often named `Manager`, `Service`, `Util`, `Context`, or after the app itself.
**Why it hurts:** Every change collides here — merge conflicts, unpredictable side effects, impossible to test in isolation. It grows because it's the easiest place to add code, which is exactly why it must be split.
**Fix:** Extract Class / Split Class along the axes of change; Move Method to relocate behavior to the data it uses; Extract Interface + Introduce Dependency Injection to break consumers' dependence on the whole object.

### Long Method
**Detect:** You can't summarize the method in one short sentence; it has comment-delimited sections ("// step 2: validate"); it mixes abstraction levels (business rules next to string formatting); it needs scrolling. Line counts are a heuristic, not a rule — a flat 30-line sequence can be fine; a dense 12-liner can be too much.
**Why it hurts:** Readers must simulate the whole method to understand any part. Sections can't be reused or tested independently.
**Fix:** Extract Method per coherent step, using the would-be comment as the name; Decompose Conditional; Replace Temp with Query to free tangled locals; Extract Variable to name sub-expressions.

### Long Class
**Detect:** Many fields used by disjoint subsets of methods; method names cluster into groups (`parse*`, `render*`, `save*`); tests for it require huge setup.
**Why it hurts:** Disjoint field/method clusters are separate responsibilities cohabiting — each with its own reasons to change (see Divergent Change).
**Fix:** Extract Class per cluster; Extract Module at file level; Introduce Value Object for field groups that travel together.

### Large Constructors
**Detect:** Constructor takes many parameters; callers pass `null`/defaults for most; construction logic contains branching; telescoping constructor overloads.
**Why it hurts:** Signals the class has too many dependencies (split it) or conflates configuration with construction. Positional argument lists breed transposition bugs.
**Fix:** If the parameters are dependencies → Extract Class (the class does too much). If they're data → Introduce Value Object / parameter object. If construction is genuinely complex → Introduce Builder or Introduce Factory.

### Deep Nesting
**Detect:** More than 2–3 levels of indentation; `if` inside `for` inside `if`; the happy path is buried at maximum depth; `else` branches far from their conditions.
**Why it hurts:** Each level multiplies the mental state a reader must track; deeply nested branches are where untested paths hide.
**Fix:** Replace Nested If with Guard Clauses (handle edge cases early, return, keep the main path flat); Extract Method for inner blocks; invert conditions; for loops, extract the body or use pipeline operations.

### Data Clumps
**Detect:** The same group of values travels together through signatures and fields: `(street, city, zip)`, `(startDate, endDate)`, `(host, port, timeout)`.
**Why it hurts:** The group has an identity and invariants (start ≤ end) that nothing enforces; adding a member means shotgun-editing every signature.
**Fix:** Introduce Value Object (`DateRange`, `Address`, `ConnectionConfig`); then behavior that belongs to the clump (validation, formatting) migrates into it via Move Method.

### Primitive Obsession
**Detect:** Domain concepts carried by bare primitives: `string email`, `int cents`, `string userId` and `string orderId` that can be swapped without a compile error. Validation and formatting of these values duplicated at call sites.
**Why it hurts:** The type system can't catch unit errors, ID mix-ups, or invalid states; every consumer re-validates (or forgets to).
**Fix:** Replace Primitive with Object / Introduce Value Object with validation in the constructor — invalid instances become unrepresentable. Extract Constant for fixed sentinel values.

## Couplers

### Feature Envy
**Detect:** A method reads or writes another object's data more than its own. Count the accesses: `customer.` six times, `this.` once — the method is homesick.
**Why it hurts:** The logic lives far from the data it governs, so a change to the data's rules must be discovered and applied in a different class — a Shotgun Surgery generator.
**Fix:** Move Method to the envied class. If it envies parts of several classes, Extract Method first to split it along envy lines, then move each piece.

### Tight Coupling
**Detect:** Classes construct their own dependencies (`new SmtpMailer()` inside business logic); reach through objects (`a.getB().getC().doThing()`); depend on concrete classes where an interface exists; can't be unit-tested without a database/network.
**Why it hurts:** Consumers are welded to implementations — no substitution, no testing in isolation, changes ripple through the chain.
**Fix:** Introduce Dependency Injection; Extract Interface for the seams; Introduce Facade or Adapter to collapse chains; Move Method when the reaching indicates misplaced behavior. See `references/architecture.md` for dependency direction rules.

### Circular Dependencies
**Detect:** Module A imports B and B imports (directly or transitively) A. Symptoms: import-order bugs, initialization failures, "temporary" lazy imports, inability to extract or test either module alone.
**Why it hurts:** The cycle is one de facto module pretending to be two — neither can be understood, built, or deployed independently.
**Fix:** Break the cycle at the weaker dependency: Extract Interface (one side depends on an abstraction — Dependency Inversion); Extract Module for the shared piece both actually need; Introduce Observer/events so the lower module signals without knowing the upper one; Move Method if something is simply in the wrong module.

### Missing Encapsulation
**Detect:** Public mutable fields; getters returning internal mutable collections (callers do `order.getItems().add(...)`); paired getter/setter for every field; invariants enforced by caller convention ("remember to call `recalculate()` after changing items").
**Why it hurts:** The class can't guarantee its own invariants — any caller anywhere can corrupt state, and you can't find who did.
**Fix:** Encapsulate Field; Encapsulate Collection (expose read-only views + intention-revealing mutators like `addItem`); move invariant maintenance inside those mutators.

## Change preventers

### Shotgun Surgery
**Detect:** One logical change requires small edits in many classes/files. Ask: "if the tax rules change, how many files do I touch?" If the answer is a list, that's the smell. Also visible in commit history: the same file sets changing together repeatedly.
**Why it hurts:** Every change risks missing one of the scattered sites; the miss compiles fine and fails in production.
**Fix:** Move Method / Move Field to gather the scattered responsibility into one home; Merge Duplicate Logic when the scattered edits are copies; Extract Class to give the concept an owner.

### Divergent Change
**Detect:** One class is edited for many unrelated reasons — new payment provider: edit `Order`; report format change: edit `Order`; validation rule: edit `Order`. The inverse of Shotgun Surgery.
**Why it hurts:** Unrelated concerns in one place mean unrelated teams/changes conflict, and any edit risks breaking the other concerns.
**Fix:** Extract Class per reason-to-change (this is the Single Responsibility Principle applied); Extract Strategy when the divergence is between behavioral variants.

### Mixed Responsibilities
**Detect:** A unit mixes *kinds* of work across abstraction layers: business rules interleaved with HTTP parsing, SQL strings, logging setup, or UI formatting. The one-sentence "This exists to ___" needs "and".
**Why it hurts:** The business logic can't be tested without the infrastructure, can't be reused in another entry point, and hides in the noise.
**Fix:** Extract Method to separate layers within the unit, then Extract Class/Module to give each layer a home; see the layering rules in `references/architecture.md`.

### Low Cohesion
**Detect:** A module's contents don't relate: utility grab-bags (`helpers.ts`, `common.py`), classes whose methods share no fields. High afferent coupling with no theme.
**Why it hurts:** Nothing findable, everything a dependency magnet — "utils" imports everywhere make refactoring anything harder.
**Fix:** Split Class / Extract Module by actual topic; move each piece next to its only consumer if it has just one (Move Method/Field); dissolve grab-bag modules entirely.

## Dispensables

### Duplicate Code
**Detect:** Identical or near-identical blocks in multiple places; parallel switch/if chains over the same cases in different files; "copy-paste-modify" siblings that differ in one line. Search for distinctive literals to find copies.
**Why it hurts:** The most expensive smell: fixes and rule changes must be applied N times, and the copies drift — the missed copy becomes a bug that only triggers on one path.
**Fix:** Merge Duplicate Logic (Extract Method/Function to a shared home). Near-duplicates: extract the common skeleton, parameterize the difference (or Extract Strategy if the difference is behavioral). Parallel case-chains: Replace Conditional with Polymorphism. Apply the Rule of Three — tolerate the second copy, refactor at the third — but *report* even the second.

### Dead Code
**Detect:** Unreferenced functions/classes/exports (verify with search *including* string-based references: reflection, DI wiring, routes, templates); unreachable branches; commented-out blocks; feature flags whose decision is long settled; parameters no caller varies.
**Why it hurts:** Readers spend effort understanding and preserving code with zero runtime value; it inflates search results and coverage denominators.
**Fix:** Remove Dead Code — deletion, after proving deadness (see mechanics in patterns.md). Version control remembers; commented-out code always deletes safely.

### Lazy Class
**Detect:** A class that doesn't earn its keep: one trivial method, pure pass-through to another class, or a leftover from a refactoring that emptied it.
**Why it hurts:** Indirection without abstraction — every reader pays a hop for no insight.
**Fix:** Inline it into its consumer (Inline Class); collapse pass-through delegation unless it's a deliberate boundary (Facade/Adapter at an architectural seam is *not* lazy).

### Speculative Generality
**Detect:** Abstractions with one implementation "for flexibility later"; unused hook parameters; generic type parameters instantiated one way; plugin systems with one plugin; layers that only forward.
**Why it hurts:** YAGNI violated: you pay complexity now for a future that usually never arrives — and when it does arrive, it's shaped differently than the speculation.
**Fix:** Remove the unused flexibility (collapse interface into the sole implementation, drop unused parameters). Reintroduce abstraction when the second real use case appears — it's cheap to add then and you'll know its real shape.

### Magic Numbers
**Detect:** Unexplained numeric literals in logic: `if (retries > 3)`, `price * 0.0825`, `buffer[1024]`. (Zero, one, and obvious indices usually don't count.)
**Why it hurts:** The reader can't tell meaning, provenance, or which occurrences are the *same* concept — so a rate change gets applied to two of the three places it appears.
**Fix:** Extract Constant with an intention-revealing name (`MAX_RETRIES`, `TEXAS_SALES_TAX_RATE`); if the value carries rules or units, go further: Replace Primitive with Object.

### Magic Strings
**Detect:** Bare string literals as behavior switches or keys: `if (status === "actve")` (note the typo — that's the point), `config["db_host"]`, event names, role names repeated across files.
**Why it hurts:** Typos compile and fail silently at runtime; renaming a key means an unsearchable hunt; the set of valid values is invisible.
**Fix:** Extract Constant; better, an enum/union type where the language has one — the compiler then enforces the valid set and finds all uses.

## Clarity and correctness hazards

### Poor Naming
**Detect:** Names that lie (`getUser()` also creates one), say nothing (`data2`, `handleStuff`, `temp`), require the body to understand (`process()`), or encode outdated meaning after the code changed around them.
**Why it hurts:** Names are the interface to human readers; a wrong name actively implants a false model, which is worse than no information.
**Fix:** Rename (tool-assisted) to intention-revealing names; if you can't name it, that usually means the unit mixes jobs — Extract Method/Class first, then the names come easily.

### Hidden Side Effects
**Detect:** Functions whose names promise a query but that mutate state, write files, send requests, or log-and-swallow: `getConfig()` that caches globally, `isValid()` that normalizes its input, property getters doing I/O.
**Why it hurts:** Callers reason from the name; a hidden effect breaks that reasoning at a distance — and makes refactoring *dangerous*, since reordering or deduplicating calls changes behavior.
**Fix:** Separate command from query (split into `validate()` and `normalize()`); make the effect explicit in the name at minimum; hoist effects to the edges so cores are pure. Treat any refactoring around hidden effects as high-risk.

### Temporary Fields
**Detect:** Instance fields that are only meaningful during one operation — set at the start of `calculate()`, read by its helpers, garbage otherwise; fields guarded by "is this set yet?" checks.
**Why it hurts:** Turns a method-local concern into object-wide mutable state: not thread-safe, order-dependent, and every reader must figure out the field's lifecycle.
**Fix:** Pass the values as parameters between the helpers; if the parameter list grows unwieldy, Extract Class — a method object whose fields legitimately live for exactly one computation.

### Improper Error Handling
**Detect:** Empty catch blocks; `catch (e) { log(e) }` then continuing as if it succeeded; catching broad `Exception` where a specific failure was meant; errors as sentinel values (`-1`, `null`, `""`) that callers forget to check; error paths with no tests; validation errors and system errors handled identically.
**Why it hurts:** Swallowed errors turn crashes into silent corruption discovered much later and far away; sentinel returns propagate invalid states through code that assumes success.
**Fix:** Make failures explicit: throw/return typed errors, narrow catch scopes, handle at the layer that can act, let the rest propagate. When refactoring, preserve *existing* error semantics exactly (contract rule 1) — flag improvements as recommendations, since callers may depend on the current behavior.
