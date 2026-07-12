#!/usr/bin/env python3
"""Static contract validation for the solid-review skill."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "# SOLID Review Report", "## Executive Summary", "## Review Scope",
    "## Context and Assumptions", "## Overall SOLID Score", "## Principle Scores",
    "## Critical and High-Priority Findings", "## Detailed Findings",
    "## Single Responsibility Review", "## Open/Closed Review", "## Liskov Substitution Review",
    "## Interface Segregation Review", "## Dependency Inversion Review",
    "## Coupling and Cohesion Analysis", "## Positive Design Findings", "## Refactoring Roadmap",
    "## Regression Risks", "## Verification Plan", "## Final Recommendation",
]

SCENARIOS = {
    "TypeScript SRP service": ["TypeScript", "validation", "persistence", "email", "formatting"],
    "payment OCP": ["Stripe", "PayPal", "bank-transfer"],
    "LSP subtype": ["UnsupportedOperation", "subtype", "composition"],
    "ISP consumer": ["read-only", "administrative", "consumer"],
    "DIP infrastructure": ["Prisma", "Supabase", "payment SDK"],
    "small CRUD": ["CRUD", "overengineering", "Non-issue"],
    "functional TypeScript": ["functional", "functions", "structural types"],
    "React concerns": ["React", "rendering", "state transitions"],
    "framework conventions": ["Nest", "Spring Boot", "decorators"],
    "PR LSP/ISP": ["PR", "Blocking", "shared interface"],
}


def absent(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if term.lower() not in lower]


def main() -> int:
    files = [
        ROOT / "SKILL.md", ROOT / "agents" / "openai.yaml",
        ROOT / "references" / "principles-and-evidence.md",
        ROOT / "references" / "refactoring-and-language.md",
        ROOT / "references" / "examples.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        print("FAIL: missing files: " + ", ".join(missing))
        return 1
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    failures = []
    if items := absent(text, REQUIRED):
        failures.append("missing output sections: " + ", ".join(items))
    if items := absent(text, ["Verified", "Hypothesis", "severity", "confidence", "validation"]):
        failures.append("missing evidence safeguards: " + ", ".join(items))
    for scenario, terms in SCENARIOS.items():
        if items := absent(text, terms):
            failures.append(f"{scenario}: missing " + ", ".join(items))
    if failures:
        print("FAIL")
        print("\n".join("- " + failure for failure in failures))
        return 1
    print("PASS: output contract, false-positive safeguards, and all 10 requested SOLID scenarios are covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
