![Image](a33eb099-f775-42d6-9c08-5d08cd80f398.png)
# SaaS AI Skills Collection

This repository is a collection of independent AI Skills for software design, code quality, debugging, refactoring, testing, and incident analysis.

Each skill lives in its own folder under `skills/` and keeps its own prompt, references, and evaluation fixtures isolated from the others.

## Overview

- Each skill is self-contained and can be installed on its own.
- The repository is organized for loaders that understand GitHub-hosted skill collections.
- No skill behavior is changed by the collection structure in this repository.

## Supported Assistants

This collection is intended to work with AI skill loaders and agents that support folder-based skill discovery, including:

- Anthropic Skills
- OpenAI Skills
- Claude Code
- Cursor
- Codex
- Roo Code
- Cline
- Windsurf

Support depends on the loader version and its GitHub install workflow.

## Repository Structure

- `skills/<skill-name>/SKILL.md` is the canonical skill prompt.
- `skills/<skill-name>/references/` contains supporting documentation for that skill.
- `skills/<skill-name>/evals/` contains evaluation fixtures and benchmark material.
- `SKILLS.md` is the catalog and discovery index.

## Installation

### Install all skills

```bash
npx skills add noorkhalel/saas-ai-skills
```

### Install one skill

```bash
npx skills add noorkhalel/saas-ai-skills --skill refactoring-code
```

### Install multiple skills

```bash
npx skills add noorkhalel/saas-ai-skills --skill refactoring-code --skill refactoring-code architecture-planning test-generation
```

If your installed `skills` CLI expects a different multi-skill selector syntax, follow that CLI's help output. This repository is structured around repository URL plus named skill selection.

## Quick Start

1. Open `SKILLS.md` to browse the catalog.
2. Choose the skill that matches the task.
3. Install all skills or only the selected skills.
4. Open the chosen skill's `SKILL.md` and follow its instructions.

## Repository Layout

```text
skills/
  architecture-planning/
  code-review/
  debugging/
  refactoring-code/
  root-cause-analysis/
  test-generation/
```

Each folder remains independent by design.

## Contributing

Contributions should keep each skill isolated.

- Do not merge skills together.
- Do not change a skill prompt unless the task explicitly requires it.
- Keep folder names stable and descriptive.
- Update `SKILLS.md` and the root docs when adding or removing skills.
- Prefer documentation and packaging changes over prompt rewrites.

See `CONTRIBUTING.md` for the full workflow.

## License

This project is licensed under the MIT License. See `LICENSE`.

## Roadmap

- Expand the catalog as new skills are added.
- Add optional GitHub issue and pull request templates.
- Add release automation when the collection format stabilizes.
- Keep the collection compatible with additional skill loaders as their install formats evolve.

## Versioning

This repository follows Semantic Versioning. The current collection version is recorded in `VERSION`.

## Credits

- Repository owner and maintainer: Noorkhalel
- Skill content authorship is preserved inside each skill folder
- Open-source packaging guidance is documented in the root docs
