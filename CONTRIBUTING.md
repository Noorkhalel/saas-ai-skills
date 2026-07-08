# Contributing

Thanks for helping improve the collection.

## Principles

- Keep every skill independent.
- Do not merge skill prompts or share prompt logic between skills.
- Preserve existing behavior unless a change is explicitly requested.
- Prefer documentation, metadata, and packaging improvements over prompt rewrites.

## Workflow

1. Identify the skill or root document you want to change.
2. Make the smallest change that solves the problem.
3. Update `SKILLS.md` if the skill catalog changes.
4. Update the relevant root docs if the repository surface changes.
5. Verify the change does not alter skill behavior.

## Skill Additions

When adding a new skill:

- Create a new folder under `skills/`.
- Add a canonical `SKILL.md` file.
- Add supporting references only inside that skill folder.
- Add a concise README if it helps discovery.
- Update `SKILLS.md`, `README.md`, and `CHANGELOG.md`.

## Review Expectations

- Use clear, descriptive folder names.
- Avoid temporary or generated files unless they are explicitly needed.
- Keep Markdown consistent and link targets relative.
- Document any compatibility caveats in the root docs.
