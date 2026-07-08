# Architecture

## Collection Model

This repository is a collection of independent prompt skills. Each skill is packaged as its own folder under `skills/` and is expected to remain self-contained.

## Folder Conventions

- `skills/<name>/SKILL.md` is the authoritative skill definition.
- `skills/<name>/references/` contains supporting reference material.
- `skills/<name>/evals/` contains evaluation fixtures and benchmark data.
- `skills/<name>/README.md` is optional but recommended for discovery.

## Design Rules

- Do not merge skills together.
- Do not introduce shared prompt modules that change behavior across skills.
- Keep the root documentation focused on collection-level concerns.
- Treat `evals/` as development and validation material, not as prompt content.

## Installation Compatibility

This layout is intended to be compatible with skill loaders that discover named skills from repository folders.

To maximize compatibility:

- Keep skill folder names stable and descriptive.
- Keep each skill's prompt in `SKILL.md`.
- Keep file paths simple and predictable.
- Document the skill catalog at the root.

## Public Distribution Strategy

The repository should present a clear collection boundary:

1. Discover the skill in `SKILLS.md`.
2. Install the repository or selected skills through the supported loader.
3. Consume only the selected skill folder and its references.

## Non-Goals

- No behavior changes to existing skill prompts.
- No consolidation of skill content into a shared runtime.
- No assumption that every loader supports the same multi-skill selector syntax.
