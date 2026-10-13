# Checks retirement_dynamic_withdrawal.html (Guyton-Klinger guardrails) against the independent reference in ref_simulator.py.
# The page's own functions (runPath, summarize, searchMaxRates, spendAtRetirement, requiredAssets, confidenceOf ...) and assets/js/mc.js are cut out of the HTML/JS
# and run in macOS JavaScriptCore (`jsc`) on the same inputs and the same random paths; every output field is compared with ref_simulator.py (written from the rules, not from the JS).
# Run:  python3 papers/verification/dynamic_withdrawal_check.py      (about 1 minute; exit code 0 = all checks pass)
import json, math, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ref_simulator as ref

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
TOL = 1e-9

# ---------- cases (units are the page's input units: percent for rates) ----------
def case(**kw):
    d = dict(goal='assets', monthlySpend=50000, yearsToRetire=0, assets=10_000_000, wr0=5, annualReturn=7, volatility=18, inflation=2,
             years=30, mode='mc', stressYears=3, stressReturn=-20, order='freeze')
    d.update(kw); return d

CASES = [
    case(),                                                     # page default
    case(order='guardrail'),
    case(years=40, wr0=5.3, annualReturn=12, volatility=17, inflation=4.5),   # paper Table 6 neighbourhood
    case(years=40, wr0=6.5, annualReturn=12, volatility=17, inflation=4.5, order='guardrail'),
    case(years=10, wr0=6),                                      # capital-preservation rule off the whole time (T <= 15)
    case(years=16, wr0=4.5, annualReturn=5, volatility=15),     # rule on for exactly the first year
    case(wr0=15, annualReturn=3),                               # almost every path fails
    case(wr0=2, annualReturn=9, volatility=10, inflation=1),    # prosperity rule fires a lot
    case(goal='spend', monthlySpend=60000, yearsToRetire=12, wr0=4.5, inflation=2.5),
    case(mode='stress', stressYears=3, stressReturn=-20),
    case(mode='stress', stressYears=5, stressReturn=-15, order='guardrail', wr0=4.5),
    case(mode='stress', stressYears=1, stressReturn=-30, years=20, wr0=6),
]
SEARCH_CASE = case(wr0=4, annualReturn=8, volatility=16, inflation=2.5)   # max-initial-rate search (Table 6/7 style)

SUMMARY_KEYS = ['success', 'endMed', 'endLo', 'ppMed', 'ppLastMed', 'ppAllMed', 'ppLastAllMed', 'cuts', 'raises', 'freezes', 'lastWdMed', 'failYear']
YEAR_KEYS = ['startMed', 'wdMed', 'wrMed', 'wrLo', 'wrHi', 'endMed', 'endLo', 'endHi', 'cutShare', 'raiseShare', 'frozenShare']

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

