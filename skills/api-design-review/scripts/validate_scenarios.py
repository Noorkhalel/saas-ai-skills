#!/usr/bin/env python3
"""Static contract validation for the api-design-review skill."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SECTIONS = [
    "# Executive Summary", "# API Score", "# API Style Review", "# Resource Model Review",
    "# Endpoint Review", "# Request Design", "# Response Design", "# Error Handling",
    "# Authentication Review", "# Authorization Review", "# Versioning Review",
    "# Performance Review", "# Security Review", "# Documentation Review",
    "# Scalability Review", "# Production Readiness", "# Priority Recommendations",
    "# Long-term Improvements",
]

SCENARIOS = {
    "REST multi-tenant CRM": ["REST", "CRM", "tenant"],
    "GraphQL commerce": ["GraphQL", "commerce", "DataLoader"],
    "gRPC microservices": ["gRPC", ".proto", "microservice"],
    "public versioned SDK": ["public", "deprecation", "SDK"],
    "Supabase Edge Function": ["Supabase", "RLS", "Edge Function"],
    "JWT and OAuth2 auth": ["JWT", "OAuth2", "authentication"],
    "payments": ["payment", "idempotency", "retries"],
    "WebSocket collaboration": ["WebSocket", "reconnect", "backpressure"],
    "AI streaming": ["AI", "stream", "TTFT"],
    "OpenAPI release": ["OpenAPI", "Spectral", "contract-test"],
}


def absent(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if term.lower() not in lower]


def main() -> int:
    files = [
        ROOT / "SKILL.md", ROOT / "agents" / "openai.yaml",
        ROOT / "references" / "rest-and-openapi.md",
        ROOT / "references" / "protocols-and-async.md",
        ROOT / "references" / "security-and-resilience.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        print("FAIL: missing files: " + ", ".join(missing))
        return 1
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    failures = []
    if items := absent(text, SECTIONS):
        failures.append("missing output sections: " + ", ".join(items))
    if items := absent(text, ["Verified", "Assumption", "authorization", "compatibility", "validation"]):
        failures.append("missing review safeguards: " + ", ".join(items))
    for scenario, terms in SCENARIOS.items():
        if items := absent(text, terms):
            failures.append(f"{scenario}: missing " + ", ".join(items))
    if failures:
        print("FAIL")
        print("\n".join("- " + item for item in failures))
        return 1
    print("PASS: output contract, review safeguards, and all 10 requested API scenarios are covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
