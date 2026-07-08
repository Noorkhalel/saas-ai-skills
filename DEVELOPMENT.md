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

## Suggested Validation

- Check Markdown links.
- Verify the catalog matches the repository contents.
- Confirm the skill count and folder names are current.
