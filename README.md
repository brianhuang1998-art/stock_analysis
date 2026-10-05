# 股票網站架設

台股投資試算工具（交易損益、目標價、定期定額複利、加權平均成本等），用 GitHub Pages 架設的靜態網站。
上線網址：https://brianhuang1998-art.github.io/stock_analysis/home_page.html
（根目錄刻意不放 `index.html`，所以只輸入到 `/stock_analysis/` 會是 404，請用上面完整網址。其他頁面都能直接用檔名開啟。）

## 快速上手

| 我想要… | 做法 |
|---|---|
| 改網站內容並上線 | 改檔案 → `git add -A` → `git commit -m "更新內容"` → `git push`（見最下方「更新網站流程」） |
| 新增一個工具頁 | 見「新增一個工具頁（流程）」：複製 `_dev/template.html`，再到 `site-config.js` 登記一筆 |
| 改某個工具的名稱、說明、所屬分類 | 只改 `assets/js/site-config.js`，commit 時會自動同步到所有頁面 |
| 改配色、字體、版面 | 只改 `assets/css/styles.css`（配色變數在最上面） |
| 改手續費、證交稅、兩平價的算法 | 只改 `assets/js/trade_math.js`，個股、ETF、加權平均成本、目標%數四頁會一起套用 |
| 改頂部選單、頁尾、回到頂部 | 改 `assets/js/nav.js`（頁尾樣式在 `styles.css` 的 `.site-footer`） |
| 換 App 圖示或分頁圖示 | 換 `assets/icons/` 裡的檔案（尺寸見該資料夾說明） |

## 網站功能

- **頂部列**：品牌（點了回首頁）、麵包屑、「全部工具 ▾」合併成一列，固定在畫面上方；手機上只顯示「上一層 › 目前頁」。
- **搜尋工具**：按 `/` 或 Ctrl／⌘+K 開啟，輸入關鍵字即時篩選，Enter 前往第一筆。關鍵字來自 `site-config.js` 的 `keywords`。
- **頁尾**：右下角顯示「最後更新」時間，取自 GitHub 最新一筆 commit（台北時間），所以每次 push 後會自動更新。
- **回到頂部**：手機上捲動超過一段距離會出現浮動「↑」按鈕。
- **加到主畫面（PWA）**：iPhone 用 Safari 按分享鈕選「加入主畫面」；Android 用 Chrome 選單選「安裝應用程式」。之後會像 App 一樣全螢幕開啟，逛過的頁面離線也能開（網路優先，有網路時一律載入最新版）。
- **空狀態**：輸入不合法時結果區變灰並顯示說明（細節見下方「空狀態」）。
- **輸入記憶**：各計算頁的輸入內容存在瀏覽器 localStorage，重新整理後保留，不會上傳到任何地方。

## 資料夾結構

```
股票網站架設/
├── home_page.html             首頁（網站入口）
├── *.html                     其他網頁（放在最外層，網址才不會變）
├── manifest.json              PWA 設定（build 自動產生，不要手改）
├── sw.js                      離線快取（必須放最外層才管得到整個網站）
├── sitemap.xml                給 Google 的網站地圖（build 自動產生）
├── .gitignore                 git 忽略清單
├── README.md                  這份說明
├── assets/                    網頁會載入的資源
│   ├── css/styles.css         全站樣式
│   ├── js/                    全站與各頁共用的程式
│   │   ├── site-config.js     全站設定（頁面、分類、工具清單）
│   │   ├── nav.js             選單、搜尋、頁尾、回到頂部
│   │   ├── util.js            共用小工具（儲存、格式、複製）
│   │   ├── stepper.js         數字欄位 ▲▼ 與點擊全選
│   │   ├── trade_math.js      交易計算（手續費、證交稅、兩平價）
│   │   └── calc.js            個股／ETF 試算頁的畫面邏輯
│   └── icons/                 favicon 與 App 圖示
├── _dev/                      開發用，不會公開（底線開頭的資料夾 GitHub Pages 不發佈）
│   ├── build.py               依 site-config.js 重新產生各頁共用部分
│   └── template.html          新增頁面用的範本
└── .githooks/pre-commit       commit 前自動執行 build
```

