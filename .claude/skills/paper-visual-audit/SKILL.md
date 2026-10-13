---
name: paper-visual-audit
description: 以大型語言模型對研究論文 PDF 做視覺審核（表格資料、圖、標籤與字型）。當使用者想驗證論文的表格與數字、核對圖與內文是否一致、比對同一篇論文的兩份版本（例如網頁擷取 vs 紙本掃描）、檢查標籤／註腳／字型，或檢查我們的程式與網頁是否與論文一致時使用。流程：把頁面轉成圖片，讓視覺模型把表格轉錄兩次，再執行確定性的一致性檢查並寫出審核報告。為 papers/ 內的 Guyton & Klinger（2006）而建，也可用於任何論文 PDF。
---

# 論文視覺審核

目標：用模型看得到的頁面圖片，加上負責運算的腳本，找出論文的數字、圖與標籤是否**讀對了、彼此一致**。模型負責閱讀，腳本負責檢查。模型可能讀錯數字，所以任何東西都不能只讀一次就相信。

這個審核無法重新推導論文的結果（輸入資料通常不在論文裡）。它能證明的是：某張表被正確轉錄、表本身內部一致、內文的說法與表格相符、兩份版本相符，以及圖與標籤和內文相符。

## 設定（只需一次）

不需要 poppler。在專案根目錄：

```bash
python3 -m venv .venv-pdf
.venv-pdf/bin/pip install pypdf pypdfium2 pillow
```

用 `.venv-pdf/bin/python .claude/skills/paper-visual-audit/scripts/<script>.py` 執行腳本。
所有輸出放在 `papers/audit/`（`images/`、`transcriptions/`、`report.md`）。

## 工作流程

### 步驟 0. 盤點
對每一份版本執行 `pdf_inventory.py <pdf>`。它會告訴你：有文字層還是只有掃描、哪些頁面含有嵌入圖片（表格與圖常常是沒有可抽取文字的圖片），以及用了哪些字型、是否嵌入。每份版本各自決定：有文字層 → 直接搜尋；掃描或嵌入圖片 → 當成圖片來讀。
如果兩份 PDF 可能是同一篇論文，先比對標題、作者、頁首，再決定把它們當成兩個來源。

### 步驟 1. 轉成圖片
- 嵌入圖片：`extract_images.py <pdf> --out papers/audit/images/<copy> --upscale 2.5`（原始解析度，再放大）。
- 掃描檔／整頁：`render_pages.py <pdf> --out ... --pages 4,7 --scale 2.2`，再用 `--crop page:x0,y0,x1,y1:name`（頁面比例）切出每張表或圖。一張圖只放一張表，絕不切斷任何一列。
- 用 Read 工具打開每一張圖，讓模型真的看到它。

### 步驟 2. 資料審核（表格）
1. **轉錄**：把每張表轉錄成 `references/transcription_schema.md` 的 JSON 格式。數字照印刷的原樣抄；讀不清楚的格子填 `null` 並加註；絕不修正看起來有問題的數字（那是發現，不是要改的東西）。
2. **第二次獨立讀取**：從不同的裁切或縮放重讀，不要看第一次的結果。存成 `<source>_<table>_pass2.json`。
3. 用 `compare_transcriptions.py a.json b.json` 比對第一次與第二次，以及版本與版本之間。每個 DIFF 都要回頭看圖解決。
4. 執行 `check_tables.py papers/audit/transcriptions --source <copy>`，跑算術與一致性檢查（增幅 = 比率 − 1，在四捨五入誤差內；信心標準越低，比率越高；成功率與購買力要達到它所列的標準），並用表格檢驗內文的說法（摘要、本文、結論）。
5. 把只出現在內文的數字（「30-43 percent」、「60 percent fewer freezes」）追溯到某張表，追不到就標為「無法驗證」。

### 步驟 3. 圖的審核
1. **先看圖**，再讀說明文字或引用它的段落，並寫下盲測描述：座標軸、線條、標籤、什麼上升或下降。
2. 把描述與內文的規格比對（例如 Figure 1：護欄在初始提領率上下 20%，上方是保本，下方是繁榮，中間是提領規則）。
3. 檢查圖號、說明文字、內文引用、單位與座標軸標籤。
4. 若審核範圍包含我們自己的圖表，截圖（需要瀏覽器），用同樣方式檢查座標單位、圖例、參考線與被裁掉的值。

### 步驟 4. 標籤與字型審核
使用 `references/audit_checklist.md` 第 3 節：表頭與內容是否相符、單位、註腳符號與註腳內容、縮寫是否在首次出現時定義且只用於一種意思、表與圖的編號、`pdf_inventory.py` 回報的字型與嵌入情形、嵌入圖片的清晰度與解析度，以及各版本之間的用字差異。

### 步驟 5. 報告
依 `references/report_template.md` 寫 `papers/audit/report.md`。每一項發現都要有編號、等級（OK / NOTE / CHECK / FAIL）、版本與頁碼、讀到什麼、預期是什麼，以及證據圖片的路徑。明確寫出什麼是**無法驗證**的。

## 規則
- 當內文可能只是寫得寬鬆（例如「portfolios with at least 65 percent equities」），而某一列表格不同時，這是 **CHECK**（由人判斷），不是錯誤。要說明為什麼可能是有意的。
- 版本之間用字或數字不一致時，優先採用紙本掃描，不用網頁擷取，並說明每一個說法出自哪個版本。
- 引用你所讀版本的頁碼；網頁擷取與紙本的頁碼不同。
- 不要把視覺模型的讀取結果當成事實。兩次讀取一致、腳本檢查通過，才算達標；重要的內容要由人確認。
- 審核對程式與網站只讀不寫。若論文與我們的程式矛盾，只回報；修改程式是另一步，要使用者同意。

## 檔案
- `scripts/pdf_inventory.py`、`render_pages.py`、`extract_images.py`：檢查與轉圖。
- `scripts/compare_transcriptions.py`：逐格比對兩份轉錄。
- `scripts/check_tables.py`：為 Guyton & Klinger（2006）的 Table 2、6、7 寫的一致性檢查（用於其他論文時，要擴充 `claims()` 與各表檢查）。
- `references/transcription_schema.md`、`audit_checklist.md`、`report_template.md`。
