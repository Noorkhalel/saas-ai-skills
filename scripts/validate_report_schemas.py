#!/usr/bin/env python3
"""Validate generated schemas and each deterministic adapter report."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from report_schema import validate_report  # noqa: E402


def main() -> int:
    errors: list[str] = []
    schema_dir = ROOT / "schemas" / "reports"
    skill_dirs = sorted(path.name for path in (ROOT / "skills").iterdir() if path.is_dir())
    for path in [schema_dir / "common-report.schema.json", *(schema_dir / f"{skill}-report.schema.json" for skill in skill_dirs)]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            errors.append(f"invalid or missing schema: {path.relative_to(ROOT)}")
            continue
        if payload.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"schema does not declare draft 2020-12: {path.relative_to(ROOT)}")
    reports = ROOT / "eval-results" / "behavioral-reports.json"
    if reports.is_file():
        try:
            items = json.loads(reports.read_text(encoding="utf-8"))
            if not isinstance(items, list): raise ValueError
            for report in items:
                skill = report.get("metadata", {}).get("skill") if isinstance(report, dict) else None
                if skill not in skill_dirs: errors.append("behavioral report has unknown skill")
                else: errors.extend(f"{skill}: {error}" for error in validate_report(report, skill))
        except (OSError, ValueError, json.JSONDecodeError):
            errors.append("behavioral report artifact is invalid")
    if errors:
        print("FAIL:\n" + "\n".join(f"- {error}" for error in errors)); return 1
    print(f"PASS: common and {len(skill_dirs)} per-skill schemas validate" + (" with deterministic reports." if reports.is_file() else ".")); return 0


if __name__ == "__main__":
    raise SystemExit(main())
