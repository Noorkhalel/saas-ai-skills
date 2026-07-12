#!/usr/bin/env python3
"""Validate optional workflow packaging and the documented standalone scenarios."""
from __future__ import annotations

import shutil
import tempfile
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from workflow_state import atomic_write, update_state
SKILLS = ROOT / "skills"
CANONICAL = ROOT / "shared" / "workflow-contract.md"
TOPIC_VOCABULARY = ROOT / "shared" / "handoff-topics.json"
REQUIRED_SECTION = "## Optional Workflow Integration"


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
    vocabulary = json.loads(TOPIC_VOCABULARY.read_text(encoding="utf-8")) if TOPIC_VOCABULARY.is_file() else {}
    TOPICS = {skill: set(topics) for skill, topics in vocabulary.get("skill_topics", {}).items()}
    if not source:
        failures.append("canonical contract is missing or empty")
    if vocabulary.get("topic_vocabulary_version") != "1.0" or not TOPICS:
        failures.append("versioned handoff topic vocabulary is missing or invalid")
    if any(topic not in set(vocabulary.get("topics", [])) for topics in TOPICS.values() for topic in topics):
        failures.append("skill topic map contains a topic outside the controlled vocabulary")
    folders = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if set(path.name for path in folders) != set(TOPICS):
        failures.append("topic map is not synchronized with skill folders")
    for folder in folders:
        skill = folder / "SKILL.md"
        packaged = folder / "shared" / "workflow-contract.md"
        packaged_topics = folder / "shared" / "handoff-topics.json"
        text = skill.read_text(encoding="utf-8") if skill.is_file() else ""
        if not packaged.is_file() or packaged.read_bytes() != source:
            failures.append(f"{folder.name}: standalone contract missing or out of sync")
        if not packaged_topics.is_file() or packaged_topics.read_bytes() != TOPIC_VOCABULARY.read_bytes():
            failures.append(f"{folder.name}: standalone topic vocabulary missing or out of sync")
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

    # Scenario 4: helper writes atomically under a lock and preserves a concurrent run.
    with tempfile.TemporaryDirectory() as tmp:
        workflow = Path(tmp) / ".ai-workflow"
        atomic_write(workflow / "state.json", json.dumps(before))
        update_state(workflow, "database-design", {"status": "completed"})
        updated = json.loads((workflow / "state.json").read_text(encoding="utf-8"))
        if updated["custom"] != before["custom"] or "security-audit" not in updated["runs"] or "database-design" not in updated["runs"]:
            failures.append("lock-safe workflow helper did not preserve state")

    # Scenario 5: malformed state is explicitly a recoverable condition in the contract.
    contract_text = source.decode("utf-8", errors="replace")
    if "malformed" not in contract_text or "state.invalid-<timestamp>.json" not in contract_text or ".state.lock" not in contract_text or "atomically replace" not in contract_text:
        failures.append("malformed-state recovery instructions are missing")

    if failures:
        print("FAIL")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"PASS: validated standalone packaging and workflow scenarios for {len(folders)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
