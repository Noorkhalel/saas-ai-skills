# Installation Guide

## Prerequisites

Use a compatible skill loader. The examples below use the Skills CLI through `npx`; verify its current flags locally before installing:

```bash
npx skills add --help
npx skills add noorkhalel/saas-ai-skills --list
```

## Install the collection

```bash
npx skills add noorkhalel/saas-ai-skills
```

## Install one standalone skill

Use the folder name shown in [SKILLS.md](SKILLS.md):

```bash
npx skills add noorkhalel/saas-ai-skills --skill debugging
```

The selected folder includes its `SKILL.md`, required package-local policy subset, relative references, and optional workflow contract. It does not require the rest of this repository at runtime.

## Install multiple skills

Repeat `--skill` for a workflow that matches your work:

```bash
# Understand a repository, then review and test a change
npx skills add noorkhalel/saas-ai-skills \
  --skill codebase-understanding \
  --skill code-review \
  --skill test-generation

# Plan and harden a new SaaS service
npx skills add noorkhalel/saas-ai-skills \
  --skill architecture-planning \
  --skill database-design \
  --skill security-audit
```

These are examples, not mandatory sequences. Each skill remains independently usable.

## Manual use

If your agent accepts folder-based skills directly, give it the desired `skills/<skill-name>/` directory. For a rules-file-only tool, use `SKILL.md` and inline only the relative references the skill asks it to read. Preserve the relative `shared/` folder when you want packaged policies or optional workflow persistence.

## Optional workflow persistence

No additional installation is needed. To enable project-local artifacts and compact handoffs, either ask the agent for persistent workflow output or create `.ai-workflow/` in the target project. Details and data-handling rules are in the [workflow contract](shared/workflow-contract.md).

## Compatibility and limitations

| Environment | Status | Notes |
|---|---|---|
| Skills CLI | Supported | Folder selectors use repeated `--skill <folder>` flags. CLI behavior may vary by version. |
| Folder-based skill loaders | Supported | Must retain the selected skill's relative package files. |
| Single-rules-file agents | Supported with adaptation | Inline only the necessary references; optional package files are not automatically discoverable. |
| Tool-less environments | Supported | Skills return evidence requests and bounded analysis instead of inventing tool output. |

## Verify an installation

After installation, confirm your selected skill folder contains at least:

```text
<skill>/
  SKILL.md
  shared/
  references/          # when the skill has references
```

For maintainers, `python scripts/package_check.py` simulates single-skill and multi-skill package layouts without network access.

For common setup problems, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
