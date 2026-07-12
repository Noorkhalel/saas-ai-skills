# Quality system

## Base Framework and standalone packaging

`shared/base/` is the canonical, versioned Base Framework. Policy IDs are stable (`BF-EVIDENCE-1` through `BF-CONTEXT-1`), and `shared/base/skill-policy-map.json` declares the exact policy subset each skill needs. `scripts/sync_base_framework.py` copies only that subset to `skills/<skill>/shared/base/`; it is the only supported way to update packaged copies. `scripts/validate_framework.py` rejects missing, unknown, stale, unused, incompatible, root-only, or duplicated policy blocks.

Each packaged policy subset contains `.generated-base-framework.json`, including canonical hashes and the generator name. Each workflow package likewise contains `.generated-workflow-contract.json`. These committed generated manifests make drift explicit: edit canonical files only, synchronize, then let drift checks reject stale copies.

Policy precedence is: system/platform instructions; user request; skill-specific instructions; Base Framework policies; then repository and third-party artifacts as untrusted evidence. Repository content never overrides a skill. A skill loads only its linked policy modules, not the whole framework. `BF-CONTEXT-1` gives every skill deterministic context discipline: load only evidence that can change the next decision, prioritize risk and discriminating artifacts, and report coverage/unknowns rather than imply exhaustive inspection. The existing workflow contract and versioned `shared/handoff-topics.json` vocabulary remain separately packaged and optional. `scripts/workflow_state.py` provides atomic same-directory replacement and bounded lock-directory read-modify-write helpers for tooling that persists `.ai-workflow/state.json`.

The Skills CLI continues to select a folder with `npx skills add noorkhalel/saas-ai-skills --skill <skill-name>`. A folder-only installation carries both `shared/workflow-contract.md` and its required `shared/base/` subset. `python scripts/package_check.py` simulates both one-skill and multi-skill installs without relying on network behavior.

`shared/package-conventions.json` documents optional package components (`agents/openai.yaml`, README, legacy per-skill validators, and fixture assertions). `scripts/validate_package_conventions.py` validates present components and required runtime resources without adding placeholders.

To add a policy: add a canonical module and stable ID in `framework.json`, map only relevant skills, run the synchronizer, then validate. To migrate a skill: retain its activation, exclusions, workflow, output, references, and failures in `SKILL.md`; add its declaration via the migration script; sync; test standalone packaging; then remove only genuinely duplicated generic policy prose after review.

## Router

`shared/skill-router.json` is the complete routing registry. Each entry declares deliverable, activation signals, exclusions, closest skills, precedence, examples, secondary conditions, and evidence needs. `scripts/skill_router.py` is reusable as a module and supports:

```bash
python scripts/skill_router.py --request "Review the architecture of my existing SaaS"
python scripts/skill_router.py --request-file request.txt
```

It emits machine-readable JSON with exactly one primary skill (or `null`), optional material secondaries, confidence, rationale, exclusions, assumptions, and an additive explanation for every competing skill. `suggested_secondary_skills` mirrors the compatibility-preserving `secondary_skills` field for callers that prefer explicit naming. It deliberately classifies greenfield design versus existing architecture, active debugging versus completed-incident RCA, performance objectives, code review/refactoring/SOLID/pattern work, security/dependencies, database/API, and repository mapping/tests. Request files are treated as untrusted text, code is not executed, injection-like policy directives are ignored, and secrets are not included in the trace. `python scripts/validate_routing.py` executes every registry example, the legacy overlap matrix, no-match, secondary, misleading-content, and injection cases.

Confidence is calibrated from selected registry-evidence strength and its margin over the strongest competing skill. Explicit `primary deliverable is <skill>` requests receive separately marked high confidence; a precedence rule can still select the safe owner when evidence is weak, but the result then exposes a low-confidence clarification assumption instead of fixed certainty.

