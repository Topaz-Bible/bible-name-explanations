#!/usr/bin/env python3
"""Build the readable lists from data/explanations.json.

Every entry records where Scripture itself explains a name as token IDs in
the Keyway Token Vault ("V.EXO.002.010:011a": book, chapter, verse, slot).
This script reads the Vault (for the original words) and a Topaz KJV package
(for the English) and writes:

  data/explanations.csv  one row per entry, with references and text
  docs/list.md           the list for readers

It also checks every entry: IDs exist in the Vault, the name token carries the
entry's Strong's number, reason endpoints are in order.

    python3 tools/build.py --vault ../keyway-data/vault \
        --kjv ../topaz-bible/assets/packages/eng.bible.kjv.zip

Python 3 plus PyYAML (the Vault is YAML).
"""
import argparse
import csv
import json
import re
import sys
import zipfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent.parent
NT = {'MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', '1CO', '2CO', 'GAL', 'EPH', 'PHP', 'COL', '1TH', '2TH',
      '1TI', '2TI', 'TIT', 'PHM', 'HEB', 'JAS', '1PE', '2PE', '1JN', '2JN', '3JN', 'JUD', 'REV'}
BOOKS = {
    'GEN': 'Genesis', 'EXO': 'Exodus', 'LEV': 'Leviticus', 'NUM': 'Numbers', 'DEU': 'Deuteronomy',
    'JOS': 'Joshua', 'JDG': 'Judges', 'RUT': 'Ruth', '1SA': '1 Samuel', '2SA': '2 Samuel',
    '1KI': '1 Kings', '2KI': '2 Kings', '1CH': '1 Chronicles', '2CH': '2 Chronicles', 'EZR': 'Ezra',
    'NEH': 'Nehemiah', 'EST': 'Esther', 'JOB': 'Job', 'PSA': 'Psalm', 'PRO': 'Proverbs',
    'ECC': 'Ecclesiastes', 'SNG': 'Song of Songs', 'ISA': 'Isaiah', 'JER': 'Jeremiah',
    'LAM': 'Lamentations', 'EZK': 'Ezekiel', 'DAN': 'Daniel', 'HOS': 'Hosea', 'JOL': 'Joel',
    'AMO': 'Amos', 'OBA': 'Obadiah', 'JON': 'Jonah', 'MIC': 'Micah', 'NAM': 'Nahum', 'HAB': 'Habakkuk',
    'ZEP': 'Zephaniah', 'HAG': 'Haggai', 'ZEC': 'Zechariah', 'MAL': 'Malachi', 'MAT': 'Matthew',
    'MRK': 'Mark', 'LUK': 'Luke', 'JHN': 'John', 'ACT': 'Acts', 'ROM': 'Romans', '1CO': '1 Corinthians',
    '2CO': '2 Corinthians', 'GAL': 'Galatians', 'EPH': 'Ephesians', 'PHP': 'Philippians',
    'COL': 'Colossians', '1TH': '1 Thessalonians', '2TH': '2 Thessalonians', '1TI': '1 Timothy',
    '2TI': '2 Timothy', 'TIT': 'Titus', 'PHM': 'Philemon', 'HEB': 'Hebrews', 'JAS': 'James',
    '1PE': '1 Peter', '2PE': '2 Peter', '1JN': '1 John', '2JN': '2 John', '3JN': '3 John', 'JUD': 'Jude',
    'REV': 'Revelation',
}
ADDRESS = re.compile(r'^V\.([1-3A-Z][A-Z]{2})\.(\d{3})\.(\d{3}):(\w+)$')


def parse(vid):
    m = ADDRESS.match(vid)
    if not m:
        raise ValueError(f'not a Vault token ID: {vid}')
    book, chapter, verse, slot = m.groups()
    return book, int(chapter), int(verse), slot


def slot_rank(slot):
    m = re.match(r'(\d+)([a-z]*)', slot)
    if not m:
        return -1
    return int(m.group(1)) * 100 + (ord(m.group(2)[0]) - 96 if m.group(2) else 0)