def page_results():
    html = open(os.path.join(ROOT, 'retirement_dynamic_withdrawal.html'), encoding='utf-8').read()
    consts = ['const GUARD', 'const STEP', 'const CPR_YEARS_BEFORE_END', 'const STANDARDS', 'const confidenceOf', 'const SCAN_START', 'const SCAN_MAX', 'const COARSE']
    funcs = ['spendAtRetirement', 'requiredAssets', 'emptyRun', 'resetRun', 'runPath', 'summarize', 'searchMaxRates']
    parts = [cut(html, c) for c in consts] + [cut(html, 'function ' + f) for f in funcs]
    js = ('var window = {};\n' + open(os.path.join(ROOT, 'assets/js/mc.js'), encoding='utf-8').read() +
          '\nvar MC = window.MC; const { percentile, sortedCopy } = MC;\n' + '\n'.join(parts) + '''
var cases = %s, searchCase = %s, out = {cases: [], search: null, confidence: []};
function toV(c){
  var v = { goal: c.goal, monthlySpend: c.monthlySpend, yearsToRetire: c.yearsToRetire, assets: c.assets, wr0: c.wr0 / 100, ret: c.annualReturn, vol: c.volatility,
            infl: c.inflation / 100, years: c.years, mode: c.mode, stressYears: c.stressYears, stressReturn: c.stressReturn, order: c.order };
  if(v.goal === 'spend'){ v.spendAtRetire = spendAtRetirement(v.monthlySpend, v.yearsToRetire, v.infl); v.assets = requiredAssets(v.spendAtRetire, v.wr0); }
  return v;
}
function simulate(v){   // same sequence as update(): stress = one path, otherwise 4,000 shared paths
  var T = v.years, dynRuns = [], fixRuns = [], paths = null;
  if(v.mode === 'stress'){
    var rets = Array.from({ length: T }, function(_, i){ return (i < v.stressYears ? v.stressReturn : v.ret) / 100; });
    dynRuns.push(runPath(v, rets, true)); fixRuns.push(runPath(v, rets, false));
  } else {
    paths = new Float64Array(MC.TRIALS * T); var k = 0;
    MC.forEachPath({ years: T, ret: v.ret, vol: v.vol }, function(rets){ paths.set(rets, k++ * T); dynRuns.push(runPath(v, rets, true)); fixRuns.push(runPath(v, rets, false)); });
  }
  return { dyn: summarize(dynRuns, T), fix: summarize(fixRuns, T), paths: paths };
}
cases.forEach(function(c){ var v = toV(c), r = simulate(v); out.cases.push({ assets: v.assets, dyn: r.dyn, fix: r.fix }); });
(function(){
  var v = toV(searchCase), r = simulate(v);
  out.search = searchMaxRates({ v: v, paths: r.paths }).map(function(x){ return { std: x.std, dynT: x.dynT, fixT: x.fixT, stats: x.stats ? { success: x.stats.success, ppMed: x.stats.ppMed } : null }; });
})();
[[0.99, 0.99], [0.99, 0.95], [0.95, 0.99], [0.95, 0.95], [0.91, 0.92], [0.5, 0.99], [0.99, null], [0.9, 0.9], [0.89, 0.99]].forEach(function(a){ out.confidence.push(confidenceOf(a[0], a[1])); });
print(JSON.stringify(out));
''' % (json.dumps(CASES), json.dumps(SEARCH_CASE)))
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(js); path = f.name
    try:
        r = subprocess.run([JSC, path], capture_output=True, text=True, timeout=900)
    finally:
        os.unlink(path)
    if r.returncode: sys.exit('jsc failed:\n' + r.stdout[-2000:] + r.stderr[-2000:])
    return json.loads(r.stdout.strip().splitlines()[-1])

# ---------- reference side ----------
def paths_for(c):
    """Same 4,000 random paths as the page (seeded mulberry32 + Box-Muller, log-normal with arithmetic mean/stdev)."""
    T, m, s = c['years'], c['annualReturn'] / 100, c['volatility'] / 100
    sig2 = math.log(1 + s * s / ((1 + m) * (1 + m))); mu = math.log(1 + m) - sig2 / 2; sig = math.sqrt(sig2)
    nrm = ref.normal_src(ref.mulberry32(20060301))
    return [[math.exp(mu + sig * nrm()) - 1 for _ in range(T)] for _ in range(4000)]

def ref_search(c):
    paths = paths_for(c)
    T, infl, A = c['years'], c['inflation'] / 100, float(c['assets'])
    cache = {}
    def ev(tenths, dynamic):
        key = (tenths, dynamic)
        if key not in cache:
            p = dict(A=A, w0=tenths / 1000, infl=infl, T=T, order=c['order'])
            ok = [ref.run(p, r, dynamic) for r in paths]
            ok = [o['pp'] for o in ok if not o['fail']]
            cache[key] = (len(ok) / len(paths), ref.pct(sorted(ok), .5) if ok else None)
        return cache[key]
    def find(meets):
        if not meets(10): return None
        t = 10
        while t + 5 <= 250 and meets(t + 5): t += 5
        while t < 250 and meets(t + 1): t += 1
        return t
    out = []
    for std in (0.99, 0.95, 0.90):
        dm = lambda t: ev(t, True)[1] is not None and ev(t, True)[0] >= std and ev(t, True)[1] >= std
        fm = lambda t: ev(t, False)[0] >= std
        dt, ft = find(dm), find(fm)
        out.append(dict(std=std, dynT=dt, fixT=ft, stats=(dict(success=ev(dt, True)[0], ppMed=ev(dt, True)[1]) if dt is not None else None)))
    return out

