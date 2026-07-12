#!/usr/bin/env python3
"""Parse committed JSON and apply a conservative structural YAML check without dependencies."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    json_files = sorted(path for path in ROOT.rglob("*.json") if ".git" not in path.parts and "eval-results" not in path.parts)
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {error}")
    yaml_files = sorted(path for path in ROOT.rglob("*.yml") if ".git" not in path.parts)
    yaml_files += sorted(path for path in ROOT.rglob("*.yaml") if ".git" not in path.parts)
    for path in yaml_files:
        text = path.read_text(encoding="utf-8")
        if "\t" in text:
            errors.append(f"{path.relative_to(ROOT)}: YAML must not use tab indentation")
        if not any(line.strip() and not line.lstrip().startswith("#") for line in text.splitlines()):
            errors.append(f"{path.relative_to(ROOT)}: YAML is empty")
    if errors:
        print("FAIL:\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PASS: parsed {len(json_files)} JSON files and structurally validated {len(yaml_files)} YAML files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
