# Routing Matrix

Route by the user's primary deliverable, not an incidental noun. When a request asks for two independent deliverables, ask which comes first or keep work limited to the explicitly primary one. Routing guidance never creates a dependency between skills.

## `api-design-review`

| Field | Value |
|---|---|
| Primary responsibility | API/interface contract |
| Secondary responsibilities | Compatibility, auth, resilience, documentation |
| Explicit exclusions | Whole-system blueprint; schema-only work; generic implementation review |
| Closest related skills | architecture-planning, database-design, security-audit |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Design this OpenAPI contract." |
| SHOULD NOT activate | "Design our entire new SaaS." |

## `architecture-planning`

| Field | Value |
|---|---|
| Primary responsibility | Future system blueprint |
| Secondary responsibilities | Data/API ownership, topology, delivery phases |
| Explicit exclusions | Existing-repository audit; PR review; incident diagnosis |
| Closest related skills | clean-architecture-review, api-design-review, database-design |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Design a new multi-tenant SaaS." |
| SHOULD NOT activate | "Review our existing architecture." |

## `clean-architecture-review`

| Field | Value |
|---|---|
| Primary responsibility | Existing architecture/boundary audit |
| Secondary responsibilities | Dependencies, coupling, modernization |
| Explicit exclusions | Greenfield design; narrow PR review; implementation change |
| Closest related skills | architecture-planning, code-review, dependency-analysis |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Audit repository layers and dependencies." |
| SHOULD NOT activate | "Design architecture for a new product." |

## `code-review`

| Field | Value |
|---|---|
| Primary responsibility | Broad implementation/PR review |
| Secondary responsibilities | Correctness, relevant security/performance/tests |
| Explicit exclusions | Security-only audit; measured tuning; test creation |
| Closest related skills | security-audit, performance-optimization, test-generation |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Review this PR before merge." |
| SHOULD NOT activate | "Perform a security audit of this repo." |

## `codebase-understanding`

| Field | Value |
|---|---|
| Primary responsibility | Repository discovery and tracing |
| Secondary responsibilities | Ownership, entry points, change maps |
| Explicit exclusions | Prescriptive design; findings audit; implementation |
| Closest related skills | debugging, security-audit, architecture-planning |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Where is invoice authorization implemented?" |
| SHOULD NOT activate | "Audit invoice authorization." |

## `database-design`

| Field | Value |
|---|---|
| Primary responsibility | Schema/data-store design |
| Secondary responsibilities | Integrity, tenancy, migrations, indexes |
| Explicit exclusions | System blueprint; live query debugging; generic audit |
| Closest related skills | architecture-planning, performance-optimization, security-audit |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Design tenant tables and constraints." |
| SHOULD NOT activate | "Why does this query time out?" |

## `debugging`

| Field | Value |
|---|---|
| Primary responsibility | Active defect investigation |
| Secondary responsibilities | Reproduction, proximate cause, safe fix |
| Explicit exclusions | Systemic postmortem; generic tuning; broad review |
| Closest related skills | root-cause-analysis, performance-optimization, test-generation |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Why does checkout fail now?" |
| SHOULD NOT activate | "Write a postmortem for last month?s outage." |

## `dependency-analysis`

| Field | Value |
|---|---|
| Primary responsibility | Dependency graph and lifecycle |
| Secondary responsibilities | Upgrades, cycles, supply-chain, licenses |
| Explicit exclusions | Broad attack-surface audit; generic bug fix |
| Closest related skills | security-audit, clean-architecture-review, performance-optimization |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Plan safe lockfile upgrades." |
| SHOULD NOT activate | "Audit all application security." |

## `design-pattern-advisor`

| Field | Value |
|---|---|
| Primary responsibility | Pattern choice/misuse assessment |
| Secondary responsibilities | Trade-offs and simpler alternatives |
| Explicit exclusions | Implementation refactor; SOLID audit; broad review |
| Closest related skills | refactoring-code, solid-review, code-review |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Strategy, Factory, or map?" |
| SHOULD NOT activate | "Refactor this code into Strategy." |

## `performance-optimization`

| Field | Value |
|---|---|
| Primary responsibility | Measured performance improvement |
| Secondary responsibilities | Profiling, experiments, benchmarks |
| Explicit exclusions | Generic cleanup; unmeasured postmortem |
| Closest related skills | debugging, root-cause-analysis, database-design |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Profile and reduce p95 latency." |
| SHOULD NOT activate | "The API returns 500; fix it." |

## `refactoring-code`

| Field | Value |
|---|---|
| Primary responsibility | Behavior-preserving restructuring |
| Secondary responsibilities | Decomposition, modernization, test guards |
| Explicit exclusions | Review-only report; new feature; behavior-changing fix |
| Closest related skills | code-review, solid-review, design-pattern-advisor |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Refactor this God class safely." |
| SHOULD NOT activate | "Find bugs in this PR." |

## `root-cause-analysis`

| Field | Value |
|---|---|
| Primary responsibility | Systemic incident postmortem |
| Secondary responsibilities | Timeline, causal chain, prevention |
| Explicit exclusions | Live generic debugging; tuning; broad audit |
| Closest related skills | debugging, performance-optimization, security-audit |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Explain and prevent this recurring outage." |
| SHOULD NOT activate | "Find and fix this current stack trace." |

## `security-audit`

| Field | Value |
|---|---|
| Primary responsibility | Security-led posture/exploitability audit |
| Secondary responsibilities | Threat model, auth, cloud, AI, supply chain |
| Explicit exclusions | Generic review; data modeling; non-security debugging |
| Closest related skills | code-review, dependency-analysis, database-design |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Audit tenant isolation and attack paths." |
| SHOULD NOT activate | "Review this PR for general readiness." |

## `solid-review`

| Field | Value |
|---|---|
| Primary responsibility | SOLID-focused design diagnosis |
| Secondary responsibilities | Responsibilities, interfaces, DIP |
| Explicit exclusions | Whole architecture; implementation refactor; pattern choice |
| Closest related skills | clean-architecture-review, refactoring-code, design-pattern-advisor |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Assess SRP/ISP/DIP risks." |
| SHOULD NOT activate | "Make these classes SOLID." |

## `test-generation`

| Field | Value |
|---|---|
| Primary responsibility | Automated test generation |
| Secondary responsibilities | Regression, integration, E2E, fixtures |
| Explicit exclusions | Unknown-cause debugging; code review; architecture design |
| Closest related skills | debugging, code-review, refactoring-code |
| Escalation rule | Use the specialist whose primary deliverable is requested; preserve this skill only for its stated scope. |
| SHOULD activate | "Write regression tests for this fixed bug." |
| SHOULD NOT activate | "Why does this test fail?" |
