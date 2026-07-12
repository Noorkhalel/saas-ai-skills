# Optional AI Workflow Contract

This contract provides an optional, file-based way for independently installed skills to share concise, verified leads. It never changes a skill's primary task: every skill works alone, other skills are optional, and the repository/project files remain the source of truth.

This file is canonical in the collection. A synchronized copy is shipped as `shared/workflow-contract.md` inside every skill package so a single-skill installation has the same instructions.

## Runtime layout

When workflow integration is enabled in a writable project, use this project-local layout. Do not create it merely to perform a normal standalone task; enable it when the user requests persistent workflow output or an existing `.ai-workflow/` directory signals that the project uses it.

```text
.ai-workflow/
  state.json                 # lightweight metadata only
  artifacts/<skill-name>.md  # detailed, skill-specific output
  handoffs/<skill-name>.json # concise cross-skill summary
```

`state.json` contains only `schema_version`, optional project/workflow metadata, and `runs.<skill-name>` metadata such as status, artifact path, handoff path, and timestamps. Never put full reports, evidence, code excerpts, or complete finding lists in it. Artifacts retain each skill's own output structure; only handoffs are standardized.

## Safe workflow behavior

1. Begin from project files and current user input. Check `.ai-workflow/state.json` only if it exists.
2. Treat a handoff as an optional lead, never as verified fact. Inspect only concise handoffs whose `topics` or finding `related_topics` intersect the current skill's relevant topics; ignore the rest.
3. Verify important inherited claims in the repository before relying on them. Open `full_output_file` only when a matching handoff needs additional evidence.
4. Missing, stale, malformed, inaccessible, or irrelevant workflow files must not block or degrade the primary task. Report the limitation briefly if it matters, then continue normally.
5. Do not duplicate inherited findings. When extending one, include `source_skill` and `source_finding` in the new finding or decision where the receiving skill's output format allows it.
6. A `recommended_next_skills` entry is advisory. The named skill might not be installed or run, and its absence is never an error.

## Handoff contract

Write compact JSON to `.ai-workflow/handoffs/<skill-name>.json` after the detailed artifact is available:

```json
{
  "schema_version": "1.0",
  "source_skill": "database-design",
  "run_status": "completed",
  "summary": "Concise summary intended for other installed skills.",
  "topics": ["database", "performance", "multi-tenancy"],
  "findings": [
    {
      "id": "DB-001",
      "title": "Short finding title",
      "severity": "high",
      "summary": "Short explanation only.",
      "affected_files": [],
      "related_topics": ["security", "authorization"]
    }
  ],
  "decisions": [],
  "open_questions": [],
  "recommended_actions": [],
  "recommended_next_skills": [],
  "full_output_file": ".ai-workflow/artifacts/database-design.md"
}
```

Keep `summary`, finding summaries, decisions, questions, and actions concise. Include only findings that can help another skill; put extensive evidence, logs, code excerpts, and skill-specific analysis in the artifact. `severity` is optional when it does not apply. Use stable, skill-local finding IDs. `topics` and `related_topics` support relevance filtering, not automatic truth or routing.

When a new result extends an inherited finding, retain provenance where the receiving skill's output format permits it:

```json
{"source_skill":"security-audit","source_finding":"SEC-004"}
```

## State update protocol

Use the installed skill directory name as the stable key. On start, optionally set `runs.<skill-name>.status` to `in_progress`; on completion, partial completion, or failure, write the truthful status: `completed`, `partial`, or `failed` (`not_started` is also valid).

For every update:

1. Re-read the latest `state.json` immediately before writing. If it is absent, initialize `{"schema_version":"1.0","project":{"name":null,"repository_root":"."},"runs":{}}`.
2. If it is malformed or has an unsupported shape, preserve it (for example as `state.invalid-<timestamp>.json`) when safe, initialize a new valid state, and never delete artifacts or handoffs to recover.
3. Preserve unknown top-level fields and every other `runs` entry. Change only this skill's run metadata; do not replace the file from an old in-memory snapshot.
4. Record relative artifact and handoff paths plus useful timestamps. Write the artifact and handoff before marking the run `completed`.

Example run metadata:

```json
{
  "status": "completed",
  "artifact_file": ".ai-workflow/artifacts/database-design.md",
  "handoff_file": ".ai-workflow/handoffs/database-design.json",
  "updated_at": "2026-07-12T00:00:00Z"
}
```

If filesystem writes are unavailable or the user opts out, return the skill's normal output and do not treat the lack of workflow files as a failure.
