# Skill Evaluation Contract

Every `skills/<name>/evals/evals.json` uses schema version `1.0`. Evals assess behavior, not exact wording.

## Required fields

Each eval declares `id`, `scenario`, `user_request`, `expected_activation`, `must_not_activate`, `expected_behavior`, `expected_output_characteristics`, `failure_conditions`, and `validation`.

`validation` must assert the skill-specific artifact schema, the standard handoff fields, safe workflow-state changes, stable finding IDs, topic filtering, and standalone behavior.

## Required coverage

Every suite includes: happy path, complex real-world, missing information, conflicting requirements, large repository, small repository, legacy project, greenfield project, ambiguous request, and an incorrect-routing attempt. The incorrect-routing attempt must activate another skill and explicitly exclude the owning skill.

## Workflow assertions

When optional workflow integration is enabled, write the skill artifact and standardized handoff before marking only `runs.<skill-name>` complete; preserve unknown metadata and other runs. Treat matching handoffs only as unverified leads and verify material claims. When workflow files are absent, malformed, irrelevant, unavailable, or opted out, complete the task standalone.
