# Visual audit report: Guyton & Klinger (2006), *Decision Rules and Maximum Initial Withdrawal Rates*

- **Audited copies** (both are the same article):
  - `web` = `papers/Guyton, J. T., & Klinger...19(3), 48.pdf`: 14 pages, FPA website capture (Acrobat Web Capture 8.0, 2008). Text layer present; Tables 1–7 and Figure 1 are embedded bitmaps (about 555 px wide), upscaled 2.2x for reading.
  - `scan` = `papers/Guytons-Guardrails-...pdf`: 9 pages, scan of the printed *Journal of Financial Planning*, March 2006, pp. 50–58 (ScanSnap, 1272 × 1620 px per page, no text layer). Rendered with pypdfium2 at 2.6–5x and cropped per table.
- **Read by:** Claude (vision), single session, 2026-10-06. Tables transcribed from the web images and, independently, from the scan crops; the two transcriptions were then compared.
- **Method / scripts:** `.claude/skills/paper-visual-audit/` (`pdf_inventory.py`, `extract_images.py`, `render_pages.py`, `compare_transcriptions.py`, `check_tables.py`). Transcriptions are in `papers/audit/transcriptions/`, evidence crops in `papers/audit/images/`, raw check output in `checks_web.md` and `checks_scan.md`.
- **Page numbers:** `p.N` = page of the web PDF; `print p.N` = printed page number in the scan (Table 1 print p.52, Table 2 p.53, Figure 1 p.54, Tables 3–4 p.55, Tables 5–6 p.56, Table 7 p.57).

## Summary

| Audit | OK | CHECK | NOTE | FAIL |
|---|---|---|---|---|
| 1 Data | 4 | 4 | 0 | 0 |
| 2 Figures | 1 | 0 | 2 | 0 |
| 3 Labels and fonts | 0 | 0 | 8 | 0 |

No arithmetic failures. Four statements in the summary and conclusion do not match the tables exactly (D-05 to D-08); they may be loose wording rather than errors, so they are marked CHECK for a human decision.

## 1. Data audit

| ID | Level | Finding | Evidence |
|---|---|---|---|
| D-01 | OK | Tables 1, 2, 3, 4, 6 and 7 are **identical in the two copies**: 466 cells compared (Table 1 after re-ordering its columns, see L-04), 0 differences. | `transcriptions/web_*.json` vs `scan_*.json` |
| D-02 | OK | Table 1: each portfolio column sums to 100%, and the equity rows add up to the equity share in the header (50/65/80). | `checks_*.md` |
| D-03 | OK | Table 2: every "withdrawal enhancement" equals the ratio of the two printed rates minus 1, within rounding of the printed one-decimal rates (e.g. all-3-rules, 65%, 95% POS: 4.3 / 3.1 = +39%). The text's "increases the maximum initial withdrawal rate 30–43 percent" matches the "All 3" rows (30% to 43%). | Table 2 (web p.5, print p.53) |
| D-04 | OK | Tables 3 and 4: initial WD rate rises and purchasing power falls as the required success level falls. Tables 6 and 7: WD rate rises as the confidence standard falls from 99% to 90%, and every row's success rate and total purchasing power are at least the standard it is listed under. Table 6 single-equity 65/25/10 agrees with the Table 3 curve (e.g. 5.7% ↔ 97% success). | `checks_*.md` |
| D-05 | **CHECK** | **Table 6 vs Table 4, multi-class 65/25/10.** Table 6 (40 years, same portfolio and rules) says 5.5% gives 99% success and 5.8% gives 99%. Table 4 says 99% success is reached at 7.1%, and 100% success holds up to 6.3%. Gap 1.3–1.6 points. The single-equity pair (Table 3 vs Table 6) agrees within 0.1 point, so only the multi-class pair is inconsistent. Possible explanations: Table 4 and Table 6 use different assumptions that the text does not state, or one table has an error. | Table 4 (web p.10, print p.55), Table 6 (web p.12, print p.56) |
| D-06 | **CHECK** | Executive summary and conclusion: "5.2–5.6 percent are sustainable at the 99 percent confidence standard for portfolios containing at least 65 percent equities (40 years)". Table 6 has one row outside the range: single-equity 80/10/10 = **4.7%** (also 4.7% in Table 7). May be a loose summary of the multi-class and 65% rows. | Table 6 |
| D-07 | **CHECK** | Conclusion: "rise to 5.7–6.2 percent at the 95 percent confidence standard (40 years)". Table 6 has two rows outside: single-equity 80/10/10 = **5.6%**, multi-class 65/25/10 = **5.5%**. In the 30-year Table 7 all four rows are inside 5.7–6.2. | Table 6, Table 7 |
| D-08 | **CHECK** | Executive summary: "with 50 percent equities, maximum initial withdrawal rates drop to as low as 4.6 percent". Table 6 single-equity 50/40/10 at 99% is **4.5%** (the multi-class row is 4.6%). | Table 6 |

