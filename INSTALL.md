# Installation Guide

This repository is designed as a GitHub-hosted collection of independent AI Skills.

## Install everything

```bash
npx skills add https://github.com/Noorkhalel/saas-ai-skills
```

## Install one skill

```bash
npx skills add https://github.com/Noorkhalel/saas-ai-skills --skill refactoring-code
```

## Install multiple skills

```bash
npx skills add https://github.com/Noorkhalel/saas-ai-skills --skill refactoring-code architecture-planning test-generation
```

If your installed `skills` CLI uses a different multi-select syntax, use the syntax documented by that CLI version. This repository keeps the skill names and folder names aligned so the selector can map directly to the skill folder.

## Manual inspection

If you are not using an install command, browse the repository in this order:

1. `SKILLS.md` for the catalog.
2. `skills/<skill-name>/SKILL.md` for the canonical prompt.
3. `skills/<skill-name>/references/` for supporting documentation.

## Notes for maintainers

- Keep new skills in their own top-level folder under `skills/`.
- Avoid changing existing skill prompts when adding packaging docs.
- Update the catalog whenever the skill list changes.
