#!/usr/bin/env python3
"""Validate optional workflow packaging and the documented standalone scenarios."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CANONICAL = ROOT / "shared" / "workflow-contract.md"
REQUIRED_SECTION = "## Optional Workflow Integration"
TOPICS = {
    "api-design-review": {"api", "security", "authentication", "authorization", "database", "performance", "multi-tenancy", "architecture", "testing"},
    "architecture-planning": {"architecture", "requirements", "database", "api", "security", "authentication", "authorization", "multi-tenancy", "performance", "infrastructure", "compliance", "data-flow", "dependencies", "integration", "reliability", "scalability", "technical-debt"},
    "clean-architecture-review": {"architecture", "code-quality", "maintainability", "dependencies", "testing", "performance", "security"},
    "code-review": {"code-quality", "bugs", "security", "performance", "database", "architecture", "testing", "api", "maintainability", "multi-tenancy"},
    "codebase-understanding": {"architecture", "dependencies", "api", "database", "security", "authentication", "authorization", "multi-tenancy", "testing", "performance", "infrastructure"},
    "database-design": {"database", "schema", "migrations", "rls", "authorization", "performance", "indexes", "data-integrity", "multi-tenancy", "security", "compliance"},
    "debugging": {"debugging", "incidents", "bugs", "performance", "concurrency", "database", "api", "frontend", "backend", "infrastructure", "security", "dependencies"},
    "dependency-analysis": {"dependencies", "security", "supply-chain", "licenses", "architecture", "performance", "build", "infrastructure", "api"},
    "design-pattern-advisor": {"architecture", "design-patterns", "code-quality", "maintainability", "testing", "performance", "security"},
    "performance-optimization": {"performance", "database", "api", "frontend", "backend", "infrastructure", "caching", "scalability", "testing", "security"},
    "refactoring-code": {"code-quality", "maintainability", "duplication", "complexity", "architecture", "testing", "performance", "security", "dependencies"},
    "root-cause-analysis": {"incidents", "debugging", "bugs", "performance", "security", "database", "api", "infrastructure", "dependencies", "concurrency", "testing"},
    "security-audit": {"security", "authentication", "authorization", "database", "secrets", "api", "infrastructure", "dependencies", "multi-tenancy", "compliance", "ai"},
    "solid-review": {"code-quality", "maintainability", "architecture", "design-patterns", "testing", "performance", "security", "dependencies"},
    "test-generation": {"testing", "regressions", "requirements", "security", "edge-cases", "api", "database", "frontend", "backend", "performance", "concurrency", "architecture"},
}


def relevant(handoff: dict[str, object], topics: set[str]) -> bool:
    if set(handoff.get("topics", [])) & topics:
        return True
    return any(set(finding.get("related_topics", [])) & topics for finding in handoff.get("findings", []))


def merged_state(current: dict[str, object], skill: str, run: dict[str, object]) -> dict[str, object]:
    """Model the contract's re-read-and-update-only-own-run rule for scenario validation."""
    merged = dict(current)
    runs = dict(merged.get("runs", {}))
    runs[skill] = run
    merged["runs"] = runs
    merged.setdefault("schema_version", "1.0")
    return merged


def main() -> int:
    failures: list[str] = []
    source = CANONICAL.read_bytes() if CANONICAL.is_file() else b""
    if not source:
        failures.append("canonical contract is missing or empty")
    folders = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if set(path.name for path in folders) != set(TOPICS):
        failures.append("topic map is not synchronized with skill folders")
    for folder in folders:
        skill = folder / "SKILL.md"
        packaged = folder / "shared" / "workflow-contract.md"
        text = skill.read_text(encoding="utf-8") if skill.is_file() else ""
        if not packaged.is_file() or packaged.read_bytes() != source:
            failures.append(f"{folder.name}: standalone contract missing or out of sync")
        if REQUIRED_SECTION not in text or "[workflow contract](shared/workflow-contract.md)" not in text:
            failures.append(f"{folder.name}: workflow integration instructions are incomplete")
        if f".ai-workflow/artifacts/{folder.name}.md" not in text or f".ai-workflow/handoffs/{folder.name}.json" not in text:
            failures.append(f"{folder.name}: workflow output paths are incomplete")
        if f"runs.{folder.name}" not in text or "preserving other runs and unknown metadata" not in text:
            failures.append(f"{folder.name}: state-preservation instructions are incomplete")
        declared = ", ".join(f"`{topic}`" for topic in sorted(TOPICS.get(folder.name, set())))
        if f"Relevant handoff topics: {declared}." not in text:
            failures.append(f"{folder.name}: relevant-topic declaration is missing or changed")

    # Scenario 1: copying only one skill still ships its contract and requires no state file.
    with tempfile.TemporaryDirectory() as tmp:
        destination = Path(tmp) / "security-audit"
        shutil.copytree(SKILLS / "security-audit", destination)
        if not (destination / "shared" / "workflow-contract.md").is_file():
            failures.append("single-skill installation does not contain the contract")
        if "initialize" not in (destination / "shared" / "workflow-contract.md").read_text(encoding="utf-8"):
            failures.append("single-skill installation lacks state-initialization guidance")

    # Scenarios 2 and 3: unrelated handoffs are ignored; related topics are discoverable;
    # updating one run preserves another run and unknown top-level metadata.
    unrelated = {"topics": ["design-patterns"], "findings": []}
    security = {"topics": ["security"], "findings": [{"related_topics": ["authorization"]}]}
    if relevant(unrelated, TOPICS["database-design"]):
        failures.append("database-design would consume an unrelated handoff")
    if not relevant(security, TOPICS["database-design"]):
        failures.append("database-design cannot discover a relevant security handoff")
    maintainability = {"topics": ["maintainability"], "findings": []}
    if not relevant(maintainability, TOPICS["code-review"]):
        failures.append("code-review cannot discover a relevant maintainability handoff")
    before = {"schema_version": "1.0", "custom": {"keep": True}, "runs": {"security-audit": {"status": "completed"}}}
    after = merged_state(before, "database-design", {"status": "completed"})
    if after["custom"] != before["custom"] or after["runs"].get("security-audit") != before["runs"]["security-audit"]:
        failures.append("state update does not preserve other metadata")

    # Scenario 4: malformed state is explicitly a recoverable condition in the contract.
    contract_text = source.decode("utf-8", errors="replace")
    if "malformed" not in contract_text or "state.invalid-<timestamp>.json" not in contract_text:
        failures.append("malformed-state recovery instructions are missing")

    if failures:
        print("FAIL")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"PASS: validated standalone packaging and workflow scenarios for {len(folders)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
