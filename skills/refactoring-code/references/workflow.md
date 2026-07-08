# Refactoring Workflow — Detailed Phases and Report Templates

Read this file for multi-step engagements: codebase audits, refactors spanning more than one or two transformations, or whenever you need the full report template. The four phases mirror the workflow summary in SKILL.md; this file adds the per-phase checklists, the incremental change protocol, and the output templates.

## Contents

- [Phase A — Understand](#phase-a--understand)
- [Phase B — Diagnose and plan](#phase-b--diagnose-and-plan)
- [Phase C — Transform and verify](#phase-c--transform-and-verify)
- [Phase D — Review and recommend](#phase-d--review-and-recommend)
- [When not to refactor](#when-not-to-refactor)
- [Report templates](#report-templates)

---

## Phase A — Understand

Judging code you don't understand produces confident, wrong plans. Spend this phase building a model of the system before forming any opinion about its quality.

**Checklist:**

- [ ] Identify what the code does for its users — the business capability, not the implementation.
- [ ] Find the entry points into the code in scope (routes, handlers, CLI commands, public exports, scheduled jobs).
- [ ] Trace the primary data flow end to end at least once.
- [ ] Map dependency direction: what does this code import, and who imports it? Note anything that flows the "wrong" way (domain depending on infrastructure, low-level utilities importing high-level modules).
- [ ] Read representative *callers* of the code you'll change — the call sites define the real contract, including quirks callers depend on.
- [ ] For each class/module in scope, write one sentence: "This exists to ___." If you can't, or the sentence needs "and", that's your first diagnostic finding.
- [ ] Check test coverage of the code in scope: which behaviors are pinned by tests, which are not?
- [ ] Check version-control history for the hot spots if available — files that change constantly with many authors are both the highest-value and highest-risk targets.

**Output of this phase:** a short system summary you could show the user — components, responsibilities, dependency direction, coverage state. In a large repo, explicitly state what you scoped *out*.

## Phase B — Diagnose and plan

**Detect smells** (`references/code-smells.md`):

- Name each smell precisely with its location: `Feature Envy — Order.calculateShipping (src/order.ts:141)`.
- Record the *evidence*, not just the label: "reads 6 fields of `Customer`, 0 of `Order`".
- Distinguish smells that hurt now (blocking the current task, causing bugs) from smells that merely offend. Prioritize the former.

**Estimate risk** (risk model in SKILL.md):

- For each candidate change, determine blast radius: search all usages, including string-based references (reflection, DI container config, serialization names, templates, SQL, docs).
- Note the danger multipliers present: concurrency, serialization, framework magic, dynamic dispatch, missing tests.
- Decide the verification each change needs: type-check only / full suite / characterization tests first / manual exercise of the flow.

**Choose transformations** (`references/patterns.md`):

- Pick the *smallest* pattern that fixes the smell. Extract Method before Extract Class; Extract Class before introducing a design pattern; a design pattern only when the smell is exactly the problem that pattern exists to solve.
- Sequence the plan so each step is independently green and independently valuable. A good plan can be abandoned halfway and still leave the code better.
- Order by dependency: rename and extract *within* a unit before moving the unit; establish the target structure before migrating callers.

**Output of this phase:** the Refactoring Plan (see template) presented to the user *before* transforming, whenever the work is more than a couple of low-risk steps. This is the decision point the contract requires.

## Phase C — Transform and verify

The green-to-green loop, per step:

1. **Confirm green.** Run the relevant tests/build before touching anything. If they're already red, stop and report — never refactor on red, you'd have no way to detect your own breakage.
2. **Apply exactly one named transformation.** Resist bundling "while I'm here" edits.
3. **Verify.** Rerun tests, type-check, build. Verification depth per the risk tier.
4. **Review the diff.** Every hunk should be explainable as part of the named transformation. Behavior-looking changes in a refactoring diff (a changed condition, a reordered side effect, a different default) are red flags — justify or revert them.
5. **Checkpoint.** Commit with a message naming the transformation ("Extract PricingCalculator from Order"). If the user's workflow doesn't use commits per step, keep a mental/written checkpoint list so any step can be undone.
6. If verification fails: **revert, don't debug forward.** The failed step told you something your model of the code missed — usually a hidden caller or side effect. Update the plan with that knowledge.

Additional rules while transforming:

- Use tool-assisted operations (IDE/language-server rename, compiler-checked moves) over hand edits when available — they see call sites you won't.
- Watch for behavior smuggling: reordering statements across side effects, changing evaluation order of conditions, converting eager to lazy (or sync to async), tightening/loosening null handling. These are the classic ways "pure structure" changes alter behavior.
- If you discover mid-refactor that a step requires a behavior change (e.g., two "duplicate" blocks turn out to differ subtly), stop, surface the difference, and let the user decide. Subtle divergence is often an undocumented bug fix — or an undocumented bug.

## Phase D — Review and recommend

After the transformation is verified, run the three review lenses over the *final* state of the code:

- **Architecture** (`references/architecture.md`): dependency direction, cohesion, boundary integrity, principle violations that remain.
- **Security** (`references/security.md`): mandatory scan of the checklist areas the code touches. Report findings; do not silently fix behavior-changing vulnerabilities.
- **Performance** (`references/performance.md`): existing issues worth reporting, plus a self-check that your refactoring didn't regress (added allocations in hot loops, dropped memoization, N+1 introduced by extracting a query into a per-item helper).

Then compile Future Improvements: out-of-scope smells you noted, next-step refactorings the new structure enables, tests worth adding. Order by value relative to risk.

## When not to refactor

Recommending *against* refactoring is a valid, sometimes best, outcome:

- **The code is about to be deleted or replaced.** Polish on condemned code is waste.
- **A rewrite is genuinely cheaper** — rare, but real for small, well-specified, badly built units with good tests around them.
- **No safety net can be built** and the change is medium/high risk. Say what test infrastructure would unlock the work.
- **The smell is cosmetic and the code is stable.** Untouched, working, low-churn code earns tolerance.
- **Mid-crisis.** Don't restructure during an incident; stabilize first.

## Report templates

Scale to the engagement. Omit sections with nothing to say rather than padding them — but for a full audit, all sections should have content.

### Full report (audits, multi-step engagements)

```markdown
# Refactoring Report: <scope>

## Executive Summary
2–5 sentences: state of the code, top findings, what you did/propose, behavior-preservation status.

## Architecture Review
Current structure, dependency direction, boundary/principle violations (SOLID etc.), verdict.

## Code Smells
| Smell | Location | Evidence | Severity |
Named per the catalog, with file:line.

## Risk Assessment
Per planned change: risk tier, blast radius, danger multipliers, required verification.

## Refactoring Plan
Ordered steps; each names a transformation, its target, and its verification. Mark step boundaries where work could stop safely.

## Incremental Changes
What was actually applied, step by step, with verification result for each. (Omit if plan-only.)

## Security Review
Findings per the security checklist, each with location and severity. State explicitly if none found — and which areas you checked.

## Performance Review
Findings + confirmation the refactoring itself introduced no regressions.

## Testing Impact
Coverage before/after; tests added; recommended tests not yet written (unit / integration / edge / regression).

## Complexity & Maintainability Analysis
Before/after on the measures that changed: nesting depth, method/class size, duplication, coupling, cohesion. Qualitative is fine; use metrics when tooling is available.

## Suggested Design Patterns
Patterns whose introduction is justified by an observed smell (not speculation), with the smell that justifies each.

## Future Improvements
Out-of-scope work worth doing next, ordered by value/risk.
```

### Lightweight response (single-transformation tasks)

```markdown
**Smells found:** <smell> at <file:line> — <one-line evidence>
**Applied:** <named refactorings and where>
**Verification:** <tests/build/type-check results — behavior preserved>
**Also noticed (not changed):** <out-of-scope observations, if any>
```
