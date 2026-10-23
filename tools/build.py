#!/usr/bin/env python3
"""Build the readable lists from data/explanations.json.

Every entry is anchored to KJV word positions ("GEN.029.033:011": book,
chapter, verse, word number in the Topaz KJV). The KJV is a settled text, so
those anchors never change. The Keyway Token Vault IDs under "vault" are
derived from them here, through the KJV's word alignment (each KJV word's `k`
/ `ka` slots), and rewritten on every build: as the alignment improves or the
Vault adds slots, the Vault ranges correct themselves.

This script writes:

  data/explanations.json the "vault" block of every entry, re-derived
  data/explanations.csv  one row per entry, with references and text
  docs/list.md           the list for readers
  docs/review.md         every entry as a short block, for proofreading

It checks every entry: the KJV anchors still hold the words they did when the
entry was made (data/anchors.json; the KJV should never change, so a mismatch
stops the build), the derived Vault IDs exist, a name token carries the
entry's Strong's number, and the reason runs forward. Entries whose words
aren't aligned yet are listed, not failed: their "vault" fills in later.

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
ADDRESS = re.compile(r'^V\.([1-3A-Z][A-Z]{2})\.(\d{3})\.(\d{3}):([\w~]+)$')
KJV_ADDRESS = re.compile(r'^([1-3A-Z][A-Z]{2})\.(\d{3})\.(\d{3}):(\d{3})$')


def parse(vid):
    m = ADDRESS.match(vid)
    if not m:
        raise ValueError(f'not a Vault token ID: {vid}')
    book, chapter, verse, slot = m.groups()
    return book, int(chapter), int(verse), slot


def parse_kjv(kid):
    m = KJV_ADDRESS.match(kid)
    if not m:
        raise ValueError(f'not a KJV word ID: {kid}')
    book, chapter, verse, n = m.groups()
    return book, int(chapter), int(verse), int(n)


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

    def book(self, book):
        if book not in self.books:
            self.books[book] = json.loads(self.zip.read(f'{book}.json'))
        return self.books[book]

    def word(self, kid):
        book, chapter, verse, n = parse_kjv(kid)
        for c in self.book(book)['chapters']:
            if c['chapter'] == chapter:
                for v in c['verses']:
                    if v['verse'] == verse:
                        for t in v['tokens']:
                            if t['n'] == n:
                                return t
        raise ValueError(f'{kid} is not in the KJV')

    def span(self, first, last):
        """Every KJV word from first to last, inclusive, across verses:
        [(chapter, verse, token)]."""
        book, c1, v1, n1 = parse_kjv(first)
        _, c2, v2, n2 = parse_kjv(last)
        return [(c['chapter'], v['verse'], t) for c in self.book(book)['chapters'] for v in c['verses']
                for t in v['tokens'] if (c1, v1, n1) <= (c['chapter'], v['verse'], t['n']) <= (c2, v2, n2)]

    def text(self, first, last):
        words = [t['t'] + t.get('a', '') for _, _, t in self.span(first, last)]
        return re.sub(r'[,;:.)]+$', '', ' '.join(words))


def slots(t):
    return [k for k in [t.get('k'), *(t.get('ka') or [])] if k]


def vid(book, chapter, verse, slot):
    return f'V.{book}.{chapter:03d}.{verse:03d}:{slot}'


def derive(e, kjv):
    """The entry's Vault IDs, from its KJV anchors and the KJV's alignment.
    A part with no aligned words yet comes back empty."""
    names = []
    for kid in e['kjv']['name']:
        book, c, v, _ = parse_kjv(kid)
        names += [vid(book, c, v, k) for k in slots(kjv.word(kid))]
    book = parse_kjv(e['kjv']['because'][0])[0]
    hits = sorted({(c, v, slot_rank(k), k) for c, v, t in kjv.span(*e['kjv']['because']) for k in slots(t)})
    because = [vid(book, *hits[0][:2], hits[0][3]), vid(book, *hits[-1][:2], hits[-1][3])] if hits else []
    return {'name': list(dict.fromkeys(names)), 'because': because}


def reference(kid):
    book, chapter, verse, _ = parse_kjv(kid)
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
        out += [f"### {r['name']} · {r['original'] or '(not aligned yet)'}", '',
                f"{where} · {kinds[r['kind']]} · found by {r['found_by']}" + (f" · bible-data `{r['bible_data']}`" if r['bible_data'] else ''), '',
                f"> {r['kjv_reason']}", '']
        if r['note']:
            out += [f"*{r['note']}*", '']
    (HERE / 'docs/review.md').write_text('\n'.join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vault', required=True)
    ap.add_argument('--kjv', required=True)
    ap.add_argument('--accept', action='store_true',
                    help='record the current KJV words as the anchors (only if the KJV was deliberately re-issued)')
    args = ap.parse_args()
    vault, kjv = Vault(args.vault), KJV(args.kjv)
    data = json.loads((HERE / 'data/explanations.json').read_text())
    rows, problems, unaligned, moved = [], [], [], []
    for e in data['entries']:
        try:
            first, last = e['kjv']['because']
            if parse_kjv(first)[0] != parse_kjv(last)[0] or parse_kjv(first)[1:] > parse_kjv(last)[1:]:
                problems.append(f"{e['id']}: reason endpoints out of order")
                continue
            for kid in e['kjv']['name'] + [first, last]:
                kjv.word(kid)
            derived = derive(e, kjv)
            names = [vault.token(v) for v in derived['name']]
            for v in derived['because']:
                vault.token(v)
        except (ValueError, KeyError, FileNotFoundError) as err:
            problems.append(f"{e['id']}: {err}")
            continue
        # A name written as several words (Jehovah-jireh: יְהוָה יִרְאֶה) needs
        # only one of them to carry the entry's number.
        if names and not any(base(t.get('s')) == base(e['strongs']) or base(e['strongs']) in map(base, t.get('sa') or [])
                             for t in names):
            problems.append(f"{e['id']}: no name token is {e['strongs']}")
        if not derived['name'] or not derived['because']:
            unaligned.append(e['id'])
        if derived != e.get('vault'):
            moved.append(e['id'])
        e['vault'] = derived
        rows.append({
            'id': e['id'],
            'name': e['name_en'],
            'strongs': e['strongs'],
            'original': ' '.join(t['t'].replace('/', '') for t in names),
            'kind': e['kind'],
            'named_at': reference(e['kjv']['name'][0]),
            'explained_at': reference(first),
            'kjv_name': ' '.join(kjv.word(k)['t'] for k in e['kjv']['name']),
            'kjv_reason': kjv.text(first, last),
            'kjv_name_words': ' '.join(e['kjv']['name']),
            'kjv_reason_from': first,
            'kjv_reason_to': last,
            'vault_name': ' '.join(derived['name']),
            'vault_reason_from': derived['because'][0] if derived['because'] else '',
            'vault_reason_to': derived['because'][-1] if derived['because'] else '',
            'found_by': ' '.join(e['found_by']),
            'note': e.get('note', ''),
            'bible_data': ' '.join(e['bible_data']) if isinstance(e.get('bible_data'), list) else e.get('bible_data', ''),
        })
    # Anchors: the KJV word behind every anchor. The KJV is settled, so these
    # should never differ; if one does, the KJV package was re-issued and every
    # entry it touches needs a look.
    anchor_path = HERE / 'data/anchors.json'
    anchors = json.loads(anchor_path.read_text()) if anchor_path.exists() else {}
    current = {}
    for e in data['entries']:
        for kid in e['kjv']['name'] + e['kjv']['because']:
            try:
                current[kid] = kjv.word(kid)['t']
            except ValueError:
                pass
    drifted = sorted({e['id'] for e in data['entries'] for kid in e['kjv']['name'] + e['kjv']['because']
                      if kid in anchors and kid in current and anchors[kid] != current[kid]})
    if drifted and not args.accept:
        problems.append('The KJV words under these entries changed (the KJV should never change); '
                        're-check them, then run with --accept:\n  ' + '\n  '.join(drifted))
    if problems:
        print('\n'.join(problems), file=sys.stderr)
        sys.exit(1)
    if args.accept or set(current) != set(anchors):
        anchor_path.write_text(json.dumps(dict(sorted(current.items())), ensure_ascii=False, indent=1) + '\n')
    (HERE / 'data/explanations.json').write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n')

    with open(HERE / 'data/explanations.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    kinds = {'naming': 'Names given with a reason', 'renaming': 'Names changed, with a reason',
             'gloss': 'Names translated in the text'}
    out = ['# The list', '',
           f"{len(rows)} places where Scripture explains a name, quoted from the KJV. Each is anchored to KJV words; "
           'the original-language words come from the KJV\'s alignment, so they read in any keyed translation.', '']
    for kind, title in kinds.items():
        group = [r for r in rows if r['kind'] == kind]
        if not group:
            continue
        out += [f'## {title} ({len(group)})', '', '| Name | | Where | The text says |', '|---|---|---|---|']
        for r in group:
            where = r['explained_at'] if r['named_at'] == r['explained_at'] else f"{r['named_at']}; {r['explained_at']}"
            out.append(f"| {r['name']} | {r['original']} | {where} | {r['kjv_reason']} |")
        out.append('')
    (HERE / 'docs/list.md').write_text('\n'.join(out))
    write_review(rows)
    print(f'{len(rows)} entries checked and written')
    if moved:
        print(f'{len(moved)} Vault ranges re-derived from the KJV alignment: ' + ', '.join(moved))
    if unaligned:
        print(f'{len(unaligned)} not fully aligned yet (their Vault IDs fill in as the alignment does): '
              + ', '.join(unaligned))


if __name__ == '__main__':
    main()
