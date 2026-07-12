#!/usr/bin/env python3
"""Run static structure and fixture validators; this is not a behavioral model evaluation."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main() -> int:
    commands=[[sys.executable,'scripts/validate_evals.py']]
    commands += [[sys.executable,str(path.relative_to(ROOT))] for path in sorted((ROOT/'skills').glob('*/scripts/validate_scenarios.py'))]
    failed=[]
    for command in commands:
        result=subprocess.run(command,cwd=ROOT)
        if result.returncode: failed.append(' '.join(command))
    if failed: print('FAIL: static eval validators failed:\n'+'\n'.join('- '+x for x in failed)); return 1
    print(f'PASS: {len(commands)} static eval/fixture validators passed (separate from behavioral evals).'); return 0
if __name__=='__main__': raise SystemExit(main())
