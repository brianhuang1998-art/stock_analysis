#!/usr/bin/env python3
"""Year-by-year retirement withdrawal schedule with the Guyton & Klinger (2006) decision rules.

Deterministic: every number comes from this script, nothing is computed by hand or by the language model.
Pure standard library. Run  schedule.py --help  or read ../SKILL.md.

Rules implemented (print page numbers of Journal of Financial Planning, March 2006):
  - withdrawal on the first day of each year, then the remainder earns that year's return        (p.52)
  - year 1 = assets x initial withdrawal rate (IWR); later years start from last year's withdrawal (p.50, p.51)
  - inflation rule: x (1 + last year's inflation), NO 6% cap                                       (p.50, p.55)
  - modified withdrawal rule (freeze): no inflation increase after a year with a negative total return
    AND when this year's withdrawal rate would be above the IWR; never made up later               (p.52)
  - capital preservation rule: current rate > IWR x 1.2 -> this year's withdrawal x 0.9; not applied
    in the last 15 years of the plan                                                                (p.54)
  - prosperity rule: current rate < IWR x 0.8 -> this year's withdrawal x 1.1                       (p.54)
  - the adjusted amount is the basis for next year                                                  (p.54)
  - success = the portfolio still holds money at the end (p.52); purchasing power is reported for
    successful runs only (p.54-55)
The paper does not say in which order the freeze and the guardrails are tested; both readings are available (--order).
"""
import argparse
import json
import math
import sys

GUARD = 0.20          # guardrails: +/-20% of the initial withdrawal rate
STEP = 0.10           # capital preservation / prosperity: one adjustment is 10%
CPR_FREE_YEARS = 15   # capital preservation rule does not apply in the last 15 years of the plan


def expand(values, years, name):
    """A single number means 'the same every year'; a list must have exactly one value per year."""
    if len(values) == 1:
        return [values[0]] * years
    if len(values) != years:
        sys.exit(f"error: --{name} has {len(values)} values but the plan has {years} years (give 1 value or {years})")
    return list(values)


def parse_series(text):
    """'7' or '7,-15,12' or a path to a file with numbers separated by commas / whitespace / newlines (percent)."""
    try:
        with open(text, encoding='utf-8') as f:
            text = f.read()
    except OSError:
        pass
    parts = [p for p in text.replace('\n', ',').replace(';', ',').replace(' ', ',').split(',') if p.strip() != '']
    try:
        return [float(p.strip().rstrip('%')) / 100 for p in parts]
    except ValueError:
        sys.exit(f"error: cannot read numbers from {text!r}")


def run(assets, iwr, years, returns, inflation, order='freeze', cpr_free_years=CPR_FREE_YEARS):
    """returns[t-1] / inflation[t-1] belong to year t (fractions). Returns a list of per-year dicts."""
    rows = []
    bal = assets
    prev_w = 0.0
    plan_factor = 1.0          # cumulative inflation: what a plain inflation-adjusted plan would withdraw
    depleted_at = 0
    for t in range(1, years + 1):
        i = t - 1
        planned = assets * iwr * plan_factor
        row = dict(year=t, start=bal, infl_prev=(inflation[i - 1] if t > 1 else None), ret=returns[i],
                   planned=planned, trial=None, rule=[], wd=0.0, cwr=None, end=0.0, status='')
        if bal <= 0:
            row.update(status='資金已用完', start=0.0)
            rows.append(row)
            plan_factor *= (1 + inflation[i])
            continue
        if t == 1:
            w = assets * iwr
            row['rule'] = ['初始']
        else:
            base = prev_w * (1 + inflation[i - 1])          # last year's withdrawal x (1 + last year's inflation)
            lost = returns[i - 1] < 0
            cpr_on = (years - t + 1) > cpr_free_years       # remaining years including this one
            row['trial'] = base / bal
            if order == 'guardrail':
                cur = base / bal
                if cpr_on and cur > iwr * (1 + GUARD):
                    w = base * (1 - STEP); row['rule'] = ['保本 −10%']
                elif cur < iwr * (1 - GUARD):
                    w = base * (1 + STEP); row['rule'] = ['繁榮 +10%']
                elif lost and cur > iwr:
                    w = prev_w; row['rule'] = ['凍結']
                else:
                    w = base; row['rule'] = ['正常調整']
            else:
                freeze = lost and base / bal > iwr
                w = prev_w if freeze else base
                tags = ['凍結'] if freeze else []
                cur = w / bal                                # guardrails look at the rate AFTER the freeze decision
                if cpr_on and cur > iwr * (1 + GUARD):
                    w *= (1 - STEP); tags.append('保本 −10%')
                elif cur < iwr * (1 - GUARD):
                    w *= (1 + STEP); tags.append('繁榮 +10%')
                row['rule'] = tags or ['正常調整']
        prev_w = w
        if w >= bal:                                          # not enough money: take what is left, plan fails
            row.update(wd=bal, cwr=w / bal, end=0.0, status='資金用完')
            depleted_at = depleted_at or t
            bal = 0.0
        else:
            row.update(wd=w, cwr=w / bal, end=(bal - w) * (1 + returns[i]))
            bal = row['end']
        rows.append(row)
        plan_factor *= (1 + inflation[i])
    for r in rows:
        r['depleted_at'] = depleted_at
    return rows


