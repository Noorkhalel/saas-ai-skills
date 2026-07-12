#!/usr/bin/env python3
"""Package only each skill's declared Base Framework policy modules."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "shared" / "base"
MAP = json.loads((BASE / "skill-policy-map.json").read_text(encoding="utf-8"))
FRAMEWORK = json.loads((BASE / "framework.json").read_text(encoding="utf-8"))


def normalized_sha256(path: Path) -> str:
    """Hash text as Git stores it, independent of the checkout line ending."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def main() -> int:
    check = argparse.ArgumentParser(description=__doc__)
    check.add_argument("--check", action="store_true")
    args = check.parse_args()
    errors = []
    policy_files = FRAMEWORK["policies"]
    for skill, ids in MAP["skills"].items():
        destination = ROOT / "skills" / skill / "shared" / "base"
        expected = {policy_files[p] for p in ids}
        actual = {p.name for p in destination.glob("*.md")} if destination.exists() else set()
        manifest = destination / ".generated-base-framework.json"
        expected_manifest = {
            "generated_by": "scripts/sync_base_framework.py",
            "framework_version": FRAMEWORK["framework_version"],
            "policy_ids": ids,
            "sha256": {filename: normalized_sha256(BASE / filename) for filename in sorted(expected)},
        }
        for filename in expected:
            source = BASE / filename
            target = destination / filename
            if args.check:
                if not target.is_file() or target.read_bytes() != source.read_bytes(): errors.append(f"{skill}: stale or missing {filename}")
            else:
                destination.mkdir(parents=True, exist_ok=True); target.write_bytes(source.read_bytes())
        for extra in actual - expected:
            if args.check: errors.append(f"{skill}: unused packaged policy {extra}")
            else: (destination / extra).unlink()
        if args.check:
            if not manifest.is_file() or manifest.read_text(encoding="utf-8") != json.dumps(expected_manifest, indent=2, sort_keys=True) + "\n":
                errors.append(f"{skill}: generated Base Framework manifest is stale or missing")
        else:
            manifest.write_text(json.dumps(expected_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if errors:
        print("FAIL:\n" + "\n".join(f"- {e}" for e in errors)); return 1
    print(f"PASS: {'checked' if args.check else 'synchronized'} Base Framework policies for {len(MAP['skills'])} skills.")
    return 0
if __name__ == "__main__": raise SystemExit(main())
