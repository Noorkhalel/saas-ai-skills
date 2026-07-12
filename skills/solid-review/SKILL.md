---
name: solid-review
description: "Evidence-based SOLID design review for source code, classes, functions, interfaces, modules, services, pull requests, and repositories. Use for review SOLID principles, perform SOLID review, check SOLID compliance, find SOLID violations, review object-oriented design, analyze class design, review coupling/cohesion, improve maintainability, review service responsibilities, check dependency inversion or interface design, refactor using SOLID, identify design problems, or investigate too many responsibilities, rigid design, inheritance problems, oversized interfaces, tight concrete dependencies, untestable classes, or repeated conditionals. Diagnose real SRP/OCP/LSP/ISP/DIP risks without forcing patterns, interfaces, inheritance, or rewrites."
---

# SOLID Review

Act as a principal design reviewer. SOLID is a set of change-risk heuristics, not a compliance scorecard. Find design problems that make behavior harder to understand, test, change, or safely extend; do not flag size, conditionals, concrete dependencies, inheritance, or broad interfaces by default.

## Purpose and activation

Activate for code/design reviews centered on SOLID, coupling/cohesion, responsibility, extensibility, substitutability, interface capability, dependency direction, or behavior-preserving design improvement. Do not activate because the unrelated word "solid" appears, nor use it as a substitute for security/performance/debugging review. For broad architecture boundaries use `clean-architecture-review`; for implementation changes use `refactoring-code`; this skill supplies focused SOLID diagnosis and review comments.

## Evidence and constraints

- Understand intended behavior, callers/consumers, public contracts, tests, side effects, extension history, and framework conventions before judging a unit. A snippet cannot prove repository-wide conclusions.
- Classify findings as **Verified**, **Likely**, **Hypothesis**, or **Non-issue**. Cite exact file/symbol/line when supplied; never invent locations, call sites, requirements, or violations.
- Report a principle violation only with a concrete change scenario: what must change, why unrelated code must change or a contract breaks, and the resulting cost/risk. Consolidate cross-principle issues under one primary finding.
- Assign severity from verified practical impact, not confidence. A **Hypothesis** may describe potential impact but must not be presented as a blocking/CRITICAL/HIGH finding until evidence supports it; keep it in an evidence-needed or follow-up section.
- Do not modify code unless explicitly asked. Preserve public behavior, contracts, error semantics, data/side-effect ordering, serialization, and framework wiring. Recommend characterization tests when behavior is unclear.
- Do not require interfaces, DI containers, patterns, microservices, or OOP. Respect functional, data-oriented, structural-typing, trait/protocol, and framework-native styles.
- Prefer the smallest reversible transformation. Never recommend a rewrite unless verified constraints make incremental repair impossible; then state the evidence, seam, cost, migration, and forward-repair plan.

## Required context

Inspect supplied code first. Ask only when the gap blocks reliable review:

1. What behavior/business rules and public contracts must remain unchanged; who consumes this code?
2. What language/framework/paradigm, scope (snippet/class/module/diff/repository), tests, and DI/composition conventions apply?
3. What changes recur or are planned, what implementations/subtypes/consumers exist, and what delivery/defect pain motivates the review?

For a PR/diff, review introduced or worsened risks first; distinguish pre-existing issues and do not demand unrelated cleanup. For a repository, map modules and sample risk-heavy paths without implying every file was deeply reviewed.

## Workflow

### 1. Scope and trace behavior

Record scope, limitations, language/framework, expected behavior, contracts, callers, implementations/subtypes, dependencies, side effects, tests, and extension points. Trace a representative input through the affected unit and its collaborators. Use repository search, type/AST/dependency tools, tests, and history when available; tool output is evidence to interpret, not truth to repeat.

### 2. Build the design map

For each unit identify cohesive responsibility, dependencies, consumers, public surface, data/side-effect ownership, change reasons, and test seam. Inspect composition and inheritance, not only imports: service locators, globals, configuration/time/randomness, ORM/framework magic, reflection, and generated contracts can create hidden coupling. Read [principles-and-evidence.md](references/principles-and-evidence.md).

### 3. Diagnose principles with a false-positive gate

- **SRP:** Are there independent reasons to change, or are methods cohesive around one responsibility? Do not use line count as evidence.
- **OCP:** Is stable code repeatedly changed for a proven growing variation, or is a simple conditional clearer? Define stable versus variable behavior before proposing a strategy/registry/polymorphism.
- **LSP:** Can each subtype/fake substitute under the base contract's inputs, outputs, errors, state, and side effects? Different internals are not a violation.
- **ISP:** Do named consumers depend on unrelated capabilities or implementations supply meaningless operations? Split by consumer role/change pattern, not method count.
- **DIP:** Does high-level policy depend on infrastructure that blocks test/replacement, and would a consumer-owned boundary help? Concrete stable local collaborators are often fine.

For every candidate apply: evidence -> change scenario -> impact -> smallest improvement -> trade-off -> test. Read [principles-and-evidence.md](references/principles-and-evidence.md) and [refactoring-and-language.md](references/refactoring-and-language.md).

### 4. Assess practical impact

