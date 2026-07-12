#!/usr/bin/env python3
"""Synchronize/check Skills.sh lock hashes after canonical SKILL.md changes."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; LOCK=ROOT/'skills-lock.json'


def normalized_sha256(path: Path) -> str:
    """Hash text as Git stores it, independent of the checkout line ending."""
    return hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest()


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args(); lock=json.loads(LOCK.read_text(encoding='utf-8')); errors=[]
    for skill, item in lock['skills'].items():
        path=ROOT/item['skillPath']; digest=normalized_sha256(path)
        if args.check:
            if item.get('computedHash') != digest: errors.append(f'{skill}: stale computedHash')
        else: item['computedHash']=digest
    if args.check:
        if errors: print('FAIL:\n'+'\n'.join('- '+x for x in errors)); return 1
        print(f"PASS: Skills.sh lock hashes match {len(lock['skills'])} canonical prompts."); return 0
    LOCK.write_text(json.dumps(lock,indent=2)+'\n',encoding='utf-8'); print(f"PASS: synchronized {len(lock['skills'])} Skills.sh lock hashes."); return 0
if __name__=='__main__': raise SystemExit(main())
