#!/usr/bin/env python3
"""Validate collection and standalone skill semantic-version metadata."""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
VERSION = re.compile(r'(?m)^\s+version:\s*["\']?([^"\'\s]+)')


def main() -> int:
    errors: list[str] = []
    collection = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(collection): errors.append("VERSION is not Semantic Versioning 2.0 compatible")
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        match = VERSION.search(path.read_text(encoding="utf-8"))
        if not match or not SEMVER.fullmatch(match.group(1)):
            errors.append(f"{path.relative_to(ROOT)}: metadata.version is missing or invalid")
    if errors:
        print("FAIL:\n" + "\n".join(f"- {error}" for error in errors)); return 1
    print(f"PASS: collection {collection} and {len(list((ROOT/'skills').glob('*/SKILL.md')))} standalone skill versions are valid SemVer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
