#!/usr/bin/env python3
"""Self-test for schedule.py. Run:  python3 .claude/skills/gk-withdrawal-schedule/scripts/verify.py

1. Three small cases worked out by hand (freeze-first, guardrail-first, running out of money).
2. 600 random cases compared with the project's independent reference simulator (papers/verification/ref_simulator.py),
   which the website's JavaScript is also checked against.
Exit code 0 = everything agrees.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', 'papers', 'verification')))
import schedule as S

bad = 0


def check(name, got, want, tol=1e-6):
    global bad
    ok = abs(got - want) <= tol * max(1.0, abs(want))
    if not ok:
        bad += 1
        print(f"FAIL {name}: got {got!r}, expected {want!r}")
    return ok


# ---- 1. hand-worked cases ------------------------------------------------------------------------------
# assets 1,000,000, IWR 5%, 3 years, returns -20% / +10% / +5%, inflation 3% / 4% / 2%, guardrail checks on in every year
r = S.run(1_000_000, 0.05, 3, [-0.20, 0.10, 0.05], [0.03, 0.04, 0.02], 'freeze', cpr_free_years=0)
check('freeze y1 wd', r[0]['wd'], 50_000); check('freeze y1 end', r[0]['end'], 760_000)
# year 2: base 51,500; lost and base/bal 6.78% > 5% -> freeze at 50,000; frozen rate 6.58% > 6% -> x0.9 = 45,000
check('freeze y2 wd', r[1]['wd'], 45_000); check('freeze y2 end', r[1]['end'], 786_500)
if r[1]['rule'] != ['凍結', '保本 −10%']: bad += 1; print('FAIL freeze y2 rule', r[1]['rule'])
# year 3: previous return +10% -> no freeze; base 46,800; rate 5.95% inside the guardrails
check('freeze y3 wd', r[2]['wd'], 46_800); check('freeze y3 end', r[2]['end'], 776_685)
if r[2]['rule'] != ['正常調整']: bad += 1; print('FAIL freeze y3 rule', r[2]['rule'])

g = S.run(1_000_000, 0.05, 3, [-0.20, 0.10, 0.05], [0.03, 0.04, 0.02], 'guardrail', cpr_free_years=0)
# year 2: guardrails first on 51,500 / 760,000 = 6.78% > 6% -> x0.9 = 46,350 (the inflation increase stays in)
check('guardrail y2 wd', g[1]['wd'], 46_350); check('guardrail y2 end', g[1]['end'], 785_015)
# year 3: base 48,204; 48,204 / 785,015 = 6.14% > 6% -> x0.9 = 43,383.6
check('guardrail y3 wd', g[2]['wd'], 43_383.6); check('guardrail y3 end', g[2]['end'], 778_713.0, 1e-5)

# running out of money: assets 100,000, IWR 30%, returns -50%, no inflation
d = S.run(100_000, 0.30, 5, [-0.5] * 5, [0.0] * 5, 'freeze', cpr_free_years=0)
check('depleted year', d[0]['depleted_at'], 3)
check('y3 takes what is left', d[2]['wd'], 4_000); check('y4 nothing', d[3]['wd'], 0); check('y5 nothing', d[4]['wd'], 0)
sm = S.summarize(d, 100_000, 0.30)
if sm['success'] or sm['total_pp'] is not None: bad += 1; print('FAIL a failed run must not report purchasing power')

# ---- 2. random cases against the reference simulator -----------------------------------------------------
try:
    import ref_simulator as ref
except ImportError:
    ref = None
    print('note: papers/verification/ref_simulator.py not found, skipping the random comparison')
if ref:
    rnd = random.Random(2006)
    n = 0
    for k in range(600):
        T = rnd.randint(1, 45)
        assets = rnd.choice([3e6, 8e6, 1.2e7, 2.5e7])
        iwr = rnd.uniform(0.02, 0.10)
        infl = rnd.uniform(-0.01, 0.08)
        rets = [math.exp(rnd.gauss(0.05, 0.17)) - 1 for _ in range(T)]
        for order in ('freeze', 'guardrail'):
            mine = S.run(assets, iwr, T, rets, [infl] * T, order)
            p = dict(A=assets, w0=iwr, infl=infl, T=T, order=order)
            theirs = ref.run(p, rets, True)
            for i in range(T):
                n += 1
                if abs(mine[i]['wd'] - theirs['wd'][i]) > 1e-6 * max(1, assets) or abs(mine[i]['end'] - theirs['end'][i]) > 1e-6 * max(1, assets):
                    bad += 1
                    print(f"FAIL random case {k} {order} year {i + 1}: {mine[i]['wd']} vs {theirs['wd'][i]}")
                    break
    print(f'random comparison: {600 * 2} schedules, {n} year-rows checked')
print('ALL CHECKS PASSED' if not bad else f'{bad} FAILURES')
sys.exit(1 if bad else 0)
