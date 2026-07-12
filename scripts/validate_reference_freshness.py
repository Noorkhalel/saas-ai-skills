#!/usr/bin/env python3
"""Validate reference metadata and emit freshness plus telemetry reports."""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from reference_telemetry import write_report  # noqa: E402
def main() -> int:
    data=json.loads((ROOT/'shared'/'reference-catalog.json').read_text(encoding='utf-8')); errors=[]; warnings=[]
    expected={'skill','path','version','last_reviewed','source','freshness_status','review_owner','sha256'}
    for item in data.get('references',[]):
        if not expected <= item.keys() or not (ROOT/item.get('path','')).is_file(): errors.append('reference catalog entry is incomplete or points to a missing file'); continue
        try: age=(date.today()-date.fromisoformat(item['last_reviewed'])).days
        except ValueError: errors.append(f"{item['path']}: invalid last_reviewed"); continue
        if age > data.get('fresh_after_days',180) or item['freshness_status'] == 'outdated': warnings.append(f"{item['path']}: outdated ({age} days since review)")
    write_report(); report={'schema_version':'1.0','outdated_references':warnings,'checked_references':len(data.get('references',[]))}; out=ROOT/'eval-results'; out.mkdir(exist_ok=True); (out/'reference-freshness-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if errors: print('FAIL:\n'+'\n'.join('- '+x for x in errors)); return 1
    for warning in warnings: print('WARNING: '+warning)
    print(f"PASS: freshness metadata validated for {report['checked_references']} references; {len(warnings)} outdated references flagged."); return 0
if __name__=='__main__': raise SystemExit(main())
