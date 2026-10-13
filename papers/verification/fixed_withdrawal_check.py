# Checks retirement_withdrawal.html (fixed withdrawal) against an independent Python reference.
# The page's own functions (simulate, walk, spendAtRetirement, requiredAssets, compareRates) and assets/js/mc.js are cut out of the HTML/JS
# and run in macOS JavaScriptCore (`jsc`); the reference below is written from the rules in the page's 「規則與算式」, not copied from the JS.
# Run:  python3 papers/verification/fixed_withdrawal_check.py      (exit code 0 = all checks pass)
import json, math, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from ref_simulator import mulberry32, normal_src   # same random number generator as the page (mulberry32 + Box-Muller)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
SEED, TRIALS = 20060301, 4000

# ---------- reference implementation ----------
def ref_fixed(A, rate, ret, inf, max_years=100):
    first = A * rate / 100
    bal, ends = A, []
    for y in range(1, max_years + 1):
        want = first * (1 + inf / 100) ** (y - 1)
        if want >= bal:
            return dict(first=first, ends=ends + [0.0], lasted=(y - 1) + bal / want)
        bal = (bal - want) * (1 + ret / 100)
        ends.append(bal)
    return dict(first=first, ends=ends, lasted=None)

def ref_need(monthly, years_to_retire, inf, rate):
    return monthly * (1 + inf / 100) ** years_to_retire * 12 / (rate / 100)

def ref_mc_success(A, rate, ret, vol, inf, T):
    m, s = ret / 100, vol / 100
    sigma2 = math.log(1 + s * s / ((1 + m) ** 2))
    mu, sigma = math.log(1 + m) - sigma2 / 2, math.sqrt(sigma2)
    normal = normal_src(mulberry32(SEED))
    ok = 0
    for _ in range(TRIALS):
        rets = [math.exp(mu + sigma * normal()) - 1 for _ in range(T)]
        bal, failed = A, False
        for i in range(T):
            want = A * rate / 100 * (1 + inf / 100) ** i
            if want >= bal: failed = True; break
            bal = (bal - want) * (1 + rets[i])
        ok += not failed
    return ok / TRIALS

# ---------- page side (JS in jsc) ----------
def cut(src, start):
    """Text from `start` through its matching closing brace (function) or end of line (const)."""
    i = src.index(start)
    if not start.startswith('function'):
        return src[i:src.index('\n', i)]
    depth, j = 0, src.index('{', i)
    while True:
        depth += src[j] == '{'; depth -= src[j] == '}'
        j += 1
        if depth == 0: return src[i:j]

def page_results(cases, mc_cases):
    html = open(os.path.join(ROOT, 'retirement_withdrawal.html'), encoding='utf-8').read()
    parts = [cut(html, 'const MAX_YEARS'), cut(html, 'const COMPARE_RATES')] + [cut(html, 'function ' + n) for n in ('spendAtRetirement', 'requiredAssets', 'simulate', 'fixedYears', 'walk')] + [cut(html, 'const compareRates')]
    js = 'var window = {};\n' + open(os.path.join(ROOT, 'assets/js/mc.js'), encoding='utf-8').read() + '\nvar MC = window.MC;\n' + '\n'.join(parts) + '''
var cases = %s, mcCases = %s, out = {fixed: [], need: [], rates: [], mc: [], chart: []};
cases.forEach(function(c){
  var r = simulate(c.A, c.rate, c.ret, c.inf);
  out.fixed.push({first: r.first, ends: r.rows.map(function(x){ return x.end; }), lasted: r.lasted});
  out.rates.push(compareRates(c.rate));
  out.chart.push(fixedYears({years: c.T}, r));
});
[[50000, 0, 4, 2], [50000, 10, 3.5, 2], [83333, 25, 5, 3], [30000, 3, 6, 0]].forEach(function(a){
  out.need.push(requiredAssets(spendAtRetirement(a[0], a[1], a[3]), a[2]));
});
mcCases.forEach(function(c){
  var ok = 0;
  MC.forEachPath({years: c.T, ret: c.ret, vol: c.vol}, function(rets){ if(!walk(c.A, c.rate, c.inf, rets, c.T).fail) ok++; });
  out.mc.push(ok / MC.TRIALS);
});
print(JSON.stringify(out));
''' % (json.dumps(cases), json.dumps(mc_cases))
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(js); path = f.name
    try:
        r = subprocess.run([JSC, path], capture_output=True, text=True, timeout=300)
    finally:
        os.unlink(path)
    if r.returncode: sys.exit('jsc failed:\n' + r.stdout + r.stderr)
    return json.loads(r.stdout.strip().splitlines()[-1])

