#!/usr/bin/env python3
"""Arithmetic / consistency checks on transcribed tables of Guyton & Klinger (2006), plus checks of claims made in the text.

  check_tables.py TRANSCRIPTION_DIR --source scan|web [--md report_section.md]

Reads  <source>_table1/2/3/4/6/7.json  (see ../references/transcription_schema.md).
A missing file is skipped. Every finding has a level:  FAIL (numbers cannot both be right),  CHECK (text and table disagree, a human must decide),  OK.
The paper's own data cannot be re-derived (it uses 1973-2004 asset-class statistics), so these checks test internal consistency only.
"""
import argparse, json, os, sys

def load(d, source, name):
    p = os.path.join(d, f'{source}_{name}.json')
    if not os.path.exists(p): return None
    return json.load(open(p, encoding='utf-8'))

def rows(t):
    return [(r['label'].split(' | '), r['values']) for r in t['rows']]

findings = []
def add(level, where, msg): findings.append((level, where, msg))

def check_table2(t, src):
    """Enhancement = (max WD rate with rule / max WD rate with no rule) - 1, allowing for the 1-decimal rounding of the printed rates."""
    base = {}
    for lab, v in rows(t):
        if lab[0] == 'No Decision Rules':
            base[lab[1]] = v
    for lab, v in rows(t):
        if lab[0] == 'No Decision Rules': continue
        if lab[1] not in base: continue
        for rate_col, enh_col, b_col in (('MaxWD_90POS', 'Enh_90POS', 'MaxWD_90POS'), ('MaxWD_95POS', 'Enh_95POS', 'MaxWD_95POS')):
            x, e, b = v.get(rate_col), v.get(enh_col), base[lab[1]].get(b_col)
            if not all(isinstance(z, (int, float)) for z in (x, e, b)): continue
            lo = ((x - 0.05) / (b + 0.05) - 1) * 100 - 0.5
            hi = ((x + 0.05) / (b - 0.05) - 1) * 100 + 0.5
            ok = lo <= e <= hi
            add('OK' if ok else 'FAIL', f'{src} Table 2 | {" | ".join(lab)} | {enh_col}',
                f'printed {e:g}%, implied {((x / b) - 1) * 100:.1f}% (allowed {lo:.1f}..{hi:.1f})')
    all3 = [v.get('Enh_90POS') for lab, v in rows(t) if lab[0].startswith('All 3')] + [v.get('Enh_95POS') for lab, v in rows(t) if lab[0].startswith('All 3')]
    all3 = [z for z in all3 if isinstance(z, (int, float))]
    if all3:
        lo, hi = min(all3), max(all3)
        add('OK' if (lo, hi) == (30, 43) or (lo >= 30 and hi <= 43) else 'CHECK', f'{src} Table 2 | text claim "increases maximum initial WR 30-43 percent"',
            f'"All 3 rules" enhancements range {lo:g}%..{hi:g}%')

def check_table67(t, src, name):
    groups = {}
    for lab, v in rows(t):
        if len(lab) != 3: continue
        groups.setdefault((lab[0], lab[1]), []).append((int(lab[2].rstrip('%')), v))
    for (grp, alloc), items in groups.items():
        items.sort(key=lambda z: -z[0])      # 99, 95, 90
        wd = [v.get('InitialWD') for _, v in items]
        if all(isinstance(z, (int, float)) for z in wd):
            ok = all(wd[i] <= wd[i + 1] for i in range(len(wd) - 1))
            add('OK' if ok else 'FAIL', f'{src} {name} | {grp} | {alloc} | WD rate rises as the confidence standard falls', f'{wd}')
        for conf, v in items:
            s, pp = v.get('SuccessRate'), v.get('TotalPP')
            if isinstance(s, (int, float)) and s < conf:
                add('FAIL', f'{src} {name} | {grp} | {alloc} | {conf}%', f'success rate {s}% is below the {conf}% standard it is listed under')
            if isinstance(pp, (int, float)) and pp < conf:
                add('FAIL', f'{src} {name} | {grp} | {alloc} | {conf}%', f'total purchasing power {pp}% is below the {conf}% standard')


def check_table1(t, src):
    """Allocation table: every portfolio column sums to 100%, and the non-cash, non-fixed-income rows sum to the equity share in its header."""
    cols = t['columns']
    for col in cols:
        total = sum(v[col] for _, v in rows(t) if isinstance(v.get(col), (int, float)))
        equity = sum(v[col] for lab, v in rows(t) if lab[0] not in ('Cash', 'Fixed Income') and isinstance(v.get(col), (int, float)))
        share = int(col.split('%')[0])
        add('OK' if total == 100 else 'FAIL', f'{src} Table 1 | {col} column sums to 100%', f'sum = {total}')
        add('OK' if equity == share else 'FAIL', f'{src} Table 1 | {col} equity rows add up to the equity share in the header', f'equity rows = {equity}')

