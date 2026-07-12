# Overlap Analysis

Each overlap is intentional: skills share domain vocabulary but deliver different outcomes. Select the skill that owns the requested outcome, not every topic mentioned. Every case below is executable in `routing-tests.json`.

## `api-design-review` vs. `architecture-planning`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `architecture-planning`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `api-design-review` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Design the entire new SaaS architecture, including APIs." -> `architecture-planning`, not `api-design-review`.

## `api-design-review` vs. `database-design`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `api-design-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `database-design` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Design versioned REST resources for the existing billing domain." -> `api-design-review`, not `database-design`.

## `api-design-review` vs. `security-audit`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `api-design-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `security-audit` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Audit the public API contract for compatibility and idempotency." -> `api-design-review`, not `security-audit`.

## `architecture-planning` vs. `clean-architecture-review`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `clean-architecture-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `architecture-planning` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Review our existing repository architecture and boundaries." -> `clean-architecture-review`, not `architecture-planning`.

## `architecture-planning` vs. `database-design`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `architecture-planning`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `database-design` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Design a new SaaS system including storage and APIs." -> `architecture-planning`, not `database-design`.

## `architecture-planning` vs. `performance-optimization`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `architecture-planning`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `performance-optimization` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Plan a scalable architecture for a greenfield analytics product." -> `architecture-planning`, not `performance-optimization`.

## `clean-architecture-review` vs. `code-review`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `clean-architecture-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `code-review` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Audit boundaries and dependency direction across this repository." -> `clean-architecture-review`, not `code-review`.

## `clean-architecture-review` vs. `dependency-analysis`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `clean-architecture-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `dependency-analysis` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Assess whether module boundaries and dependency direction are healthy." -> `clean-architecture-review`, not `dependency-analysis`.

## `clean-architecture-review` vs. `solid-review`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `clean-architecture-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `solid-review` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Review framework leakage and clean boundaries in this repository." -> `clean-architecture-review`, not `solid-review`.

## `clean-architecture-review` vs. `refactoring-code`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `clean-architecture-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `refactoring-code` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Assess legacy layers and propose an incremental modernization path." -> `clean-architecture-review`, not `refactoring-code`.

## `code-review` vs. `security-audit`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `code-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `security-audit` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Review this PR for correctness, security, performance, and tests." -> `code-review`, not `security-audit`.

## `code-review` vs. `performance-optimization`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `code-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `performance-optimization` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Review this PR for correctness and production readiness." -> `code-review`, not `performance-optimization`.

## `code-review` vs. `dependency-analysis`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `code-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `dependency-analysis` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Review this changed service for bugs and maintainability." -> `code-review`, not `dependency-analysis`.

## `code-review` vs. `refactoring-code`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `code-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `refactoring-code` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Find bugs and risks in this pull request." -> `code-review`, not `refactoring-code`.

## `code-review` vs. `test-generation`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `code-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `test-generation` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Review this endpoint before merge." -> `code-review`, not `test-generation`.

## `codebase-understanding` vs. `security-audit`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `codebase-understanding`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `security-audit` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Where are authorization decisions made in this repository?" -> `codebase-understanding`, not `security-audit`.

## `codebase-understanding` vs. `debugging`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `codebase-understanding`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `debugging` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Map the order-submission request path in this unfamiliar service." -> `codebase-understanding`, not `debugging`.

## `database-design` vs. `performance-optimization`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `database-design`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `performance-optimization` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Design a tenant-safe PostgreSQL schema and migration plan." -> `database-design`, not `performance-optimization`.

## `database-design` vs. `security-audit`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `database-design`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `security-audit` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Review this ERD for integrity and tenant ownership rules." -> `database-design`, not `security-audit`.

## `database-design` vs. `debugging`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `debugging`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `database-design` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Why does this existing database query time out?" -> `debugging`, not `database-design`.

## `debugging` vs. `root-cause-analysis`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `debugging`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `root-cause-analysis` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "The checkout request fails now; identify and safely fix the cause." -> `debugging`, not `root-cause-analysis`.

