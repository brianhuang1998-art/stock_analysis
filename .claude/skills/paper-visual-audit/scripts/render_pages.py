#!/usr/bin/env python3
"""Render PDF pages (or cropped regions) to PNG so a vision model can read them. Needs pypdfium2 + pillow (no poppler).

  render_pages.py paper.pdf --out DIR [--pages 1,3-5] [--scale 2.2]
  render_pages.py paper.pdf --out DIR --crop 4:0.05,0.08,0.95,0.55:table2   # page:x0,y0,x1,y1 (fractions of the page):name
Crops are the right way to read tables: a table at 2-3x scale is read far more reliably than a whole page.
"""
import argparse, os
import pypdfium2 as pdfium

def parse_pages(spec, n):
    if not spec: return list(range(1, n + 1))
    out = []
    for part in spec.split(','):
        if '-' in part:
            a, b = part.split('-'); out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return [p for p in out if 1 <= p <= n]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf'); ap.add_argument('--out', required=True)
    ap.add_argument('--pages'); ap.add_argument('--scale', type=float, default=2.2)
    ap.add_argument('--crop', action='append', default=[], help='page:x0,y0,x1,y1:name (fractions)')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pdf = pdfium.PdfDocument(a.pdf)
    stem = os.path.splitext(os.path.basename(a.pdf))[0][:24].replace(' ', '_')
    if a.crop:
        for spec in a.crop:
            page, box, name = spec.split(':')
            x0, y0, x1, y1 = [float(v) for v in box.split(',')]
            img = pdf[int(page) - 1].render(scale=a.scale).to_pil()
            w, h = img.size
            path = os.path.join(a.out, f'{name}.png')
            img.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))).save(path)
            print('wrote', path)
        return
    for p in parse_pages(a.pages, len(pdf)):
        path = os.path.join(a.out, f'{stem}_p{p:02d}.png')
        pdf[p - 1].render(scale=a.scale).to_pil().save(path)
        print('wrote', path)

if __name__ == '__main__':
    main()
