#!/usr/bin/env python3
"""Synchronize the canonical workflow contract into every standalone skill package."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "shared" / "workflow-contract.md"
TOPICS = ROOT / "shared" / "handoff-topics.json"
SKILLS = ROOT / "skills"


def normalized_sha256(path: Path) -> str:
    """Hash text as Git stores it, independent of the checkout line ending."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def destinations() -> list[Path]:
    return sorted(skill / "shared" / "workflow-contract.md" for skill in SKILLS.iterdir() if skill.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if a packaged copy is missing or differs")
    args = parser.parse_args()
    if not CANONICAL.is_file() or not TOPICS.is_file():
        print(f"FAIL: canonical contract missing: {CANONICAL.relative_to(ROOT)}")
        return 1
    source = CANONICAL.read_bytes()
    topic_source = TOPICS.read_bytes()
    failures: list[str] = []
    for destination in destinations():
        topic_destination = destination.parent / "handoff-topics.json"
        manifest = destination.parent / ".generated-workflow-contract.json"
        expected_manifest = {
            "generated_by": "scripts/sync_workflow_contract.py",
            "contract_sha256": normalized_sha256(CANONICAL),
            "topics_sha256": normalized_sha256(TOPICS),
        }
        if args.check:
            if not destination.is_file() or destination.read_bytes() != source or not topic_destination.is_file() or topic_destination.read_bytes() != topic_source:
                failures.append(str(destination.relative_to(ROOT)))
            elif not manifest.is_file() or manifest.read_text(encoding="utf-8") != json.dumps(expected_manifest, indent=2, sort_keys=True) + "\n":
                failures.append(str(manifest.relative_to(ROOT)))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source)
            topic_destination.write_bytes(topic_source)
            manifest.write_text(json.dumps(expected_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print("FAIL: unsynchronized workflow contracts:")
        print("\n".join(f"- {path}" for path in failures))
        return 1
    action = "checked" if args.check else "synchronized"
    print(f"PASS: {action} {len(destinations())} standalone skill contract copies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
