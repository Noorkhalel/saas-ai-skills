# Portability: Running This Skill Across Platforms

This skill is plain Markdown with no runtime, tool, or platform dependencies, so it runs anywhere an agent can read instructions: Claude Skills, OpenAI/Codex skills, Cursor rules, Windsurf, Roo Code, Cline, and MCP-powered agents. Two loading models exist and this skill supports both.

## Folder-loading platforms (Claude Skills and compatible)

`SKILL.md` loads when the audit triggers; the `references/*.md` load on demand as each phase begins and the target touches that domain. Nothing to configure — the reference map in SKILL.md drives which files to read. This is the intended mode and keeps context focused (a Terraform audit never loads `ai-security.md`).

## Single-rules-file platforms (Cursor, Windsurf, Cline, Roo)

These load one rules file, not a folder. Use `SKILL.md` as the rule content, then **inline only the reference sections your stack needs** rather than pasting all twelve files (which would bloat every request). Map your target to the references to inline:

| If auditing… | Inline these references |
|--------------|-------------------------|
| A web app (frontend + backend) | `secure-coding.md`, `owasp.md`, `auth.md`, `api.md`, `database.md` |
| An API service | `api.md`, `auth.md`, `secure-coding.md`, `database.md` |
| A multi-tenant SaaS backend | `auth.md`, `database.md`, `api.md`, `secure-coding.md` |
| Docker/Kubernetes | `containers.md`, `secure-coding.md` (secrets) |
| Terraform / cloud IaC | `cloud.md`, `secure-coding.md` (secrets) |
| A CI/CD pipeline | `cicd.md`, `dependencies.md` |
| An AI/LLM/agent/MCP system | `ai-security.md`, `secure-coding.md`, `auth.md` |
| A full repo (unsure) | Start with `threat-modeling.md` + `secure-coding.md` + `owasp.md`, then add by stack |

`threat-modeling.md` and `report-schema.md` are useful in every configuration — the first shapes where to look, the second shapes the deliverable.

## Tooling and MCP are opportunistic

Every tooling/scanner/MCP integration mentioned in SKILL.md is a *bonus when present*, never a requirement. With no tools, the skill degrades gracefully to reading the code and reasoning about it — which is the majority of the value. When tools exist, use them to *verify* (read the real query, run the real SAST, check the real cloud config) and to *triage* their output, never to replace judgment or to fabricate results you didn't observe.

## What stays constant everywhere

The auditor principles (verify-before-report, name-the-attack, severity honesty, no invented vulnerabilities), the severity model, and the report structure are platform-independent. Whatever the host, the deliverable is the same: verified, exploitable, prioritized findings with fixes, ending in a production-readiness verdict.
