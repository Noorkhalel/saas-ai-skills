#!/usr/bin/env python3
"""Verify deterministic-evaluation fixtures are inert and security cases are present for every skill."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; data=json.loads((ROOT/'evals'/'behavioral'/'cases.json').read_text(encoding='utf-8'))
def main() -> int:
    errors=[]; by={}
    for case in data['cases']: by.setdefault(case['skill'],set()).add(case['id'].split('-')[-2])
    for case in data['cases']:
        layers=case.get('evaluation_layers',{})
        if set(layers) != {'routing_contract','prompt_context','model_behavior'}: errors.append(f"{case.get('id','unknown')}: missing evaluation-layer declarations")
        if not isinstance(case.get('input',{}).get('files'),list): errors.append(f"{case.get('id','unknown')}: fixture list is invalid")
    for skill in (p.name for p in (ROOT/'skills').iterdir() if p.is_dir()):
        names=' '.join(by.get(skill,set()))
        for required in ['prompt-injection','secret-redaction','workflow-handoff','false-positive-resistance']:
            if required not in ' '.join(x['id'] for x in data['cases'] if x['skill']==skill): errors.append(f'{skill}: missing {required} behavioral case')
    for fixture in (ROOT/'evals'/'fixtures').iterdir():
        if fixture.suffix not in {'.txt','.md','.json'}: errors.append(f'{fixture}: dangerous fixture extension')
        if fixture.stat().st_mode & 0o111: errors.append(f'{fixture}: fixture is executable')
        if 'INERT' not in fixture.read_text(encoding='utf-8',errors='replace'): errors.append(f'{fixture}: missing inert label')
    if errors: print('FAIL:\n'+'\n'.join('- '+x for x in errors)); return 1
    print(f'PASS: security fixtures are inert and coverage exists for {len(by)} skills.'); return 0
if __name__=='__main__': raise SystemExit(main())
