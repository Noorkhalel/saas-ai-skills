# Ecosystem inventory and tools

## Sources and commands

| Ecosystem | Inspect | Useful evidence commands |
|---|---|---|
| JS/TS | `package.json`, lockfile, workspaces, `tsconfig`, Nx/Turbo | `npm ls`, `npm explain`, `npm audit`, `pnpm why`, `yarn why`, Knip/depcheck, dependency-cruiser/Madge, bundle analyzer |
| Python | requirements, `pyproject.toml`, Poetry/Pipenv locks, setup files | `pipdeptree`, `pip-audit`, Poetry/uv resolution, Ruff/import-linter |
| Maven/Gradle | POM/build/settings/lock files | Maven dependency tree, Gradle dependencies, OWASP Dependency-Check, ArchUnit |
| .NET | project files, central package/lock files, solution | `dotnet list package`, NuGet audit, NetArchTest |
| Go | `go.mod`, `go.sum`, workspace | `go mod graph`, `go mod why`, `govulncheck` |
| Rust | `Cargo.toml`, `Cargo.lock`, workspace | `cargo tree`, `cargo audit`, `cargo deny`, feature graph |
| PHP/Ruby | Composer/Gem manifests and locks | `composer audit`, Bundler tooling |
| Infra/AI | Docker/Compose, Terraform, K8s/Helm, CI, MCP/tool/model configs | Trivy/Grype, Syft/CycloneDX, registry/image/IaC tooling |

Run only safe read-only commands unless the user authorizes change. Capture manager/runtime/version, command scope, output date, affected workspace, and lockfile state. A nonzero command or incomplete tree is an evidence limitation, not an empty result.

For Python FastAPI/Django/Flask projects, include application settings, entry points, plugin discovery, optional extras, test configuration, task workers, and dynamic import strings before calling a package unused. For Maven/Spring applications, inspect dependency management/BOM imports, scopes, exclusions, plugin dependencies, and dependency convergence; resolve conflicts through compatible managed versions rather than arbitrary exclusions.

## Monorepos

Support npm/pnpm/Yarn workspaces, Nx, Turborepo, Lerna, Bazel, Gradle/Maven multi-projects, .NET solutions, Go workspaces, and Cargo workspaces. Inventory workspace graph, package ownership, deep imports, public/internal API boundaries, version policy, duplicate packages, affected-project build/test scope, circular project edges, and internal publishing. Analyze each manifest/lock and environment before declaring a monorepo-wide conclusion.

## Tool cautions

Static scanners miss runtime configuration, plugins, generated code, remote modules, native loading, and dynamic imports. Package audit results need package/version/path, advisory source, reachability/affected runtime, and remediation compatibility before severity. SBOM/provenance tools report components/artifacts, not automatically exploitability or license approval.
