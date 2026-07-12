#!/usr/bin/env python3
"""Lightweight structural validation for the public skill collection."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REQUIRED_ROOT = ["README.md", "SKILLS.md", "ARCHITECTURE.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE", "VERSION"]
Kebab = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"\[[^]]*\]\(([^)#]+)(?:#[^)]+)?\)")


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    for name in REQUIRED_ROOT:
        if not (ROOT / name).is_file():
            failures.append(f"missing root file: {name}")
    contract = ROOT / "shared" / "workflow-contract.md"
    if not contract.is_file():
        failures.append("missing canonical workflow contract: shared/workflow-contract.md")
    folders = sorted(path for path in SKILLS.iterdir() if path.is_dir()) if SKILLS.is_dir() else []
    if not folders:
        failures.append("no skill folders found")
    catalog = (ROOT / "SKILLS.md").read_text(encoding="utf-8") if (ROOT / "SKILLS.md").is_file() else ""
    for folder in folders:
        if not Kebab.fullmatch(folder.name):
            failures.append(f"invalid skill folder name: {folder.relative_to(ROOT)}")
        skill = folder / "SKILL.md"
        if not skill.is_file():
            failures.append(f"missing canonical file: {folder.relative_to(ROOT)}/SKILL.md")
            continue
        if f"skills/{folder.name}/SKILL.md" not in catalog:
            failures.append(f"catalog missing skill: {folder.name}")
        text = skill.read_text(encoding="utf-8", errors="replace")
        packaged_contract = folder / "shared" / "workflow-contract.md"
        if not packaged_contract.is_file():
            failures.append(f"missing packaged workflow contract: {packaged_contract.relative_to(ROOT)}")
        elif contract.is_file() and packaged_contract.read_bytes() != contract.read_bytes():
            failures.append(f"out-of-sync packaged workflow contract: {packaged_contract.relative_to(ROOT)}")
        if "## Optional Workflow Integration" not in text:
            failures.append(f"missing workflow integration section: {skill.relative_to(ROOT)}")
        if re.search(r"[A-Za-z]:\\", text):
            failures.append(f"Windows local path in: {skill.relative_to(ROOT)}")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            target_path = (skill.parent / target).resolve()
            if not target_path.exists():
                failures.append(f"broken relative link in {skill.relative_to(ROOT)}: {target}")
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".pem", ".p12", ".pfx"}:
            warnings.append(f"review sensitive artifact: {path.relative_to(ROOT)}")
    for warning in warnings:
        print("WARNING:", warning)
    if failures:
        print("FAIL")
        print("\n".join(f"- {item}" for item in failures))
        return 1
    print(f"PASS: {len(folders)} skill folders validated; catalog and basic links are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
