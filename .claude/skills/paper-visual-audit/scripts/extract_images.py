#!/usr/bin/env python3
"""Save every embedded image of a PDF (tables and figures are often pictures) at native size, optionally upscaled.

  extract_images.py paper.pdf --out DIR [--upscale 2.5]
Output names: p<page>_<n>.png
"""
import argparse, io, os
from pypdf import PdfReader
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf'); ap.add_argument('--out', required=True); ap.add_argument('--upscale', type=float, default=1.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for pno, page in enumerate(PdfReader(a.pdf).pages, 1):
        for n, im in enumerate(page.images, 1):
            img = Image.open(io.BytesIO(im.data)).convert('RGB')
            if a.upscale != 1.0:
                img = img.resize((int(img.width * a.upscale), int(img.height * a.upscale)), Image.LANCZOS)
            path = os.path.join(a.out, f'p{pno:02d}_{n}.png')
            img.save(path)
            print('wrote', path, img.size)

if __name__ == '__main__':
    main()
