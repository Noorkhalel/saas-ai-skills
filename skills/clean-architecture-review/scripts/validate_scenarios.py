#!/usr/bin/env python3
"""Static contract validation for the clean-architecture-review skill."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SECTIONS = [
    "# Executive Summary", "# Architecture Score", "# Architecture Style", "# Layer Review",
    "# Dependency Review", "# Module Review", "# Domain Review", "# Clean Architecture Compliance",
    "# DDD Review", "# SOLID Review", "# Architecture Smells", "# Coupling & Cohesion Analysis",
    "# Testability Review", "# Scalability Review", "# Refactoring Recommendations",
    "# Priority Improvements", "# Production Readiness",
]

SCENARIOS = {
    "React and FastAPI SaaS": ["React", "FastAPI", "Clean Architecture"],
    "NestJS DDD monolith": ["NestJS", "modular monolith", "DDD"],
    "legacy MVC": ["legacy MVC", "incremental", "characterization"],
    "Spring Hexagonal": ["Spring Boot", "Hexagonal", "port"],
    "commerce microservices": ["microservices", "commerce", "data ownership"],
    "Supabase SaaS": ["Supabase", "feature module", "tenant"],
    "CQRS event sourcing": ["CQRS", "event sourcing", "replay"],
    "tightly coupled startup": ["tightly coupled", "coupling", "cycle"],
    "enterprise monolith": ["enterprise monolith", "modernization", "strangler"],
    "long-term SaaS": ["production-ready SaaS", "maintainability", "team"],
}


def absent(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if term.lower() not in lower]


def main() -> int:
    files = [
        ROOT / "SKILL.md", ROOT / "agents" / "openai.yaml",
        ROOT / "references" / "patterns-and-boundaries.md",
        ROOT / "references" / "dependency-and-testability.md",
        ROOT / "references" / "evolution-and-modernization.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        print("FAIL: missing files: " + ", ".join(missing))
        return 1
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    failures = []
    if items := absent(text, SECTIONS):
        failures.append("missing output sections: " + ", ".join(items))
    if items := absent(text, ["Verified", "Assumption", "dependency", "incremental", "validation"]):
        failures.append("missing review safeguards: " + ", ".join(items))
    for scenario, terms in SCENARIOS.items():
        if items := absent(text, terms):
            failures.append(f"{scenario}: missing " + ", ".join(items))
    if failures:
        print("FAIL")
        print("\n".join("- " + item for item in failures))
        return 1
    print("PASS: output contract, review safeguards, and all 10 requested architecture scenarios are covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