# ---------- compare ----------
def close(a, b): return a == b or (a is not None and b is not None and abs(a - b) <= 1e-6 * max(1, abs(a), abs(b)))

def main():
    if not os.path.exists(JSC): sys.exit('jsc not found (this check needs macOS JavaScriptCore)')
    cases = [dict(A=1e7, rate=r, ret=ret, inf=inf, T=30) for r, ret, inf in
             [(4, 5, 2), (3, 5, 2), (6, 3, 2), (3.5, 5, 2), (5, 0, 0), (4, 2, 3), (8, 1, 2), (4, 7, 0), (0, 5, 2), (2.5, 6, 2)]]
    mc_cases = [dict(A=1e7, rate=4, ret=5, vol=18, inf=2, T=30), dict(A=1e7, rate=6, ret=7, vol=18, inf=2, T=40), dict(A=1e7, rate=3, ret=4, vol=10, inf=2.5, T=30)]
    page = page_results(cases, mc_cases)
    fails, n = [], 0
    def check(name, ok, detail=''):
        nonlocal n; n += 1
        if not ok: fails.append(f'{name} {detail}')
    for c, ch in zip(cases, page['chart']):   # 圖表資料：每年底資產與每年提領率，資金用完之後是 0 與 100%
        bal, ends, wrs = c['A'], [], []
        for i in range(c['T']):
            want = c['A'] * c['rate'] / 100 * (1 + c['inf'] / 100) ** i
            if bal <= 0 or want >= bal: ends.append(0.0); wrs.append(1.0); bal = 0
            else: wrs.append(want / bal); bal = (bal - want) * (1 + c['ret'] / 100); ends.append(bal)
        check(f"chart {c}", all(close(a, y['endMed']) and close(b, y['wrMed']) for a, b, y in zip(ends, wrs, ch)) and len(ch) == c['T'])
    for c, p in zip(cases, page['fixed']):
        ref, tag = ref_fixed(c['A'], c['rate'], c['ret'], c['inf']), f"fixed {c}"
        check(tag + ' first', close(ref['first'], p['first']))
        check(tag + ' lasted', close(ref['lasted'], p['lasted']), f"ref={ref['lasted']} page={p['lasted']}")
        check(tag + ' years', len(ref['ends']) == len(p['ends']), f"ref={len(ref['ends'])} page={len(p['ends'])}")
        check(tag + ' ends', all(close(a, b) for a, b in zip(ref['ends'], p['ends'])))
    for (m, y, rate, inf), p in zip([(50000, 0, 4, 2), (50000, 10, 3.5, 2), (83333, 25, 5, 3), (30000, 3, 6, 0)], page['need']):
        check(f'need {m},{y},{rate},{inf}', close(ref_need(m, y, inf, rate), p), f"ref={ref_need(m, y, inf, rate)} page={p}")
    check('need 5萬/月 4% = 1500萬', close(page['need'][0], 15_000_000))
    for c, p in zip(cases, page['rates']):
        want = sorted(set([3, 4, 5, 6] + ([c['rate']] if c['rate'] not in (3, 4, 5, 6) else [])))
        check(f"rates {c['rate']}", p == want, f'ref={want} page={p}')
    for c, p in zip(mc_cases, page['mc']):
        ref = ref_mc_success(c['A'], c['rate'], c['ret'], c['vol'], c['inf'], c['T'])
        check(f'mc {c}', abs(ref - p) <= 1 / TRIALS, f'ref={ref} page={p}')
    print(f'{n} checks, {len(fails)} failed')
    for f in fails: print('  FAIL', f)
    sys.exit(1 if fails else 0)

main()
