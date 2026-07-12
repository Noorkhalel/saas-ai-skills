# Installation Guide

This repository is designed as a GitHub-hosted collection of independent AI Skills.

## Install everything

```bash
npx skills add noorkhalel/saas-ai-skills
```

## Install one skill

```bash
npx skills add noorkhalel/saas-ai-skills --skill refactoring-code
```

## Install multiple skills

```bash
npx skills add noorkhalel/saas-ai-skills \
  --skill refactoring-code \
  --skill architecture-planning \
  --skill test-generation
```

Use `npx skills add noorkhalel/saas-ai-skills --list` before installation to inspect the current catalog. The folder name is the skill selector. If installed CLI help differs, follow `npx skills add --help`.

## Manual inspection

If you are not using an install command, browse the repository in this order:

1. `SKILLS.md` for the catalog.
2. `skills/<skill-name>/SKILL.md` for the canonical prompt.
3. `skills/<skill-name>/references/` for supporting documentation.

## Notes for maintainers

- Keep new skills in their own top-level folder under `skills/`.
- Avoid changing existing skill prompts when adding packaging docs.
- Update the catalog whenever the skill list changes.