Not verifiable from the paper alone: the table values themselves (they come from a Monte Carlo model fed with 1973–2004 asset-class statistics that the paper does not reproduce); the "about 60 percent fewer freezes" and "20 percent fewer failures" statements in the text (Table 2 shows the freeze counts 6/7/8 vs 3/3/3, which is consistent with "about 60 percent fewer" but is only one table's evidence).

## 2. Figure audit

The only figure is Figure 1 "Decision Rule 'Guardrails'". Described blind, before reading the text: three roughly parallel curves rising to the right; the upper one (red in the web copy, orange in the print) is labelled "CAPITAL PRESERVATION RULE" and "Current WD Rate is 20% Above Initial WD Rate"; the lower one (green) is labelled "PROSPERITY RULE" and "Current WD Rate is 20% Below Initial WD Rate"; a blue dashed curve between them is labelled "Withdrawal Rule".

| ID | Level | Finding | Evidence |
|---|---|---|---|
| F-01 | OK | The figure matches the text (web p.7–8): capital preservation applies when the current rate is more than 20% above the initial rate, prosperity when more than 20% below, and the withdrawal rule governs in between. Both copies show the same figure. | `images/web/p09_1.png`, `images/scan/figure1.png` |
| F-02 | NOTE | Figure 1 has no axes, units or scale. It is a schematic; what the upward slope means is not stated. | same |
| F-03 | NOTE | Line colours differ between the copies (red vs orange). Rendering difference only. | same |

## 3. Label and font audit

| ID | Level | Finding | Evidence |
|---|---|---|---|
| L-01 | NOTE | **Table 7 is a 30-year table but its last column is headed "Year 40 PP%"** (both copies). Probably should read Year 30. | `images/web/p13_1.png`, `images/scan/table7.png` |
| L-02 | NOTE | Table 5 title is misspelled "Intitial" (both copies). | `images/web/p11_1.png`, `images/scan/table6.png` |
| L-03 | NOTE | **Copies differ in Table 2's footnotes.** The web copy has markers WD¹, POS², WR³ and a footnote line defining them; the print scan has no markers and no footnote line under Table 2 (bottom of the table and page checked). In print, "WD", "POS" and "WR" are not defined in the table; "WD" is not spelled out anywhere in the running text. | `images/scan/table2_bottom.png`, `images/web/p05_1.png` |
| L-04 | NOTE | Table 1 column order differs: web 50 / 65 / 80% equities, print **65 / 80 / 50%**. The values per label are identical. | `images/scan/table1.png`, `images/web/p03_1.png` |
| L-05 | NOTE | Table 6 header "Total PP%": the footnote marker is not readable in the scan at its resolution (the web copy shows ²; footnote 2 defines PP). Not verifiable in print. | `images/scan/table6_header.png` |
| L-06 | NOTE | **Wording differs between copies** (web text layer vs print): p.2 web "5.8 percent for a portfolio containing **50** percent equities", print "**65** percent equities"; web "is the current year's withdrawal is reduced" vs print "the current year's withdrawals are reduced"; web "maintains quite purchasing power" vs print "greater purchasing power". The print reads correctly. Not a full text diff: only these passages were compared. | `images/scan/scan_p2_left.png` (print p.51) |
| L-07 | NOTE | Fonts and legibility. Web copy: 8 fonts (Arial, Arial Bold/Italic/BoldItalic, HUNTEU+Arial, Tahoma, Verdana, ZapfDingbats), **none embedded**, so rendering depends on the viewer's fonts; tables are low-resolution bitmaps (about 555 px wide), footnote text is blurry but readable after upscaling. Scan: no fonts (images only), about 150 dpi, not searchable; table digits readable at 2.6x, superscripts are not (L-05). | `inventory_web.json`, `inventory_scan.json` |
| L-08 | NOTE | Table 5 ("Decision Rule Summary") lists four condition/action pairs without saying in which order they are tested or that the freeze depends on the withdrawal rate (the 2006 modification). It cannot settle the order of the withdrawal rule and the guardrails. | `images/web/p11_1.png` |

## What this audit cannot show
- It shows that the tables were transcribed consistently and that the paper is largely internally consistent. It cannot show the paper's results are right: their inputs are not in the paper.
- The vision model can misread digits. Here the web and print readings were made from different images and agree in all 466 cells, which is strong evidence for the digits but not proof; anything that matters should be confirmed against the images by a person.
- Only the passages named in L-06 were compared word by word between the copies. A complete text diff would need OCR of the scan.
