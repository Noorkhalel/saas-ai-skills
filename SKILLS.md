# Skills Catalog

This catalog is generated from the canonical `skills/<folder>/SKILL.md` structure. Installation identifiers are the folder names. Install a selected skill with `npx skills add noorkhalel/saas-ai-skills --skill <folder>`.

| Skill | Folder | Category | Description | Installation |
|---|---|---|---|---|
| [API Design Review](skills/api-design-review/SKILL.md) | [api-design-review](skills/api-design-review/) | API Design | Reviews REST, GraphQL, gRPC, realtime, OpenAPI, and AI API contracts. | `--skill api-design-review` |
| [Architecture Planning](skills/architecture-planning/SKILL.md) | [architecture-planning](skills/architecture-planning/) | SaaS Architecture | Plans production architecture, SaaS boundaries, data, cloud, and delivery. | `--skill architecture-planning` |
| [Clean Architecture Review](skills/clean-architecture-review/SKILL.md) | [clean-architecture-review](skills/clean-architecture-review/) | Code Quality | Reviews architectural boundaries, dependency direction, and modernization paths. | `--skill clean-architecture-review` |
| [Code Review](skills/code-review/SKILL.md) | [code-review](skills/code-review/) | Code Quality | Reviews correctness, security, performance, maintainability, and tests. | `--skill code-review` |
| [Codebase Understanding](skills/codebase-understanding/SKILL.md) | [codebase-understanding](skills/codebase-understanding/) | Developer Workflow | Maps unfamiliar repositories and focused change paths using evidence. | `--skill codebase-understanding` |
| [Database Design](skills/database-design/SKILL.md) | [database-design](skills/database-design/) | Database Design | Designs SaaS schemas, tenancy, migrations, security, and operations. | `--skill database-design` |
| [Debugging](skills/debugging/SKILL.md) | [debugging](skills/debugging/) | Debugging | Diagnoses software failures with reproducible evidence. | `--skill debugging` |
| [Dependency Analysis](skills/dependency-analysis/SKILL.md) | [dependency-analysis](skills/dependency-analysis/) | Dependency Management | Audits package, module, runtime, service, and supply-chain dependencies. | `--skill dependency-analysis` |
| [Design Pattern Advisor](skills/design-pattern-advisor/SKILL.md) | [design-pattern-advisor](skills/design-pattern-advisor/) | Software Design | Selects the simplest justified design pattern or no pattern. | `--skill design-pattern-advisor` |
| [Performance Optimization](skills/performance-optimization/SKILL.md) | [performance-optimization](skills/performance-optimization/) | Performance | Profiles and improves full-stack SaaS performance with validation. | `--skill performance-optimization` |
| [Refactoring Code](skills/refactoring-code/SKILL.md) | [refactoring-code](skills/refactoring-code/) | Refactoring | Safely improves internal structure while preserving behavior. | `--skill refactoring-code` |
| [Root Cause Analysis](skills/root-cause-analysis/SKILL.md) | [root-cause-analysis](skills/root-cause-analysis/) | Incident Response | Builds postmortems and systemic corrective actions. | `--skill root-cause-analysis` |
| [Security Audit](skills/security-audit/SKILL.md) | [security-audit](skills/security-audit/) | Security | Audits application, cloud, API, data, and AI security. | `--skill security-audit` |
| [SOLID Review](skills/solid-review/SKILL.md) | [solid-review](skills/solid-review/) | Code Quality | Reviews practical SRP, OCP, LSP, ISP, and DIP risks. | `--skill solid-review` |
| [Test Generation](skills/test-generation/SKILL.md) | [test-generation](skills/test-generation/) | Testing | Designs deterministic unit, integration, and end-to-end tests. | `--skill test-generation` |

## Selection boundaries

- Use **Codebase Understanding** before other skills when repository context is missing.
- Use **Architecture Planning** for future system design; **Clean Architecture Review** for current boundaries; **SOLID Review** for focused design-principle issues.
- Use **Code Review** for broad quality/correctness; **Refactoring Code** when implementing behavior-preserving structural changes; **Design Pattern Advisor** only to select/evaluate a pattern.
- Use **Debugging** for an active defect and **Root Cause Analysis** for systemic incident analysis after or alongside investigation.
- Use **Dependency Analysis** for package/module/runtime dependency risk, **Security Audit** for broad security, and **Performance Optimization** for measured bottlenecks.