def to_ref_input(c):
    return dict(assets=c['assets'], goal=c['goal'], monthlySpend=c['monthlySpend'], inflation=c['inflation'], yearsToRetire=c['yearsToRetire'], wr0=c['wr0'],
                years=c['years'], order=c['order'], annualReturn=c['annualReturn'], mode=c['mode'], stressYears=c['stressYears'], stressReturn=c['stressReturn'], volatility=c['volatility'])

# ---------- compare ----------
def close(a, b):
    if a is None or b is None: return a is None and b is None
    return a == b or abs(a - b) <= TOL * max(1.0, abs(a), abs(b))

def main():
    if not os.path.exists(JSC): sys.exit('jsc not found (this check needs macOS JavaScriptCore)')
    page = page_results()
    fails, n = [], 0
    def check(name, ok, detail=''):
        nonlocal n; n += 1
        if not ok: fails.append(f'{name} {detail}')
    for c, pg in zip(CASES, page['cases']):
        tag = f"{c['mode']}/{c['order']}/T{c['years']}/wr{c['wr0']}" + ('/spend' if c['goal'] == 'spend' else '')
        rd, rf, _, _ = ref.simulate(to_ref_input(c))
        if c['goal'] == 'spend':
            want = c['monthlySpend'] * (1 + c['inflation'] / 100) ** c['yearsToRetire'] * 12 / (c['wr0'] / 100)
            check(tag + ' required assets', close(want, pg['assets']), f"ref={want} page={pg['assets']}")
        for side, r, p in (('dyn', rd, pg['dyn']), ('fix', rf, pg['fix'])):
            for k in SUMMARY_KEYS:
                check(f'{tag} {side}.{k}', close(r[k], p[k]), f'ref={r[k]} page={p[k]}')
            check(f'{tag} {side} years', len(r['years']) == len(p['years']) == c['years'])
            bad = [(i + 1, k) for i, (ry, py) in enumerate(zip(r['years'], p['years'])) for k in YEAR_KEYS if not close(ry[k], py[k])]
            check(f'{tag} {side} per-year fields', not bad, f'first mismatches (year, field): {bad[:3]}')
    # max initial withdrawal rate search (paper Tables 6/7)
    want = ref_search(SEARCH_CASE)
    for w, p in zip(want, page['search']):
        t = f"search {int(w['std'] * 100)}%"
        check(t + ' dynT', w['dynT'] == p['dynT'], f"ref={w['dynT']} page={p['dynT']}")
        check(t + ' fixT', w['fixT'] == p['fixT'], f"ref={w['fixT']} page={p['fixT']}")
        check(t + ' stats', (w['stats'] is None) == (p['stats'] is None) and (w['stats'] is None or (close(w['stats']['success'], p['stats']['success']) and close(w['stats']['ppMed'], p['stats']['ppMed']))), f"ref={w['stats']} page={p['stats']}")
    # confidence standard (paper p.56): success AND purchasing-power median both reach the level
    def conf(s, pp): return None if pp is None else next((x for x in (0.99, 0.95, 0.90) if s >= x and pp >= x), None)
    for (s, pp), got in zip([(0.99, 0.99), (0.99, 0.95), (0.95, 0.99), (0.95, 0.95), (0.91, 0.92), (0.5, 0.99), (0.99, None), (0.9, 0.9), (0.89, 0.99)], page['confidence']):
        check(f'confidence({s},{pp})', conf(s, pp) == got, f'ref={conf(s, pp)} page={got}')
    print(f'{n} checks, {len(fails)} failed')
    for f in fails[:40]: print('  FAIL', f)
    sys.exit(1 if fails else 0)

main()
