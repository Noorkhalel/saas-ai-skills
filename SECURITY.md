# Security Policy

This repository contains instructional prompts and documentation, not application runtime code.

## What to protect

- Do not add secrets, API keys, tokens, or personal data to prompts or docs.
- Do not embed environment-specific credentials in examples.
- Treat evaluation fixtures as non-sensitive unless they are explicitly sanitized.

## Safe contribution practices

- Prefer public-safe examples and neutral placeholder data.
- Review external links and copied examples before committing them.
- Keep generated documentation free of secrets and tenant-specific data.

## Reporting a vulnerability

If you discover a security issue in the repository structure, release process, or documentation:

1. Use GitHub private vulnerability reporting if it is enabled for this repository.
2. If private reporting is unavailable, open a minimal issue requesting a private contact channel; do not publish secrets or exploit details.
3. Include the file path, the issue description, and the affected distribution method.

## Repository-specific notes

- The skills themselves are prompt content and should not be altered to include hidden behavior.
- Public documentation should not claim support for loaders or install formats that have not been verified.
- Removing a secret from the working tree does not remove it from Git history; rotate it immediately and use the repository host's documented history-cleanup process if needed.
