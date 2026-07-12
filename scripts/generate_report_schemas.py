#!/usr/bin/env python3
"""Generate portable, per-skill report schemas from the skill directory list."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "schemas" / "reports"


def common_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "common-report.schema.json",
        "title": "Skill report contract",
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "metadata", "sections", "findings", "recommendations", "workflow"],
        "properties": {
            "schema_version": {"const": "1.0"},
            "metadata": {"type": "object", "additionalProperties": False, "required": ["skill", "adapter", "generated_at"], "properties": {"skill": {"type": "string"}, "adapter": {"type": "string"}, "generated_at": {"type": "string", "format": "date-time"}, "case_id": {"type": "string"}}},
            "sections": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}, "required": ["scope", "evidence", "assumptions", "findings", "recommendations"], "properties": {"scope": {"type": "array", "items": {"type": "string"}}, "evidence": {"type": "array", "items": {"type": "string"}}, "assumptions": {"type": "array", "items": {"type": "string"}}, "findings": {"type": "array", "items": {"type": "string"}}, "recommendations": {"type": "array", "items": {"type": "string"}}}},
            "findings": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["id", "title", "severity", "confidence", "evidence", "recommendation"], "properties": {"id": {"type": "string"}, "title": {"type": "string"}, "severity": {"enum": ["critical", "high", "medium", "low", "info"]}, "confidence": {"enum": ["high", "medium", "low"]}, "evidence": {"type": "array", "items": {"type": "string"}}, "recommendation": {"type": "string"}}}},
            "recommendations": {"type": "array", "items": {"type": "string"}},
            "workflow": {"type": "object", "additionalProperties": False, "required": ["enabled", "artifact_generated", "handoff_generated"], "properties": {"enabled": {"type": "boolean"}, "artifact_generated": {"type": "boolean"}, "handoff_generated": {"type": "boolean"}}},
        },
    }


def rendered() -> dict[Path, str]:
    common = common_schema()
    result = {OUT / "common-report.schema.json": json.dumps(common, indent=2) + "\n"}
    for directory in sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir()):
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": f"{directory.name}-report.schema.json", "title": f"{directory.name} report", "allOf": [{"$ref": "common-report.schema.json"}], "properties": {"metadata": {"properties": {"skill": {"const": directory.name}}}}}
        result[OUT / f"{directory.name}-report.schema.json"] = json.dumps(schema, indent=2) + "\n"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    expected = rendered(); errors = []
    for path, text in expected.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                errors.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")
    actual = set(OUT.glob("*-report.schema.json")) if OUT.exists() else set()
    expected_skill_schemas = {path for path in expected if path.name != "common-report.schema.json"}
    for path in actual - set(expected):
        errors.append(f"obsolete schema: {path.relative_to(ROOT)}")
    if errors:
        print("FAIL: report schemas are stale or invalid:\n" + "\n".join(f"- {error}" for error in errors)); return 1
    print(f"PASS: {'checked' if args.check else 'generated'} common and {len(expected_skill_schemas)} per-skill report schemas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