## 檔案說明

### 網頁（最外層）

| 檔案 | 用途 |
|---|---|
| `home_page.html` | 真正的首頁內容，網站入口，四張分類卡片（試算工具、交易與部位管理、估值與基本面分析、股息與現金流規劃）由 `build.py` 產生 |
| `tools.html` | 試算工具列表頁，列出目前提供的四個試算工具（ETF、個股、目標%數、加權平均成本法），卡片由 `build.py` 產生 |
| `etf_calculator.html` | ETF 損益試算機。可選 ETF 類型（股票型／債券型／主動式），自動帶入對應證交稅率 |
| `stock_calculator.html` | 個股損益試算機。稅率預設一般交易 0.3%、現股當沖 0.15% |
| `target_price_calculator.html` | 目標%數試算機。輸入價格並選擇個股／ETF，即時算出漲跌 1%～30%（含 21-24% 區間）各百分比對應的目標價，並依升降單位調整成可掛單價格 |
| `avg_cost_calculator.html` | 加權平均成本法試算機（放在「試算工具」分類下）。可新增／刪除多筆買進紀錄，算出加權平均成本、逐筆明細、損益兩平價與可掛單價、淨損益（手續費原價 vs 目前折數），附損益兩平進度條、即時註解與「複製結果」。商品類型（個股／股票型 ETF／債券型 ETF／自訂）決定證交稅率。計算使用 `trade_math.js` |
| `trading_position.html` | 交易與部位管理分類頁。「定期定額複利試算」已上線，部位大小、停損停利比、再平衡等仍為開發中 |
| `dca_calculator.html` | 定期定額複利試算機。輸入期初本金、每月扣款、預期年化報酬率與年數（1～100 年整數），算出累積投入、期末資產、報酬與逐年明細；輸入不合理時顯示紅字提示、結果區變灰並顯示說明。結果下方有「資產成長圖」（累積投入 vs 期末資產折線圖，滑鼠移上去或手機點一下會顯示該年數字，純 SVG、不依賴外部套件）。右欄附定期定額觀念與計算假設說明。計算腳本與圖表都寫在頁面內，儲存與格式使用 `util.js` |
| `valuation_analysis.html` | 估值與基本面分析分類頁，列出本益比河流圖、DDM、DCF、ROE 杜邦拆解等分析工具（開發中） |
| `dividend_cashflow.html` | 股息與現金流規劃分類頁，列出月配息現金流月曆、股利稅務、退休提領試算等工具（開發中） |

### 全域設定與共用程式（`assets/`，改一處，全站套用）

