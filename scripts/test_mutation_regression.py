#!/usr/bin/env python3
"""Regression tests for the offline instruction-to-case mutation matrix."""
from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import mutation_regression as mutations


class MutationRegressionTests(unittest.TestCase):
    def test_full_matrix_kills_every_mapped_instruction_mutation(self) -> None:
        report = mutations.run_all()
        self.assertEqual(8, report["mutations_total"])
        self.assertEqual(report["mutations_total"], report["mutations_killed"])
        self.assertEqual(0, report["mutations_survived"])
        self.assertGreaterEqual(len(report["skills_covered"]), 5)
        self.assertGreaterEqual(len(report["behavior_categories"]), 6)
        for result in report["results"]:
            self.assertTrue(result["baseline_passed"], self.diagnostic(result, "baseline must pass"))
            self.assertFalse(result["mutated_passed"], self.diagnostic(result, "mutated case must fail"))
            self.assertIn(result["expected_failure"], result["failed_behaviors"], self.diagnostic(result, "expected failure missing"))
            self.assertTrue(result["controls_passed"], self.diagnostic(result, "unrelated controls must pass"))

    def test_helpers_reject_missing_and_ambiguous_locators(self) -> None:
        with self.assertRaises(mutations.MutationError):
            mutations.replace_exactly_once("one instruction", "missing", "", instruction_id="missing")
        with self.assertRaises(mutations.MutationError):
            mutations.replace_exactly_once("instruction instruction", "instruction", "", instruction_id="ambiguous")

    def test_mutated_full_content_flows_through_rendered_adapter_request(self) -> None:
        entry = mutations.load_map()[0]
        baseline_request = mutations._baseline_request(entry, entry["dependent_case"])
        mutated_request = mutations.mutate_request(baseline_request, entry)
        baseline = mutations.prompt_regression_verdict(baseline_request, entry)
        mutated = mutations.prompt_regression_verdict(mutated_request, entry)
        self.assertTrue(baseline["passed"])
        self.assertFalse(mutated["passed"])
        self.assertNotEqual(baseline["rendered_context_sha256"], mutated["rendered_context_sha256"])
        self.assertIn(entry["expected_failure"], mutated["failed_behaviors"])

    def test_matrix_does_not_modify_tracked_skill_or_policy_sources(self) -> None:
        paths = [mutations.ROOT / "skills" / "security-audit" / "SKILL.md", mutations.ROOT / "shared" / "base" / "untrusted-content-policy.md"]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        mutations.run_all()
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self.assertEqual(before, after)

    @staticmethod
    def diagnostic(result: dict, expectation: str) -> str:
        return (
            f"Skill: {result['skill']}; Instruction ID: {result['instruction_id']}; Mutation: {result['mutation']}; "
            f"Dependent case: {result['dependent_case']}; Expected: {expectation}; "
            f"Expected failure: {result['expected_failure']}; Rendered prompt hash: {result['rendered_context_sha256']}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
