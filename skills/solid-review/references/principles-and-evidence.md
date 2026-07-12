# SOLID diagnostics and evidence

## SRP: one coherent reason to change

Find independent responsibilities, not many methods. A service that validates an order, decides domain policy, persists it, formats an email, and sends it has distinct business, persistence, presentation, and delivery reasons to change. Extract around cohesive boundaries and preserve transaction/side-effect ordering. A class with parsing, validation, and formatting methods all serving one invoice-import responsibility can be cohesive; do not split it merely because it is long.

## OCP: demonstrated variation, not anti-conditional dogma

Look for repeated edits to a stable dispatch point as new variants arrive, scattered provider/type branches, or a change surface that grows with each supported variant. Separate stable orchestration from variable behavior, then consider a strategy/handler/adapter/registry/configuration. A closed two-case rule with no expected variants is often clearer as a conditional. Count current variants, change frequency, and consumer/operating cost before adding indirection.

## LSP: observable contract preservation

Establish base preconditions, postconditions, errors, nullability, mutability, side effects, ordering, and invariants from callers/types/docs/tests. A subtype that throws `UnsupportedOperation`, rejects previously valid input, weakens an output guarantee, or changes a required side effect violates substitution. A different algorithm or stricter internal invariant is fine if callers observe the same contract. Prefer a narrower abstraction, capability split, composition, or contract redesign over a fake override.

## ISP: consumer capabilities

Map consumers to methods/capabilities. A read-only reporting client forced to depend on unrelated administrative methods such as `exportAuditLog`, `resetPassword`, and `deleteTenant` has a meaningful ISP risk if interface evolution/deployment/testing are coupled. Split into cohesive read/admin/audit capabilities only when consumer roles/change patterns diverge. A broad cohesive interface with one implementation and one consumer is not automatically wrong.

## DIP: policy owns the boundary it consumes

Trace high-level policy to concrete database, HTTP, cloud SDK, Prisma/Supabase client, payment SDK, file, clock, random, environment, email, message, or service-locator dependency. It is a DIP issue when infrastructure volatility/testing/replacement leaks into policy and a stable consumer-owned boundary would reduce it. Do not wrap a local pure formatter or stable language collection in an interface. Functions, protocols, traits, structural types, parameter objects, and test doubles can be the appropriate seam; a container is optional.

## Evidence record

For each finding record the exact location and scope, observed code/caller/test/contract fact, the inferred mechanism, a realistic next change/failure scenario, affected consumer/capability, severity, confidence, counter-evidence, and the cheapest validation. Mark findings **Verified**, **Likely**, **Hypothesis**, **Trade-off**, or **Non-issue**. Consolidate a single mechanism with related principles: for example, a god service may have primary SRP and related DIP concerns.

## Smell translation

God class/service, fat controller, shotgun surgery, divergent change, feature envy, inappropriate intimacy, refused bequest, parallel inheritance, message chains, middle man, service locator, hidden dependency, interface explosion, abstraction leakage, and speculative generality are useful labels only when tied to an engineering consequence. They are not severity by themselves.
