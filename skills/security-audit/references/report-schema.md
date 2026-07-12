# Security Audit Report Schema

The full template, the per-finding schema, and a worked example. SKILL.md carries the abbreviated version; read this when you want the complete structure or an example of the expected depth and tone.

## Per-finding schema

Every finding — in the Findings section — uses this shape. Scale the prose to severity: a CRITICAL earns a full trace, a LOW earns two lines.

```markdown
### [SEVERITY] Short title — path/file.ext:line  ·  OWASP Axx (if applicable)
- **What:** the vulnerability in one sentence.
- **Attack:** the actor (anonymous / authenticated user / peer tenant / admin), the concrete steps, and what they gain.
- **Evidence:** the source→sink trace or config that proves it — quote the exact code/line. This is what separates a finding from a guess.
- **Likelihood:** High/Med/Low · **Impact:** High/Med/Low · **Exploitability:** trivial / needs-auth / needs-specific-state · **Business impact:** the concrete consequence (data breach, fund loss, downtime, compliance) · **Confidence:** Confirmed / Likely / Needs-verification.
- **Fix:** the smallest change that closes it, with a snippet where useful. Note any behavior change or trade-off.
```

**Confidence discipline:** *Confirmed* = you traced source to sink in the code. *Likely* = strong signal but one link inferred. *Needs-verification* = you suspect it but couldn't confirm reachability — say what you'd need. Never label a Needs-verification finding CRITICAL without the trace; it's a question until proven.

## Full report template

```markdown
# Security Audit: [target]

## Executive Summary
2–4 sentences for a decision-maker: what was audited, overall posture, headline risks, deploy verdict. Scope, visibility limits, and key assumptions stated here.

## Security Score
Score: N/10 — one-line justification.
Findings: Critical N · High N · Medium N · Low N · Informational N.

## Risk Overview & Attack Surface
Entry points, trust boundaries, where risk concentrates. Tight.

## Threat Model
- **Assets:** …
- **Actors:** anonymous · user · admin · service …
- **Trust boundaries:** …
- **Entry points:** …
- **Key STRIDE threats:** per boundary, the ones that matter.

## Findings
(All CRITICAL, then HIGH, MEDIUM, LOW, INFORMATIONAL — each in the per-finding schema above.)

## Domain Reviews
(Only in-scope sections; others "N/A — not in scope." Each: what you checked, what you found (link to findings), what you ruled out.)
- Authentication
- Authorization & Tenant Isolation
- Secure Coding
- OWASP Top 10 (category-by-category coverage)
- API Security
- Database Security
- Cloud Security
- Infrastructure (Docker / K8s / IaC)
- CI/CD & Supply Chain
- Dependency Audit
- AI / LLM / MCP Security

## Compliance Considerations
(Only if the stated context implies an obligation — PCI-DSS / GDPR / HIPAA / SOC 2. Map findings to obligations; don't invent scope.)

## Remediation Plan & Priority Order
1. All CRITICAL first, then HIGH, then by leverage. Each: fix · effort (S/M/L) · what it unblocks.

## Production Readiness
Ready / Not Ready / Ready with conditions — reason tied to findings. Any open CRITICAL ⇒ Not Ready. Exactly what must change to flip it.

## Long-term Recommendations
Architectural/process improvements, separated from must-fix.

## Coverage & Tooling
Audited deeply / skimmed / not reached; tools run or recommended.
```

## Scaling the report to the target

- **Single file or snippet:** keep Executive Summary, Score, Findings, Production Readiness. Collapse Threat Model to two lines and mark infra/CI/AI domains "N/A — not in scope." Don't manufacture a 12-section report for 40 lines.
- **A PR/diff:** use Pull Request audit mode (SKILL.md) — findings scoped to the change, Blocking vs Non-blocking, Approve/Request-changes verdict.
- **A whole service or repo:** the full template, plus an explicit coverage statement (what you audited deeply vs sampled vs didn't reach).
- **An infra-only target** (Terraform/K8s): lead with Cloud/Infrastructure domains; code-level domains become "N/A."

## Worked example (abbreviated)

**Trigger:** "Security audit this Express orders endpoint — is it safe to ship?" + a handler that does `jwt.decode(token)`, string-interpolates `req.query.status` into SQL, fetches order by `:id` with no ownership check, and returns `err.stack` on error.

**Report (compressed):**

> **Executive Summary** — Audited a single Express orders endpoint (~45 lines); no infra or CI in scope. Posture is unsafe to ship: authentication is fully bypassable and the primary query is injectable, both reachable by an unauthenticated attacker. **Not Ready.**
>
> **Security Score:** 2/10 — auth bypass + SQL injection on a public path. Critical 2 · High 1 · Medium 1 · Low 0 · Info 0.
>
> **Threat Model** — Asset: customer orders (PII, amounts). Actors: anonymous attacker, authenticated user. Boundary: internet→app→DB. Entry point: `GET /orders`, `GET /orders/:id`. STRIDE: Spoofing (forgeable token), Info-disclosure (injection, IDOR).
>
> **Findings**
> **### [CRITICAL] Auth bypass — `jwt.decode` never verifies signature — orders.js:14 · OWASP A07**
> What: the token is decoded, not verified, so any forged JWT is accepted. Attack: anonymous attacker crafts `{"user_id":1,"role":"admin"}`, base64-encodes it, calls the API — full access as any user. Evidence: `const user = jwt.decode(token)` — no `jwt.verify(token, secret)`. Likelihood High · Impact High · Exploitability trivial · Business impact full account/data compromise · Confidence Confirmed. Fix: `jwt.verify(token, process.env.JWT_SECRET, {algorithms:['HS256']})`; reject on throw.
>
> **### [CRITICAL] SQL injection via `status` — orders.js:23 · OWASP A03**
> What: `req.query.status` is interpolated into the query string. Attack: `?status=x' OR '1'='1` dumps all orders; `; DROP`/stacked queries per driver. Evidence: `` `...WHERE status='${req.query.status}'` ``. …Confidence Confirmed. Fix: parameterized query with a bound `$1`; allowlist status values.
>
> **### [HIGH] IDOR on GET /orders/:id — orders.js:38 · OWASP A01** … no `WHERE user_id = session.user`; any authenticated user reads any order. Fix: add the ownership predicate.
>
> **### [MEDIUM] Stack trace leaked to client — orders.js:51 · A09** … `res.send(err.stack)` exposes internals. Fix: generic client error, log detail server-side.
>
> **Remediation & Priority:** 1) verify JWT (S) 2) parameterize + allowlist status (S) 3) add ownership predicate (S) 4) generic error handler (S). **Production Readiness: Not Ready** — two open CRITICALs; ship only after items 1–3. **Coverage:** endpoint audited line-by-line; DB schema, auth middleware config, and deployment not seen — recommend confirming JWT secret strength and DB account privileges.

Note what the example does: every CRITICAL is traced to a quoted line, each names a concrete attacker and gain, severities aren't inflated (the stack-trace leak stays MEDIUM), and coverage is stated honestly. That's the bar.