class Vault:
    def __init__(self, root):
        self.root = Path(root)
        self.chapters = {}

    def verse(self, book, chapter, verse):
        key = (book, chapter)
        if key not in self.chapters:
            path = self.root / ('nt' if book in NT else 'ot') / book / f'{chapter:03d}.yaml'
            data = yaml.safe_load(path.read_text())
            self.chapters[key] = {v['verse']: v['tokens'] for v in data['verses']}
        return self.chapters[key].get(verse, [])

    def token(self, vid):
        book, chapter, verse, slot = parse(vid)
        for t in self.verse(book, chapter, verse):
            if t['n'] == slot:
                return t
        raise ValueError(f'{vid} is not in the Vault')


class KJV:
    def __init__(self, path):
        self.zip = zipfile.ZipFile(path)
        self.books = {}

    def verse(self, book, chapter, verse):
        if book not in self.books:
            self.books[book] = json.loads(self.zip.read(f'{book}.json'))
        for c in self.books[book]['chapters']:
            if c['chapter'] == chapter:
                for v in c['verses']:
                    if v['verse'] == verse:
                        return v['tokens']
        return []

    def words(self, first, last, keep_end=False):
        """The KJV words rendering the Vault slots first..last. A reason that
        runs on across verses is read verse by verse and joined."""
        book, c1, v1, lo = parse(first)
        _, c2, v2, hi = parse(last)
        if (c1, v1) != (c2, v2):
            parts = []
            for c, v, a, z in self.verses_between(book, c1, v1, c2, v2):
                start = first if (c, v) == (c1, v1) else f'V.{book}.{c:03d}.{v:03d}:000a'
                end = last if (c, v) == (c2, v2) else f'V.{book}.{c:03d}.{v:03d}:999z'
                parts.append(self.words(start, end, keep_end=(c, v) != (c2, v2)))
            return ' '.join(p for p in parts if p)
        verse = v1
        chapter = c1
        tokens = self.verse(book, chapter, verse)
        lo, hi = slot_rank(lo), slot_rank(hi)
        hits = [t['n'] for t in tokens
                if any(k and slot_rank(k) >= lo and slot_rank(k) <= hi for k in [t.get('k'), *t.get('ka', [])])]
        if not hits:
            return ''
        first, last = min(hits), max(hits)
        by_n = {t['n']: t for t in tokens}
        tagged = lambda n: by_n[n].get('k') or by_n[n].get('ka')
        # Untagged words at the edges belong to the reason up to punctuation:
        # "I have gotten", "will love me".
        # Only a run that reaches punctuation (or the verse's edge) joins;
        # "rock I will build" stops at "rock".
        n = first
        while n - 1 in by_n and not tagged(n - 1) and not by_n[n - 1].get('a'):
            n -= 1
        if n - 1 not in by_n or by_n[n - 1].get('a'):
            first = n
        n = last
        while n + 1 in by_n and not tagged(n + 1) and not by_n[n].get('a'):
            n += 1
        if by_n[n].get('a') or n + 1 not in by_n:
            last = n
        span = [t for t in tokens if first <= t['n'] <= last]
        return ' '.join(t['t'] + (t.get('a', '') if i < len(span) - 1 or keep_end else '') for i, t in enumerate(span))


def _between(self, book, c1, v1, c2, v2):
    self.verse(book, c1, v1)
    out = []
    for c in self.books[book]['chapters']:
        for v in c['verses']:
            if (c1, v1) <= (c['chapter'], v['verse']) <= (c2, v2):
                out.append((c['chapter'], v['verse'], None, None))
    return out


KJV.verses_between = _between


def reference(vid):
    book, chapter, verse, _ = parse(vid)
    return f'{BOOKS[book]} {chapter}:{verse}'


def base(code):
    return re.sub(r'^([GH])0*(\d+).*$', r'\1\2', code or '')


