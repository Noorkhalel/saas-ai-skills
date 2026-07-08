# Corrective and Preventive Actions (Phase 8)

The RCA's value is measured here: an incident whose actions don't prevent recurrence was investigated for nothing. This file covers the corrective/preventive split, the four prevention questions, action quality standards, and lessons-learned writing.

## Corrective vs preventive — keep them separate

- **Corrective actions** fix *this* incident: repair the defect, reconcile the damaged data, restore the degraded capacity. Standards: minimal, behavior-preserving (except the bug), reversible where possible, verified by a test that reproduces the incident. Corrective actions close the incident; they do **not** close the RCA.
- **Preventive actions** kill the *class*: the guard, gate, test, alert, or design property that makes recurrence impossible or immediately visible. The recurrence test from SKILL.md is the acceptance criterion: *with these shipped, can this incident happen again?*

Never present the corrective fix as closure. The report's headline action is preventive — that's the difference between a postmortem and a patch note.

## The four prevention questions — answer all four explicitly

**1. Could monitoring have detected this earlier?**
Work from the timeline's failure→detection gap. What signal existed but wasn't watched (the metric that moved first)? What signal *didn't exist* (the Unknowns from evidence collection)? Recommendations must be concrete: the metric, the threshold, the alert route — "alert when pool utilization >80% for 5m" not "improve monitoring." Include synthetic checks for the user flow that broke (the outage was invisible until users hit it = no synthetic probe existed). Detection-time target: the alert should fire before the second user is affected, not after the 7th minute.

**2. Could automated testing have prevented this?**
Name the *specific* test at the *right layer*: the unit test on the branch that misbehaved; the integration test that would have exercised the real dependency (the mock hid it); the migration test against production-shaped data; the concurrency test firing N parallel requests at the invariant; the config/startup test asserting required keys resolve. The first Recommended Test is always the regression test that reproduces this incident — written to fail on the pre-fix code.

**3. Could CI/CD have caught this?**
The gate that was missing: config-schema validation, migration/code ordering check, dependency-diff review on lockfile changes, smoke test post-deploy, canary with automatic rollback on error-rate delta, startup health gate (fail the rollout when the new pods crash — the deploy should have stopped itself). If the pipeline *had* the gate and it didn't fire, that's a different finding (gate coverage/threshold) — say which.

**4. Could architecture make this impossible?**
The strongest prevention: make the failure unrepresentable rather than caught — idempotency keys (duplicates become no-ops), constraints in the schema (corruption fails fast at write), timeouts/breakers/bulkheads (propagation physically contained), fail-fast startup on invalid config (bad deploys never take traffic), immutable/versioned artifacts (drift impossible). Weigh cost honestly (`systemic.md` cost classes) — recommend the architectural fix when the class justifies it, the cheap guard when it doesn't.

## Action quality standards

Every action in the Final Action Plan must be:

- **Specific** — "add `CHECK (quantity >= 0)` to inventory" not "improve data integrity."
- **Verifiable** — it has a done-condition someone can check (the test exists and fails on old code; the alert fired in a game-day drill).
- **Owned-able** — scoped so one team could own it (you may not know the org; scope it anyway).
- **Prioritized** — P0: corrective + anything leaving the system currently exposed. P1: prevention for this class (the recurrence-test items). P2: broader hardening the incident motivated.
- **Deduplicated** — Five Whys, fishbone, and systemic analysis converge on overlapping actions; merge them in the Final Action Plan and keep the traceability ("addresses Why #3 and Monitoring finding").

A plan of 25 actions is a plan to do none of them — cap at the vital few (typically 3–8), and explicitly park the rest as "considered, deferred because…".

## Lessons learned — writing them so they transfer

2–4 lessons, each a *transferable engineering statement*, not a restatement of the fix:

- Bad: "We fixed the missing null check." (patch note)
- Bad: "Be more careful with deploys." (unfalsifiable, blames diligence)
- Good: "Config and code that must change together shipped through disconnected paths; any pair of coupled changes without a shared gate will eventually skew — we found three more such pairs." (names the pattern, generalizes, shows the sweep)

Include what went *well* (the rollback that worked, the alert that did fire) — future incidents depend on knowing which defenses are real.

## Blameless writing

Process and people findings are load-bearing and must be sayable — which requires blameless framing: name conditions, not culprits. "The review checklist has no migration-ordering item" (actionable) vs "the reviewer missed the ordering problem" (same fact, now unactionable and unsayable in front of the team). The test: every sentence should remain true and useful if all names were swapped. Systems that punish honest postmortems stop getting honest evidence; the report you write should be one the person closest to the incident would endorse as fair.

## Recurring-incident analysis

If this incident (or its class) has happened before: prior occurrence dates and prior action items go *in the report*. Were the previous preventive actions shipped? If shipped and it recurred, the prior RCA's root cause was wrong or shallow — re-open the Five Whys from where it stopped. If never shipped, the finding is a process one: postmortem actions lack follow-through (tracking, ownership, priority) — and *that* becomes the headline preventive action. Recurrence is the strongest evidence in RCA; use it.
