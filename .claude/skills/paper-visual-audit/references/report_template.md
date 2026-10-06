# Visual audit report: <paper>

- Audited copies: <file names, pages, kind (scan / text layer)>
- Date / model used for reading the images: <...>
- Method: images rendered with pypdfium2 at <scale>x; tables transcribed in <n> independent passes; scripts: compare_transcriptions.py, check_tables.py, pdf_inventory.py

## Summary
| Audit | OK | CHECK | FAIL | NOTE | Not verifiable |
|---|---|---|---|---|---|
| 1 Data | | | | | |
| 2 Figures | | | | | |
| 3 Labels and fonts | | | | | |

## Findings
For each finding: ID, level, location (copy, page, table/figure, row/column), what was read, what was expected, evidence image path, status (needs human confirmation / resolved).

## What this audit cannot show
- It checks whether the paper is internally consistent and was transcribed correctly. It cannot re-derive the paper's results (the inputs, e.g. 1973-2004 asset-class statistics, are not in the paper).
- A vision model can misread digits; every number that matters was read at least twice and any disagreement resolved against the image by a person.
