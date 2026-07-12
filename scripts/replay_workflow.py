#!/usr/bin/env python3
"""Replay and validate persisted workflow state without executing skill artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
TOPICS = set(json.loads((ROOT / "shared" / "handoff-topics.json").read_text(encoding="utf-8"))["topics"])
RUN_STATUSES = {"not_started", "in_progress", "completed", "partial", "failed"}
HANDOFF_FIELDS = {"schema_version", "source_skill", "run_status", "summary", "topics", "findings", "decisions", "open_questions", "recommended_actions", "recommended_next_skills", "full_output_file"}


def _safe_project_path(project: Path, value: object, expected_prefix: str) -> Path | None:
    if not isinstance(value, str) or not value.startswith(expected_prefix): return None
    candidate = (project / value).resolve()
    return candidate if project.resolve() in candidate.parents else None


def replay(workflow_dir: Path) -> dict[str, Any]:
    """Return a non-mutating integrity/provenance report for one workflow run."""
    errors: list[str] = []; inspected: list[str] = []; project = workflow_dir.parent
    try:
        state = json.loads((workflow_dir / "state.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": "1.0", "workflow": str(workflow_dir), "valid": False, "runs": [], "errors": ["state.json is missing or invalid"]}
    if not isinstance(state, Mapping) or not isinstance(state.get("runs"), Mapping):
        return {"schema_version": "1.0", "workflow": str(workflow_dir), "valid": False, "runs": [], "errors": ["state.json has unsupported shape"]}
    for skill, run in state["runs"].items():
        inspected.append(str(skill))
        if not isinstance(skill, str) or not isinstance(run, Mapping) or run.get("status") not in RUN_STATUSES:
            errors.append(f"{skill}: invalid run metadata"); continue
        if run.get("status") != "completed": continue
        artifact = _safe_project_path(project, run.get("artifact_file"), ".ai-workflow/artifacts/")
        handoff_path = _safe_project_path(project, run.get("handoff_file"), ".ai-workflow/handoffs/")
        if artifact is None or not artifact.is_file(): errors.append(f"{skill}: completed artifact is missing or unsafe")
        if handoff_path is None or not handoff_path.is_file(): errors.append(f"{skill}: completed handoff is missing or unsafe"); continue
        try: handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): errors.append(f"{skill}: handoff is invalid JSON"); continue
        if not isinstance(handoff, Mapping) or not HANDOFF_FIELDS <= handoff.keys(): errors.append(f"{skill}: handoff schema is incomplete"); continue
        if handoff.get("source_skill") != skill or handoff.get("run_status") != "completed": errors.append(f"{skill}: handoff provenance/status does not match state")
        if not isinstance(handoff.get("topics"), list) or not all(isinstance(topic, str) and topic in TOPICS for topic in handoff["topics"]): errors.append(f"{skill}: handoff topics are invalid")
        full_output = _safe_project_path(project, handoff.get("full_output_file"), ".ai-workflow/artifacts/")
        if full_output is None or not full_output.is_file(): errors.append(f"{skill}: handoff artifact reference is missing or unsafe")
    return {"schema_version": "1.0", "workflow": str(workflow_dir), "valid": not errors, "runs": inspected, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--workflow-dir", type=Path, required=True); args = parser.parse_args()
    report = replay(args.workflow_dir); print(json.dumps(report, indent=2)); return 0 if report["valid"] else 1


if __name__ == "__main__": raise SystemExit(main())
