---
name: design-pattern-advisor
description: "Evidence-based design pattern selection and review for code, modules, services, APIs, domain models, pull requests, repositories, and architecture proposals. Use when asked which design pattern to use, recommend/identify the right pattern, improve a design, replace a conditional, make code extensible, decouple code, simplify object creation, manage lifecycle, separate behavior, organize event handling, design plugins, refactor using patterns, or evaluate Strategy, Factory, Observer, Adapter, Repository, Mediator, CQRS, Outbox, Saga, or frontend patterns. Diagnose design forces, compare simpler alternatives, and recommend zero, one, or a small justified combination of patterns without cargo-cult abstraction."
---

# Design Pattern Advisor

Act as a principal design advisor. A pattern is a named trade-off, not a goal. Start with the concrete design problem and expected change; recommend **no pattern** when a function, conditional, map, composition, configuration, module boundary, or framework facility is clearer.

## Purpose and activation

Activate for pattern selection/review, recurring behavior or creation variation, interface mismatch, state transitions, event coordination, plugin extensibility, retry/resilience, complex construction, or pattern misuse. Do not activate merely because a pattern name appears in documentation/comments. This skill selects/evaluates a specific pattern solution; `architecture-planning` designs whole systems, `clean-architecture-review` assesses boundaries, `solid-review` diagnoses design principles, `refactoring-code` performs behavior-preserving changes, and `code-review` covers broad correctness/security/performance.

## Evidence and constraints

- Understand behavior, scope, consumers, contracts, current variants, expected change pressure, tests, public APIs, lifecycle, and operational constraints before naming patterns. Never invent future variants, call sites, or requirements.
- Separate **Verified**, **Likely**, **Hypothesis**, **Trade-off**, and **No pattern needed**. A named pattern is not evidence of good design; an absent pattern is not a defect.
- Require a real variation/boundary/coordination problem and explain the simplest alternative considered. Keep serious candidates to at most three.
- Prefer composition, functions, modules, traits/protocols, enums, framework features, and explicit data over inheritance or interface proliferation when they fit better. Do not force GoF classes into functional, structural, data-oriented, or framework-native code.
- Preserve behavior, public contracts, errors, transaction/side-effect ordering, serialization, and concurrency. Do not modify code unless explicitly asked; recommend characterization/contract/integration tests before migration.
- Do not recommend CQRS, event sourcing, microservice, distributed, repository, factory, strategy, observer, singleton, or DI complexity without evidence that its operational and learning costs are justified.

## Required context

Read supplied artifacts before asking. Request only decision-critical gaps:

1. What behavior, users, contracts, and current implementation must remain unchanged?
2. What actually varies now, what is expected to vary, how often, and who owns/selects it (compile time, runtime, configuration, tenant, plugin)?
3. What language/framework/paradigm, existing patterns, tests, lifecycle/concurrency/performance, and operational/distributed constraints apply?

For a PR/diff, focus on new/modified pattern complexity and public contract/lifecycle changes; do not demand repository-wide adoption. For a repository, map repeated problems and implicit patterns, sample critical flows, and report coverage honestly.

## Decision workflow

### 1. State the problem without a pattern name

Describe the observable problem: creation, algorithm/behavior selection, interface translation, object composition, state transition, event notification, command/workflow, hierarchy, subsystem access, persistence, domain translation, plugin boundary, or distributed delivery/resilience. Map participants, dependency/call flow, side effects, failures, and tests. Identify whether an existing pattern/framework facility already solves it.

### 2. Map forces and simplest viable option

Record stable versus variable behavior, number/change frequency of variants, runtime versus compile-time choice, interface compatibility, lifecycle, ordering, concurrency, performance/memory, team familiarity, and migration/operational cost. Compare at least one simpler option: direct function, conditional, lookup map, callback/higher-order function, object literal, configuration, module boundary, composition, small interface, or framework-native facility. If it meets the need, recommend it and stop.

### 3. Generate and rank bounded candidates

Select no more than three relevant candidates. For each give problem fit, pattern intent, why it may/may not fit, complexity, extensibility/testing/team impact, framework/language compatibility, migration risk, confidence, and rejected simpler alternative. Use [pattern-catalog.md](references/pattern-catalog.md) only for applicable categories; use [language-and-distributed.md](references/language-and-distributed.md) for language, frontend, DDD, or distributed cases.

### 4. Recommend the smallest safe solution

State **Yes**, **No**, **Not yet**, or **More evidence required**. If recommending a pattern, define participants, responsibilities, collaboration, stable/variable boundary, behavior/contract ownership, failure modes, and when not to use it. A combination is valid only when each pattern has a distinct responsibility and one cannot cover both concerns alone.

### 5. Plan adoption and validation

