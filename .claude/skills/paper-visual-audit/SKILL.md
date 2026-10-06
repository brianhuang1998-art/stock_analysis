---
name: paper-visual-audit
description: LLM-powered visual audit of a research paper PDF (data in tables, figures, labels and fonts). Use when the user wants to verify a paper's tables and numbers, check its figures against the text, compare two copies of a paper (e.g. a web capture vs a print scan), check labels/footnotes/fonts, or check that our code and web page agree with a paper. Renders pages to images, has the vision model transcribe tables twice, then runs deterministic consistency checks and writes an audit report. Built for Guyton & Klinger (2006) in papers/, usable for any paper PDF.
---

# Paper visual audit

Goal: find out whether a paper's numbers, figures and labels are **read correctly and consistent with each other**, using page images the model looks at, plus scripts that do the arithmetic. The model does the reading; scripts do the checking. A model can misread digits, so nothing is trusted from one pass.

This audit cannot re-derive a paper's results (their inputs are usually not in the paper). It can show that a table was transcribed correctly, that it is internally consistent, that the text's claims match the tables, that two copies agree, and that figures and labels match the text.

## Setup (once)

No poppler needed. From the project root:

```bash
python3 -m venv .venv-pdf
.venv-pdf/bin/pip install pypdf pypdfium2 pillow
```

Run the scripts with `.venv-pdf/bin/python .claude/skills/paper-visual-audit/scripts/<script>.py`.
Put all outputs in `papers/audit/` (`images/`, `transcriptions/`, `report.md`).

## Workflow

### Step 0. Inventory
`pdf_inventory.py <pdf>` for every copy. It says whether there is a text layer or only a scan, which pages carry embedded images (tables and figures are often pictures with no extractable text), and which fonts are used and embedded. Decide per copy: text layer → search it; scan or embedded picture → read it as an image.
If two PDFs may be the same paper, compare title, authors, page headers before treating them as two sources.

### Step 1. Render
- Embedded pictures: `extract_images.py <pdf> --out papers/audit/images/<copy> --upscale 2.5` (native resolution, upscaled).
- Scans / whole pages: `render_pages.py <pdf> --out ... --pages 4,7 --scale 2.2`, then cut each table or figure with `--crop page:x0,y0,x1,y1:name` (fractions of the page). One table per image, never cutting a row.
- Open each image with the Read tool so the model actually sees it.

### Step 2. Data audit (tables)
1. **Transcribe** each table into the JSON format in `references/transcription_schema.md`. Copy numbers exactly as printed; unreadable cell → `null` plus a note; never correct a number that looks wrong (that is a finding, not an edit).
2. **Second, independent pass**: re-read from a different crop or scale without looking at pass 1. Save as `<source>_<table>_pass2.json`.
3. `compare_transcriptions.py a.json b.json` for pass 1 vs pass 2, and for copy vs copy. Resolve each DIFF by looking at the image again.
4. `check_tables.py papers/audit/transcriptions --source <copy>` runs the arithmetic and consistency checks (enhancement = rate ratio − 1 within rounding; rates rise as the confidence standard falls; success rate and purchasing power meet the standard they are listed under) and tests the text's claims against the tables (summary, body, conclusion).
5. Trace text-only numbers ("30-43 percent", "60 percent fewer freezes") to a table or label them "not verifiable".

### Step 3. Figure audit
1. Look at the figure image **before** reading the caption or the paragraph that cites it, and write a blind description: axes, lines, labels, what increases or decreases.
2. Compare the description with the text's specification (e.g. Figure 1: guardrails at 20% above and below the initial withdrawal rate, capital preservation above, prosperity below, withdrawal rule between).
3. Check figure number, caption, in-text reference, units and axis labels.
4. If our own charts are part of the audit, take a screenshot (needs a browser) and check axis units, legend, reference lines and clipped values the same way.

### Step 4. Label and font audit
Use `references/audit_checklist.md` section 3: table headers vs content, units, footnote markers and their footnotes, abbreviations defined at first use and used for one thing only, numbering of tables and figures, fonts and embedding from `pdf_inventory.py`, legibility and resolution of embedded images, and wording differences between copies.

### Step 5. Report
Write `papers/audit/report.md` from `references/report_template.md`. Every finding has an ID, a level (OK / NOTE / CHECK / FAIL), the copy and page, what was read, what was expected, and the path of the evidence image. State plainly what is **not verifiable**.

## Rules
- A finding is a **CHECK** (a human decides), not an error, when the text may simply be loose ("portfolios with at least 65 percent equities") while a table row differs. Say why it might be intentional.
- Prefer the print scan over a web capture when copies disagree on wording or a number, and say which copy each statement comes from.
- Cite page numbers of the copy you read; web captures and print pages use different numbers.
- Do not present a vision-model reading as ground truth. Two passes agreeing and the scripts passing is the bar; a person confirms anything that matters.
- Keep the audit read-only with respect to the code and the website. If the paper contradicts our code, report it; fixing the code is a separate step the user approves.

## Files
- `scripts/pdf_inventory.py`, `render_pages.py`, `extract_images.py`: inspect and render.
- `scripts/compare_transcriptions.py`: cell-by-cell comparison of two transcriptions.
- `scripts/check_tables.py`: consistency checks written for Guyton & Klinger (2006) Tables 2, 6, 7 (extend `claims()` and the table checks for other papers).
- `references/transcription_schema.md`, `audit_checklist.md`, `report_template.md`.
