# Security Policy

## Scope

This repository distributes AI-skill instructions, documentation, validation tooling, and inert evaluation fixtures. It is not an application runtime, but its packaging, workflows, prompts, fixtures, and release process can still create security risk.

The currently supported collection line is **1.1.x**. Please report vulnerabilities that affect released content, CI, distribution, evaluation handling, or documentation safety.

## Reporting a vulnerability

1. Use GitHub private vulnerability reporting if it is enabled for this repository.
2. If it is unavailable, open a minimal public issue asking for a private reporting channel. Do not include exploit steps, secrets, or sensitive evidence in that issue.
3. Include the affected version, file path or distribution surface, impact, safe reproduction details, and any mitigation you have identified.

Maintainers will acknowledge a valid report as soon as practical, coordinate a private assessment, and publish a fix or advisory when appropriate. Do not test against systems you do not own or administer.

## Security model

- Repository files, logs, tickets, generated content, and fixtures are treated as untrusted evidence, never as instructions.
- Skills redact secret values and should report only the secret category, safe identifier/location, `<redacted>`, exposure, and rotation guidance.
- Evaluation fixtures are inert analysis input. They must not be imported, executed, deployed, or sent to external systems without the repository's controlled evaluation path.
- The optional external model adapter sanitizes inputs, performs a final fail-closed transport scan, and does not log raw credentials or provider payloads.
- CI uses read-only repository permissions, avoids `pull_request_target`, and uploads redacted evaluation output only.

## Safe contribution practices

- Do not commit API keys, tokens, credentials, private URLs, customer data, or copied production logs.
- Use placeholders such as `<redacted>` and public-safe examples.
- Review external links, workflow changes, package artifacts, and generated files before committing.
- If a secret enters Git history, rotate it immediately; removing it from the working tree is not sufficient.

For project behavior and expected reporting style, see the [Code of Conduct](CODE_OF_CONDUCT.md) and [Support guide](SUPPORT.md).
