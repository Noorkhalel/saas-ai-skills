# Security Review During Refactoring

Run this review on every engagement (workflow step 9). Refactoring puts you in a rare position: you are reading this code more closely than anyone has in months. Use that attention — but keep the hats separate.

## The two duties

**1. Do no harm (mandatory, silent).** Your refactoring must never weaken existing security properties. This is part of behavior preservation and needs no permission:

- Moving SQL/commands into helpers must keep parameterization/escaping exactly — never "simplify" a parameterized query into string concatenation, and never build a generic helper that takes pre-formatted query strings.
- Moving or deduplicating code must not drop, reorder, or weaken validation, authorization checks, or sanitization that sat in its path. When merging "duplicate" blocks, check whether one copy carries a check the other lacks — merging to the unchecked version is how vulnerabilities are *introduced* by refactoring.
- Extracting/renaming must not widen visibility (private → public), broaden a catch that previously let security failures propagate, relax a type that enforced validation, or expose internals through a new interface that were previously unreachable.
- Preserve fail-closed behavior: if the old code denied on error, the new structure must too.
- Never move secrets into more-readable places (logs, error messages, config committed to VCS, client-side code) as a side effect of restructuring.

**2. Inspect and report (mandatory, explicit).** Check the areas below for the code in scope and report findings with location and severity. **Fixing a vulnerability changes behavior** — it rejects inputs it used to accept, adds checks, alters responses. So findings go in the Security Review section of your report for the user's decision; don't silently fold fixes into the refactor. (Exception: if the user asked for security fixes, they're approved behavior changes — still list them.)

In the report, state which areas you checked even when you found nothing: "no findings" is only meaningful with a stated scope.

## Inspection checklist

Check each area that the code in scope touches:

**Injection**
- **SQL Injection** — queries built by string concatenation/interpolation with external input; dynamic table/column names from input; ORMs escape-hatched into raw SQL. Safe form: parameterized queries/prepared statements everywhere; identifiers from allowlists.
- **Command Injection** — shell commands assembled from input (`exec`, `system`, backticks, `shell=True`); user data in command arguments without argument-array APIs. Safe form: argument arrays, no shell interpolation, allowlisted binaries.
- **XSS** — user content rendered into HTML/JS without context-appropriate encoding; framework escape hatches (`innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `| safe`); user input reaching `eval`-like sinks or attribute/URL contexts.
- **Unsafe deserialization** — native deserializers on untrusted bytes (`pickle`, Java `ObjectInputStream`, PHP `unserialize`, YAML full loaders); type information taken from the payload. Safe form: data-only formats (JSON) + schema validation.

**Request forgery**
- **CSRF** — state-changing endpoints without CSRF tokens or same-site protections; GET handlers with side effects (also a Hidden Side Effects smell).
- **SSRF** — server-side fetches of URLs derived from user input without allowlisting; redirects followed blindly; internal metadata endpoints reachable.

**Identity and access**
- **Authentication flaws** — homegrown password hashing (or fast hashes like MD5/SHA-1 for passwords), tokens that never expire, credentials compared with non-constant-time equality, session fixation, missing auth on "internal" endpoints.
- **Authorization flaws** — the classic during refactoring: auth checked at the entry point but not at the object level (IDOR — `GET /orders/123` fetches any user's order); role checks scattered and inconsistent (Shotgun Surgery of authz — a *good* refactoring target: centralize, with user approval); trust in client-supplied identifiers.

**Data and inputs**
- **Secrets** — API keys, passwords, tokens hardcoded in source or config-in-repo; secrets in logs, error messages, or exception traces; secrets in client-delivered code. Flag every one; recommend env/secret-manager injection and rotation of anything already committed.
- **Missing validation** — external input (params, headers, files, message payloads, third-party API responses) used without type/range/format checks; validation only client-side; validation present but bypassable via alternate entry points (a boundary refactoring like Introduce Value Object with constructor validation is the structural fix — recommend it).
- **Unsafe file handling** — paths joined with user input without canonicalization + containment checks (traversal); uploaded filenames trusted; file type inferred from extension/Content-Type; temp files with predictable names; archives extracted without path checks (zip-slip).

**Systemic**
- **Race conditions** — check-then-act on shared state (balance check then debit, exists-check then create) without locking/transactions/atomic ops; TOCTOU on files. Note: refactoring itself can *introduce* races by splitting an atomic operation across extracted methods or by making a sync path async — check your own diff for this.
- **Dependency vulnerabilities** — while you're in the manifest: obviously abandoned or known-vulnerable dependencies, wildly outdated pinned versions. Recommend an audit (`npm audit`, `pip-audit`, `cargo audit`, Dependabot); don't bump versions as part of a refactor (behavior change + separate risk).

## Reporting format

Per finding, in the Security Review section:

```markdown
- **[Severity: critical/high/medium/low] <category>** — <file:line>
  <what the code does and why it's exploitable, one or two sentences>
  Recommendation: <specific fix; note that it is a behavior change requiring approval>
```

Severity honestly: reachable-with-untrusted-input injection is critical; a hardcoded secret in a private repo is high; a missing validation on an internal admin tool is lower. If you're unsure whether something is exploitable, report it with your uncertainty stated rather than dropping it.
