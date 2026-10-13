---
name: organize-files
description: 把這個專案的每個新檔案放進正確的資料夾（Claude Code skill、論文檔案、全域設定、網站頁面、資源檔、開發工具），回報放錯位置的檔案，並在不弄壞引用的情況下搬移。只要在這個專案裡即將建立、儲存、產生、下載或搬移檔案，使用者說他加了檔案，或被要求整理或檢查資料夾結構時就使用。它執行依 rules.json 規則運作的腳本，所以檔案該放哪裡由規則決定，不靠猜測。
---

# 整理檔案

檔案該放哪裡由 `rules.json` 決定，由 `scripts/organize.py` 執行。不要憑感覺決定，也不要手動搬檔：搬動檔案時，所有指向它的地方也必須一併修正。

## 資料夾（摘要）
| 檔案類型 | 放到 |
|---|---|
| Claude Code skill（`SKILL.md` 及其腳本與參考資料） | `.claude/skills/<skill-name>/`（Claude Code 只會在這裡找 skill） |
| 論文 PDF | `papers/source/` |
| 論文的表格轉錄 | `papers/audit/transcriptions/` |
| 論文審核報告、檢查輸出、檔案清單 | `papers/audit/` |
| 論文與我們程式的對照：比對說明、模擬器、分析 | `papers/verification/` |
| 全域（全站）設定，例如 `site-config.js` | `config/` |
| 網站頁面（`*.html`） | 專案根目錄（頁面的網址就是檔名，所以不能移動） |
| 網站樣式／腳本／圖示 | `assets/css/`、`assets/js/`、`assets/icons/` |
| 網站開發工具（`build*.py`、模板） | `_dev/` |
| 留在原位（必須在那個位置才有作用） | `README.md`、`.gitignore`、`manifest.json`、`sw.js`、`sitemap.xml`、`.githooks/*`、`.claude/settings*.json` |

完整清單與理由：`references/categories.md`。

## 建立檔案時
1. **儲存之前**，先問它該放哪裡：
   ```bash
   python3 .claude/skills/organize-files/scripts/organize.py where <檔名> [--skill <skill-name>]
   ```
   存到它印出的資料夾。新 skill 要建立 `.claude/skills/<skill-name>/SKILL.md`（用 `--skill` 指定名稱）。
2. **一批修改之後**執行 `python3 .claude/skills/organize-files/scripts/organize.py check`。它會列出放錯位置的檔案、無法分類的檔案，以及沒有 `SKILL.md` 的 skill 資料夾。
3. 若有放錯位置的，先看搬移計畫，再搬：
   ```bash
   python3 .claude/skills/organize-files/scripts/organize.py apply        # 試跑：只顯示會搬什麼
   python3 .claude/skills/organize-files/scripts/organize.py apply --yes  # 實際搬移（已追蹤的檔案用 git mv），並改寫完全相符的路徑引用
   ```
4. 搬完後，搜尋檔名，找出腳本無法改寫的引用（用片段組成的路徑，例如 `ROOT / 'assets' / 'js'`），修正它們；若搬動了頁面或全域設定，要執行 `python3 _dev/build.py`。接著執行專案的檢查。

## 腳本回報 UNCLASSIFIED 時
沒有任何規則符合這個檔案。**要問使用者**它屬於哪一類，不要猜。然後在 `rules.json` 加一條規則（一個含 `match` 樣式與 `dest` 的類別），讓下一個同類檔案自動放對位置，並更新 `README.md` 中的資料夾結構。

## 新增一種資料夾時
把資料夾加到 `rules.json` 的 `containers`，並加一個類別，再更新 `README.md`（資料夾樹與檔案表）；若在 `papers/` 底下，也要更新 `papers/README.md`。

## 腳本遵守的規則
- 固定位置的檔案（pinned）永遠不搬。`.claude/skills/` 內的檔案不論檔名為何，都不會被搬出它所屬的 skill。
- 不覆蓋、不刪除任何東西：若目的地已有同名檔案，這次搬移會被略過並回報。
- 除非加上 `--yes`，否則 `apply` 只是試跑。
- 已追蹤的檔案用 `git mv` 搬移，所以歷史紀錄會保留。
- 文字檔中只改寫完整的路徑字串；只是包含舊名稱的較長路徑不會被動到。

## 限制
- skill 無法監看檔案系統。它在 Claude 即將建立或搬移檔案時、被要求時執行，另外 pre-commit hook 會印出警告（絕不會擋下 commit）。使用者手動放進來的檔案，會在 `check` 或下一次 commit 時被發現。
- 分類依據是檔名與副檔名。同樣的檔名放在錯誤的情境（例如不是論文轉錄的 `.json`）會被回報為無法分類，而不是猜測。

## 檢查工具本身
`python3 .claude/skills/organize-files/scripts/selftest.py` 會建立一個用完即丟的專案，檢查分類、試跑、衝突處理與引用改寫。
