# Visual audit report: Guyton & Klinger (2006), *Decision Rules and Maximum Initial Withdrawal Rates*

- **Audited copy:** `papers/source/Guytons-Guardrails-Maximum-Inisital-Withdrawal-Rates.pdf`, 9 pages, a scan of the printed *Journal of Financial Planning*, March 2006, pp. 50–58 (ScanSnap, 1272 × 1620 px per page, about 150 dpi, no text layer).
- **Read by:** Claude (vision), 2026-10-06. Page images rendered with pypdfium2 and cropped per table; **every table was transcribed twice** from different crops and scales (pass 1 at 2.6x, pass 2 at 3.4x with the larger tables split in halves), then the two passes were compared cell by cell.
- **Method / scripts:** `.claude/skills/paper-visual-audit/` (`pdf_inventory.py`, `render_pages.py`, `compare_transcriptions.py`, `check_tables.py`). Transcriptions are in `papers/audit/transcriptions/` (`scan_<table>.json` = pass 1, `scan_<table>_pass2.json` = pass 2), evidence crops in `papers/audit/images/scan/`, raw check output in `checks_scan.md`, file inventory in `inventory_scan.json`.
- **Page numbers** are the printed page numbers: Table 1 p.52, Table 2 p.53, Figure 1 p.54, Tables 3–4 p.55, Tables 5–6 p.56, Table 7 p.57.

## Summary

| Audit | OK | CHECK | NOTE | FAIL |
|---|---|---|---|---|
| 1 Data | 4 | 4 (one minor) | 0 | 0 |
| 2 Figures | 1 | 0 | 2 | 0 |
| 3 Labels and fonts | 0 | 0 | 7 | 0 |

No arithmetic failures. One table-to-table gap and three statements in the summary and conclusion do not match the tables exactly (D-05 to D-08); they may be loose wording rather than errors, so they are marked CHECK for a human decision.

## 1. Data audit

| ID | Level | Finding | Evidence |
|---|---|---|---|
| D-01 | OK | The two independent transcriptions of Tables 1, 2, 3, 4, 6 and 7 are **identical**: 466 cells compared, 0 differences. | `transcriptions/scan_*.json` vs `scan_*_pass2.json` |
| D-02 | OK | Table 1: each portfolio column sums to 100%, and the equity rows add up to the equity share in the header (50/65/80). | `checks_scan.md` |
| D-03 | OK | Table 2: every "withdrawal enhancement" equals the ratio of the two printed rates minus 1, within rounding of the printed one-decimal rates (e.g. all-3-rules, 65%, 95% POS: 4.3 / 3.1 = +39%). The text's "increases the maximum initial withdrawal rate 30–43 percent" matches the "All 3" rows (30% to 43%). | Table 2 (p.53) |
| D-04 | OK | Tables 3 and 4: initial WD rate rises and purchasing power falls as the required success level falls. Tables 6 and 7: WD rate rises as the confidence standard falls from 99% to 90%, and every row's success rate and total purchasing power are at least the standard it is listed under. Table 6 single-equity 65/25/10 agrees with the Table 3 curve (e.g. 5.7% ↔ 97% success). | `checks_scan.md` |
| D-05 | CHECK (minor) | **Table 6 vs Table 4, multi-class 65/25/10.** Table 6 (40 years) lists 5.5% and 5.8% with a success rate of **99%**; Table 4 (same portfolio and rules) shows **100%** success up to 6.3% and 99% only at 7.1%. In success terms the gap is **about 1 point (99% vs 100%)**. It looks large when read as an initial WD rate (1.3–1.6 points) only because the success curve is flat near 100%. Sampling noise with 14,000 trials is about 0.1 point, so a 1-point rounded gap is more than noise, but small. The extra purchasing-power standard behind Table 6 lowers the WD rate it lists; it does not change the plain success rate printed next to that rate, so it does not explain the gap. Single-equity Tables 3 and 6 agree within 0.1 point. Cause unknown. | Table 4 (p.55), Table 6 (p.56) |
| D-06 | **CHECK** | Executive summary and conclusion: "5.2–5.6 percent are sustainable at the 99 percent confidence standard for portfolios containing at least 65 percent equities (40 years)". Table 6 has one row outside the range: single-equity 80/10/10 = **4.7%** (also 4.7% in Table 7). May be a loose summary of the multi-class and 65% rows. | Table 6 |
| D-07 | **CHECK** | Conclusion: "rise to 5.7–6.2 percent at the 95 percent confidence standard (40 years)". Table 6 has two rows outside: single-equity 80/10/10 = **5.6%**, multi-class 65/25/10 = **5.5%**. In the 30-year Table 7 all four rows are inside 5.7–6.2. | Table 6, Table 7 |
| D-08 | **CHECK** | Executive summary: "with 50 percent equities, maximum initial withdrawal rates drop to as low as 4.6 percent". Table 6 single-equity 50/40/10 at 99% is **4.5%** (the multi-class row is 4.6%). | Table 6 |