| 檔案 | 用途 |
|---|---|
| `assets/js/site-config.js` | **全站設定的唯一來源**：站名、網址、主題色、分類、每個工具的名稱／網址／圖示／說明／搜尋關鍵字、哪些是「開發中」。頂部選單、搜尋、麵包屑、頁面標題、說明文字、分享預覽、分類頁與首頁的卡片、離線快取清單，全都從這份產生。注意 `self.SITE =` 後面必須是嚴格 JSON（雙引號、不能有註解或結尾逗號），因為 `_dev/build.py` 要讀它 |
| `assets/css/styles.css` | 全部頁面共用的樣式（配色變數在檔案最上面），改版面風格只要改這一個檔案。各頁共用或專屬的規則放在檔案後半，頁面本身不再有 `<style>` |
| `assets/js/nav.js` | 每頁共用的外殼：「全部工具 ▾」下拉選單附搜尋框（按 `/` 或 Ctrl／⌘+K 開啟，Enter 前往第一筆，方向鍵選取）、頁尾（右下角顯示最後更新時間）、手機浮動「回到頂部」按鈕、註冊離線快取。頁尾的「最後更新」是用 GitHub API 讀取這個 repo 最新一筆 commit 的時間（台北時間），快取 10 分鐘，讀不到時退回檔案修改時間 |
| `assets/js/util.js` | 共用小工具 `Util`：`Util.store`（安全的 localStorage）、`Util.fmt`（金額／價格／百分比格式）、`Util.copyText`（複製並顯示「已複製 ✓」）。放在頁首，頁面腳本可直接用 |
| `assets/js/stepper.js` | 所有數字欄位（`.input-wrap` 內的 `type="number"`，之後動態新增的也算）自動套用：①較大的 ▲▼ 按鈕、②點到或聚焦時全選數字。新欄位不用再寫 `onfocus` |
| `assets/js/trade_math.js` | 共用的交易計算（手續費、證交稅、淨損益、損益兩平價、升降單位與可掛單價），個股、ETF、加權平均成本、目標%數四頁都使用這份，改公式只要改這一個檔案 |
| `assets/js/calc.js` | 個股、ETF 兩個試算頁的畫面邏輯（讀取輸入、顯示結果、進度條、註解、複製結果），計算本身呼叫 `trade_math.js`，所以頁面要先載入 `trade_math.js` |
| `assets/icons/favicon.svg` | 瀏覽器分頁圖示 |
| `assets/icons/icon-192.png`、`icon-512.png`、`icon-maskable-512.png`、`apple-touch-icon.png` | App 圖示（綠底「B」）；maskable 版留了安全邊距給 Android 裁切，apple-touch-icon 給 iPhone 用 |

### 自動產生的檔案（不要手改）

| 檔案 | 用途 |
|---|---|
| `manifest.json` | PWA 設定（加到主畫面用），由 `build.py` 依 `site-config.js` 產生 |
| `sitemap.xml` | 給 Google 的網站地圖，由 `build.py` 產生 |
| 各頁 `<!-- BUILD:XXX -->` 標記之間的內容 | 頁首標籤與標題（`HEAD`）、頂部列與麵包屑（`TOPBAR`）、工具卡片（`CARDS`）、結尾腳本（`TAIL`），由 `build.py` 產生；標記以外手寫的內容不會被動到 |

### 開發與離線

| 檔案 | 用途 |
|---|---|
| `sw.js` | Service worker：網路優先、離線時用快取。頁面清單讀自 `site-config.js`，新增頁面會自動被快取。只在 https／localhost 生效，由 `nav.js` 註冊。必須放在最外層，否則管不到整個網站 |
| `_dev/build.py` | 讀取 `site-config.js`，重新產生上表的自動產生內容。發現有 html 沒登記到設定檔，會印出警告 |
| `_dev/template.html` | 新增頁面用的範本，已包含輸入欄、結果卡、空狀態、儲存輸入的寫法。放在 `_dev/` 底下不會公開，也不會被 build 處理 |
| `.githooks/pre-commit` | commit 前自動執行 `_dev/build.py` 並把結果一起提交；有 html 沒登記就擋下 commit |
| `.gitignore` | 告訴 git 忽略哪些檔案（`.DS_Store`、Python 暫存檔等），不影響網站 |

## 新增一個工具頁（流程）

1. 複製 `_dev/template.html` 到**最外層**，改成新檔名（例如 `rebalance_calculator.html`），改標題、輸入欄與計算。
2. 在 `assets/js/site-config.js` 對應分類的 `tools` 加一筆（`title`、`href`、`icon`、`desc`、`keywords`）。如果原本是「開發中」的佔位項目，把 `"soon": true` 拿掉並補上 `href` 即可。
3. commit 時會自動執行 `python3 _dev/build.py`（也可以手動先跑一次預覽）：頁面標題、說明、分享預覽、頂部列與麵包屑、分類頁卡片、sitemap 都會自動補好。選單、搜尋和離線快取不需要 build，直接讀設定檔。
4. 照「更新網站流程」上傳。

新增分類頁：複製一個現有分類頁（例如 `tools.html`），在 `site-config.js` 的 `categories` 加一筆，再執行 build。

頁面標題格式由 `build.py` 統一產生：首頁 `Brian工具箱`、分類頁 `分類 | Brian工具箱`、工具頁 `頁名 - 分類 | Brian工具箱`。

