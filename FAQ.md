# Frequently Asked Questions

## Is this one large prompt?

No. This is a collection of 15 independent skills. Each skill owns a focused deliverable and can be installed on its own.

## How do I choose the right skill?

Choose by the primary outcome: use Codebase Understanding for discovery, Architecture Planning for future design, Clean Architecture Review for existing boundaries, Debugging for an active failure, and Root Cause Analysis for a completed incident. See [SKILLS.md](SKILLS.md) and the [routing matrix](shared/routing-matrix.md) for the full comparison.

## Can I install only one skill?

Yes. Use its folder name with `--skill`, for example:

```bash
npx skills add noorkhalel/saas-ai-skills --skill security-audit
```

## Can I install several skills together?

Yes. Repeat `--skill` for each selected folder. See [INSTALL.md](INSTALL.md) for tested examples and compatibility notes.

## Do skills require each other?

No. Each selected package includes its own `SKILL.md`, relevant policy subset, references, and optional workflow contract. Skills may use optional handoffs when a project enables `.ai-workflow/`, but a missing handoff never blocks normal work.

## What are workflow artifacts and handoffs?

Artifacts are full specialist reports. Handoffs are compact JSON summaries that later skills may use as unverified leads. The receiving skill filters by topic and re-verifies material claims. Read the [workflow contract](shared/workflow-contract.md).

## Will a skill expose repository secrets?

It should not. The shared security policy requires redaction, and evaluation tooling uses a fail-closed external-transmission check. Do not place real credentials in prompts, fixtures, or issues. See [SECURITY.md](SECURITY.md).

## What happens when tools or evidence are unavailable?

The skills should return a bounded result, label unknowns, and name the smallest next artifact or command needed. They must not fabricate tool output, metrics, or production behavior.

## Are model evaluations required to use the collection?

No. Deterministic validations run without provider credentials. The optional protected real-model evaluation is for maintainers and may be skipped when credentials are unavailable.

## Where should I ask for help or propose an idea?

Use [SUPPORT.md](SUPPORT.md). Questions and ideas belong in GitHub Discussions when enabled; reproducible defects belong in Issues; security reports follow [SECURITY.md](SECURITY.md).
