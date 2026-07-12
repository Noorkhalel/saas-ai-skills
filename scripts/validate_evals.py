#!/usr/bin/env python3
"""Validate behavior eval coverage and repository-wide routing tests."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SCENARIOS = {
    "happy-path", "complex-real-world", "missing-information", "conflicting-requirements",
    "large-repository", "small-repository", "legacy-project", "greenfield-project",
    "ambiguous-request", "incorrect-routing-attempt",
}
EVAL_FIELDS = {
    "id", "scenario", "user_request", "expected_activation", "must_not_activate",
    "expected_behavior", "expected_output_characteristics", "failure_conditions", "validation",
}
VALIDATION_FIELDS = {
    "artifact_schema", "handoff_schema", "workflow_state", "stable_finding_ids",
    "topic_filtering", "standalone_behavior",
}
HANDOFF_FIELDS = {
    "schema_version", "source_skill", "run_status", "summary", "topics", "findings",
    "decisions", "open_questions", "recommended_actions", "recommended_next_skills", "full_output_file",
}


def load(path: Path, failures: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        failures.append(f"invalid JSON: {path.relative_to(ROOT)}: {error}")
        return None


def main() -> int:
    failures: list[str] = []
    names = sorted(path.name for path in SKILLS.iterdir() if path.is_dir())
    routes = load(ROOT / "shared" / "routing-tests.json", failures)
    if not isinstance(routes, dict) or not isinstance(routes.get("tests"), list):
        failures.append("routing-tests.json lacks a tests array")
        routes = {"tests": []}
    route_ids: dict[str, dict] = {}
    for route in routes["tests"]:
        required = {"id", "skills", "user_request", "expected_activation", "must_not_activate", "selection_rule"}
        if not isinstance(route, dict) or not required <= route.keys():
            failures.append("routing test has missing fields")
            continue
        if route["id"] in route_ids:
            failures.append(f"duplicate routing test id: {route['id']}")
        route_ids[route["id"]] = route
        if len(route["skills"]) != 2 or route["expected_activation"] not in route["skills"] or not route["must_not_activate"]:
            failures.append(f"invalid routing test: {route['id']}")
    if len(route_ids) < 30:
        failures.append("routing test catalog is incomplete")
    all_ids: set[str] = set()
    requests: set[str] = set()
    for name in names:
        skill = SKILLS / name / "SKILL.md"
        text = skill.read_text(encoding="utf-8") if skill.is_file() else ""
        if "## Routing Boundary" not in text or "**Use this skill when**" not in text or "**Do NOT use this skill when**" not in text:
            failures.append(f"{name}: incomplete routing boundary")
        suite = load(SKILLS / name / "evals" / "evals.json", failures)
        if not isinstance(suite, dict):
            continue
        if suite.get("schema_version") != "1.0" or suite.get("skill_name") != name or suite.get("eval_contract") != "shared/eval-schema.md":
            failures.append(f"{name}: invalid eval-suite header")
        cases = suite.get("evals", [])
        if not isinstance(cases, list) or len(cases) < 10:
            failures.append(f"{name}: fewer than ten evals")
            continue
        covered: set[str] = set()
        has_wrong_route = False
        for case in cases:
            if not isinstance(case, dict) or not EVAL_FIELDS <= case.keys():
                failures.append(f"{name}: eval missing fields")
                continue
            if case["id"] in all_ids:
                failures.append(f"duplicate eval id: {case['id']}")
            all_ids.add(case["id"])
            request = " ".join(case["user_request"].lower().split())
            if request in requests:
                failures.append(f"duplicate eval request: {case['user_request']}")
            requests.add(request)
            covered.add(case["scenario"])
            validation = case["validation"]
            if not isinstance(validation, dict) or not VALIDATION_FIELDS <= validation.keys():
                failures.append(f"{case['id']}: incomplete output validation")
            elif not HANDOFF_FIELDS <= set(validation["handoff_schema"]):
                failures.append(f"{case['id']}: incomplete handoff schema assertion")
            if case["scenario"] == "incorrect-routing-attempt":
                has_wrong_route = case["expected_activation"] != name and name in case["must_not_activate"]
        if missing := SCENARIOS - covered:
            failures.append(f"{name}: missing scenarios {sorted(missing)}")
        if not has_wrong_route:
            failures.append(f"{name}: incorrect-routing case does not refuse owner")
        linked = suite.get("routing_test_ids")
        if not isinstance(linked, list) or not linked:
            failures.append(f"{name}: no linked routing tests")
        for route_id in linked or []:
            route = route_ids.get(route_id)
            if route is None or name not in route.get("skills", []):
                failures.append(f"{name}: invalid routing-test link {route_id}")
    if failures:
        print("FAIL")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"PASS: {len(names)} skill suites, {len(all_ids)} evals, and {len(route_ids)} routing tests validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
