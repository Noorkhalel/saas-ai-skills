#!/usr/bin/env python3
"""Static contract validation for the dependency-analysis skill."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SECTIONS = [
    "# Dependency Analysis Report", "## Executive Summary", "## Review Scope",
    "## Context and Limitations", "## Dependency Health Score", "## Dependency Overview",
    "## Dependency Graph", "## Critical and High-Priority Findings",
    "## Package Dependency Findings", "## Architectural Dependency Findings",
    "## Circular Dependencies", "## Unused and Missing Dependencies",
    "## Version Conflicts", "## Security and Supply-Chain Findings",
    "## Deprecated and Abandoned Dependencies", "## Performance and Bundle Impact",
    "## External Runtime Dependencies", "## Upgrade Readiness",
    "## Recommended Upgrade Plan", "## Dependency Reduction Opportunities",
    "## Validation Commands", "## Regression Risks", "## Final Recommendations",
]

SCENARIOS = {
    "TypeScript monorepo": ["TypeScript", "monorepo", "deep imports", "cycle"],
    "React bundle": ["React", "bundle", "duplicate"],
    "Python plugins": ["FastAPI", "pip-audit", "dynamic"],
    "Maven conflict": ["Maven", "convergence", "Spring"],
    ".NET boundaries": ["NuGet", ".NET", "architecture"],
    "Go vulnerable module": ["Go", "go mod", "vulnerab"],
    "Rust features": ["Rust", "Cargo", "feature"],
    "SaaS vendor coupling": ["payment", "AI", "adapter"],
    "PR package": ["PR", "lockfile", "transitive"],
    "AI MCP": ["MCP", "permission", "least privilege"],
}


def absent(text: str, terms: list[str]) -> list[str]:
    lower = text.lower()
    return [term for term in terms if term.lower() not in lower]


def main() -> int:
    files = [
        ROOT / "SKILL.md", ROOT / "agents" / "openai.yaml",
        ROOT / "references" / "ecosystem-tools.md", ROOT / "references" / "risk-and-upgrades.md",
        ROOT / "references" / "architecture-and-runtime.md", ROOT / "references" / "examples.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        print("FAIL: missing files: " + ", ".join(missing))
        return 1
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    failures = []
    if items := absent(text, SECTIONS):
        failures.append("missing output sections: " + ", ".join(items))
    if items := absent(text, ["Confirmed", "Scanner warning", "dynamic", "lockfile", "validation"]):
        failures.append("missing evidence safeguards: " + ", ".join(items))
    for scenario, terms in SCENARIOS.items():
        if items := absent(text, terms):
            failures.append(f"{scenario}: missing " + ", ".join(items))
    if failures:
        print("FAIL")
        print("\n".join("- " + item for item in failures))
        return 1
    print("PASS: output contract, evidence safeguards, and all 10 requested dependency scenarios are covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
