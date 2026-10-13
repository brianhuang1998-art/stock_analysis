# 類別與理由

定義在 `../rules.json`；第一個符合的類別勝出。

| id | 資料夾 | 樣式 | 為什麼放這裡 |
|---|---|---|---|
| skill | `.claude/skills/<name>/` | `SKILL.md` | Claude Code 只會在這個資料夾找 skill。skill 自己的 `scripts/` 與 `references/` 留在裡面。 |
| paper-source | `papers/source/` | `*.pdf` | 論文本身。 |
| paper-transcription | `papers/audit/transcriptions/` | `scan_table*.json`、`*_pass2.json`、`transcription*.json` | paper-visual-audit skill 的輸出：從掃描檔讀兩次的表格。 |
| paper-audit | `papers/audit/` | `checks_*.md`、`inventory_*.json`、`audit_report*.md` | 針對論文本身的報告與檢查結果。 |
| paper-verification | `papers/verification/` | `paper_check*.md`、`ref_simulator*.py`、`*sensitivity*.py`、`*_vs_paper*.md` | 用論文來檢查**我們的**網站與 skill 的資料。 |
| global-config | `config/` | `site-config.*`、`*.config.json`、`*.config.js`、`config.json`、`settings.json`、`*.toml` | 全站設定：只放一處，其他都由它產生。 |
| dev-tool | `_dev/` | `build*.py`、`template*.html`、`*.template.html` | 建置網站用的工具；資料夾名稱以 `_` 開頭，所以 GitHub Pages 不會發布它。 |
| site-style / site-script / site-icon | `assets/css/`、`assets/js/`、`assets/icons/` | `*.css`、`*.js`、`*.svg`、`*.ico` | 頁面會載入的檔案。 |
| site-page | 專案根目錄 | `*.html` | 頁面的網址就是檔名；搬動會弄壞連結與書籤。 |

## 固定位置（永不搬動）
| 檔案 | 為什麼必須留著 |
|---|---|
| `README.md`（任何資料夾）、`.gitignore`、`.nojekyll`、`CLAUDE.md` | git、GitHub 與 Claude Code 的慣例。 |
| `manifest.json`、`sitemap.xml` | 由 `_dev/build.py` 產生在根目錄；瀏覽器與搜尋引擎預期它們在那裡。 |
| `sw.js` | service worker 只能控制它所在的資料夾，所以必須放在根目錄。 |
| `.githooks/*`、`.claude/settings*.json` | git 與 Claude Code 會從這些路徑讀取。 |

## 容器
位於 `assets/`、`papers/`、`config/`、`_dev/`、`.claude/skills/` 或 `.githooks/` 內、且不符合任何規則的檔案，視為已放在正確位置（例如 `papers/audit/images/` 底下的審核圖片）。位於所有容器之外、又不符合任何規則的檔案，會被判為 UNCLASSIFIED。
