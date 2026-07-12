# Release Process

## Versioning

The collection follows Semantic Versioning.

- **MAJOR**: incompatible collection changes, removed or renamed skill folders, or incompatible packaging conventions.
- **MINOR**: new compatible skills, substantial compatible capabilities, or material documentation/evaluation additions.
- **PATCH**: compatible fixes, documentation corrections, catalog updates, and non-behavioral cleanup.

Each standalone skill also carries a SemVer `metadata.version`. Changing an existing skill's behavior requires updating its version and validating its package.

## Release checklist

### Before creating a tag

- [ ] Confirm `VERSION`, skill versions, `CHANGELOG.md`, and `RELEASE_NOTES.md` describe the intended release.
- [ ] Run `python scripts/ci.py validate`.
- [ ] Run `python scripts/ci.py eval:all`.
- [ ] Run `python scripts/ci.py package:check`.
- [ ] Confirm generated catalogs, schemas, policies, workflow copies, and `skills-lock.json` are synchronized.
- [ ] Review `eval-results/` locally; do not commit it or include sensitive content in release material.
- [ ] Verify one-skill and multi-skill package simulation succeeds.
- [ ] Confirm documentation links, installation commands, comparison/routing guidance, support links, and security contacts are current.
- [ ] Review the diff for accidental secrets, private paths, untracked build output, or unrelated implementation changes.

### GitHub publication settings

- [ ] Set the repository description to: `Evidence-based AI skills for building, reviewing, securing, testing, and operating SaaS applications.`
- [ ] Set topics: `ai-agents`, `ai-skills`, `saas`, `developer-tools`, `prompt-engineering`, `software-architecture`, `code-review`, `security`, `testing`, `open-source`.
- [ ] Enable GitHub Discussions and create categories for Announcements, Q&A, Ideas, and Show and Tell.
- [ ] Confirm private vulnerability reporting is enabled, or establish a private reporting channel documented in `SECURITY.md`.
- [ ] Confirm the default branch, license, repository homepage, and issue/PR templates are visible to first-time visitors.

### Publish

1. Commit the approved release changes and push the release commit.
2. Create and push an annotated `v<version>` tag.
3. Confirm the tag-triggered validation workflow completes successfully and uploads only redacted evaluation artifacts.
4. Create the GitHub Release from the tag using [RELEASE_NOTES.md](RELEASE_NOTES.md).
5. Publish a Discussion announcement, link the release, and monitor issues after publication.

## Required release gates

Do not publish if any required validator, deterministic evaluation, composition evaluation, or package check fails. A release is blocked by stale generated copies, invalid versions, broken routing, incomplete standalone packages, unsafe/executable fixtures, failed redaction or prompt-injection regression checks, invalid workflow state behavior, or report-schema failure.

The optional protected model evaluation is reported separately. Missing protected credentials is a skipped optional check, not a substitute for deterministic coverage.

## Current release

The next prepared release is **1.1.0**. It is a compatible minor release: existing skill identifiers and installation paths are unchanged. Do not tag it until the release owner has completed the publication settings and required gates above.
