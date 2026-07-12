![Image](a33eb099-f775-42d6-9c08-5d08cd80f398.png)
# SaaS AI Skills Collection

[![skills.sh](https://skills.sh/b/noorkhalel/saas-ai-skills)](https://skills.sh/noorkhalel/saas-ai-skills)

An open-source collection of independent AI Skills for building, operating, securing, testing, and improving modern SaaS applications. The repository currently contains **15 independent AI Skills**. Each one is self-contained, portable, and designed to give coding agents a disciplined, evidence-based workflow.

## Why this exists

SaaS work crosses architecture, APIs, databases, auth, operations, incidents, and AI integrations. These skills help agents apply the right specialist workflow without coupling skills together or hiding their instructions in a monolithic prompt.

Benefits include clearer planning, safer repository changes, stronger reviews, reproducible investigations, and a catalog that scales as the collection grows.

## Skill overview

| Skill | Purpose | Category | Link |
|---|---|---|---|
| API Design Review | Review API contracts and production readiness. | API Design | [skill](skills/api-design-review/SKILL.md) |
| Architecture Planning | Plan production SaaS architecture before implementation. | SaaS Architecture | [skill](skills/architecture-planning/SKILL.md) |
| Clean Architecture Review | Review boundaries, dependencies, and maintainability. | Code Quality | [skill](skills/clean-architecture-review/SKILL.md) |
| Code Review | Perform senior-engineer correctness and quality review. | Code Quality | [skill](skills/code-review/SKILL.md) |
| Codebase Understanding | Build evidence-based repository context before changes. | Developer Workflow | [skill](skills/codebase-understanding/SKILL.md) |
| Database Design | Design production SaaS data models and migrations. | Database Design | [skill](skills/database-design/SKILL.md) |
| Debugging | Diagnose failures from evidence. | Debugging | [skill](skills/debugging/SKILL.md) |
| Dependency Analysis | Audit package, module, runtime, and supply-chain dependencies. | Dependency Management | [skill](skills/dependency-analysis/SKILL.md) |
| Design Pattern Advisor | Select patterns only when design forces justify them. | Software Design | [skill](skills/design-pattern-advisor/SKILL.md) |
| Performance Optimization | Find and validate system performance improvements. | Performance | [skill](skills/performance-optimization/SKILL.md) |
| Refactoring Code | Plan and execute behavior-preserving refactoring. | Refactoring | [skill](skills/refactoring-code/SKILL.md) |
| Root Cause Analysis | Produce evidence-based incident root-cause analysis. | Incident Response | [skill](skills/root-cause-analysis/SKILL.md) |
| Security Audit | Audit SaaS security, cloud, API, and AI risks. | Security | [skill](skills/security-audit/SKILL.md) |
| SOLID Review | Review practical SOLID design risks. | Code Quality | [skill](skills/solid-review/SKILL.md) |
| Test Generation | Generate meaningful deterministic tests. | Testing | [skill](skills/test-generation/SKILL.md) |

See [SKILLS.md](SKILLS.md) for the complete catalog, installation identifiers, and category details.

## Installation

The repository works with the [Skills CLI](https://www.skills.sh/docs/cli) and compatible folder-based skill loaders.

Install the collection interactively:

```bash
npx skills add noorkhalel/saas-ai-skills
```

Install one skill:

```bash
npx skills add noorkhalel/saas-ai-skills --skill refactoring-code
```

Install selected skills with repeated `--skill` flags:

```bash
npx skills add noorkhalel/saas-ai-skills \
  --skill refactoring-code \
  --skill architecture-planning \
  --skill test-generation
```

Use `npx skills add noorkhalel/saas-ai-skills --list` to inspect available skills first. CLI behavior can vary by installed version; consult `npx skills add --help` if its output differs.

## Quick start

1. Browse [SKILLS.md](SKILLS.md) and choose a skill.
2. Install it with the matching folder name passed to `--skill`.
3. Let your compatible agent load `skills/<skill-name>/SKILL.md` and its relative references.
4. Keep skill prompts independent; use repository documentation to choose related skills.

## Repository structure

```text
skills/<skill-name>/
  SKILL.md          # canonical instructions
  references/       # optional, loaded on demand
  evals/            # optional evaluation fixtures
  examples/         # optional examples
.github/             # community files and lightweight validation
SKILLS.md            # full catalog
```

## Contributing, releases, and security

Read [CONTRIBUTING.md](CONTRIBUTING.md) before adding a skill. The collection uses [Semantic Versioning](RELEASE.md); the current recorded version is [`VERSION`](VERSION). Security reports follow [SECURITY.md](SECURITY.md). The project is licensed under [MIT](LICENSE).

See [Issues](https://github.com/Noorkhalel/saas-ai-skills/issues) for bugs and proposals, and [Discussions](https://github.com/Noorkhalel/saas-ai-skills/discussions) for questions and ideas.

## Roadmap

- Keep the catalog and validation tooling synchronized as skills are added.
- Improve evaluation coverage without coupling independent skills.
- Add only lightweight, dependency-free repository automation.