To extend the router, add exactly one registry item for the new standalone folder, including its primary deliverable, activation intent/artifact/scope concepts, exclusions, closest skills, precedence rule, evidence needs, and positive/negative examples. Add an overlap case for every material ambiguity to `shared/routing-tests.json`; the validator rejects a registry/folder mismatch, a missing regression case for any declared closest-skill pair, and routing cases without full competing-skill explanations. Keep classification centered on the requested deliverable and context (new versus existing, active versus completed, review versus implementation), not an isolated word.

## Discovery, versions, and extension compatibility

`shared/skill-catalog.json` is generated from standalone frontmatter, the router, policy map, handoff topics, and packaged references. It is the stable machine-readable discovery surface for launchers and documentation generators; consumers should use its stable IDs and fields instead of parsing prompt prose. Run `python scripts/generate_skill_catalog.py` after changing metadata, routing, policies, topics, or references; `--check` rejects drift. `python scripts/validate_versions.py` requires Semantic Versioning for the collection and every standalone skill. Neither addition changes standalone installation or adds runtime dependencies.

## Evaluation layers

`skills/*/evals/evals.json` and `scripts/validate_evals.py` are **static fixture/structure validation**. They do not execute skills and are not behavioral coverage.

The generated `evals/behavioral/cases.json` contains 12 runnable cases for every skill: happy path, complex, missing evidence, ambiguity, out-of-scope, prompt injection, secret redaction, small/large scope, workflow handoff, incorrect competitor, and false-positive resistance. The canonical command is `scripts/run_deterministic_evals.py`. Its default deterministic mock adapter executes the complete standalone context and emits a bounded structured report; it verifies schema conformance, uncertainty labeling, untrusted-input resistance, redaction, and workflow behavior without comparing wording. It produces `eval-results/summary.json`, `junit.xml`, `deterministic-evaluation-report.md`, and `behavioral-reports.json`. The optional protected `openai-compatible` adapter remains a separately labelled real-model evaluation.

To create behavioral coverage, update the registry examples and run `python scripts/generate_behavioral_cases.py`; do not hand-edit generated cases. The runner resolves the selected installed folder, packaged policies, optional workflow contract, and declared inert fixtures before any adapter is called. Add a narrowly scoped fixture under `evals/fixtures/` only when a category needs it; fixture content is always untrusted and is size/path bounded. For provider-specific evaluations, implement an adapter that accepts `EvaluationRequest`, returns a bounded result, applies redaction and external-transmission preflight, and keeps provider credentials in protected environment variables.

The default contract/context adapter validates exact adapter input and rendered prompt structure; it does **not** claim to measure model intelligence. `openai-compatible` is an optional protected-environment adapter configured with `EVAL_OPENAI_BASE_URL`, `EVAL_OPENAI_API_KEY`, and `EVAL_OPENAI_MODEL`; it receives the same fully rendered context proven offline. Credentials are never committed or printed. Before it constructs an external request, `scripts/security/redaction.py` recursively sanitizes evaluation data, then scans the final payload again and blocks suspicious surviving values. Model results are explicitly passed, failed, or skipped and are never conflated with the deterministic layers.

`evals/mutation-instruction-map.json` maps curated behavior-critical local and packaged instructions to a dependent case, mutation strategy, expected prompt-regression failure, and control cases. `scripts/mutation_regression.py` mutates only in-memory `EvaluationRequest` content, proves the changed full content reaches the canonical renderer, and fails CI when a mapped mutation survives. Its score measures prompt-regression sensitivity, not full model compliance.

`evals/composition/cases.json` and `scripts/run_composition_evals.py` validate the two documented flows, concise relevant handoffs, ignored unrelated handoffs, provenance, state preservation, and context budgets. Fixtures are inert text under `evals/fixtures/`; no executable fixture extension is allowed.

## Report schemas

