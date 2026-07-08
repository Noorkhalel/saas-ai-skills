# RCA Techniques: Hypotheses, Five Whys, Fishbone (Phases 4–6)

The structured-reasoning core. Each technique has a specific failure mode when done sloppily; the discipline notes exist to prevent exactly those.

## Hypothesis generation and elimination (Phase 4)

**Generate wide before going deep.** Write down every mechanism that could produce the observed symptoms — including unflattering ones (our bad deploy) and external ones (provider outage, upstream API change). Anchoring on the first plausible story is the most common RCA failure; forcing 3–6 written hypotheses breaks the anchor.

For each hypothesis, fill all five fields — the empty fields are where sloppy RCAs cheat:

| Field | Forces you to… |
|-------|----------------|
| Confidence (H/M/L) | Commit to how strongly the evidence supports it *now* |
| Supporting evidence | Cite artifacts, not vibes |
| **Contradicting evidence** | Actively look for disconfirmation — the step everyone skips |
| Missing information | Name what would settle it |
| Validation method | Design the cheapest test that would confirm/kill it |

**Eliminate, don't confirm.** Test hypotheses by trying to *disprove* them, cheapest first. Use the symptom shape as a mass filter before any individual test:

- **100% failure since T** → rules out races/load-dependence; implicates a discrete change at T.
- **Intermittent, load-correlated** → concurrency, resource exhaustion, or timeout; rules out simple logic errors.
- **Intermittent, load-independent** → data-dependent (specific records), time-dependent (expiry, midnight, DST), or instance-dependent (one bad pod/node — check if failures cluster by host).
- **Gradual degradation** → accumulation: leak, growth, bloat, backlog. Rules out discrete triggers.
- **Scoped to some users/tenants/regions** → whatever is *different* about that scope is on the causal path.

A hypothesis must explain **all** the symptom dimensions (onset, frequency, scope, timing). One that explains the error but not why it started Tuesday at 14:02 is incomplete — keep it, but say what it fails to explain. Keep ruled-out hypotheses in the report table with what killed them: the elimination *is* the proof of the survivor.

## Five Whys (Phase 5)

Drive from the verified immediate cause down to the process level. The mechanics are trivial; the discipline is everything:

1. **Each answer must be evidence-backed.** The chain is only as strong as its weakest "why." If an answer is a guess, stop — that "why" is your next investigation task, not a link to write down.
2. **Branch on multiple causes.** Real incidents are holes lining up. "Why did bad code reach prod?" legitimately has two parallel answers ("review missed it" *and* "no test covers it") — follow both branches; don't force a single chain.
3. **Don't stop at the person.** "Because the engineer forgot X" is never a root cause — the next why is "why does the system depend on someone remembering X?" The chain ends at a *system or process property*, blamelessly stated.
4. **Don't overshoot into the void.** Stop when the next why no longer yields an actionable engineering improvement ("why do businesses have deadlines?" is past the stop line). The last useful why usually lands on: a missing gate (test/CI/review item/validation), a missing signal (alert/log), or a design property (no idempotency, no isolation, no timeout).
5. **Each level implies an action.** A well-built chain reads back upward as a defense-in-depth plan: fix the code, add the guard, add the gate, add the alert. If a level has no conceivable action, it's probably a symptom restated — merge it.

Worked example (connection-exhaustion incident):
```
Server returned 503s                                    [symptom]
→ why? DB connection pool exhausted                     [metrics: pool at max]
→ why? Connections acquired but never released          [pool telemetry + code read]
→ why? Error path in report job skips release()         [code: early return before finally added in PR #841]
→ why? The acquire/release pattern is hand-rolled at 14 call sites   [grep]
→ why? No pooled-resource abstraction; nothing (lint/review/test) checks release-on-error
ROOT: resource lifecycle left to per-call-site discipline with no enforcement
Actions, reading back up: fix PR #841's early return (corrective) → wrap acquisition
in a with/finally helper and migrate call sites → add lint rule for raw acquire →
add pool-saturation alert at 80% (detection was at 100% = outage).
```

## Fishbone analysis (Phase 6)

Purpose: **sweep for contributing factors the causal chain didn't pass through.** The Five Whys goes deep on one line; the fishbone goes wide so the "second hole" (the one that lined up with the root cause) isn't missed. Run the categories with these prompts:

- **People** — knowledge gaps, onboarding, single-owner components, alert fatigue, unclear ownership at handoffs. (Blameless: name the systemic condition, not the individual.)
- **Process** — review checklist gaps, missing runbooks, change-management holes (config outside review, manual deploy steps), no rollback rehearsal, incident response friction.
- **Code** — the defect class itself, error-handling gaps, missing validation, dead assumptions ("can't happen" comments on the thing that happened).
- **Architecture** — SPOFs, hidden coupling, missing timeouts/breakers/bulkheads, sync where async would contain, shared fate (see `systemic.md`).
- **Infrastructure** — resource limits, scaling policy, node/zone events, capacity vs growth.
- **Dependencies** — version bumps, deprecated APIs, provider incidents, transitive changes, unpinned versions.
- **Configuration** — drift between environments, unvalidated config, silent defaults, secrets/certs expiry.
- **Security** — was the failure exploitable, or exploitation-caused? Auth/authz gaps on the failure path; does the incident reveal an attack surface?
- **Database** — schema assumptions, migration ordering, lock behavior, growth-related plan changes, missing constraints that would have failed fast.
- **Deployment** — pipeline gaps (no canary, no smoke test, no config gate), ordering hazards (migration vs code), artifact drift.
- **Monitoring** — the detection gap: missing signal, wrong threshold, no synthetic check, dashboard that hid it.
- **Operations** — runbook currency, on-call load, escalation clarity, tooling access at 3 a.m.

Report format: list findings under the categories that have them; write "none identified" for the swept-but-empty ones (proves the sweep happened). Every fishbone finding either joins Contributing Factors or spawns a preventive action — a finding with no action attached is an observation, not analysis.
