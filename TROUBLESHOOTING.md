# Troubleshooting

## The Skills CLI command differs from the examples

CLI behavior may vary by installed version. Check the local help and available skills first:

```bash
npx skills add --help
npx skills add noorkhalel/saas-ai-skills --list
```

Use the exact folder name from [SKILLS.md](SKILLS.md) as the `--skill` value.

## A selected skill cannot find a relative file

Install or copy the complete selected `skills/<skill-name>/` folder, not only `SKILL.md`. The folder may require `shared/` and `references/` resources. See [INSTALL.md](INSTALL.md).

## I am unsure which skill should run

Start with [Codebase Understanding](skills/codebase-understanding/SKILL.md) when repository context is missing. For close cases, consult [shared/routing-matrix.md](shared/routing-matrix.md) or run:

```bash
python scripts/skill_router.py --request "<your request>"
```

The router is guidance; the requested primary deliverable remains the routing signal.

## Workflow persistence is not created

Persistence is opt-in. Ask for persistent workflow output or create `.ai-workflow/` in the target project. The target directory must be writable. A skill should still return its normal report when state locking, writes, or recovery are unavailable.

## A handoff is ignored

That is expected when its topics do not match the receiving skill, its data is malformed or stale, or its important claims cannot be verified against project evidence. Handoffs are leads, not authority.

## Validation fails after modifying shared policies or workflow files

Edit only the canonical shared source, then synchronize before validation:

```bash
python scripts/sync_base_framework.py
python scripts/sync_workflow_contract.py
python scripts/ci.py validate
```

Do not hand-edit packaged copies under `skills/*/shared/`.

## Generated catalog, schema, or reference checks fail

Regenerate the affected artifact and review its diff:

```bash
python scripts/generate_skill_catalog.py
python scripts/generate_report_schemas.py
python scripts/generate_reference_catalog.py
```

Then run `python scripts/ci.py validate` and `python scripts/ci.py eval:all`.

## Evaluation output contains sensitive material

Stop sharing the output. Confirm the input did not contain a real secret, rotate any exposed credential, and report a suspected redaction failure through [SECURITY.md](SECURITY.md). Generated `eval-results/` is local and ignored by Git.

## I need more help

Read [SUPPORT.md](SUPPORT.md) before opening an issue. Include the selected skill, installation method, agent/CLI version, operating system, exact sanitized error, and a minimal reproduction.
