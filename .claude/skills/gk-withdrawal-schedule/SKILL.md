---
name: gk-withdrawal-schedule
description: Compute an exact year-by-year retirement withdrawal schedule with the Guyton & Klinger (2006) guardrail rules (freeze rule, capital preservation, prosperity, no inflation cap) for a person's assets, initial withdrawal rate, planning horizon and a return and inflation path. Use when the user asks for a year-by-year withdrawal table or schedule, wants to replay a historical or stress path (for example a 1973-style early crash) through the guardrail rules, wants the effect of a specific return sequence, or wants a schedule produced by another model checked. It runs a deterministic script; never do this arithmetic by hand or in your head.
---

# Guyton-Klinger year-by-year withdrawal schedule

Turns assets, an initial withdrawal rate and a return/inflation path into the table "year, opening assets, rule triggered, withdrawal, withdrawal rate, closing assets". **Every number comes from `scripts/schedule.py`.** Do not compute any row yourself: forty years of compounding and conditional rules are exactly where a language model makes silent mistakes.

The rules are those of Guyton & Klinger (2006), *Decision Rules and Maximum Initial Withdrawal Rates*, J. Financial Planning, March 2006 (page numbers below are the printed ones; the scan is `papers/source/Guytons-Guardrails-Maximum-Inisital-Withdrawal-Rates.pdf`). Only the 2006 rules exist here. Details, edge cases and page references: `references/rules.md`. Output format: `references/output_format.md`.

## 1. Collect the inputs
Ask for anything missing; do not invent values. Defaults only where stated.

| Input | Meaning | Default |
|---|---|---|
| `--assets` | retirement assets on day one (e.g. 10000000) | ask |
| `--iwr` | initial withdrawal rate in percent (5.3 means 5.3%) | ask |
| `--years` | planning horizon in years (the paper uses 40 and 30) | ask |
| `--returns` | annual **total return of the whole portfolio**, percent. One number = the same every year; or one value per year (comma list or a file) | ask |
| `--inflation` | annual inflation, percent; one number or one per year. The value for year *t* is applied to year *t*+1's withdrawal ("last year's inflation") | ask |
| `--order` | `freeze` (default) or `guardrail`: see section 4 | `freeze` |
| `--start-age` | age in year 1; adds an age column | optional |
| `--first-years N --first-return=X` | stress shortcut: the first N years return X%, the rest use `--returns` | optional |

The portfolio is treated as a single asset. The paper's portfolio management rule (which asset to sell) therefore does not apply; say so if the user's portfolio is not 100% in one asset class.

## 2. Run the script
From the project root (Python 3, standard library only):

```bash
python3 .claude/skills/gk-withdrawal-schedule/scripts/schedule.py \
  --assets 10000000 --iwr 5.3 --years 40 --returns 7 --inflation 2.5
```

- Negative numbers need the `=` form: `--returns=-15,7,-3`, `--first-return=-15`.
- A series with one value per year can be a file: `--returns returns.txt` (commas, spaces or newlines).
- `--json` prints rows and summary as JSON.
- Stress example, first three years −15% then 7%: `--returns 7 --first-years 3 --first-return=-15`.

## 3. Report the result
1. Show the output tables as they are (rule thresholds, year-by-year table, summary). Do not retype or "tidy" the numbers.
2. In plain Chinese, say which years triggered which rule and why (use the "trial rate" and "actual rate" columns), and what the summary means: counts of cuts, raises and freezes; success or the year the money ran out; purchasing power.
3. State which **order** was used and that the paper does not settle it.
4. Say it is **one return path, not a probability**. For probabilities use the website's Monte Carlo page (`retirement_dynamic_withdrawal.html`).
5. Mention what is not modelled: taxes, fees, other income, one-off expenses, and the portfolio management rule.

## 4. The order of the freeze and the guardrails
The paper does not say whether the freeze (withdrawal rule) or the guardrails are tested first.
- `freeze` (default, same as the website): decide the freeze first, then test the guardrails on the frozen amount. Basis: p.54 says the capital preservation rule looks at the rate "using the decision rules in effect"; also the paper's Table 6 freeze counts are closer to this order.
- `guardrail`: test the guardrails on the inflation-adjusted amount first and freeze only if neither guardrail fires (reads Table 5 as a decision tree). A capital-preservation year then still includes the inflation increase.
On the same random paths the second order gives a success rate about 0.3–3.6 percentage points lower (`papers/verification/paper_check.md` §6). Offer to run both when the difference matters.

## 5. Checking a schedule made elsewhere
If the user pastes a table (for example from another model), run the script with the same inputs and compare row by row. List the first row that differs, which number, and which rule explains it (often the order in section 4, a wrong 15-year cutoff, a 6% inflation cap that the 2006 paper removed, or an inflation rate taken from the wrong year). Do not "split the difference".

## 6. After changing the script
Run `python3 .claude/skills/gk-withdrawal-schedule/scripts/verify.py`. It checks three cases worked out by hand and 1,200 random schedules against the project's independent simulator (`papers/verification/ref_simulator.py`, which the website is also verified against). All checks must pass before the results are trusted.

## Limits
- One path per run; no probabilities, no sampling.
- Inflation and returns are inputs; nothing is looked up. If the user wants "what actually happened in 1973", they must supply the series.
- Not investment advice.
