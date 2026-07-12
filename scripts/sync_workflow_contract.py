#!/usr/bin/env python3
"""Synchronize the canonical workflow contract into every standalone skill package."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "shared" / "workflow-contract.md"
SKILLS = ROOT / "skills"


def destinations() -> list[Path]:
    return sorted(skill / "shared" / "workflow-contract.md" for skill in SKILLS.iterdir() if skill.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if a packaged copy is missing or differs")
    args = parser.parse_args()
    if not CANONICAL.is_file():
        print(f"FAIL: canonical contract missing: {CANONICAL.relative_to(ROOT)}")
        return 1
    source = CANONICAL.read_bytes()
    failures: list[str] = []
    for destination in destinations():
        if args.check:
            if not destination.is_file() or destination.read_bytes() != source:
                failures.append(str(destination.relative_to(ROOT)))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source)
    if failures:
        print("FAIL: unsynchronized workflow contracts:")
        print("\n".join(f"- {path}" for path in failures))
        return 1
    action = "checked" if args.check else "synchronized"
    print(f"PASS: {action} {len(destinations())} standalone skill contract copies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
