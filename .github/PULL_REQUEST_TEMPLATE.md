## Summary

Describe the user-visible or maintainer-visible outcome and why this change is needed.

## Scope

- [ ] Documentation or community files
- [ ] New skill
- [ ] Existing skill behavior or references
- [ ] Routing, policy, workflow, packaging, or generated artifacts
- [ ] Validation or evaluation tooling

## Affected skills and compatibility

List affected skills, installation identifiers, generated artifacts, and any compatibility or migration impact. Write `None` when not applicable.

## Validation

List exact commands run and their results. At minimum, run the relevant focused checks; for material changes run:

```text
python scripts/ci.py validate
python scripts/ci.py eval:all
python scripts/ci.py package:check
```

## Checklist

- [ ] The change is focused and does not include unrelated cleanup.
- [ ] Documentation, catalog, changelog, and release notes are updated where needed.
- [ ] Standalone package resources remain complete and synchronized.
- [ ] Routing, schemas, references, and evaluations are updated where behavior changed.
- [ ] Installation identifiers and public contracts remain compatible or have a documented migration.
- [ ] No secrets, private paths, customer data, generated local output, or executable fixtures are included.
- [ ] I have followed the [Code of Conduct](../CODE_OF_CONDUCT.md).
