# papers/ 論文相關檔案

研究 Guyton & Klinger（2006）*Decision Rules and Maximum Initial Withdrawal Rates* 所用的所有資料，依用途分三個資料夾。這些檔案不是網站內容（網站不會發佈 `papers/`，除了被瀏覽器直接引用的檔案之外，其餘都只是專案內的研究與驗證紀錄）。

| 資料夾 | 放什麼 | 回答的問題 |
|---|---|---|
| `source/` | 論文本身：紙本掃描版 PDF（9 頁，*Journal of Financial Planning* 2006 年 3 月號，紙本頁碼 pp.50–58） | 原文是什麼？ |
| `audit/` | 對**論文本身**的視覺檢核：`report.md`（發現清單）、`transcriptions/`（表格轉錄 JSON，每個表格讀兩次）、`images/scan/`（證據圖片）、`checks_scan.md`、`inventory_scan.json`。由 `.claude/skills/paper-visual-audit/` 產生 | 論文的表格、圖、標籤有沒有被讀對、內部是否一致？ |
| `verification/` | 拿論文來檢查**我們的程式**：`paper_check.md`（規則逐條對照，附紙本頁碼）、`ref_simulator.py`（獨立驗算）、`order_sensitivity.py`（凍結與護欄檢定順序的差異） | 我們的網頁與 skill 有沒有照論文的規則算對？ |

## 怎麼用
- 想看某條規則的出處與驗證結果 → `verification/paper_check.md`。
- 想確認論文表格的數字與疑點 → `audit/report.md`（例如 Table 4 與 Table 6 的不一致）。
- 重新驗證程式 → `python3 .claude/skills/gk-withdrawal-schedule/scripts/verify.py`（會用到 `verification/ref_simulator.py`）。
- 頁碼一律是紙本頁碼：Table 1 p.52、Table 2 p.53、Figure 1 p.54、Tables 3–4 p.55、Tables 5–6 p.56、Table 7 p.57。