頁面間的導覽路徑：

- `首頁 → 試算工具 → ETF 試算 / 個股試算 / 目標%數試算 / 加權平均成本法試算`
- `首頁 → 交易與部位管理 → 定期定額複利試算`
- `首頁 → 估值與基本面分析 / 股息與現金流規劃`（這兩個分類頁目前都還是開發中的佔位卡片）

每頁頂端的麵包屑（例如 `🏠 首頁 › 試算工具 › ETF 試算`）每一層都能點擊，目前所在頁面以白色粗體顯示（`styles.css` 的 `.crumbs a.here`）。頂部列左側的「Brian工作室」可以點，回到首頁；麵包屑與全部工具選單都在同一列、固定在畫面上方（手機上只顯示「上一層 › 目前頁」）。

## 計算邏輯摘要（`assets/js/trade_math.js`）

- 成交金額 = 價格 × 股數，不先四捨五入（所有頁面一致）
- 手續費 = 成交金額 × 0.1425%（券商牌價）× 折數，未達低消以低消計，小數點無條件捨去（捨去前加極小容差，避免浮點數誤差少算 1 元）
- 證交稅：個股一般交易 0.3%、當沖 0.15%；股票型 ETF 一般交易與當沖都是 0.1%；債券型 ETF 免稅（當沖減半與債券 ETF 免稅都是有期限的優惠）
- 損益兩平價：以 0.01 元為單位逐一試價，找出賣出淨得 ≥ 買進總成本的最低賣價（已含低消與捨去的影響）
- 可掛單價：把兩平價依升降單位往上調整到第一個可以下單的價格
- 基準：個股、ETF、加權平均成本三頁的兩平價、報酬率、總成本都以手續費原價（10 折）計算，只有「淨損益」的「目前 X 折」欄使用折扣後的手續費
- 頁面上的「證交稅率」欄位選了類別後會自動帶入，但仍可手動覆蓋（例如遇到 `00981A` 這類新掛牌、分類不確定的 ETF，需自行查證後填入正確稅率）

## 計算邏輯摘要（`dca_calculator.html`）

- 月報酬率 = (1 + 年化報酬率)^(1/12) − 1，每月複利 12 次剛好等於年化報酬率
- 假設每月月底扣款，期初本金與每月扣款都用相同報酬率成長
- 未計入手續費、ETF 內扣費用、通貨膨脹與市場波動

## 空狀態

輸入不合法（或沒有任何有效買進紀錄）時，結果卡片會加上 `is-empty`：數字區變灰並顯示一行說明（`styles.css` 的 `.empty-hint`、`.card.is-empty`）。新頁面只要在結果卡片放 `<p class="empty-hint">…</p>`，並在驗證失敗時對該卡片 toggle `is-empty` 即可。

## 計算邏輯摘要（`avg_cost_calculator.html`）

- 每筆買進成本 = 價格 × 股數 + 手續費（每筆分開算）；加權平均成本 = 總買進成本 ÷ 總股數
- 淨損益 = 以現價全部賣出、扣除賣出手續費與證交稅後的淨得 − 總買進成本；「目前 X 折」欄把買賣手續費都改用你的折數重算
- 可掛單價在商品類型選「自訂」時不顯示（不確定該用個股還是 ETF 的升降單位）
- 輸入內容存在瀏覽器 localStorage，重新整理後仍會保留

## 更新網站流程

改完任何檔案後，在這個資料夾內執行：

```bash
git add -A
git commit -m "更新內容"
git push
```

commit 時會自動執行 `_dev/build.py`（`.githooks/pre-commit`），把頁面的共用部分依 `site-config.js` 重新產生並一起提交；如果有 html 沒登記到 `site-config.js`，commit 會被擋下並說明原因。

**第一次在新電腦 clone 這個專案時**，要執行一次 `git config core.hooksPath .githooks` 才會啟用這個自動步驟（git 的設定不會跟著 repo 走）。

push 完約 1 分鐘後 GitHub Pages 會自動部署新版本，網址不會變。
