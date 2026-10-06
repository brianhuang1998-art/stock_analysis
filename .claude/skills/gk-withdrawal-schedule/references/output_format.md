# Output format

Three parts, in this order (the script prints all of them; show them unchanged).

1. **Rule thresholds**: IWR, upper guardrail (capital preservation trigger), lower guardrail (prosperity trigger), the years in which capital preservation is active, the order used, the inflation rule.
2. **Year-by-year table**, columns:

| Column | Meaning |
|---|---|
| 年份 / 年齡 | year (and age if `--start-age`) |
| 年初資產 | opening assets |
| 前年通膨率 | last year's inflation (blank in year 1) |
| 試算提領率 | last year's withdrawal × (1 + last year's inflation) ÷ opening assets |
| 觸發規則 | 初始 / 正常調整 / 凍結 / 保本 −10% / 繁榮 +10% (a year can be 凍結 + 保本 in `freeze` order) / 資金用完 / 資金已用完 |
| 當年實際提領 | final withdrawal after the rules |
| 實際提領率 | final withdrawal ÷ opening assets |
| 購買力 | final withdrawal ÷ the plain inflation-adjusted plan (100% = same standard of living) |
| 當年報酬 | the year's portfolio total return |
| 年底資產 | (opening − withdrawal) × (1 + return) |

3. **Summary**: number of cuts, raises and freezes; success or the year the money ran out; closing assets; purchasing power (average over the years and last year, successful runs only); total withdrawn.

When explaining to the user (Traditional Chinese): name the year, the rule and the reason in one sentence each, e.g. "第 2 年前一年虧損 15%，含通膨的提領率 6.32% 高於初始 5%，所以先凍結；凍結後的提領率 5.57%…". Never present the single path as a probability.
