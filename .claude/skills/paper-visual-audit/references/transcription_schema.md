# 轉錄格式（每張表、每次讀取一個 JSON 檔）

檔名：`<source>_<table>.json`，例如 `scan_table6.json`、`web_table6.json`、`scan_table6_pass2.json`。
`source` 是 `scan`、`web`，或任何你用來標示版本／讀取次數的標籤。

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
  "notes": ["讀不清楚或有歧義的內容寫在這裡，並註明指的是哪一格"]
}
```

轉錄者（視覺模型）的規則：
- 數字照印刷的原樣抄。百分號省略（`3.6%` → `3.6`）；`N/A` 保持字串 `"N/A"`。
- 沒把握讀清楚的格子填 `null`，並在 `notes` 加一行。**絕不猜測或「修正」數字**，即使它看起來有問題；對不上的地方正是審核的發現。
- `label` 是 `組別 | 列 | 子列`，以 ` | ` 分隔，順序依印刷順序。同一張表的各列，在每一次讀取中必須使用完全相同的標籤，否則比對時無法配對。
- 第二次讀取要**獨立**（不同的裁切或縮放，不要看第一次的結果），然後執行 `compare_transcriptions.py`。

`check_tables.py` 使用的欄名：

| 表 | 欄 |
|---|---|
| Table 2 | `MaxWD_90POS`、`MaxWD_95POS`、`Enh_90POS`、`Enh_95POS`、`WRFreezes_95POS`；標籤 `<規則組別> \| <配置>` |
| Table 3、4 | `InitialWD`、`Cuts`、`Raises`、`TotalPP`、`Year40PP`；標籤 `<使用的規則> \| <成功率水準>` |
| Table 6、7 | `InitialWD`、`SuccessRate`、`Cuts`、`Freezes`、`Raises`、`TotalPP`、`Year40PP`；標籤 `<One Equity (S&P 500) 或 Multi-Class Equities> \| <配置> \| <信心標準>%` |
