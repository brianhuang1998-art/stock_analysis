# Rules implemented (Guyton & Klinger 2006, printed page numbers)

Notation: A = starting assets, IWR = initial withdrawal rate, W(t) = withdrawal in year t, B(t) = assets at the start of year t, T = plan length in years, r(t) = total return of year t, i(t) = inflation of year t.

| # | Rule | Paper | In `schedule.py` |
|---|---|---|---|
| 1 | Withdraw on the first day of the year; the rest then earns the year's return | p.52 | end(t) = (B(t) − W(t)) × (1 + r(t)); B(t+1) = end(t) |
| 2 | Year 1 withdrawal = A × IWR | p.50 | W(1) = A × IWR |
| 3 | Withdrawals rise with last year's inflation; **no 6% cap** (the cap was dropped) | p.50, p.51, p.55 | base(t) = W(t−1) × (1 + i(t−1)) |
| 4 | Freeze (modified withdrawal rule): no inflation increase after a year with a negative total return **and** when this year's withdrawal rate would be above the IWR; no make-up | p.52 | freeze if r(t−1) < 0 and base(t) / B(t) > IWR |
| 5 | Capital preservation: current rate more than 20% above the IWR → this year's withdrawal reduced by 10% | p.54 | rate > IWR × 1.2 → × 0.9 |
| 6 | Capital preservation expires 15 years before the end of the plan | p.54 | active only if T − t + 1 > 15 (remaining years including this one) |
| 7 | Prosperity: current rate more than 20% below the IWR → this year's withdrawal raised by 10% | p.54 | rate < IWR × 0.8 → × 1.1 |
| 8 | The adjusted amount is the basis for next year; nothing is made up | p.54 | prev_w = W(t) |
| 9 | Success = money left at the end | p.52 | no year with W ≥ opening assets |
| 10 | Purchasing power: only in successful simulations; total and year-N | p.54–55 | planned(t) = A × IWR × Π(1 + i(k)), k < t; ratio = W(t) / planned(t); total = mean over years |
| 11 | Portfolio management rule (which asset to sell) | p.51 | not applicable: single asset |

"Current rate" = this year's withdrawal ÷ opening assets B(t).

## Order of the freeze and the guardrails (not settled by the paper)
- `freeze`: freeze decision → rate on the frozen amount → guardrails. A year can show both "凍結" and "保本".
- `guardrail`: rate on base(t) → if above the upper guardrail (and the rule is active): base × 0.9; else if below the lower: base × 1.1; else freeze test; else base. At most one tag per year.
The column "試算提領率" is base(t) / B(t), the rate before any freeze.

## Edge cases (all fixed in the code)
- Thresholds are strict: a rate exactly equal to IWR × 1.2 or × 0.8 does not trigger; a return of exactly 0% is not negative.
- Year 1 has no tests.
- If W(t) ≥ B(t) the plan fails: the withdrawal is whatever is left, the money is 0 afterwards, later rows read "資金已用完", and purchasing power is not reported for a failed run (the paper only measures successful ones); an all-years figure that includes the zeros is printed for reference.
- Nothing is rounded during the calculation; money is displayed in whole yuan (halves round up, as on the website).
- A yearly return of −100% or lower is rejected.
- A one-year plan or a plan of 15 years or less never uses the capital preservation rule.
- Hand-worked cases and random comparisons are in `scripts/verify.py`.
