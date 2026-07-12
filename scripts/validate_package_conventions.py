#!/usr/bin/env python3
"""Validate documented optional package components without requiring placeholders."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONVENTIONS = json.loads((ROOT / "shared" / "package-conventions.json").read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    skills = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
    for skill in skills:
        for required in CONVENTIONS["required_in_every_skill"]:
            if not (skill / required).is_file():
                errors.append(f"{skill.name}: missing required packaged component {required}")
        for optional, rule in CONVENTIONS["optional_components"].items():
            candidate = skill / optional
            if candidate.exists() and rule["validate_when_present"] and candidate.is_file() and not candidate.read_text(encoding="utf-8", errors="replace").strip():
                errors.append(f"{skill.name}: optional component is empty: {optional}")
    if errors:
        print("FAIL:\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PASS: package conventions document and validate optional metadata for {len(skills)} skills without placeholders.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
