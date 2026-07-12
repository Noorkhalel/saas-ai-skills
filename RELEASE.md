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

## Current recommendation

`VERSION` is currently `1.0.0`. The untracked collection expansion adds independent skills without changing existing skill identifiers or installation paths, so the next release should be **1.1.0** when the maintainer is ready. Do not create a tag until the release owner approves the version and notes.
