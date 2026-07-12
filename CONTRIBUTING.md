# Contributing

Keep skills independent, behavior-preserving, and easy to discover. Do not merge prompts, move references between skills, or change an existing skill's meaning unless the change is explicitly scoped and reviewed.

## Add a skill

1. Create `skills/<kebab-case-name>/`.
2. Add `SKILL.md` with clear name and description.
3. Add optional references, evaluations, examples, or assets only inside that skill folder.
4. Validate relative links and remove local paths/secrets.
5. Add the skill to `SKILLS.md`.
6. Add a concise README summary entry.
7. Update `CHANGELOG.md` under `Unreleased`.
8. Run documentation validation.
9. Test installation with the supported Skills CLI syntax.
10. Submit a pull request.

## Required checklist

- [ ] The skill has a unique and clear scope
- [ ] The folder name uses lowercase kebab-case
- [ ] `SKILL.md` exists
- [ ] References use relative paths
- [ ] No secrets or local paths are included
- [ ] `SKILLS.md` is updated
- [ ] README summary is updated
- [ ] CHANGELOG is updated
- [ ] Installation was tested
- [ ] The skill does not unintentionally duplicate another skill
- [ ] The optional workflow section declares only topics relevant to the skill

## Validation

Run `python scripts/validate_repository.py`, `python scripts/sync_workflow_contract.py --check`, and `python scripts/validate_workflow_integration.py`. If changing the workflow contract, edit only `shared/workflow-contract.md` and run `python scripts/sync_workflow_contract.py` to update every packaged copy. Review the output, then run the relevant skill-specific validator or evaluation fixtures when present. Keep generated output, caches, and private configuration out of commits.

## Pull requests

Use the pull request template. Keep changes scoped, state affected skills, explain compatibility, and include exact commands/tests used. For a new skill, cite its catalog row and installation identifier.