## `debugging` vs. `performance-optimization`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `debugging`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `performance-optimization` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "The API returns 500 after deploy; reproduce and fix it." -> `debugging`, not `performance-optimization`.

## `debugging` vs. `test-generation`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `debugging`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `test-generation` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Why does this regression test fail intermittently?" -> `debugging`, not `test-generation`.

## `dependency-analysis` vs. `security-audit`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `dependency-analysis`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `security-audit` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Analyze this lockfile for obsolete packages and a safe upgrade path." -> `dependency-analysis`, not `security-audit`.

## `dependency-analysis` vs. `performance-optimization`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `dependency-analysis`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `performance-optimization` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Find duplicate packages and import cycles in this monorepo." -> `dependency-analysis`, not `performance-optimization`.

## `design-pattern-advisor` vs. `refactoring-code`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `design-pattern-advisor`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `refactoring-code` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Should this provider switch use Strategy, Factory, or a map?" -> `design-pattern-advisor`, not `refactoring-code`.

## `design-pattern-advisor` vs. `solid-review`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `design-pattern-advisor`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `solid-review` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Is Strategy appropriate for this extension point?" -> `design-pattern-advisor`, not `solid-review`.

## `design-pattern-advisor` vs. `clean-architecture-review`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `design-pattern-advisor`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `clean-architecture-review` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Choose a pattern for this plugin extension point." -> `design-pattern-advisor`, not `clean-architecture-review`.

## `performance-optimization` vs. `root-cause-analysis`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `performance-optimization`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `root-cause-analysis` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Profile and reduce p95 latency for this API." -> `performance-optimization`, not `root-cause-analysis`.

## `performance-optimization` vs. `refactoring-code`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `performance-optimization`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `refactoring-code` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Measure memory use and reduce it without regressing throughput." -> `performance-optimization`, not `refactoring-code`.

## `refactoring-code` vs. `solid-review`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `refactoring-code`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `solid-review` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Refactor this God class without changing behavior." -> `refactoring-code`, not `solid-review`.

## `solid-review` vs. `code-review`

- Why it exists: adjacent scopes share domain vocabulary.
- Winner: `solid-review`.
- Why: Choose the skill that owns the request's primary deliverable; incidental adjacent concerns remain secondary.
- Should overlap remain: yes; separate scopes preserve useful specialist depth.
- Routing guidance: `code-review` must not activate for this request; redirect when its primary deliverable is requested.
- Test: "Assess these classes specifically for SRP, ISP, and DIP risks." -> `solid-review`, not `code-review`.

## `codebase-understanding` vs. `clean-architecture-review`

- Why it exists: both inspect existing repositories and dependency direction.
- Winner: `codebase-understanding` when the requested deliverable is a current-state map before judgment.
- Why: discovery produces verified entry points, modules, and flows; architecture review owns the subsequent assessment.
- Should overlap remain: yes; preserving this boundary prevents unsolicited architecture findings during reconnaissance.
- Test: "Understand this unfamiliar codebase's modules and entry points before an architecture review." -> `codebase-understanding`, not `clean-architecture-review`.

## `codebase-understanding` vs. `code-review`

- Why it exists: both read implementation and callers.
- Winner: `codebase-understanding` when the user asks to trace current behavior before evaluating quality.
- Why: a flow map is evidence preparation, while code review owns correctness and production-readiness findings.
- Should overlap remain: yes; it keeps discovery free of unsupported review conclusions.
- Test: "Understand this codebase and trace the checkout request path before reviewing any implementation quality." -> `codebase-understanding`, not `code-review`.

## `refactoring-code` vs. `test-generation`

- Why it exists: safe refactoring relies on tests and test generation can recommend refactoring for untestable code.
- Winner: `refactoring-code` when structural implementation is the requested deliverable and existing tests are the guard.
- Why: tests are verification evidence in this case, not the primary artifact.
- Should overlap remain: yes; it prevents a requested refactor from being reduced to a test-only response.
- Test: "Refactor this class without changing behavior; existing tests are green and test creation is not the requested deliverable." -> `refactoring-code`, not `test-generation`.
