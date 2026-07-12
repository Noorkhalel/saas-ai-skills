#!/usr/bin/env python3
"""Offline prompt-regression mutations over the production evaluation request path."""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluation_context import ContextDocument, EvaluationRequest, build_evaluation_request, render_evaluation_prompt
from run_behavioral_evals import deterministic_contract_adapter, evaluate, load_cases


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "evals" / "mutation-instruction-map.json"
OUT = ROOT / "eval-results" / "instruction-mutation-report.json"


class MutationError(RuntimeError):
    """Safe mutation configuration error; locators are identifiers, not content dumps."""


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def replace_exactly_once(content: str, locator: str, replacement: str, *, instruction_id: str) -> str:
    count = content.count(locator)
    if count != 1:
        raise MutationError(f"instruction {instruction_id} matched {count} locations; expected exactly one")
    return content.replace(locator, replacement, 1)


def load_map() -> list[dict[str, Any]]:
    data = json.loads(MAP.read_text(encoding="utf-8"))
    required = {"skill", "instruction_id", "source", "instruction_locator", "mutation", "replacement", "behavior", "required_fragments", "dependent_case", "same_skill_control", "other_skill_control", "expected_failure"}
    if data.get("schema_version") != "1.0" or not isinstance(data.get("mutations"), list):
        raise MutationError("mutation instruction map has an unsupported schema")
    if any(not isinstance(item, dict) or not required <= item.keys() for item in data["mutations"]):
        raise MutationError("mutation instruction map has an incomplete entry")
    return data["mutations"]


def case_by_id(case_id: str) -> dict[str, Any]:
    for case in load_cases():
        if case["id"] == case_id:
            return case
    raise MutationError("mapped evaluation case is missing")


def _metadata_for(request: EvaluationRequest, documents: tuple[ContextDocument, ...], skill_markdown: str) -> Mapping[str, object]:
    metadata = dict(request.metadata)
    metadata["skill_sha256"] = _sha(skill_markdown)
    metadata["shared_context_sha256"] = {document.relative_path: document.sha256 for document in documents}
    return MappingProxyType(metadata)


def mutate_request(request: EvaluationRequest, entry: Mapping[str, Any]) -> EvaluationRequest:
    """Mutate only in-memory request content and refresh structural integrity data."""
    locator, replacement, instruction_id = entry["instruction_locator"], entry["replacement"], entry["instruction_id"]
    if entry["source"] == "skill_markdown":
        mutated_skill = replace_exactly_once(request.skill_markdown, locator, replacement, instruction_id=instruction_id)
        return replace(request, skill_markdown=mutated_skill, metadata=_metadata_for(request, request.shared_context, mutated_skill))
    if entry["source"] == "shared_policy":
        target = entry["source_logical_name"]
        matches = [document for document in request.shared_context if document.logical_name == target]
        if len(matches) != 1:
            raise MutationError(f"instruction {instruction_id} has no unique packaged shared policy")
        original = matches[0]
        content = replace_exactly_once(original.content, locator, replacement, instruction_id=instruction_id)
        mutated_document = replace(original, content=content, sha256=_sha(content))
        documents = tuple(mutated_document if document is original else document for document in request.shared_context)
        return replace(request, shared_context=documents, metadata=_metadata_for(request, documents, request.skill_markdown))
    raise MutationError(f"instruction {instruction_id} has an unsupported source")


def _source_content(request: EvaluationRequest, entry: Mapping[str, Any]) -> str:
    if entry["source"] == "skill_markdown":
        return request.skill_markdown
    matches = [document for document in request.shared_context if document.logical_name == entry["source_logical_name"]]
    if len(matches) != 1:
        return ""
    return matches[0].content


def prompt_regression_verdict(request: EvaluationRequest, entry: Mapping[str, Any]) -> dict[str, Any]:
    """Case-specific offline probe; it checks instruction semantics, not model output."""
    structural = deterministic_contract_adapter(request)
    source = _source_content(request, entry)
    missing = [fragment for fragment in entry["required_fragments"] if fragment not in source]
    rendered = render_evaluation_prompt(request)
    mutation_applied = entry["instruction_locator"] not in source
    expected_rendered_content = entry["replacement"] if mutation_applied else entry["instruction_locator"]
    mutated_present = expected_rendered_content in rendered if expected_rendered_content else entry["instruction_locator"] not in rendered
    failures: list[str] = []
    if structural["errors"]:
        failures.append("contract_context_invalid")
    if missing:
        failures.append(entry["expected_failure"])
    if not mutated_present:
        failures.append("mutated_content_not_supplied_to_adapter")
    return {"passed": not failures, "failed_behaviors": failures, "rendered_context_sha256": _sha(rendered), "structural_errors": structural["errors"]}


def _baseline_request(entry: Mapping[str, Any], case_id: str) -> EvaluationRequest:
    case = case_by_id(case_id)
    return build_evaluation_request(case, entry["skill"])


def run_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    baseline_request = _baseline_request(entry, entry["dependent_case"])
    baseline = prompt_regression_verdict(baseline_request, entry)
    mutated_request = mutate_request(baseline_request, entry)
    mutated = prompt_regression_verdict(mutated_request, entry)
    same_control_request = mutate_request(_baseline_request(entry, entry["same_skill_control"]), entry)
    same_control = deterministic_contract_adapter(same_control_request)
    other_control = evaluate(case_by_id(entry["other_skill_control"]), "contract")
    killed = baseline["passed"] and not mutated["passed"] and entry["expected_failure"] in mutated["failed_behaviors"]
    controls_passed = not same_control["errors"] and other_control["status"] == "passed"
    return {
        "skill": entry["skill"], "instruction_id": entry["instruction_id"], "mutation": entry["mutation"], "dependent_case": entry["dependent_case"],
        "expected_failure": entry["expected_failure"], "baseline_passed": baseline["passed"], "mutated_passed": mutated["passed"], "failed_behaviors": mutated["failed_behaviors"],
        "rendered_context_sha256": mutated["rendered_context_sha256"], "killed": killed, "controls_passed": controls_passed,
        "same_skill_control": entry["same_skill_control"], "other_skill_control": entry["other_skill_control"],
    }


def run_all() -> dict[str, Any]:
    results = [run_entry(entry) for entry in load_map()]
    killed = sum(result["killed"] for result in results)
    surviving = len(results) - killed
    return {"schema_version": "1.0", "mutations_total": len(results), "mutations_killed": killed, "mutations_survived": surviving, "mutation_score": killed / len(results) if results else 0.0, "skills_covered": sorted({result["skill"] for result in results}), "behavior_categories": sorted({result["expected_failure"] for result in results}), "results": results}


def main() -> int:
    try:
        report = run_all()
    except MutationError as error:
        print(f"FAIL: {error}")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    failures = [result for result in report["results"] if not result["killed"] or not result["controls_passed"]]
    if failures:
        print(f"FAIL: {report['mutations_killed']}/{report['mutations_total']} instruction mutations killed; controls failed or mutations survived.")
        return 1
    print(f"PASS: {report['mutations_killed']}/{report['mutations_total']} instruction mutations killed; mutation sensitivity is not model-behavior assurance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
