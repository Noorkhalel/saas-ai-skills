# Contributing

Thank you for improving the SaaS AI Skills Collection. Contributions should keep skills independent, evidence-based, portable, and easy to select.

## Before you start

- Read [ARCHITECTURE.md](ARCHITECTURE.md), [QUALITY_SYSTEM.md](QUALITY_SYSTEM.md), and the relevant `SKILL.md`.
- Search existing issues and discussions before opening a new proposal.
- Keep a pull request focused. Do not combine unrelated refactors, generated-file churn, and behavior changes.
- Never add secrets, private paths, customer data, executable evaluation fixtures, or hidden instructions.

## Contribution types

### Documentation, examples, and release material

Update the relevant root documentation, keep installation examples accurate, and run Markdown validation. Documentation must not claim compatibility, validation results, or runtime behavior that the repository cannot verify.

### Skill improvement

Preserve the skill's primary deliverable and routing boundary unless the proposal explicitly changes them. Update evaluations, routing cases, references, report schemas, catalog output, and standalone package resources when affected.

### New skill

1. Create `skills/<kebab-case-name>/SKILL.md` with a clear name, description, activation boundary, exclusions, workflow, output contract, and metadata version.
2. Keep references, examples, assets, and evaluation fixtures package-local.
3. Add the skill to the routing registry and add regression cases for material overlaps.
4. Declare the smallest necessary Base Framework policy subset and synchronize packaged copies.
5. Generate catalog, report-schema, and reference metadata artifacts.
6. Verify standalone packaging and add behavioral, redaction, prompt-injection, handoff, and false-positive coverage.

## Required checks

Run these from the repository root before opening a pull request:

```bash
python scripts/ci.py validate
python scripts/ci.py eval:all
python scripts/ci.py package:check
```

For focused work, also run the named generator or validator with `--check` as documented in [QUALITY_SYSTEM.md](QUALITY_SYSTEM.md). If a generated artifact changes, include it in the same pull request. Do not hand-edit synchronized policy or workflow copies; change the canonical shared source, run the synchronizer, and review the resulting diff.

## Pull request checklist

- [ ] The change has one clear purpose and identifies affected skills.
- [ ] Skill behavior, routing, compatibility, and assumptions are documented.
- [ ] Catalog, docs, release notes, and changelog are updated when required.
- [ ] Relevant tests, validators, and package checks pass locally.
- [ ] New findings, examples, and fixtures contain no secrets or private data.
- [ ] The change preserves standalone installation or explicitly documents a compatible migration.

## Review expectations

Maintainers review for scope, evidence quality, security, independent packaging, deterministic validation, documentation accuracy, and community impact. A reviewer may request a smaller change, additional routing coverage, or clearer compatibility notes before merge.

## Community standards

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report security concerns through [SECURITY.md](SECURITY.md), not a public issue.