def check_table34(t, src, name):
    """Within each rule set the initial WD rate must rise as the required success level falls; purchasing power must not rise."""
    blocks = {}
    for lab, v in rows(t):
        blocks.setdefault(lab[0], []).append((int(lab[1].split('%')[0]), v))
    for blk, items in blocks.items():
        items.sort(key=lambda z: -z[0])
        wd = [v.get('InitialWD') for _, v in items]
        pp = [v.get('TotalPP') for _, v in items]
        add('OK' if all(wd[i] <= wd[i + 1] for i in range(len(wd) - 1)) else 'FAIL', f'{src} {name} | {blk} | WD rate rises as success level falls', f'{wd}')
        add('OK' if all(pp[i] >= pp[i + 1] for i in range(len(pp) - 1)) else 'FAIL', f'{src} {name} | {blk} | total purchasing power does not rise as success level falls', f'{pp}')

def curve_wd_at(points, success):
    """points: [(wd, success)] sorted by wd. Initial WD rate at which the curve reaches the given success level (linear interpolation)."""
    for (w0, s0), (w1, s1) in zip(points, points[1:]):
        if s1 <= success <= s0 and s0 != s1:
            return w0 + (w1 - w0) * (s0 - success) / (s0 - s1)
    return None

def cross_check(t_curve, t6, src, curve_name, group):
    """Table 6 rows (65/25/10) give a success rate for an initial WD rate. Table 3 (single class) and Table 4 (multi class) give the
    same relationship for the same portfolio and rules. A Table 6 row should sit on that curve (horizontal distance <= 0.5 percentage point)."""
    pts = []
    for lab, v in rows(t_curve):
        if lab[0] == 'PMR, WR, CPR, PR':
            pts.append((v['InitialWD'], int(lab[1].split('%')[0])))
    pts.sort()
    for lab, v in rows(t6):
        if len(lab) == 3 and lab[0] == group and lab[1] == '65/25/10':
            s, w = v.get('SuccessRate'), v.get('InitialWD')
            if not isinstance(s, (int, float)) or s >= 100: continue      # 100% is a range on the curve, not a point
            wd_at = curve_wd_at(pts, s)
            if wd_at is None: continue
            gap = w - wd_at
            add('OK' if abs(gap) <= 0.5 else 'CHECK', f'{src} Table 6 vs {curve_name} | {group} 65/25/10 | confidence {lab[2]}',
                f'Table 6 says {w}% gives {s}% success; {curve_name} reaches {s}% success at {wd_at:.1f}% (gap {gap:+.1f} points)')

def claims(t6, src):
    """Claims in the paper's summary / conclusion that can be tested against Table 6 (40-year)."""
    def pick(conf, allocs):
        out = []
        for lab, v in rows(t6):
            if len(lab) == 3 and lab[2] == f'{conf}%' and any(lab[1].startswith(a) for a in allocs):
                out.append((lab[0], lab[1], v.get('InitialWD')))
        return out
    for conf, lo, hi, text in ((99, 5.2, 5.6, 'Executive Summary / Conclusion: "5.2-5.6 percent ... 99 percent confidence ... at least 65 percent equities"'),
                               (95, 5.7, 6.2, 'Conclusion: "rise to 5.7-6.2 percent at the 95 percent confidence standard"')):
        rowsel = pick(conf, ('65', '80'))
        out = [(g, a, x) for g, a, x in rowsel if isinstance(x, (int, float)) and not (lo <= x <= hi)]
        add('OK' if not out else 'CHECK', f'{src} Table 6 | {text}',
            'all 65%/80% rows inside the range' if not out else 'outside the range: ' + '; '.join(f'{g} {a} = {x}%' for g, a, x in out))
    low = [x for g, a, x in pick(99, ('50',)) if isinstance(x, (int, float))]
    if low:
        add('OK' if min(low) >= 4.6 else 'CHECK', f'{src} Table 6 | Executive Summary: "with 50 percent equities ... as low as 4.6 percent"',
            f'99% rows for 50/40/10 give {sorted(low)} (min {min(low)})')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir'); ap.add_argument('--source', required=True); ap.add_argument('--md')
    a = ap.parse_args()
    t1, t2, t3, t4, t6, t7 = (load(a.dir, a.source, n) for n in ('table1', 'table2', 'table3', 'table4', 'table6', 'table7'))
    if t1: check_table1(t1, a.source)
    if t3: check_table34(t3, a.source, 'Table 3')
    if t4: check_table34(t4, a.source, 'Table 4')
    if t6 and t3: cross_check(t3, t6, a.source, 'Table 3', 'One Equity (S&P 500)')
    if t6 and t4: cross_check(t4, t6, a.source, 'Table 4', 'Multi-Class Equities')
    if t2: check_table2(t2, a.source)
    if t6: check_table67(t6, a.source, 'Table 6'); claims(t6, a.source)
    if t7: check_table67(t7, a.source, 'Table 7')
    counts = {k: sum(1 for f in findings if f[0] == k) for k in ('OK', 'CHECK', 'FAIL')}
    for level, where, msg in findings:
        if level != 'OK': print(f'{level:<5} {where}\n        {msg}')
    print(f'\n{a.source}: {counts["OK"]} OK, {counts["CHECK"]} CHECK (human decision), {counts["FAIL"]} FAIL')
    if a.md:
        with open(a.md, 'w', encoding='utf-8') as f:
            f.write('| Level | Where | Detail |\n|---|---|---|\n')
            for level, where, msg in findings:
                if level != 'OK': f.write(f'| {level} | {where} | {msg} |\n')
    sys.exit(1 if counts['FAIL'] else 0)

if __name__ == '__main__':
    main()
