# Cross-Platform Portability Guide

## Core Architecture

The test-generation skill is written as platform-neutral Markdown instructions that assume only three universal agent capabilities:

1. **Read code** — access and understand source files
2. **Write files** — create test files and reports
3. **Follow instructions** — execute the six-phase workflow described in SKILL.md

No platform-specific tools, APIs, or extensions are required for core functionality. The framework detection, behavior analysis, test planning, and test generation workflow works on any agent platform that can read and write files.

## Platform Adaptation Notes

### Claude Skills (Native Platform)

The skill is designed for direct use as a Claude Skill:
- Place the `test-generation/` directory under `.agents/skills/` in your project
- The SKILL.md frontmatter (`name`, `description`) follows Claude's skill-triggering conventions
- No additional configuration needed — Claude reads SKILL.md and references automatically

### OpenAI Skills / Codex

- Copy the `test-generation/` directory into the project's custom instructions or skills folder
- The SKILL.md body can be used as a system prompt or custom instruction
- For Codex: include the SKILL.md content in the agent's instructions; reference files can be loaded via file context
- Adapt the `description` field to match OpenAI's skill/tool declaration format if needed

### Cursor Rules

- Convert SKILL.md to a `.cursorrules` file or add it to your project's rules directory
- Cursor loads rules from `.cursor/rules/` or project-root `.cursorrules`
- The workflow phases translate directly as numbered instructions
- Reference files can be included inline or via `@file` references

### Windsurf

- Add SKILL.md content to Windsurf's rules configuration
- Windsurf reads rules from `.windsurfrules` or project-level configuration
- The six-phase workflow and quality checklist map directly to Windsurf's instruction format

### Roo Code

- Place SKILL.md content in Roo Code's custom instructions
- Roo supports markdown-based instructions natively
- Reference files can be loaded on-demand via file system access

### Cline

- Add SKILL.md to Cline's custom instructions or rules
- Cline supports project-level instructions via `.clinerules` or settings
- The workflow structure maps directly to Cline's instruction-following model

### MCP-Powered Agents

- The skill works with any MCP-capable agent that has file read/write tools
- No MCP servers are required for core functionality (see Optional Enhancements below)
- For MCP-based setups, the agent reads SKILL.md and references via the Filesystem MCP server

## Optional Enhancements

The following tools and MCP servers can enhance the skill's capabilities but are **not required**. The core workflow produces complete, meaningful tests using only file read/write capabilities.

### Test Runners (Optional — for live validation)

| Tool | Use Case | Required? |
|------|----------|-----------|
| Jest | Running generated JavaScript/TypeScript tests | No — tests are valid without running |
| Vitest | Running generated Vite-based tests | No |
| Playwright | Running generated E2E tests | No |
| Cypress | Running generated E2E tests | No |
| Testing Library | Enhancing component test queries | No |
| pytest | Running generated Python tests | No |
| xUnit | Running generated .NET tests | No |
| JUnit | Running generated Java tests | No |
| Newman / Postman | Running generated API test collections | No |
| k6 | Running generated performance test scaffolds | No |

### MCP Servers (Optional — for enhanced context)

| MCP Server | Enhancement | Required? |
|------------|-------------|-----------|
| GitHub MCP | Access PR diffs, issue history for regression context | No |
| Filesystem MCP | Read/write project files (redundant if agent has native file access) | No |
| PostgreSQL MCP | Inspect database schema for more accurate database tests | No |
| Browser MCP | Inspect running UI for more accurate E2E selectors | No |
| Playwright MCP | Run and validate generated Playwright tests | No |
| Documentation MCP | Access external API docs for integration tests | No |

**Important**: The skill's instructions never reference these tools as requirements. Test generation produces complete, runnable test code using only the information available in the source files. These enhancements add convenience (live validation, richer context) but do not change the skill's core output.

## Adaptation Checklist

When porting to a new platform:

- [ ] Verify the platform can read multi-file markdown instructions (SKILL.md + references/)
- [ ] Confirm the platform has file read access to the project under test
- [ ] Confirm the platform can write files (test files, report)
- [ ] Adapt the triggering mechanism (description/frontmatter → platform-specific trigger format)
- [ ] Test with a simple fixture (e.g., a TypeScript utility) to verify the workflow produces valid output
- [ ] Reference files load correctly when routed from the detection table