def write_review(rows):
    """docs/review.md: every entry as a short block, for proofreading."""
    kinds = {'naming': 'named', 'renaming': 'renamed', 'gloss': 'translated in the text'}
    flagged = [r for r in rows if r['note'].startswith('Proofread')]
    out = ['# Review', '',
           f'All {len(rows)} entries, in Bible order, for proofreading. For each, check that the quoted reason '
           'is the reason the text gives for that name, and that it starts and stops in the right place.', '',
           'Judgement calls are marked **Proofread** and listed first. Entries found by `review` were settled by hand; '
           'the rest came from the original-language formula search.', '',
           f'## Judgement calls ({len(flagged)})', '']
    for r in flagged:
        out.append(f"- **{r['name']}**, {r['explained_at']}: {r['note'][len('Proofread: '):]}")
    out += ['', '## Every entry', '']
    for r in rows:
        where = r['explained_at'] if r['named_at'] == r['explained_at'] else f"named {r['named_at']}, explained {r['explained_at']}"
        out += [f"### {r['name']} · {r['original']}", '',
                f"{where} · {kinds[r['kind']]} · found by {r['found_by']}" + (f" · bible-data `{r['bible_data']}`" if r['bible_data'] else ''), '',
                f"> {r['kjv_reason'] or '(no KJV words aligned to the reason yet)'}", '']
        if r['note']:
            out += [f"*{r['note']}*", '']
    (HERE / 'docs/review.md').write_text('\n'.join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vault', required=True)
    ap.add_argument('--kjv', required=True)
    args = ap.parse_args()
    vault, kjv = Vault(args.vault), KJV(args.kjv)
    data = json.loads((HERE / 'data/explanations.json').read_text())
    rows, problems = [], []
    for e in data['entries']:
        try:
            names = [vault.token(v) for v in e['name']]
            # A name written as several words (Jehovah-jireh: יְהוָה יִרְאֶה) needs
            # only one of them to carry the entry's number.
            if not any(base(t.get('s')) == base(e['strongs']) or base(e['strongs']) in map(base, t.get('sa') or [])
                       for t in names):
                problems.append(f"{e['id']}: no name token is {e['strongs']}")
            first, last = e['because']
            vault.token(first), vault.token(last)
            a, b = parse(first), parse(last)
            if a[0] != b[0] or (a[1], a[2], slot_rank(a[3])) > (b[1], b[2], slot_rank(b[3])):
                problems.append(f"{e['id']}: reason endpoints out of order")
        except (ValueError, FileNotFoundError) as err:
            problems.append(f"{e['id']}: {err}")
            continue
        rows.append({
            'id': e['id'],
            'name': e['name_en'],
            'strongs': e['strongs'],
            'original': ' '.join(t['t'].replace('/', '') for t in names),
            'kind': e['kind'],
            'named_at': reference(e['name'][0]),
            'explained_at': reference(first),
            'kjv_reason': kjv.words(first, last),
            'name_tokens': ' '.join(e['name']),
            'reason_from': first,
            'reason_to': last,
            'found_by': ' '.join(e['found_by']),
            'note': e.get('note', ''),
            'bible_data': ' '.join(e['bible_data']) if isinstance(e.get('bible_data'), list) else e.get('bible_data', ''),
        })
    if problems:
        print('\n'.join(problems), file=sys.stderr)
        sys.exit(1)

    with open(HERE / 'data/explanations.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    kinds = {'naming': 'Names given with a reason', 'renaming': 'Names changed, with a reason',
             'gloss': 'Names translated in the text'}
    out = ['# The list', '',
           f"{len(rows)} places where Scripture explains a name. The reason is quoted from the KJV; "
           'the data records it as original-language token ranges, so it reads in any keyed translation.', '']
    for kind, title in kinds.items():
        group = [r for r in rows if r['kind'] == kind]
        if not group:
            continue
        out += [f'## {title} ({len(group)})', '', '| Name | | Where | The text says |', '|---|---|---|---|']
        for r in group:
            where = r['explained_at'] if r['named_at'] == r['explained_at'] else f"{r['named_at']}; {r['explained_at']}"
            out.append(f"| {r['name']} | {r['original']} | {where} | {r['kjv_reason'] or '—'} |")
        out.append('')
    (HERE / 'docs/list.md').write_text('\n'.join(out))
    write_review(rows)
    print(f'{len(rows)} entries checked and written')


if __name__ == '__main__':
    main()
