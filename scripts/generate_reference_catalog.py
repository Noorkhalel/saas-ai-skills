#!/usr/bin/env python3
"""Generate canonical version/freshness metadata for every skill reference."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'shared'/'reference-catalog.json'
def render() -> str:
    today=date.today().isoformat(); references=[]
    for path in sorted((ROOT/'skills').glob('*/references/*')):
        if path.is_file(): references.append({'skill':path.parents[1].name,'path':path.relative_to(ROOT).as_posix(),'version':'1.0.0','last_reviewed':today,'source':'repository-curated','freshness_status':'current','review_owner':'maintainers','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    return json.dumps({'schema_version':'1.0','generated_by':'scripts/generate_reference_catalog.py','fresh_after_days':180,'references':references},indent=2)+'\n'
def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args(); text=render()
    if args.check and (not OUT.is_file() or OUT.read_text(encoding='utf-8') != text): print('FAIL: reference catalog is stale; run python scripts/generate_reference_catalog.py'); return 1
    if not args.check: OUT.write_text(text,encoding='utf-8')
    print(f"PASS: {'checked' if args.check else 'generated'} reference metadata catalog."); return 0
if __name__=='__main__': raise SystemExit(main())