Not verifiable from the paper alone: the table values themselves (they come from a Monte Carlo model fed with 1928–2004 and 1973–2004 asset-class statistics that the paper does not reproduce); the "about 60 percent fewer freezes" statement (p.53; Table 2 shows the freeze counts 6/7/8 vs 3/3/3, which is consistent but is only one table's evidence).

## 2. Figure audit

The only figure is Figure 1 "Decision Rule 'Guardrails'" (p.54). Described blind, before reading the text: three roughly parallel curves rising to the right; the upper one (orange) is labelled "CAPITAL PRESERVATION RULE" and "Current WD Rate is 20% Above Initial WD Rate"; the lower one (green) is labelled "PROSPERITY RULE" and "Current WD Rate is 20% Below Initial WD Rate"; a blue dashed curve between them is labelled "Withdrawal Rule".

| ID | Level | Finding | Evidence |
|---|---|---|---|
| F-01 | OK | The figure matches the text (p.54–55): capital preservation applies when the current rate is more than 20% above the initial rate, prosperity when more than 20% below, and the withdrawal rule governs in between. | `images/scan/figure1.png` |
| F-02 | NOTE | Figure 1 has no axes, units or scale. It is a schematic; what the upward slope means is not stated. | same |
| F-03 | NOTE | The figure is a bitmap with soft edges at the scan resolution; the line labels are legible but the thin blue dashes are faint. | same |

## 3. Label and font audit

| ID | Level | Finding | Evidence |
|---|---|---|---|
| L-01 | NOTE | **Table 7 is a 30-year table but its last column is headed "Year 40 PP%".** Probably should read Year 30. | `images/scan/table7.png`, `images/scan/pass2/t7_a.png` |
| L-02 | NOTE | Table 5 title is misspelled "Intitial". | `images/scan/table6.png` (Table 5 is at its top) |
| L-03 | NOTE | **Table 2 has no footnote markers and no footnote line**, while Tables 3, 4, 6 and 7 do. "WD", "POS" and "WR" are therefore not defined in Table 2 itself ("POS" is defined in the text, p.52; "WD" is never spelled out in the running text). | `images/scan/table2_bottom.png`, `images/scan/pass2/t2_a.png` |
| L-04 | NOTE | Table 1 lists its columns as **65% / 80% / 50%** equities instead of ascending order; the values are consistent with the headers (checked by D-02). | `images/scan/pass2/t1.png` |
| L-05 | NOTE | Table 6 header "Total PP%": the footnote marker **appears to be ¹** (the same as for "WD¹"), whereas Table 7 reads ²; footnote 2 is the one that defines PP. Possibly a print typo; at the available resolution the superscript is at the limit of legibility. | `images/scan/pass2/t6_a.png`, `images/scan/pass2/t7_a.png` |
| L-06 | NOTE | Fonts and legibility: the file is images only (no fonts, no text layer, not searchable), about 150 dpi. Table digits are readable at 2.6–3.4x; superscripts (L-05) are not reliably readable. | `inventory_scan.json` |
| L-07 | NOTE | Table 5 ("Decision Rule Summary") lists four condition/action pairs without saying in which order they are tested or that the freeze depends on the withdrawal rate (the paper's modification, p.52). It cannot settle the order of the withdrawal rule and the guardrails. | `images/scan/table5.png` |

## What this audit cannot show
- It shows that the tables were transcribed consistently and that the paper is largely internally consistent. It cannot show the paper's results are right: their inputs are not in the paper.
- A vision model can misread digits. The two passes were made by the same model from different crops of the same scan and agree in all 466 cells; that is strong evidence for the digits but not proof, and the superscripts (L-05) are beyond what the scan resolves. Anything that matters should be confirmed against the printed journal.
- Only one copy (a personal scan) was audited. A scan can be incomplete or mis-ordered; the official journal version would be the authoritative source.

## Reviewer comments received (2026-10-06) and how each was handled

A written explanation of the findings was supplied by the project owner (its author is not stated). Each claim is sorted by what the evidence supports. Nothing below changed a finding's level, except D-05 which was re-examined and softened (above).

| Claim in the comment | Status | Why |
|---|---|---|
| The numbers behind D-06/D-07/D-08 (Table 6 has 4.7%, 5.6%, 5.5%, 4.5%; the text says 5.2–5.6, 5.7–6.2, 4.6) | **Supported** | Re-read twice from the scan; the checker reproduces them. |
| The authors "roughly picked" 5.7 and 6.2 as the range ends, ignoring 5.5 and 5.6 | **Unverified (intent)** | The paper does not say how the range was chosen. The 30-year Table 7 rows for 95% all lie inside 5.7–6.2, so the sentence may mix the two tables or refer to particular portfolios. It stays a CHECK, not a confirmed error. |
| Table 3 and Table 6 single-equity figures are consistent | **Supported** | Checked (gap about 0.1 point). |
| Table 4 is "a run anomaly / non-converged extreme value" that scholars "generally" regard as unreliable | **Not supported** | No source is given and nothing in the paper says so. The text (p.55) presents the higher multi-class rates as a result: "using multiple-equity asset classes produced higher initial withdrawal rates and fewer capital preservation rule cuts". Table 4's own purchasing power (79–93%) shows why those rates are not the paper's recommendation, which is a different reason from "anomaly". |
| Table 6 is the table the authors finally adopted, because of the dual confidence standard | **Supported** | The text and conclusion use Table 6 (and Table 7) for the recommended rates, and the dual standard (success and purchasing power both at least 99% or 95%) is defined on p.56. |
| The dual standard explains the difference between Table 4 and Table 6 | **Partly** | It explains why Table 6's WD rates are lower than the plain-success rates of Tables 3/4. It does not explain the 99% vs 100% success mismatch in D-05 (see above). |
| For planning use Table 6's 5.2–5.6% | **Caution** | Table 6's own rows for portfolios with at least 65% equities also include 4.7% (single-equity 80/10/10) and 5.5% at the 95% standard; 5.2–5.6% is the summary's range, which is exactly what D-06 questions. The tested allocations are at most 80% equities on 1928–2004 and 1973–2004 U.S. data, so they do not transfer directly to a 100% equity portfolio. |
| Table 7 "Year 40 PP%" is a copy-paste error from Table 6 | **Plausible, unverified** | The header is wrong for a 30-year table; whether it came from copying Table 6 cannot be known. |
| Table 5 "Intitial" is a typo | **Supported** | Visible in the scan. |
| Table 2 lacks footnotes in print; the other layout differences came "later" | **Partly** | The print Table 2 does lack them (L-03). Nothing shows what came before or after. |
| Figure 1 is a schematic with no axes | **Supported** | See F-02. |
