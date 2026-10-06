# Transcription format (one JSON file per table per reading pass)

File name: `<source>_<table>.json`, e.g. `scan_table6.json`, `web_table6.json`, `scan_table6_pass2.json`.
`source` is `scan`, `web`, or any label you use for a copy / reading pass.

```json
{
  "table": "Table 6",
  "source": "scan",
  "page": 7,
  "pass": 1,
  "columns": ["InitialWD", "SuccessRate", "Cuts", "Freezes", "Raises", "TotalPP", "Year40PP"],
  "rows": [
    { "label": "One Equity (S&P 500) | 50/40/10 | 99%",
      "values": { "InitialWD": 4.5, "SuccessRate": 100, "Cuts": 3, "Freezes": 7, "Raises": 7, "TotalPP": 100, "Year40PP": 108 } }
  ],
  "notes": ["anything unreadable or ambiguous goes here, with the cell it refers to"]
}
```

Rules for the transcriber (the vision model):
- Copy numbers exactly as printed. Percent signs are dropped (`3.6%` → `3.6`); `N/A` stays the string `"N/A"`.
- A cell you cannot read with confidence is `null` and gets a line in `notes`. **Never guess or "fix" a number**, even when it looks wrong; mismatches are the audit's findings.
- `label` is `group | row | sub-row`, separated by ` | `, in the order printed. The rows of one table must use identical labels in every pass, or the comparison cannot match them.
- Do the second pass **independently** (different crop or scale, do not look at pass 1), then run `compare_transcriptions.py`.

Column names used by `check_tables.py`:

| Table | Columns |
|---|---|
| Table 2 | `MaxWD_90POS`, `MaxWD_95POS`, `Enh_90POS`, `Enh_95POS`, `WRFreezes_95POS`; labels `<rule group> \| <allocation>` |
| Table 3, 4 | `InitialWD`, `Cuts`, `Raises`, `TotalPP`, `Year40PP`; labels `<rules used> \| <success level>` |
| Table 6, 7 | `InitialWD`, `SuccessRate`, `Cuts`, `Freezes`, `Raises`, `TotalPP`, `Year40PP`; labels `<One Equity (S&P 500) or Multi-Class Equities> \| <allocation> \| <confidence>%` |
