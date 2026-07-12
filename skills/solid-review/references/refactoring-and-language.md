# Safe refactoring and language-aware guidance

## Safe sequence

1. Inspect current tests, callers, contracts, serialization/ORM/framework wiring, and side effects.
2. Add characterization tests for unclear behavior; preserve API, errors, transaction, ordering, and event behavior.
3. Make one small reversible change, run relevant tests/type/build checks, and recheck callers.
4. Use contract tests for new capability boundaries, substitution tests for LSP, integration tests for infrastructure adapters, and architecture tests for dependency rules.
5. Keep old and new paths compatible during a multi-caller migration; remove legacy paths after usage/validation/rollback windows.

## Transformation selection

| Proven mechanism | Smallest likely transformation | Guardrail |
|---|---|---|
| Mixed independent responsibilities | Extract Method/Class; Move Method | Keep transaction and side-effect ordering |
| Growing provider variation | Strategy/handler/adapter/factory | Keep simple conditional if variation is small/closed |
| Broken subtype contract | Replace inheritance with composition; narrower capability | Test every consumer against contract |
| Forced client capability | Split interface by consumer role | Migrate consumers compatibly |
| Policy coupled to external detail | Consumer-owned port/function parameter; isolate adapter | Do not abstract stable local code |
| Hidden time/random/config | Inject clock/RNG/config boundary | Preserve defaults and deterministic tests |

## Language and framework adaptation

- **TypeScript/JavaScript, React/Next/Node/Express/Nest:** structural types/functions may be better than classes; do not criticize decorators/DI merely for existing. Check component rendering, fetching, state transitions, and business calculations for actual independent change pressure.
- **Python, Django/FastAPI/Flask:** protocols/callables and module boundaries can express DIP; ORM models/framework views are adapters where policy needs isolation, not automatic violations.
- **Java/Spring Boot and C#/ASP.NET Core:** respect framework DI/annotations; inspect whether domain/application policy imports framework/ORM/HTTP concerns and whether interfaces have real consumers.
- **Go/Rust/PHP/Laravel:** favor small consumer-facing interfaces, traits, functions, packages/modules, composition, and explicit dependencies; do not impose Java inheritance patterns.
- **Functional/data-oriented code:** assess module responsibility, effect boundaries, parameterization, data invariants, and coupling. SOLID ideas apply without class-heavy OOP.

## Review modes

For a PR, limit blockers to new/worsened verified HIGH/CRITICAL design risks. Output blocking/non-blocking findings, positives, ready-to-post comments, and an approval recommendation. For a repository, sample representative critical flows, report reviewed coverage, use import/SCC/co-change/test evidence, and rank patterns. For a snippet, withhold call-site/substitution/consumer claims unless supplied.
