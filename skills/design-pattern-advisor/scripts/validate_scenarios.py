#!/usr/bin/env python3
"""Static contract validation for the design-pattern-advisor skill."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SECTIONS = [
    "# Design Pattern Advisory Report", "## Executive Summary", "## Review Scope",
    "## Context and Assumptions", "## Problem Definition", "## Design Forces",
    "## Current Design Assessment", "## Does This Need a Pattern?", "## Candidate Patterns",
    "## Recommended Pattern", "## Rejected Alternatives", "## Implementation Plan",
    "## Example Structure", "## Required Tests", "## Migration Risks",
    "## Validation Checklist", "## Final Recommendation",
]

SCENARIOS = {
    "payment variation": ["Stripe", "PayPal", "bank", "Strategy"],
    "SDK incompatibility": ["Adapter", "third-party", "contract-test"],
    "workflow variation": ["Template Method", "composition", "Strategy"],
    "order state": ["State", "state machine", "transition"],
    "React fetching": ["React", "custom hook", "state"],
    "small CRUD": ["CRUD", "No pattern", "simple"],
    "reliable events": ["Outbox", "idempotency", "delivery"],
    "complex creation": ["Factory", "Builder", "construction"],
    "Singleton global state": ["Singleton", "global state", "lifetime"],
    "PR complexity": ["PR", "interfaces", "factories"],
}


def absent(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if term.lower() not in lower]


def main() -> int:
    files = [
        ROOT / "SKILL.md", ROOT / "agents" / "openai.yaml",
        ROOT / "references" / "pattern-catalog.md",
        ROOT / "references" / "language-and-distributed.md",
        ROOT / "references" / "implementation-and-examples.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        print("FAIL: missing files: " + ", ".join(missing))
        return 1
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    failures = []
    if items := absent(text, SECTIONS):
        failures.append("missing output sections: " + ", ".join(items))
    if items := absent(text, ["No pattern", "simpler", "confidence", "trade-off", "validation"]):
        failures.append("missing anti-overengineering safeguards: " + ", ".join(items))
    for scenario, terms in SCENARIOS.items():
        if items := absent(text, terms):
            failures.append(f"{scenario}: missing " + ", ".join(items))
    if failures:
        print("FAIL")
        print("\n".join("- " + failure for failure in failures))
        return 1
    print("PASS: output contract, anti-overengineering safeguards, and all 10 requested pattern scenarios are covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
