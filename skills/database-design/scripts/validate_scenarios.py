#!/usr/bin/env python3
"""Static contract validation for the database-design skill."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OUTPUT_SECTIONS = [
    "# Executive Summary", "# Database Recommendation", "# Requirements Analysis",
    "# Domain Model", "# Entity Relationship Diagram", "# Schema Design",
    "# Relationships", "# Constraints", "# Index Strategy", "# Query Optimization",
    "# Performance Considerations", "# Multi-Tenant Strategy", "# Security Review",
    "# Migration Plan", "# Operational Considerations", "# Risks",
    "# Future Scalability", "# Final Recommendations",
]

SCENARIOS = {
    "multi-tenant CRM": ["CRM", "organization", "RLS"],
    "commerce at scale": ["commerce", "order", "millions"],
    "financial ledger": ["ledger", "immutable", "idempotency"],
    "social network": ["social", "feed", "likes"],
    "Supabase RLS": ["Supabase", "JWT", "tenant isolation"],
    "healthcare privacy": ["healthcare", "PHI", "compliance"],
    "AI embeddings": ["embedding", "vector", "RAG"],
    "background jobs": ["event-driven", "background jobs", "dead-letter"],
    "PostgreSQL review": ["PostgreSQL", "EXPLAIN", "N+1"],
    "zero-downtime migration": ["zero-downtime", "backfill", "rollback"],
}


def missing_terms(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if term.lower() not in lower]


def main() -> int:
    required_files = [
        ROOT / "SKILL.md", ROOT / "agents" / "openai.yaml",
        ROOT / "references" / "architecture-and-modeling.md",
        ROOT / "references" / "postgres-and-supabase.md",
        ROOT / "references" / "operations-and-migrations.md",
        ROOT / "references" / "workload-patterns.md",
    ]
    absent_files = [str(path.relative_to(ROOT)) for path in required_files if not path.is_file()]
    if absent_files:
        print("FAIL: missing files: " + ", ".join(absent_files))
        return 1

    text = "\n".join(path.read_text(encoding="utf-8") for path in required_files)
    failures = []
    absent = missing_terms(text, OUTPUT_SECTIONS)
    if absent:
        failures.append("missing output sections: " + ", ".join(absent))
    safeguards = ["requirements", "invariant", "normaliz", "constraint", "index", "security", "migration", "rollback"]
    absent = missing_terms(text, safeguards)
    if absent:
        failures.append("missing design safeguards: " + ", ".join(absent))
    for scenario, terms in SCENARIOS.items():
        absent = missing_terms(text, terms)
        if absent:
            failures.append(f"{scenario}: missing " + ", ".join(absent))
    if failures:
        print("FAIL")
        print("\n".join("- " + failure for failure in failures))
        return 1
    print("PASS: output contract, integrity safeguards, and all 10 requested design scenarios are covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
