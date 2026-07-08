# Architecture, Structure & Code Smells (Phases 2 and 7)

How to judge structure like a senior reviewer: principles as diagnostic lenses with named consequences — never acronym policing. An architecture finding must answer "what future change does this make expensive or dangerous?" If you can't name that change, it's taste, not a finding.

## Phase 2 — code quality and structure

**Readability & naming.** Names that lie (`getUser` also creates one) are HIGH-adjacent — they implant false models that cause the *next* bug; names that say nothing (`data2`, `handle`, `temp`) are MEDIUM; spelling/convention nits are LOW-batch material. A function whose body surprises you given its name is always reportable.

**Function/class size & complexity.** Judge by *responsibility count*, not line count: mixed abstraction levels (business rule next to string formatting), comment-delimited sections ("// step 2"), deep nesting (>2–3 levels — guard clauses fix most of it), boolean-flag parameters that fork behavior (two functions pretending to be one). A flat 40-line sequence can be fine; a dense 15-liner doing four jobs isn't.

**Duplication.** The most expensive smell — but verify it's *knowledge* duplication (same business rule in N places → will drift, HIGH-adjacent) vs coincidental similarity (two lookalike blocks that will evolve independently → merging them creates false coupling; not a finding). Parallel switch/if chains over the same cases in multiple files = the strongest signal (each new case is a shotgun edit).

**Dead weight.** Unused variables/params/imports/exports (verify with search before claiming — reflection, DI wiring, and dynamic access hide callers); commented-out code; unreachable branches; **speculative generality** — interfaces with one implementation, hooks nobody calls, config nobody sets. Unnecessary abstraction is a real cost: every layer that only forwards makes the next reader pay a hop for nothing.

**Classic smells worth naming** (names give the author a searchable fix): God object/function, feature envy (method mostly touching another object's data — it's in the wrong home), data clumps (same param group everywhere → parameter object), primitive obsession (domain meaning in bare strings/ints), shotgun surgery (one logical change → edits everywhere), temporal coupling (must call A before B, nothing enforces it), hidden side effects (query-named functions that mutate).

## SOLID — with judgment

Report the violation *by its consequence*, and only when the consequence is real:

- **SRP:** the class/module changes for unrelated reasons (payment logic edits and report-format edits both land here) — predicts merge conflicts and fear-driven development. Not: "this class has two methods."
- **OCP:** each new variant requires editing the same N files (parallel conditionals) — flag when the variant axis is *actually growing*; a stable 3-case switch is fine.
- **LSP:** subtype throws on inherited methods, or callers type-check before calling — the hierarchy is a lie; usually wants composition.
- **ISP:** implementations stubbing most of a fat interface; consumers recompiled/retested for members they never use.
- **DIP:** business logic importing concrete infrastructure (DB driver, HTTP client, vendor SDK) — untestable without the real thing, unswappable. The most consequential of the five in review practice.

**Coupling & cohesion in practice:** can this unit be tested without booting the world? (constructor `new`-ing its dependencies, global/singleton reach-ins, and env access scattered through logic all say no — dependency injection is the fix, and "hard to test" is the evidence to cite). Do the pieces of this module belong together, or is it a grab-bag (`utils.ts` absorbing everything — a dependency magnet)?

## Phase 7 — architecture review

**Dependency direction is the top check.** Domain/business logic must not import infrastructure, frameworks, or delivery mechanisms; dependencies point inward (Clean/Hexagonal). Concretely greppable: does `domain/`/`services/` import from `db/`, `http/`, framework packages, vendor SDKs? Each such arrow = the business logic can't be tested or reused without that machinery. Also: **circular dependencies** between modules (two modules that are secretly one — initialization bugs and extraction impossibility follow).

**Module boundaries.** Does each module have one describable responsibility and *own its data* (no other module touching its tables/stores directly — shared tables are the coupling that shows last and hurts most)? Do boundaries follow the domain (bounded contexts) or accidents of history? Layering skips (controller → DB directly, bypassing the service/domain layer that enforces the rules) mean invariants are enforceable only by memory.

**Cross-cutting placement.** Auth, tenancy, validation, transactions, logging: enforced at chokepoints (middleware, decorators, base classes) or copy-pasted per endpoint? Per-endpoint discipline is an architecture finding even when every current instance is correct — the next endpoint won't be.

**Scalability of the structure.** What breaks at 10×? — in-process state that prevents horizontal scaling (see stateless-process rule), synchronous chains that should queue, the module everything depends on (change bottleneck), background work done inline in requests.

**DDD & patterns as lenses.** Anemic domain model (all data-bags + one giant service layer holding every rule) vs rules living with their data; aggregate boundaries matching transaction needs. **Pattern misuse is as reportable as pattern absence:** factories/strategies/observers with one variant, event indirection where a function call was honest (debuggability sacrificed for nothing), abstraction layers wrapping vendor SDKs 1:1. The question is never "does it use pattern X" but "does the structure make the likely next changes cheap?"

## Severity guide for this file

| Finding | Typical severity |
|---------|------------------|
| Boundary violation enabling data corruption or bypassing invariant enforcement | HIGH |
| Dependency-direction violations, circular deps, missing chokepoint for authz/tenancy | HIGH |
| God object on the hot path of change, knowledge duplication, untestable core logic | MEDIUM–HIGH |
| Ordinary smells (naming, size, clumps), speculative generality | MEDIUM |
| Style, minor structure preferences | LOW, batched |

Architecture findings should come with the *incremental* path (extract module, introduce interface at the seam, move rule into the domain) — "restructure the app" is not a recommendation (see `SKILL.md` principle 4).
