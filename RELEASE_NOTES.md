# SaaS AI Skills Collection 1.1.0

## Why this release matters

Version 1.1.0 turns the collection into a more dependable, independently installable set of specialist workflows. It adds nine skills while strengthening the guardrails that keep all skills evidence-based, scoped, secure, and useful in real repositories.

## Highlights

- **15 independent skills** covering discovery, architecture, APIs, data, security, dependencies, performance, debugging, incident analysis, reviews, refactoring, patterns, and testing.
- **Base Framework** with shared policy modules for evidence, routing, redaction, untrusted input, safe commands, partial results, quality gates, and context discipline.
- **Standalone packaging** that includes the policy subset and workflow resources required by each selected skill.
- **Deterministic routing and validation** for skill selection, package completeness, report schemas, generated catalogs, and workflow state.
- **Optional workflow handoffs** that preserve detailed artifacts while sharing only concise, topic-filtered, re-verifiable summaries.
- **Security and evaluation hardening** through redaction, prompt-injection resistance, inert fixtures, mutation regressions, behavioral and composition checks.

## Upgrade notes

- Existing folder names and `--skill <folder>` installation identifiers are unchanged; this is a compatible minor release.
- Reinstall or update selected skills to receive their packaged `shared/base/`, handoff vocabulary, and workflow contract.
- Workflow output remains opt-in. Existing users do not need to create `.ai-workflow/` or change their prompts.
- Maintainers changing policies or the workflow contract should edit the canonical shared copy, run the appropriate synchronizer, and then run the full validation suite.

## Contributor notes

- Use [CONTRIBUTING.md](CONTRIBUTING.md) and the pull-request template for changes.
- Run `python scripts/ci.py validate` and `python scripts/ci.py eval:all` before requesting review.
- Add routing regressions and package/evaluation coverage whenever a new skill or material overlap is introduced.

## Known limitations

- Skills CLI flag behavior is verified through repository packaging checks, but individual CLI versions may differ; use `npx skills add --help` locally.
- Optional real-model evaluations require protected environment credentials and may be skipped in public CI.
- GitHub Discussions, repository description, topics, and private vulnerability reporting are host-level settings; they must be confirmed during publication.
- Tool integrations are opportunistic. In a tool-less environment, skills provide bounded analysis and evidence requests rather than fabricated results.

## Full details

See [CHANGELOG.md](CHANGELOG.md), [QUALITY_SYSTEM.md](QUALITY_SYSTEM.md), and [RELEASE.md](RELEASE.md).