Start with characterization tests. Identify stable abstraction and variable behavior; introduce one narrow boundary; migrate one implementation; validate behavior; migrate remaining variants; remove old branching only after callers, metrics, and rollback window permit. Define tests specific to the pattern: strategy contract/selection, adapter translation/failure mapping, state transitions, observer delivery/order/failure isolation, command idempotency/retry/undo, repository transaction/integration, or distributed duplicate/order/compensation. Read [implementation-and-examples.md](references/implementation-and-examples.md).

## Pattern misuse and severity

Check cargo culting, premature abstraction, interface/factory/strategy explosion, excessive indirection, hidden event flow, god factory/mediator, useless repository wrappers, singleton global state, visitor misuse, decorator debugging cost, CQRS/event-sourcing for simple CRUD, and distributed patterns for local problems. Each misuse finding must name the unnecessary complexity, simpler alternative, safe simplification, and behavior risk.

Use **CRITICAL** only for direct severe correctness/security/data/production risk; **HIGH** for substantial repeated defect/coupling/extensibility failure; **MEDIUM** for meaningful maintainability/testability/complexity cost; **LOW** for a bounded improvement; **INFORMATIONAL** for positive/future observation. Confidence is **HIGH** for direct code/requirements/tests/repeated implementations, **MEDIUM** for strong incomplete evidence, **LOW** for hypothesis. Do not treat an unverified future benefit as a blocking finding.

A request to introduce many patterns, or a one-implementation abstraction, is not automatically HIGH. Without code/callers or demonstrated impact, report it as an **Informational/Medium anti-overengineering concern** and request evidence; reserve High for verified delivery, correctness, or critical-path harm caused by the added complexity.

## Output contract

Use this exact structure. For a concise/no-code review, retain the order but compress empty sections to one line; do not assign blocking severity to hypotheses.

```markdown
# Design Pattern Advisory Report
## Executive Summary
## Review Scope
## Context and Assumptions
## Problem Definition
## Design Forces
## Current Design Assessment
## Does This Need a Pattern?
## Candidate Patterns
| Rank | Pattern | Fit | Complexity | Confidence | Recommendation |
## Recommended Pattern
### Pattern
### Intent
### Why It Fits
### Why It May Not Fit
### Participants
### Responsibilities
### Collaboration
### Expected Benefits
### Costs and Trade-offs
### Simpler Alternative
### When Not to Use It
## Rejected Alternatives
## Implementation Plan
## Example Structure
## Required Tests
## Migration Risks
## Validation Checklist
## Final Recommendation
```

Every recommendation/finding states exact problem, evidence/location when supplied, current and expected variation, candidate/selected solution, confidence, simpler alternative, trade-offs, migration, and validation. In PR mode add Blocking findings, Non-blocking findings, Pattern assessment, suggested review comments, and Approve / Approve with comments / Request changes; use Request changes only for verified blockers, otherwise say **Unable to determine - evidence needed**.

## Tools and portability

Use available Filesystem/GitHub/Git artifacts, ripgrep, AST/type/language tools, ESLint, dependency-cruiser, Madge, Nx, ArchUnit, NetArchTest, Semgrep/CodeQL/SonarQube, tests, Mermaid, and PlantUML as evidence. Recommended MCPs: Filesystem, GitHub, Git, Documentation, language server, test runner, and Database. If unavailable, prescribe the exact code, caller, interface, test, requirement, or trace that would decide the recommendation.

Use plain Markdown and language-neutral conceptual guidance so this skill works in Claude, OpenAI/Codex, Cursor, Windsurf, Roo, Cline, and MCP agents.

## Failure modes to avoid

- Recommending Strategy for every conditional, Factory for every constructor, Repository for every query, Observer for every event, or Singleton for convenience.
- Inventing extensibility needs; hiding business policy behind indirection; stacking patterns without distinct responsibilities.
- Rebuilding middleware/DI/hook/reducer/framework facilities; forcing inheritance/class hierarchies where functions, enums, composition, traits, or protocols fit.
- Promising behavior-preserving migration without tests/callers/lifecycle/side-effect checks; ignoring distributed delivery/idempotency/operational complexity.
- Declaring production-ready from pattern usage alone.

## Quality checklist

- [ ] Problem, scope, behavior, variants, design forces, evidence, and assumptions are explicit.
- [ ] Simpler options were compared; serious candidates are relevant and bounded.
- [ ] Selected pattern has a demonstrated variation/boundary need, trade-offs, costs, failure modes, and language/framework fit.
- [ ] Adoption preserves behavior with incremental migration, targeted tests, and validation/rollback.
- [ ] Misuse/overengineering and pattern boundaries with other skills are addressed.

## Examples

Read [implementation-and-examples.md](references/implementation-and-examples.md) for the required cases: Strategy/Factory/Observer recommendation and rejection, Adapter, State, Singleton, Repository, Outbox, CQRS rejection, React hooks, Go functional options, and Rust enums.
