#!/usr/bin/env python3
"""每次改完笔记后运行：检查所有笔记字数是否达标"""
import json, os, sys

MIN = 1500
MAX = 3000

issues = []
for f in sorted(os.listdir('.')):
    if not f.startswith('notes_2026') or not f.endswith('.json') or '_old' in f: continue
    with open(f) as ff:
        posts = json.load(ff)
        for p in posts:
            w = len(p['body'])
            if w < MIN or w > MAX:
                status = '❌过短' if w < MIN else '❌过长'
                issues.append((f[6:10], p['city'], w, status))

if issues:
    print(f'⚠️ {len(issues)}篇字数不达标：')
    for d, c, w, s in issues:
        print(f'  {d} {c}: {w}字 {s}')
    sys.exit(1)
else:
    print(f'✅ 全部达标 ({MIN}-{MAX}字)')
