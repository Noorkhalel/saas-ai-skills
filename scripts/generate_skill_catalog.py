#!/usr/bin/env python3
"""Generate the portable machine-readable skill discovery and capability catalog."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "shared" / "skill-catalog.json"
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
FIELD = re.compile(r"(?m)^([a-z_]+):\s*[\"']?(.*?)[\"']?\s*$")
DECLARATION = re.compile(r"<!-- base-framework: ([^;]+); policies: ([^>]+) -->")


def _frontmatter(path: Path) -> dict[str, str]:
    match = FRONTMATTER.search(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"{path.relative_to(ROOT)} has no frontmatter")
    fields = dict(FIELD.findall(match.group(1)))
    version = re.search(r'(?m)^\s+version:\s*["\']?([^"\'\s]+)', match.group(1))
    if version:
        fields["version"] = version.group(1)
    return fields


def render() -> str:
    router = json.loads((ROOT / "shared" / "skill-router.json").read_text(encoding="utf-8"))
    topics = json.loads((ROOT / "shared" / "handoff-topics.json").read_text(encoding="utf-8"))
    policies = json.loads((ROOT / "shared" / "base" / "skill-policy-map.json").read_text(encoding="utf-8"))
    router_items = {item["id"]: item for item in router["skills"]}
    items = []
    for directory in sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir()):
        source = directory / "SKILL.md"; text = source.read_text(encoding="utf-8")
        fields = _frontmatter(source); declaration = DECLARATION.search(text)
        if directory.name not in router_items or not declaration:
            raise ValueError(f"{directory.name} is not fully registered")
        route = router_items[directory.name]
        items.append({
            "id": directory.name,
            "version": fields.get("version"),
            "description": fields.get("description"),
            "primary_deliverable": route["primary_deliverable"],
            "activation": route["activation"],
            "exclusions": route["exclusions"],
            "closest_skills": route["closest_skills"],
            "secondary_when": route["secondary_when"],
            "required_evidence": route["required_evidence"],
            "topics": topics["skill_topics"][directory.name],
            "base_framework_version": declaration.group(1),
            "policy_ids": [item.strip() for item in declaration.group(2).split(",")],
            "references": sorted(path.relative_to(directory).as_posix() for path in (directory / "references").glob("*") if path.is_file()),
            "standalone": {"skill_file": "SKILL.md", "workflow_contract": "shared/workflow-contract.md", "handoff_topics": "shared/handoff-topics.json"},
        })
    document = {"schema_version": "1.0", "generated_by": "scripts/generate_skill_catalog.py", "collection_version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(), "skills": items}
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    try:
        expected = render()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: skill catalog cannot be generated: {exc}"); return 1
    if args.check and (not OUT.is_file() or OUT.read_text(encoding="utf-8") != expected):
        print("FAIL: shared/skill-catalog.json is stale; run python scripts/generate_skill_catalog.py"); return 1
    if not args.check: OUT.write_text(expected, encoding="utf-8")
    print(f"PASS: {'checked' if args.check else 'generated'} capability catalog for {len(json.loads(expected)['skills'])} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
