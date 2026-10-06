#!/usr/bin/env python3
"""Regenerate the shared parts of every page from site-config.js.

Run from anywhere:  python3 _dev/build.py

What it writes (only between the BUILD markers in each page, so hand-written content is never touched):
  <!-- BUILD:HEAD -->    meta tags, icons, manifest link, <title>, description, Open Graph, stylesheet, shared scripts
  <!-- BUILD:TOPBAR -->  top bar with the brand link and breadcrumb
  <!-- BUILD:CARDS -->   the tool cards on the home page and the category pages
  <!-- BUILD:TAIL -->    the scripts every page loads last
It also rewrites manifest.json and sitemap.xml.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
esc = lambda s: html.escape(s, quote=True)


def load_config():
    text = (ROOT / 'config' / 'site-config.js').read_text(encoding='utf-8')
    return json.loads(text[text.index('{'):text.rindex('}') + 1])


def build_pages(cfg):
    """href -> page info (kind, title, description, crumbs)."""
    home = cfg['home']
    pages = {home['file']: dict(kind='home', title=cfg['siteName'], desc=cfg['description'], url=home['href'],
                                crumbs=[(home['title'], home['href'])])}
    for cat in cfg['categories']:
        home_crumb = (home['title'], home['href'])
        pages[cat['href']] = dict(kind='category', cat=cat, desc=cat['description'], url=cat['href'],
                                  title=f"{cat['title']} | {cfg['siteName']}",
                                  crumbs=[home_crumb, (cat['title'], cat['href'])])
        for tool in cat['tools']:
            if tool.get('soon') or not tool.get('href'):
                continue
            pages[tool['href']] = dict(kind='tool', desc=tool['desc'], url=tool['href'],
                                       title=f"{tool['title']} - {cat['title']} | {cfg['siteName']}",
                                       crumbs=[home_crumb, (cat['title'], cat['href']), (tool['title'], tool['href'])])
    return pages


def head_block(cfg, href, p):
    url = cfg['baseUrl'] + ('' if p['url'] == './' else p['url'])
    t, d = esc(p['title']), esc(p['desc'])
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="icon" type="image/svg+xml" href="assets/icons/favicon.svg">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="{esc(cfg['themeColor'])}">
<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{esc(cfg['siteName'])}">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(cfg['siteName'])}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(cfg['baseUrl'])}assets/icons/icon-512.png">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="assets/css/styles.css">
<script src="config/site-config.js"></script>
<script src="assets/js/util.js"></script>'''


def topbar_block(cfg, p):
    crumbs = []
    last = len(p['crumbs']) - 1
    for i, (title, href) in enumerate(p['crumbs']):
        label = ('🏠 ' if i == 0 else '') + title
        attrs = ' class="here" aria-current="page"' if i == last else ''
        crumbs.append(f'<a{attrs} href="{esc(href)}">{esc(label)}</a>')
    return f'''<div class="topbar">
  <a class="home-link" href="{esc(cfg['home']['href'])}" aria-label="回{esc(cfg['home']['title'])}"><span class="dot"></span><span class="brand">{esc(cfg['studio'])}</span></a>
  <nav class="crumbs" aria-label="麵包屑">{'<span>›</span>'.join(crumbs)}</nav>
</div>'''


def card(icon, title, desc, href=None, cta=None, soon=False):
    small = ' sm' if re.search(r'[一-鿿]', icon) else ''
    icon_html = f'<div class="icon{small}">{esc(icon)}</div>'
    if soon:
        return f'''    <div class="tool-card soon">
      <span class="badge muted corner">開發中</span>
      {icon_html}
      <h3>{esc(title)}</h3>
      <p>{esc(desc)}</p>
    </div>'''
    return f'''    <a class="tool-card" href="{esc(href)}">
      {icon_html}
      <h3>{esc(title)}</h3>
      <p>{esc(desc)}</p>
      <div class="go">{esc(cta)}</div>
    </a>'''


def cards_block(cfg, p):
    if p['kind'] == 'home':
        items = [card(c['icon'], c['title'], c['homeDesc'], c['href'], c['homeCta']) for c in cfg['categories']]
    else:
        items = []
        for t in p['cat']['tools']:
            if t.get('soon'):
                items.append(card(t['icon'], t['title'], t['desc'], soon=True))
            else:
                items.append(card(t['icon'], t['title'], t['desc'], t['href'], t.get('cta', '開始試算 →')))
    return '\n'.join(items)


TAIL = '<script src="assets/js/stepper.js"></script>\n<script src="assets/js/nav.js"></script>'


def replace_block(text, name, body, path):
    pat = re.compile(rf'(<!-- BUILD:{name} -->)\n.*?\n?(<!-- /BUILD:{name} -->)', re.S)
    if not pat.search(text):
        return text, False
    return pat.sub(lambda m: f'{m.group(1)}\n{body}\n{m.group(2)}', text, count=1), True


def main():
    cfg = load_config()
    pages = build_pages(cfg)
    problems = []
    changed = []

    for href, p in pages.items():
        path = ROOT / href
        if not path.exists():
            problems.append(f'{href}: listed in site-config.js but the file does not exist')
            continue
        text = original = path.read_text(encoding='utf-8')
        if p['kind'] == 'home' and not text.startswith('---\npermalink: /\n---\n'):
            problems.append(f"{href}: must start with the front matter lines '---', 'permalink: /', '---' (this is what publishes it as the site root)")
        blocks = {'HEAD': head_block(cfg, href, p), 'TOPBAR': topbar_block(cfg, p), 'TAIL': TAIL}
        if p['kind'] in ('home', 'category'):
            blocks['CARDS'] = cards_block(cfg, p)
        for name, body in blocks.items():
            text, ok = replace_block(text, name, body, path)
            if not ok:
                problems.append(f'{href}: missing <!-- BUILD:{name} --> ... <!-- /BUILD:{name} --> markers')
        if text != original:
            path.write_text(text, encoding='utf-8')
            changed.append(href)

    # Pages that exist but are not in the config (a new page that was forgotten)
    ignore = set()
    for f in sorted(ROOT.glob('*.html')):
        if f.name not in pages and f.name not in ignore and not f.name.startswith('_'):
            problems.append(f'{f.name}: not listed in site-config.js (it will be missing from menus and the sitemap)')

    manifest = {
        'name': cfg['appName'],
        'short_name': cfg['siteName'],
        'description': cfg['description'],
        'lang': 'zh-Hant',
        'start_url': cfg['home']['href'],
        'scope': './',
        'display': 'standalone',
        'background_color': '#ffffff',
        'theme_color': cfg['themeColor'],
        'icons': [
            {'src': 'assets/icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': 'assets/icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
            {'src': 'assets/icons/icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        ],
    }
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    urls = ''.join(f'  <url><loc>{esc(cfg["baseUrl"] + ("" if p["url"] == "./" else p["url"]))}</loc></url>\n' for p in pages.values())
    (ROOT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n',
        encoding='utf-8')

    print(f'{len(pages)} pages checked, {len(changed)} updated' + (': ' + ', '.join(changed) if changed else ''))
    for msg in problems:
        print('WARNING:', msg)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
