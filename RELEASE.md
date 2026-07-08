# Release Process

## Versioning

This repository follows Semantic Versioning.

- MAJOR: incompatible collection changes or breaking folder conventions
- MINOR: new skills, major documentation additions, or new compatible loaders
- PATCH: documentation fixes, catalog updates, and non-behavioral cleanup

## Release Checklist

1. Confirm the skill catalog is current.
2. Verify no skill behavior changed unintentionally.
3. Update `CHANGELOG.md`.
4. Bump `VERSION`.
5. Tag the release in git.
6. Publish the release notes.

## Release Notes Guidance

- List new skills and renamed folders.
- Call out any loader compatibility changes.
- Mention any files that are internal-only and should not be packaged separately.
