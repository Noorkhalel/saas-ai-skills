#!/usr/bin/env python3
"""Generate canonical version/freshness metadata for every skill reference."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'shared'/'reference-catalog.json'


def normalized_sha256(path: Path) -> str:
    """Hash text as Git stores it, independent of checkout line endings."""
    return hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest()


def existing_references() -> dict[str, dict]:
    if not OUT.is_file():
        return {}
    try:
        catalog = json.loads(OUT.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}
    return {
        item['path']: item
        for item in catalog.get('references', [])
        if isinstance(item, dict) and isinstance(item.get('path'), str)
    }


def render() -> str:
    today=date.today().isoformat(); references=[]; existing=existing_references()
    for path in sorted((ROOT/'skills').glob('*/references/*')):
        if path.is_file():
            relative_path=path.relative_to(ROOT).as_posix(); digest=normalized_sha256(path)
            previous=existing.get(relative_path, {})
            reviewed=previous.get('last_reviewed', today) if previous.get('sha256') == digest else today
            references.append({'skill':path.parents[1].name,'path':relative_path,'version':'1.0.0','last_reviewed':reviewed,'source':'repository-curated','freshness_status':'current','review_owner':'maintainers','sha256':digest})
    return json.dumps({'schema_version':'1.0','generated_by':'scripts/generate_reference_catalog.py','fresh_after_days':180,'references':references},indent=2)+'\n'
def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args(); text=render()
    if args.check and (not OUT.is_file() or OUT.read_text(encoding='utf-8') != text): print('FAIL: reference catalog is stale; run python scripts/generate_reference_catalog.py'); return 1
    if not args.check: OUT.write_text(text,encoding='utf-8')
    print(f"PASS: {'checked' if args.check else 'generated'} reference metadata catalog."); return 0
if __name__=='__main__': raise SystemExit(main())
