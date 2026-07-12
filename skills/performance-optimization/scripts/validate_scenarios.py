#!/usr/bin/env python3
"""Static contract validation for the performance-optimization skill."""
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"

REQUIRED_SECTIONS = [
    "# Executive Summary", "# Performance Score", "# Current Bottlenecks",
    "# Performance Profile", "# Backend Review", "# Frontend Review",
    "# Database Review", "# API Review", "# Infrastructure Review",
    "# Caching Review", "# Scalability Review", "# Optimization Opportunities",
    "# Estimated Impact", "# Priority Order", "# Benchmarking Plan",
    "# Regression Risks", "# Validation Strategy", "# Long-term Recommendations",
]

SCENARIOS = {
    "Next.js dashboard": ["LCP", "hydration", "accessibility"],
    "Node REST API": ["event-loop", "N+1", "timeouts"],
    "FastAPI database": ["FastAPI", "EXPLAIN", "transaction"],
    "Supabase multi-tenant": ["Supabase", "RLS", "tenant isolation"],
    "PostgreSQL N+1": ["PostgreSQL", "missing index", "N+1"],
    "Docker and Kubernetes": ["Kubernetes", "autoscal", "throttling"],
    "Redis e-commerce cache": ["Redis", "stampede", "freshness"],
    "GraphQL load": ["GraphQL", "DataLoader", "authorization"],
    "Millions of jobs": ["queue", "idempotency", "dead-letter"],
    "RAG and MCP": ["RAG", "MCP", "quality"],
}


def contains_all(text: str, required: list[str]) -> list[str]:
    lower = text.lower()
    return [item for item in required if item.lower() not in lower]


def main() -> int:
    files = [SKILL, ROOT / "agents" / "openai.yaml", ROOT / "references" / "evidence-and-experiments.md",
             ROOT / "references" / "database-and-cache.md", ROOT / "references" / "frontend.md",
             ROOT / "references" / "cloud-and-async.md", ROOT / "references" / "domain-playbooks.md"]
    missing_files = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing_files:
        print("FAIL: missing files: " + ", ".join(missing_files))
        return 1

    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    failures = []
    absent = contains_all(text, REQUIRED_SECTIONS)
    if absent:
        failures.append("missing output sections: " + ", ".join(absent))
    for scenario, markers in SCENARIOS.items():
        absent = contains_all(text, markers)
        if absent:
            failures.append(f"{scenario}: missing coverage for " + ", ".join(absent))

    behavioral = ["Verified", "Hypothesis", "Benchmark", "rollback", "correctness"]
    absent = contains_all(text, behavioral)
    if absent:
        failures.append("missing evidence/validation safeguards: " + ", ".join(absent))
    if failures:
        print("FAIL")
        print("\n".join("- " + failure for failure in failures))
        return 1
    print("PASS: output contract, evidence safeguards, and all 10 requested scenario playbooks are covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
