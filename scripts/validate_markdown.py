#!/usr/bin/env python3
"""Fast Markdown/frontmatter lint for independently installable skill prompts."""
from __future__ import annotations
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main() -> int:
    errors=[]
    for path in sorted((ROOT/'skills').glob('*/SKILL.md')):
        text=path.read_text(encoding='utf-8')
        if not text.startswith('---\n') or text.find('\n---\n',4)<0: errors.append(f'{path.relative_to(ROOT)}: missing YAML frontmatter'); continue
        front=text[4:text.find('\n---\n',4)]
        if not re.search(r'^name: [a-z0-9-]+$',front,re.M): errors.append(f'{path.relative_to(ROOT)}: invalid frontmatter name')
        if not re.search(r'^description: ',front,re.M): errors.append(f'{path.relative_to(ROOT)}: missing frontmatter description')
        if not re.search(r'^# [^#]', text, re.M): errors.append(f'{path.relative_to(ROOT)}: missing document H1')
    if errors: print('FAIL:\n'+'\n'.join('- '+x for x in errors)); return 1
    print('PASS: Markdown frontmatter lint passed.'); return 0
if __name__=='__main__': raise SystemExit(main())
