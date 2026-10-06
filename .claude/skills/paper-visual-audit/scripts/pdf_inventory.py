#!/usr/bin/env python3
"""Inventory of a PDF: metadata, per-page text size, embedded images and fonts.

Tells you whether a PDF has a text layer (searchable) or is a scan (images only), which pages hold tables/figures
as pictures, and which fonts are used / embedded.   Usage:  pdf_inventory.py paper.pdf [--json out.json]
"""
import argparse, json, sys
from pypdf import PdfReader

def fonts_of(page):
    out = []
    try:
        res = page.get('/Resources')
        res = res.get_object() if res is not None else {}
        fdict = res.get('/Font')
        fdict = fdict.get_object() if fdict is not None else {}
        for key, ref in fdict.items():
            f = ref.get_object()
            desc = f.get('/FontDescriptor')
            desc = desc.get_object() if desc is not None else {}
            embedded = any(k in desc for k in ('/FontFile', '/FontFile2', '/FontFile3'))
            out.append({'key': str(key), 'base': str(f.get('/BaseFont', '')), 'subtype': str(f.get('/Subtype', '')), 'embedded': embedded})
    except Exception as e:  # malformed resource trees are common in web captures
        out.append({'error': str(e)})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf'); ap.add_argument('--json')
    a = ap.parse_args()
    r = PdfReader(a.pdf)
    meta = {k.lstrip('/'): str(v)[:120] for k, v in (r.metadata or {}).items()}
    pages = []
    for i, p in enumerate(r.pages, 1):
        text = p.extract_text() or ''
        try:
            imgs = [{'name': im.name, 'size': list(im.image.size)} for im in p.images]
        except Exception as e:
            imgs = [{'error': str(e)}]
        pages.append({'page': i, 'text_chars': len(text), 'images': imgs, 'fonts': fonts_of(p)})
    total_chars = sum(p['text_chars'] for p in pages)
    kind = 'scan (no text layer)' if total_chars == 0 else 'text layer present'
    inv = {'file': a.pdf, 'pages': len(pages), 'kind': kind, 'metadata': meta, 'per_page': pages}
    print(f"{a.pdf}\n  pages={len(pages)}  kind={kind}")
    for k in ('Title', 'Author', 'Creator', 'Producer', 'CreationDate'):
        if k in meta: print(f"  {k}: {meta[k]}")
    fonts = sorted({(f.get('base'), f.get('subtype'), f.get('embedded')) for p in pages for f in p['fonts'] if 'base' in f})
    print(f"  fonts: {len(fonts)} distinct")
    for base, sub, emb in fonts: print(f"    {base:<40} {sub:<10} embedded={emb}")
    print("  page | text chars | images (WxH)")
    for p in pages:
        print(f"  {p['page']:>4} | {p['text_chars']:>10} | {[tuple(i['size']) for i in p['images'] if 'size' in i]}")
    if a.json:
        json.dump(inv, open(a.json, 'w'), ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
