#!/usr/bin/env python3
"""Simulate folder-only Skills.sh installations without invoking networked installers."""
from __future__ import annotations
import json, re, shutil, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; F=json.loads((ROOT/'shared'/'base'/'framework.json').read_text(encoding='utf-8'))
def check(folder: Path) -> list[str]:
    errors=[]; text=(folder/'SKILL.md').read_text(encoding='utf-8'); match=re.search(r'<!-- base-framework: [^;]+; policies: ([^>]+) -->',text)
    if not match: return ['missing Base Framework declaration']
    for policy in [x.strip() for x in match.group(1).split(',')]:
        filename=F['policies'].get(policy)
        if not filename or not (folder/'shared'/'base'/filename).is_file(): errors.append(f'missing packaged policy {policy}')
    if not (folder/'shared'/'workflow-contract.md').is_file(): errors.append('missing packaged workflow contract')
    if not (folder/'shared'/'handoff-topics.json').is_file(): errors.append('missing packaged handoff-topic vocabulary')
    if not (folder/'shared'/'.generated-workflow-contract.json').is_file(): errors.append('missing generated workflow manifest')
    if not (folder/'shared'/'base'/'.generated-base-framework.json').is_file(): errors.append('missing generated Base Framework manifest')
    if '../../shared/' in text: errors.append('root-only shared dependency')
    return errors
def main() -> int:
    failures=[]; skills=sorted(p for p in (ROOT/'skills').iterdir() if p.is_dir())
    with tempfile.TemporaryDirectory() as tmp:
        destination=Path(tmp)
        for source in skills:
            target=destination/source.name; shutil.copytree(source,target)
            for error in check(target): failures.append(f'{source.name}: {error}')
        # Multi-skill simulation: copied folders remain independent and have no shared root dependency.
        selected=destination/'selected'; selected.mkdir(); shutil.copytree(skills[0],selected/skills[0].name); shutil.copytree(skills[1],selected/skills[1].name)
        for source in skills[:2]:
            for error in check(selected/source.name): failures.append(f'multi {source.name}: {error}')
    if failures: print('FAIL:\n'+'\n'.join('- '+x for x in failures)); return 1
    print(f'PASS: simulated single-skill installation for {len(skills)} skills and a multi-skill installation.'); return 0
if __name__=='__main__': raise SystemExit(main())