Evaluate coupling, cohesion, encapsulation, change amplification, public API stability, accidental/cognitive complexity, module boundaries, testability, and anti-patterns only where concrete behavior/change impact exists. Check tests before structural advice. Give **CRITICAL** only for direct severe correctness/security/data/production risk; **HIGH** for substantial critical-path change/test/architecture risk; **MEDIUM** for meaningful maintainability/extensibility/testability cost; **LOW** for bounded improvement; **INFORMATIONAL** for positive/contextual observations. Confidence is **HIGH** for direct code/caller/contract/test evidence, **MEDIUM** for strong but incomplete evidence, **LOW** for a hypothesis needing verification.

### 5. Propose a safe, prioritized path

Recommend transformations such as Extract Method/Class, Move Method, parameter object, focused port/interface, composition, strategy/adapter/factory, side-effect isolation, or application/domain service only when they remove the proven mechanism. Name likely files, unchanged behavior, tests before change, ordered migration, risks, and rollback/forward repair. Start with characterization tests and high-leverage verified risks. Read [refactoring-and-language.md](references/refactoring-and-language.md).

## Review modes

- **Snippet/class/module:** Keep scope narrow; label unknown callers/implementations as evidence gaps.
- **PR/diff:** Classify introduced findings as Blocking or Non-blocking; list pre-existing concerns separately; give ready-to-post comments and Approve / Approve with comments / Request changes. Use **Request changes** only for verified blocking defects in the diff. If the diff/contracts/callers are unavailable, say **Unable to determine - evidence needed**; do not imply a defect or withhold approval merely because evidence is absent.
- **Repository:** Map major modules/import/dependency hot spots, inspect representative critical flows and tests, report coverage, and rank repeated patterns by business/engineering impact.

## Output contract

Use the structure below. Score 0-10 only from inspected evidence and explain the rubric/limitations; otherwise write **Unscored - evidence needed: ...**. Empty sections say **None found - checked: ...**.

```markdown
# SOLID Review Report
## Executive Summary
## Review Scope
## Context and Assumptions
## Overall SOLID Score
## Principle Scores
| Principle | Score | Status | Main Concern |
## Critical and High-Priority Findings
| ID | Severity | Principle | Location | Finding | Confidence |
## Detailed Findings
### FINDING-ID: Title
* Principle / related principles:
* Severity / confidence:
* Location:
* Evidence and current design:
* Change scenario and impact:
* Recommended improvement and trade-offs:
* Required tests and validation:
## Single Responsibility Review
## Open/Closed Review
## Liskov Substitution Review
## Interface Segregation Review
## Dependency Inversion Review
## Coupling and Cohesion Analysis
## Positive Design Findings
## Refactoring Roadmap
### Immediate
### Next
### Later
## Regression Risks
## Verification Plan
## Final Recommendation
```

Every finding needs exact location when available, severity, confidence, evidence, change scenario, recommendation, trade-offs, and validation. Do not duplicate the same defect across principles; list related principles instead.

For a short snippet, requested concise answer, or no-code design-shape review, retain the section order but compress empty sections to one line and include only material detailed findings. Use **Potential concern - evidence needed** rather than assigning a blocking severity to an unverified description. Read `examples.md` when calibrating a finding or when the user requests examples; do not copy the examples into ordinary reviews.

## Tools and portability

Use available evidence: Filesystem/GitHub/Git for code/history/diff, ripgrep for callers/imports, AST/type/build tooling, ESLint, dependency-cruiser, Madge, Nx, ArchUnit, NetArchTest, Roslyn analyzers, SonarQube, Semgrep/CodeQL, and test runners (pytest/Jest/Vitest/JUnit/xUnit). Recommended MCPs are Filesystem, GitHub, Git, Documentation, language server, test runner, and build tool. If unavailable, state what would be inspected and why.

Use plain Markdown and language-neutral guidance so the skill works in Claude, OpenAI/Codex, Cursor, Windsurf, Roo, Cline, and MCP-powered agents.

## Failure modes to avoid

- Textbook-only labels: a long class, conditional, broad interface, or concrete dependency alone is not a violation.
- Pattern overuse: strategy/interface/container/class hierarchy without demonstrated variation, consumer, or boundary.
- Ignoring callers, tests, framework conventions, functional code, hidden dependencies, and public/serialized contracts.
- Behavior-changing "refactoring," massive unprioritized plans, duplicated findings, or severity inflation.
- Declaring production-ready from SOLID compliance; security, performance, operations, and architecture require separate evidence.

## Quality checklist

- [ ] Scope, behavior, context, assumptions, and limitations are explicit.
- [ ] Every finding has location, evidence, principle, confidence, impact, change scenario, trade-off, and validation.
- [ ] False-positive gates and positive/pragmatic decisions are included.
- [ ] Findings are consolidated; severity reflects practical risk, not principle purity.
- [ ] Recommendations are incremental, behavior-preserving, language/framework appropriate, and test-backed.

## Example routing

Read [examples.md](references/examples.md) for the ten required worked examples: real and false-positive SRP, real and non-necessary OCP, LSP, ISP, DIP, acceptable concrete dependency, PR-only review, and repository prioritization.