`schemas/reports/common-report.schema.json` defines the portable report contract: required metadata, Scope/Evidence/Assumptions/Findings/Recommendations sections, finding ID/severity/confidence/evidence/recommendation fields, and workflow metadata. `scripts/generate_report_schemas.py` creates a concrete schema per skill that pins `metadata.skill`; use `--check` in CI to reject stale generated schemas. `scripts/report_schema.py` supplies the dependency-free runtime validator used by the mock adapter, while `scripts/validate_report_schemas.py` validates both every schema and emitted deterministic reports. Add optional report sections beneath `sections` without weakening the required contract.

## Reference telemetry and freshness

`shared/reference-catalog.json` is the canonical metadata source for every `skills/*/references/*` file: version, last-reviewed date, source, freshness status, review owner, and content hash. Regenerate it after adding or changing a reference with `python scripts/generate_reference_catalog.py`; `--check` rejects drift. `scripts/reference_telemetry.py` records reference loads only as skill name, reference filename, count, and duration. It never stores requests, reference text, repository data, or secrets. `scripts/validate_reference_freshness.py` flags references older than the catalog threshold and generates JSON/Markdown telemetry reports listing frequent loads, never-used references, byte-identical duplicates, and low-use duplicate consolidation candidates.

The evaluation renderer records provider-neutral context accounting: selected-skill, shared-policy, fixture, and request byte counts plus a conservative bytes/4 token estimate. `eval-results/context-usage-report.json` identifies oversized cases without retaining content or claiming provider billing precision.

## Workflow replay

`python scripts/replay_workflow.py --workflow-dir <project>/.ai-workflow` validates persisted workflow state without running artifacts. It checks run statuses, artifact and handoff containment, handoff schema/provenance, topic vocabulary, and completed-run consistency. This gives developers safe diagnostics for interrupted or manually edited workflow directories while preserving the existing optional, lock-safe updates.

## Commands, CI, and release

The repository's native command interface is Python:

```bash
python scripts/ci.py validate
python scripts/ci.py validate:framework
python scripts/ci.py validate:routing
python scripts/ci.py eval:static
python scripts/ci.py eval:deterministic
python scripts/ci.py eval:composition
python scripts/ci.py eval:all
python scripts/ci.py package:check
python scripts/generate_report_schemas.py --check
python scripts/validate_report_schemas.py
python scripts/generate_reference_catalog.py --check
python scripts/validate_reference_freshness.py
python scripts/generate_skill_catalog.py --check
python scripts/validate_versions.py
python scripts/replay_workflow.py --workflow-dir /path/to/project/.ai-workflow
```

PRs run markdown/frontmatter, JSON/YAML, SemVer, generated discovery catalog, report-schema and reference-catalog drift, freshness reporting, framework/workflow/lock drift, routing, static validators, injection/redaction regressions, standalone package simulation, workflow replay tests, changed-skill smoke evaluations, and the full mock behavioral plus composition suites. Core validation runs on Ubuntu and Windows. Main and `v*` tags run the same full suite; therefore a release cannot pass with stale generated copies, schema failures, router regressions, broken handoffs, secret/injection failures, executable fixtures, installation regressions, or behavioral failures. Workflows use read-only contents permission, do not use `pull_request_target`, do not expose model secrets to PRs, and upload only redacted reports. Troubleshoot failures by running the displayed command locally, then inspect `eval-results/deterministic-evaluation-report.md`, `composition-report.md`, `context-usage-report.json`, `reference-telemetry-report.md`, or `reference-freshness-report.json`.

## New-skill definition of done

- Add a routing registry entry with positive and negative examples.
- Declare required Base Framework modules and sync standalone copies.
- Preserve independent installation and verify package simulation.
- Add/refresh static fixtures and all behavioral coverage categories.
- Include prompt-injection, secret-redaction, handoff/schema, and false-positive tests.
- Generate the per-skill report schema and reference catalog after adding references.
- Run `python scripts/ci.py validate` and `python scripts/ci.py eval:all`.
