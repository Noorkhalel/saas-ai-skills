# Root Cause Analysis: Techniques and Output

Read for Phase 4 — turning a ranked list of hypotheses into a proven root cause — and for the full output template. The goal of RCA is not to find *a* cause but *the* cause: the thing that, if it had been different, the bug would not have happened, and that is worth fixing.

## The causal chain

The exception line is where the bug *surfaced*. Trace it back through layers — each answers "but why did that happen?":

1. **Immediate cause** — the mechanical fault. "`getUser` dereferenced `undefined`." Fixing only here (`user?.id`) suppresses the symptom and usually hides the real bug.
2. **Underlying cause** — why the immediate cause occurred. "`req.user` was undefined because auth middleware ran after the route handler."
3. **System-design cause** — what in the design *allowed* it. "Middleware order is implicit and unenforced; nothing fails when it's wrong."
4. **Process cause** — how it reached production. "No integration test covers unauthenticated access; the reordering PR wasn't caught in review."
5. **Preventive action** — the fix at each level. Immediate: restore order. Design: make auth a global guard with explicit opt-out. Process: add the missing test + a middleware-order check in CI.

Report the immediate + underlying cause always (that's *the root cause* for fixing); report system/process causes when the bug reveals a pattern that will recur — that's the difference between fixing a bug and fixing the *class* of bug.

## Five Whys

Ask "why" until you reach something actionable and non-obvious — typically 3–5 levels. Discipline that keeps it honest:

- Each "why" must be **supported by evidence**, not a guess. If you can't answer a "why" from evidence, that's your next investigation step, not a place to invent an answer.
- **Branch when there are multiple causes.** "Why was the value null?" may have two contributing paths — follow both; real incidents are often a coincidence of two things (the "Swiss cheese" model: several small holes lining up).
- Stop at what you can *change*. "Why did the network partition?" bottoms out at "networks partition" — the actionable level is "why did a partition cause data loss?" (missing idempotency/retry design).

Worked: *500 error* → why? *`charge()` threw* → why? *Stripe returned a duplicate-charge error* → why? *the request was retried* → why? *the client retried on a timeout, and the call isn't idempotent* → why? *no idempotency key is sent*. Root cause: non-idempotent payment call under a retrying client (HIGH — trace confirms the retry + the missing key). Fix operates at "add idempotency key," not "catch the Stripe error."

## Elimination

When several hypotheses survive Phase 3, disprove rather than confirm — it's faster and less biased:

- **Order by cost to test, cheapest first.** A hypothesis you can kill with one log line or one query goes before one needing a repro harness.
- **Design each test to distinguish** between surviving hypotheses, not merely confirm your favorite. "If it's the cache, this key is stale; if it's the query, the plan shows a seq scan — the same request tells me which."
- **Use the symptom shape as a filter.** *100% failure* rules out data-dependent and race hypotheses (those are intermittent). *Only in production* points at environment/config/scale/data, not logic. *Started at 14:30* aligns to a deploy/config change/cron/traffic shift — get the timeline. *Only for some users* → data-specific (their record, their locale, their tenant, their permissions).
- **Bisect in time and space.** `git bisect` finds the commit; binary-searching the data flow (log the value at the midpoint of the pipeline — is it wrong yet?) finds the location. Both halve the search each step.

## Dependency and execution-path tracing

- **Data flow (backward from the bad value):** where was it born, what transformed it, where did it go wrong? Log/inspect at the midpoint; recurse into the half that's already wrong.
- **Control flow (forward to the failure):** which branch actually executed? Confirm — don't assume — which path ran; the bug is often "the else branch you didn't think about" or a guard that didn't trigger.
- **Dependency tracing:** does the fault track a version bump, a changed config, an upstream API change, a schema migration? Cross-reference the failure's start time with every change in that window.

## Reproduction

A reliably reproducible bug is nearly solved. Escalate toward determinism:

- Capture exact inputs, environment, and state that trigger it. Turn "sometimes fails" into "fails when the queue has ≥2 items for the same key" — the condition *is* the diagnosis.
- Shrink to the minimal repro (smallest input/steps that still fails) — it strips away everything that isn't the cause.
- For intermittent bugs, force the condition: inject the delay that makes the race deterministic, pin the clock/timezone, cap memory to reproduce the OOM, replay the exact payload. See `references/concurrency.md`.
- The endpoint of reproduction is a **failing automated test** — it verifies the cause now and guards the regression forever.

## When you cannot fully prove it

Sometimes access is limited and the top hypothesis stalls at MEDIUM. That's a legitimate stopping point — deliver it honestly:

- State the leading cause, its confidence, and the *specific* evidence that would raise it to HIGH ("run `EXPLAIN ANALYZE` on this query" / "add this log line and reproduce" / "share the auth middleware file").
- Give a safe interim mitigation if one exists (rate-limit, feature-flag off, roll back the suspect deploy) distinct from the real fix — and label it as buying time, not fixing.
- Never upgrade the confidence to justify shipping a fix. A wrong fix on a MEDIUM guess restarts the clock and adds risk.

## Full output template

```markdown
# Debugging Summary
One paragraph: problem, root cause (confidence), fix in a sentence.

## Problem Statement
## Environment
## Reproduction Steps
## Symptoms
## Collected Evidence          ← cite locations/log lines/commits; facts, not guesses
## Possible Causes
| Confidence | Cause | Evidence for | Evidence against / missing |
## Root Cause                  ← proven cause + confidence + why alternatives are ruled out
## Why It Happened             ← causal chain: immediate → underlying → system → process
## Code Analysis
## Architecture Analysis
## Security Analysis           ← or "N/A — checked, no auth/input/data-boundary surface"
## Performance Analysis        ← or "N/A — checked"
## Recommended Fix             ← chosen level, why safe, behavior preserved
## Alternative Fixes           ← minimal / recommended / long-term, trade-offs
## Risks
## Regression Risks
## Tests to Add                ← the repro-as-test + edge cases (name + assertion)
## Prevention Recommendations  ← monitor/alert/lint/guardrail beyond the code
## Final Action Plan           ← ordered steps; verification that closes the incident
```

Scale down for small bugs (Problem, Root Cause+confidence, Recommended Fix, Tests) but never drop the confidence tag on the root cause or the regression test — those are what make it a *diagnosis* and not a guess.
