#!/usr/bin/env python3
"""Compare two transcriptions of the same table (two reading passes, or two copies of the paper).

  compare_transcriptions.py a.json b.json
Rows are matched by their label, cells by column name. Prints every cell that differs or exists on one side only.
Exit code 1 if anything differs.  See ../references/transcription_schema.md for the format.
"""
import json, sys

def load(path):
    d = json.load(open(path, encoding='utf-8'))
    cells = {}
    for row in d['rows']:
        for col, v in row['values'].items():
            cells[(row['label'], col)] = v
    return d, cells

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    da, a = load(sys.argv[1]); db, b = load(sys.argv[2])
    keys = sorted(set(a) | set(b), key=lambda k: (list(a).index(k) if k in a else 10**6, k))
    bad = 0
    for k in keys:
        va, vb = a.get(k, '<missing>'), b.get(k, '<missing>')
        if va != vb:
            bad += 1
            print(f"DIFF  {k[0]} | {k[1]}:  {da.get('source','A')}={va!r}  {db.get('source','B')}={vb!r}")
    print(f"{da.get('table')}: compared {len(keys)} cells, {bad} differ ({da.get('source')} vs {db.get('source')})")
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
