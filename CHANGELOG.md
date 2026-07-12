# Changelog

All notable changes to this project are documented here. This project follows [Semantic Versioning](RELEASE.md).

## [Unreleased]

No unreleased changes yet.

## [1.1.0] - 2026-07-12

### Added

- Nine specialist skills: API Design Review, Clean Architecture Review, Codebase Understanding, Database Design, Dependency Analysis, Design Pattern Advisor, Performance Optimization, Security Audit, and SOLID Review.
- A canonical, versioned Base Framework with evidence, scope, security, untrusted-content, command-safety, workflow, output, partial-result, quality, and context-budget policies.
- An executable routing registry, routing matrix, overlap regressions, and generated machine-readable skill catalog.
- Optional project-local workflow persistence with detailed artifacts, concise JSON handoffs, topic filtering, provenance, and lock-safe state updates.
- Deterministic behavioral, composition, schema, mutation-regression, redaction, prompt-injection, reference-freshness, and standalone-package evaluations.
- Release documentation, support guidance, troubleshooting, a public roadmap, and expanded community templates.

### Changed

- All skills now package their declared Base Framework policy subset, workflow contract, handoff vocabulary, and required relative resources for standalone installation.
- Validation now checks framework/workflow synchronization, package conventions, versions, generated discovery artifacts, report schemas, routing regressions, and persistence behavior.
- Documentation now explains routing, context discipline, workflow handoffs, evaluation boundaries, CI, and release gates.

### Security

- Added fail-closed secret redaction and external-transmission preflight for optional model evaluations.
- Added inert prompt-injection and synthetic-secret fixtures, plus CI regression coverage for unsafe fixture execution and workflow-data handling.
- Documented a security-reporting process and defensive-evaluation boundaries.

### Breaking changes

- None. Existing skill folder names and Skills CLI installation identifiers remain compatible.

## [1.0.0] - 2026-07-08

- Published the initial SaaS AI Skills collection, root documentation, catalog, contribution guidance, release process, and per-skill discovery material.
