# Checklist for the three audits

## 1. Data audit (tables)
- [ ] Every table crop rendered at 2-3x; one table per image; no row cut in half.
- [ ] Two independent transcription passes per table, per copy of the paper; `compare_transcriptions.py` run; every DIFF resolved by looking at the image again (never by averaging).
- [ ] Copy vs copy (e.g. web capture vs print scan) compared cell by cell.
- [ ] `check_tables.py` run: enhancement arithmetic, monotonic rates, success/purchasing-power vs the confidence standard, claims in the text vs the tables.
- [ ] Text numbers (executive summary, body, conclusion) compared with the tables; text-only numbers (e.g. "30-43 percent", "60 percent fewer freezes") traced to their table.
- [ ] Anything that cannot be reproduced from the paper alone is labelled "not verifiable" instead of "correct".

## 2. Figure audit
- [ ] Describe each figure **before** reading its caption or the text that refers to it (blind description): axes, lines, labels, direction of curves.
- [ ] Then compare the description with the specification in the text (for Figure 1: current withdrawal rate 20% above / below the initial rate, the capital preservation and prosperity rules, the withdrawal rule between them).
- [ ] Figure numbers, captions and in-text references agree; units and axis labels present.
- [ ] If the audited material includes our own charts: render a screenshot, then check axis units, legend, guardrail lines at initial rate x 1.2 and x 0.8, clipped values.

## 3. Label and font audit
- [ ] Table headers match the column content; units (%, PP%, years) present; footnote markers (1, 2, 3 ...) have matching footnotes and the same marker means the same thing everywhere.
- [ ] Every abbreviation (WD, POS, PP, WR, PMR, CPR, PR, IR) is defined at first use; the same abbreviation is not used for two things.
- [ ] Heading hierarchy and table/figure numbering consistent (Table 1 ... 7, Figure 1).
- [ ] `pdf_inventory.py`: fonts used, whether embedded, text layer present or scan; mixed fonts or missing glyphs (boxes, ligature loss) in extracted text.
- [ ] Legibility of the printed table text at the original size; low-resolution embedded images flagged.
- [ ] Differences in wording between copies (typos, changed numbers) listed with page and image evidence.

## Severity
- **FAIL** two numbers in the paper cannot both be right (arithmetic, ordering, a row violating the table's own rule).
- **CHECK** text and table disagree or wording is ambiguous; a human must decide (could be a loose summary, not an error).
- **NOTE** cosmetic: typos, label/footnote problems, low resolution.
- **OK** verified and consistent (state what was verified).
