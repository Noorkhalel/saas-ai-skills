#!/usr/bin/env python3
"""Structurally validate GitHub Actions permissions and required release gates."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
POLICY = ROOT / "shared" / "ci-permissions-policy.json"
PINNED_ACTION = re.compile(r"^\s*(?:-\s+)?uses: [^@\s]+@[0-9a-f]{40}(?:\s+#.*)?$", re.M)
ALLOWED_LEVELS = {"none", "read", "write"}


def _permissions(value: Any, *, location: str, errors: list[str]) -> dict[str, str]:
    if value is None:
        return {}
    if isinstance(value, str) and value in {"read-all", "write-all"}:
        errors.append(f"{location}: broad permission shorthand is forbidden: {value}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{location}: permissions must be a mapping or explicit empty mapping")
        return {}
    parsed: dict[str, str] = {}
    for permission, level in value.items():
        if not isinstance(permission, str) or level not in ALLOWED_LEVELS:
            errors.append(f"{location}: invalid permission declaration")
            continue
        parsed[permission] = level
    return parsed

def _yaml_for_parser(text: str) -> str:
    """GitHub expressions are scalars, although generic YAML parsers see `{`."""
    return re.sub(r"(?m)(:\s*)\$\{\{[^\n]*\}\}(\s*)$", r'\1"__github_expression__"\2', text)


def validate_workflow(name: str, document: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    top = _permissions(document.get("permissions"), location=f"Workflow: {name}", errors=errors)
    defaults = policy["default_permissions"]
    jobs = document.get("jobs", {})
    if not isinstance(jobs, dict):
        return [*errors, f"Workflow: {name}: jobs must be a mapping"]
    triggers = document.get(True, document.get("on", {}))  # PyYAML parses unquoted 'on' as True in YAML 1.1.
    unsafe_pr = isinstance(triggers, dict) and ("pull_request_target" in triggers or "workflow_run" in triggers)
    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            errors.append(f"Workflow: {name}; Job: {job_id}: job must be a mapping")
            continue
        declared = _permissions(job.get("permissions"), location=f"Workflow: {name}; Job: {job_id}", errors=errors)
        effective = declared if "permissions" in job else top
        effective = {**defaults, **effective}
        for permission, level in effective.items():
            if level == "none":
                continue
            exception = next((item for item in policy["exceptions"] if item.get("workflow") == name and item.get("job") == job_id and item.get("permission") == permission and item.get("access") == level), None)
            allowed = defaults.get(permission) == level
            if not allowed and not exception:
                errors.append(f"Workflow: {name}; Job: {job_id}; Permission: {permission}: {level} rejected: not in explicit allowlist")
            if level == "write" and unsafe_pr:
                errors.append(f"Workflow: {name}; Job: {job_id}; Permission: {permission}: write rejected for unsafe trigger")
            if permission == "id-token" and level == "write" and not exception:
                errors.append(f"Workflow: {name}; Job: {job_id}; Permission: id-token: write requires an exact trusted-job exception")
        if "uses" in job and "permissions" not in job and not top:
            errors.append(f"Workflow: {name}; Job: {job_id}: reusable workflow must declare effective permissions")
    return errors


def main() -> int:
    if yaml is None:
        print("FAIL: PyYAML is required for structural GitHub Actions validation.")
        return 1
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if policy.get("schema_version") != "1.0" or not isinstance(policy.get("default_permissions"), dict) or not isinstance(policy.get("exceptions"), list):
        print("FAIL: CI permission policy is invalid.")
        return 1
    errors: list[str] = []
    workflow_text: dict[str, str] = {}
    for path in sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")]):
        text = path.read_text(encoding="utf-8"); workflow_text[path.name] = text
        try:
            document = yaml.safe_load(_yaml_for_parser(text))
        except yaml.YAMLError:
            errors.append(f"Workflow: {path.name}: invalid YAML")
            continue
        if not isinstance(document, dict):
            errors.append(f"Workflow: {path.name}: root must be a mapping")
            continue
        errors.extend(validate_workflow(path.name, document, policy))
        if "pull_request_target" in text:
            errors.append(f"Workflow: {path.name}: pull_request_target is forbidden")
        for line in [line for line in text.splitlines() if "uses:" in line]:
            if not PINNED_ACTION.match(line):
                errors.append(f"Workflow: {path.name}: action is not commit-pinned")
    validate = workflow_text.get("validate-skills.yml", "")
    for required in ["python scripts/ci.py validate", "python scripts/ci.py eval:all", "python scripts/ci.py package:check", "python scripts/run_deterministic_evals.py --skill"]:
        if required not in validate:
            errors.append("validate-skills.yml: required release gate missing")
    if "windows-latest" not in validate or "matrix.os" not in validate:
        errors.append("validate-skills.yml: cross-platform validation matrix is missing")
    model = workflow_text.get("model-evals.yml", "")
    if "pull_request" in model or "push:" in model:
        errors.append("model-evals.yml: protected model evaluation must remain manually dispatched")
    if errors:
        print("FAIL:\n" + "\n".join(f"- {error}" for error in errors)); return 1
    print("PASS: all workflow and job effective permissions match the explicit allowlist; actions are pinned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
