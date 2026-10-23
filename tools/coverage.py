#!/usr/bin/env python3
"""Mark which candidate passages (data/candidates.json) the list already has,
and write docs/coverage.md. A candidate counts as covered when an entry's name
or reason sits in its naming or reason verse. Plain Python 3."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def verse(vid):
    m = re.match(r'(\w+)\.(\d+)\.(\d+)', vid)
    return f'{m.group(1)}.{int(m.group(2))}.{int(m.group(3))}'


entries = json.loads((HERE / 'data/explanations.json').read_text())['entries']
have = {}
for e in entries:
    for v in e['kjv']['name'] + e['kjv']['because']:
        have.setdefault(verse(v), set()).add(e['id'])
candidates = json.loads((HERE / 'data/candidates.json').read_text())['candidates']
excluded = [c for c in candidates if c.get('decision') == 'excluded']
done = [c for c in candidates if c not in excluded and (c['named'] in have or c['reason'] in have)]
todo = [c for c in candidates if c not in done and c not in excluded]
out = ['# Coverage', '',
       f'{len(candidates)} candidate passages checked against the list: {len(done)} covered, {len(excluded)} excluded, {len(todo)} to settle.',
       'Candidates live in `data/candidates.json`; run `python3 tools/coverage.py` after adding entries.', '',
       '## To settle', '', '| Name | Named | Reason | Note |', '|---|---|---|---|']
out += [f"| {c['name']} | {c['named']} | {c['reason']} | {c['note']} |" for c in todo]
out += ['', '## Excluded', '', '| Name | Where | Why |', '|---|---|---|']
out += [f"| {c['name']} | {c['named']} | {c['why']} |" for c in excluded]
out += ['', '## Covered', '', '| Name | Named | Reason |', '|---|---|---|']
out += [f"| {c['name']} | {c['named']} | {c['reason']} |" for c in done]
(HERE / 'docs/coverage.md').write_text('\n'.join(out) + '\n')
print(f'{len(done)} covered, {len(excluded)} excluded, {len(todo)} to settle')
