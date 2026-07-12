# AI / LLM / MCP Security (Phase 10)

Read this when the system integrates an LLM, an AI agent, RAG, a vector store, or MCP tools. Aligned to the OWASP Top 10 for LLM Applications. The core shift: **the model's input and output are both untrusted**. Prompt content is attacker-controllable data, model output is not to be trusted as a command, and any tool the model can call is an entry point an attacker reaches *through* the model.

## Prompt injection (LLM01) — the defining risk

- **Direct prompt injection:** a user tells the model to ignore its instructions, reveal its system prompt, or misbehave. Verify what the model can actually *do* if steered — if it only returns text to the same user, impact is low; if it can call tools, read other users' data, or take actions, impact is high.
- **Indirect prompt injection:** the dangerous one. Untrusted content the model ingests — a web page it browses, a document in RAG, an email it summarizes, a code comment, a tool's response, a file name — contains instructions that the model then follows. The attacker never talks to the model directly; they plant the payload where the model will read it. **Check every path where external/user content enters the context window**, and treat all of it as potentially adversarial.
- **Mitigations to look for (and flag if absent):** untrusted content clearly delimited and labeled as data, not instructions; the model's authority scoped so injection can't reach privileged tools; a human-in-the-loop or confirmation on consequential actions; output/action validation independent of the model. There is no perfect prompt-level defense — the real control is limiting what a hijacked model can *do*.

## Tool / function calling & agency (LLM06/LLM08)

- **Excessive agency:** the agent holds tools far broader than its task needs — a support bot that can delete users, a summarizer with shell access, database tools with write/delete when read suffices. Combined with prompt injection, the tool set *is* the blast radius. **Fix:** least-privilege tools, scoped credentials per tool, read-only where possible.
- **Unsafe tool execution:** model-generated arguments flowing unvalidated into a sink — model output into `exec`/SQL/a file path/an HTTP request/`eval`. This is classic injection with the LLM as the untrusted source; apply `secure-coding.md` sinks to tool arguments. A model that writes a SQL string you execute is a SQL-injection vector.
- **Missing human confirmation** on irreversible/high-impact actions (sending money, deleting data, emailing customers, changing permissions).
- **Tool-triggered SSRF/RCE:** a "fetch URL" or "run code" tool reachable via injection → `secure-coding.md` (SSRF, command injection).

## RAG, memory & data poisoning (LLM03/LLM04/LLM08)

- **RAG/vector-store poisoning:** if users (or ingested external sources) can write to the knowledge base or vector store, an attacker plants documents that (a) carry indirect-injection payloads or (b) bias/mislead answers. Check who can write to the index and whether ingested content is trusted.
- **Memory poisoning:** persistent agent memory that stores unvalidated content across sessions/users — one user poisons another's context, or escalates over time.
- **Cross-tenant/context bleed:** in multi-tenant AI, the vector store and memory must be tenant-scoped exactly like the database (`auth.md`) — a retrieval that isn't filtered by tenant leaks documents across customers. Frequently missed.
- **Training/fine-tuning data:** if user data flows into fine-tuning, check for poisoning and for sensitive-data memorization.

## Sensitive information & context leakage (LLM02/LLM06)

- **System-prompt / context leakage:** secrets, API keys, internal instructions, or other users' data placed in the context window can be extracted by prompting. Don't put secrets in prompts; don't put one user's data in another's context.
- **Sensitive data in responses / logs:** model output (and the full prompt+completion logged for debugging) carrying PII/secrets to the wrong audience or an over-retained log store.
- **Output disclosure:** the model revealing training data, other tenants' data retrieved via RAG, or internal system details.

## Output handling (LLM05)

- **Insecure output handling:** treating model output as safe when it reaches a sink — rendering it as HTML (XSS), inserting it into SQL, using it as a shell command or file path, or as a URL to fetch. **Model output is untrusted input to the next component** — encode/validate it exactly as you would user input. This is the mirror of prompt injection and just as common.

## Resource & cost (LLM04/LLM10)

- **Unbounded consumption:** no rate/quota limits on expensive model/tool calls → cost-amplification DoS ("denial of wallet"), and unbounded loops in agentic flows (an agent that retries or recurses without a cap).
- **Model DoS:** very long inputs or adversarial prompts driving cost/latency.

## MCP-specific (Model Context Protocol)

- **Tool trust & provenance:** which MCP servers are connected, and are they trusted? A malicious or compromised MCP server can return tool descriptions and results that are themselves injection payloads (tool-description injection) or that exfiltrate data. Treat third-party MCP servers as untrusted code paths.
- **Over-broad tool permissions:** MCP tools granting filesystem, database, cloud, or shell access wider than the agent needs — least privilege per server, scoped credentials, read-only where possible.
- **Credential exposure through tools:** tokens/keys handed to MCP tools, logged in tool I/O, or embedded in tool configs. Check what each server can reach and with whose credentials.
- **Confused deputy:** the agent using its own elevated permissions on behalf of a lower-privileged user's request — enforce the *user's* authorization on tool actions, not just the agent's.
- **Prompt/response boundary:** untrusted tool output re-entering the model context is an indirect-injection channel — same defense as RAG content.

## Reporting

Per finding: the LLM/OWASP-LLM category, the untrusted-content path (where the attacker plants input), what a hijacked model can *do* (the tool/authority it reaches), the impact, and the fix (scope tools, validate output at the sink, tenant-filter retrieval, add confirmation, delimit untrusted content). Emphasize agency-limiting over prompt-patching — the durable control is minimizing what a compromised model can reach. State what you ruled out (e.g., "tools are read-only and tenant-scoped; injection impact limited to the requesting user's own data").
