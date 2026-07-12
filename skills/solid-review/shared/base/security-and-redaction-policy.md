<!-- policy_id: BF-SECURITY-1; framework_version: 1.1.0 -->
# Security and redaction policy

Never reproduce secrets in output, handoffs, state, logs, examples, or snapshots. Replace values with `<redacted>` and report only the category, safe identifier/location, exposure, impact, and appropriate rotation or containment guidance. Do not weaken authentication, authorization, tenancy, privacy, or deployment safeguards merely to make a change easier.