def summarize(rows, assets, iwr):
    n = len(rows)
    cuts = sum(1 for r in rows if any('保本' in x for x in r['rule']))
    raises = sum(1 for r in rows if any('繁榮' in x for x in r['rule']))
    freezes = sum(1 for r in rows if any('凍結' in x for x in r['rule']))
    depleted = rows[0]['depleted_at'] if rows else 0
    pp = [r['wd'] / r['planned'] if r['planned'] else 0.0 for r in rows]
    return dict(years=n, cuts=cuts, freezes=freezes, raises=raises, success=not depleted, depleted_at=depleted,
                final_assets=rows[-1]['end'], total_pp=(sum(pp) / n if not depleted else None),
                last_year_pp=(pp[-1] if not depleted else None), pp_all_years=sum(pp) / n,
                total_withdrawn=sum(r['wd'] for r in rows))


def money(x):
    """Whole yuan, rounding halves up (same as the website); the calculation itself is never rounded."""
    return f"{int(math.floor(x + 0.5)):,}"


def pct(x, d=2):
    return '—' if x is None else f"{x * 100:.{d}f}%"


def markdown(rows, s, a):
    lines = []
    lines.append("### 提領規則門檻")
    lines.append("")
    up, lo = a.iwr * (1 + GUARD), a.iwr * (1 - GUARD)
    lines.append("| 項目 | 數值 |\n|---|---|")
    lines.append(f"| 初始提領率 (IWR) | {a.iwr * 100:.2f}% |")
    lines.append(f"| 上限護欄（保本規則觸發門檻） | 目前提領率 > {up * 100:.2f}% |")
    lines.append(f"| 下限護欄（繁榮規則觸發門檻） | 目前提領率 < {lo * 100:.2f}% |")
    if a.years <= a.cpr_free_years:
        lines.append(f"| 保本規則 | **整個計畫都停用**（計畫只有 {a.years} 年，不超過最後 {a.cpr_free_years} 年的停用期；只剩凍結與繁榮規則） |")
    else:
        lines.append(f"| 保本規則停用 | 退休規劃最後 {a.cpr_free_years} 年（第 1～{a.years - a.cpr_free_years} 年適用，第 {a.years - a.cpr_free_years + 1} 年起不再下調） |")
    lines.append(f"| 檢定順序 | {'先決定是否凍結，再用凍結後的金額檢定護欄' if a.order == 'freeze' else '先用含通膨的金額檢定護欄，沒觸發才凍結'} |")
    lines.append(f"| 通膨調整 | 前一年提領 × (1 + 前一年通膨率)，不設上限 |")
    lines.append("")
    lines.append("### 逐年退休金提領與資產試算表")
    lines.append("")
    age = a.start_age
    head = "| 年份" + (" / 年齡" if age is not None else "") + " | 年初資產 | 前年通膨率 | 試算提領率 | 觸發規則 | 當年實際提領 | 實際提領率 | 購買力 | 當年報酬 | 年底資產 |"
    lines.append(head)
    lines.append("|" + "---|" * (head.count('|') - 1))
    for r in rows:
        who = f"第 {r['year']} 年" + (f" / {age + r['year'] - 1} 歲" if age is not None else "")
        rule = '、'.join(r['rule']) if r['rule'] else r['status']
        if r['status'] == '資金已用完':
            rule = '資金已用完'
        elif r['status'] == '資金用完':
            rule += '（資金用完，只領剩下的）'
        pp = r['wd'] / r['planned'] if r['planned'] else 0.0
        lines.append(f"| {who} | {money(r['start'])} | {pct(r['infl_prev'])} | {pct(r['trial'])} | {rule} | {money(r['wd'])} | "
                     f"{pct(r['cwr'])} | {pct(pp, 0)} | {pct(r['ret'])} | {money(r['end'])} |")
    lines.append("")
    lines.append("### 試算總結")
    lines.append("")
    lines.append(f"- 保本下調 **{s['cuts']}** 次、繁榮上調 **{s['raises']}** 次、凍結 **{s['freezes']}** 次（同一年同時凍結與保本會各計一次）。")
    if s['success']:
        lines.append(f"- 結果：**資金撐過 {s['years']} 年**，期末剩餘資產 {money(s['final_assets'])} 元。")
        lines.append(f"- 購買力維持（論文定義，僅成功的模擬）：各年平均 **{pct(s['total_pp'], 0)}**，最後一年 **{pct(s['last_year_pp'], 0)}**（100% = 實際提領與一般隨通膨調整的計畫提領相同）。")
    else:
        lines.append(f"- 結果：**失敗，第 {s['depleted_at']} 年資金用完**，期末資產 0 元。論文只在成功的模擬裡計算購買力，所以不列出；含失敗年度的各年平均為 {pct(s['pp_all_years'], 0)}。")
    lines.append(f"- 退休期間共提領 {money(s['total_withdrawn'])} 元。")
    lines.append("")
    lines.append("> 這是單一條報酬路徑的結果，不是機率。購買力欄 = 當年實際提領 ÷ 「首年提領隨通膨調整」的計畫提領。")
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog="Returns and inflation are in percent. Give one number (same every year) or one value per year, "
                                       "as a comma list or a file path. Negative numbers need the = form: --returns=-15,7,-3")
    p.add_argument('--assets', type=float, required=True, help='retirement assets at the start (e.g. 10000000)')
    p.add_argument('--iwr', type=float, required=True, help='initial withdrawal rate in percent (e.g. 5.3)')
    p.add_argument('--years', type=int, required=True, help='planning horizon in years (e.g. 40)')
    p.add_argument('--returns', required=True, help='annual portfolio total return in percent: one value or one per year')
    p.add_argument('--inflation', required=True, help='annual inflation in percent: one value or one per year')
    p.add_argument('--first-years', type=int, default=0, help='stress shortcut: the first N years use --first-return, the rest use --returns')
    p.add_argument('--first-return', default=None, help='percent, used with --first-years (write it as --first-return=-15)')
    p.add_argument('--order', choices=['freeze', 'guardrail'], default='freeze',
                   help='freeze (default): decide the freeze first, test guardrails on the frozen amount; '
                        'guardrail: test guardrails on the inflation-adjusted amount first, freeze only if none fires')
    p.add_argument('--start-age', type=int, default=None, help='age in year 1 (adds an age column)')
    p.add_argument('--cpr-free-years', type=int, default=CPR_FREE_YEARS, help='capital preservation rule is off in the last N years (paper: 15)')
    p.add_argument('--json', action='store_true', help='print the rows and summary as JSON instead of Markdown')
    a = p.parse_args()
    if not (a.assets > 0 and a.iwr > 0 and a.years >= 1):
        sys.exit('error: assets, iwr and years must be positive')
    a.iwr /= 100
    if a.first_years:
        base = parse_series(a.returns)
        if len(base) != 1 or a.first_return is None:
            sys.exit('error: --first-years needs one value for --returns and a --first-return')
        first = parse_series(a.first_return)
        if len(first) != 1:
            sys.exit('error: --first-return must be a single number')
        returns = [first[0]] * min(a.first_years, a.years) + [base[0]] * max(a.years - a.first_years, 0)
    else:
        returns = expand(parse_series(a.returns), a.years, 'returns')
    inflation = expand(parse_series(a.inflation), a.years, 'inflation')
    if any(r <= -1 for r in returns):
        sys.exit('error: a yearly return of -100% or lower is not possible')
    rows = run(a.assets, a.iwr, a.years, returns, inflation, a.order, a.cpr_free_years)
    s = summarize(rows, a.assets, a.iwr)
    if a.json:
        print(json.dumps(dict(summary=s, rows=rows), ensure_ascii=False, indent=1))
    else:
        print(markdown(rows, s, a))


if __name__ == '__main__':
    main()
