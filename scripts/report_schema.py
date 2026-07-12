"""Small dependency-free validator for the repository's report JSON Schemas.

The schemas remain portable JSON Schema documents.  This validator deliberately
implements the stable report contract used by the deterministic adapter so CI
does not depend on a third-party package manager.
"""
from __future__ import annotations

from typing import Any, Mapping

REQUIRED_SECTIONS = ("scope", "evidence", "assumptions", "findings", "recommendations")
SEVERITIES = {"critical", "high", "medium", "low", "info"}
CONFIDENCE = {"high", "medium", "low"}


def validate_report(report: object, skill: str) -> list[str]:
    """Return contract violations without retaining or echoing report content."""
    if not isinstance(report, Mapping):
        return ["report must be an object"]
    errors: list[str] = []
    for key in ("schema_version", "metadata", "sections", "findings", "recommendations", "workflow"):
        if key not in report:
            errors.append(f"missing required property: {key}")
    if report.get("schema_version") != "1.0":
        errors.append("unsupported report schema version")
    metadata = report.get("metadata")
    if not isinstance(metadata, Mapping):
        errors.append("metadata must be an object")
    elif metadata.get("skill") != skill or not isinstance(metadata.get("adapter"), str) or not isinstance(metadata.get("generated_at"), str):
        errors.append("metadata must include selected skill, adapter, and generation timestamp")
    sections = report.get("sections")
    if not isinstance(sections, Mapping):
        errors.append("sections must be an object")
    else:
        for name in REQUIRED_SECTIONS:
            if not isinstance(sections.get(name), list):
                errors.append(f"required section must be an array: {name}")
    findings = report.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be an array")
    else:
        for index, finding in enumerate(findings):
            if not isinstance(finding, Mapping):
                errors.append(f"finding {index} must be an object")
                continue
            required = {"id", "title", "severity", "confidence", "evidence", "recommendation"}
            if not required <= finding.keys() or not isinstance(finding.get("evidence"), list):
                errors.append(f"finding {index} is structurally invalid")
            if finding.get("severity") not in SEVERITIES or finding.get("confidence") not in CONFIDENCE:
                errors.append(f"finding {index} has invalid severity or confidence")
    if not isinstance(report.get("recommendations"), list):
        errors.append("recommendations must be an array")
    workflow = report.get("workflow")
    if not isinstance(workflow, Mapping) or not all(isinstance(workflow.get(key), bool) for key in ("enabled", "artifact_generated", "handoff_generated")):
        errors.append("workflow metadata is invalid")
    return errors
