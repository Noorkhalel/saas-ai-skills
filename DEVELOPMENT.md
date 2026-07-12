# Development Guide

## Working on the Repository

This repository is documentation- and prompt-focused.

When making changes:

- Keep edits localized to one skill or one root document.
- Preserve skill behavior unless a change is explicitly requested.
- Update the catalog when skills are added, removed, or renamed.
- Keep Markdown clean and consistent.

## Adding a Skill

1. Create `skills/<new-skill>/`.
2. Add `SKILL.md`.
3. Add references only if the skill needs them.
4. Add `README.md` if it improves discoverability.
5. Update `SKILLS.md`, `README.md`, and `CHANGELOG.md`.

## Maintaining Compatibility

- Keep folder names short, lowercase, and hyphenated.
- Prefer one canonical prompt file per skill.
- Avoid introducing cross-skill dependencies.
- Keep temporary and evaluation content clearly separated from prompts.
- Update `metadata.version` using Semantic Versioning when a standalone skill changes.
- Regenerate `shared/skill-catalog.json` after changing skill metadata, routing, policy selection, topics, or references.
- For workflow-contract changes, edit `shared/workflow-contract.md`, run the synchronizer, and do not hand-edit packaged copies.
- For Base Framework changes, edit only `shared/base/`, update its versioned policy map, run `python scripts/sync_base_framework.py`, and preserve standalone package copies.
- For any new or changed closest-skill relationship, add an executable pair regression to `shared/routing-tests.json`; `python scripts/validate_routing.py` rejects missing pair coverage.
- Treat context size as a compatibility concern: load phase-relevant references only, preserve the no-user-data telemetry rule, and inspect `eval-results/context-usage-report.json` when changing evaluation inputs.

## Suggested Validation

Run:

```bash
python scripts/validate_repository.py
python scripts/sync_workflow_contract.py --check
python scripts/validate_workflow_integration.py
python scripts/validate_versions.py
python scripts/generate_skill_catalog.py --check
python scripts/validate_routing.py
python scripts/validate_framework.py
```

For the complete repository gate use `python scripts/ci.py validate` followed by `python scripts/ci.py eval:all`. See `QUALITY_SYSTEM.md` for deterministic routing/contract/context versus optional real-model evaluation guidance.

Then run the skill-specific validator or evaluation fixtures when present. Check Markdown links, catalog membership, folder names, and relevant installation flow before opening a pull request.

## Documentation and release work

For a documentation-only change, run `python scripts/validate_markdown.py` and `python scripts/validate_repository.py`. For a release, follow [RELEASE.md](RELEASE.md), update [CHANGELOG.md](CHANGELOG.md) and [RELEASE_NOTES.md](RELEASE_NOTES.md), and run the complete required gate. Release artifacts are prepared locally; GitHub repository description, topics, Discussions, and private vulnerability reporting remain host-level publication settings.
