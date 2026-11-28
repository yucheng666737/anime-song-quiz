# tanime · 猜動漫歌 ♪

從 [AnimeThemes.moe](https://animethemes.moe) 開放資料庫即時抽題的動漫片頭／片尾曲（OP / ED）猜歌網頁遊戲，支援純靜態線上遊玩與本地伺服器執行。

🔗 **Live Demo（線上立即玩）：[https://woodycheng987.github.io/anime-song-quiz/](https://woodycheng987.github.io/anime-song-quiz/)**

---

## ✨ 功能特色（Features）

- **即時題庫與原生音訊串流**：串接 AnimeThemes 官方 GraphQL API（`https://graphql.animethemes.moe/`），免預先下載龐大題庫即可跨年份隨機抽題。
- **日文原名優先顯示**：動畫名稱、歌曲標題與演唱歌手皆優先顯示日文原名（`native`），揭曉答案時一併附上羅馬拼音方便對照。
- **年代快捷與自訂篩選**：
  - 支援 **1963 ～ 最新年份**自由區間設定，並內建「經典 ~90s」、「2000s」、「2010s」、「近五年新番」、「全部年份」一鍵快捷按鈕。
  - 支援三種難易度（簡單 3 選 1、普通 4 選 1、困難 6 選 1）與「僅限片頭 (OP)」篩選。
- **題庫條件分享連結（Deep Link）**：可點擊「🔗 複製目前題庫挑戰連結」產生帶有 `?from=...&to=...&diff=...&op=1` 的專屬網址，將相同題庫條件分享給朋友挑戰。
- **流暢操控與快捷鍵**：
  - **🔥 跳至副歌 (0:45)**：前奏聽不出來時，一鍵跳至 45 秒副歌精華段落。
  - **四階段無壓力提示**：年份、歌名、演唱歌手、動畫封面皆可按需點開提示。
  - **完整鍵盤快捷鍵**：`1`～`6` 選答案、`Space` 播放/暫停、`←` / `→` 倒退/快轉 10 秒、`C` 跳副歌、`H` 依序開提示、`N` 下一題/略過。
- **預載加速與本局歷程**：
  - 開局採用**雙年份並行抽題**縮短等待時間，並在作答時於**背景預熱下一首音檔**，按「下一題」零等待秒切。
  - 自動保存個人歷史「最高分 / 最高連對」與音量設定（`localStorage`），並於下方即時列出「📜 本局答題歷程」方便回顧找歌。

---

## 🚀 快速開始（Quick Start）

### 方式一：線上直接玩（推薦）
直接開啟 **[https://woodycheng987.github.io/anime-song-quiz/](https://woodycheng987.github.io/anime-song-quiz/)**，選擇年份範圍與難度後點擊 **「出題！」** 即可開始。

### 方式二：在電腦本地執行
1. 下載或 Clone 本專案：
   ```bash
   git clone https://github.com/woodycheng987/anime-song-quiz.git
   cd anime-song-quiz
   ```
2. **Windows 一鍵啟動**：雙擊 [播放遊戲.bat](./播放遊戲.bat)（會自動偵測系統中的 Python 啟動 [server.py](./server.py) 並開啟瀏覽器）。
3. **跨平台指令啟動**（避免瀏覽器 `file://` 跨網域或 Referrer 限制）：
   ```bash
   python server.py
   # 或使用任意靜態 HTTP 伺服器：
   python -m http.server 8080
   ```

---

## 📁 專案結構與金鑰安全對照表（Project Structure & Secret Safety）

本專案採用建置期設定生成機制，確保敏感設定或自訂代理端點不進入 Git 版控：

| 檔案路徑 | 版控狀態 | 用途與安全說明 |
| :--- | :---: | :--- |
| [index.html](./index.html) | ✅ Committed | 遊戲主程式（介面、GraphQL 抽題邏輯、音訊播放器與快捷鍵） |
| [config.example.js](./config.example.js) | ✅ Committed | 前端設定範本（僅含公開預設端點，不含任何私密金鑰） |
| `config.js` | 🚫 Gitignored | 本地或 CI 建置期動態產生的執行期設定檔（已列入 `.gitignore`） |
| [build-config.mjs](./build-config.mjs) | ✅ Committed | 零依賴 Node.js 建置腳本，從環境變數自動產生 `config.js` |
| [_headers](./_headers) | ✅ Committed | 靜態主機安全標頭（`nosniff`、`DENY`、`no-referrer` 等） |
| [server.py](./server.py) | ✅ Committed | 本地 Python 標準庫伺服器（含靜態白名單、`/graphql` 快取與 `/media` 安全代理） |
| [播放遊戲.bat](./播放遊戲.bat) | ✅ Committed | Windows 本地快速啟動批次檔 |
| [.github/workflows/deploy.yml](./.github/workflows/deploy.yml) | ✅ Committed | GitHub Pages 雙階段（`build` → `deploy`）自動部署工作流 |
| [.gitignore](./.gitignore) | ✅ Committed | 排除 `config.js`、`.env*`、`_site/` 與暫存檔 |

---

## 🛠️ 自架與自動化部署指南（Self-Hosting & CI/CD Deployment）

### 1. 本地自訂端點設定
若想在本地覆寫 API 端點或啟用本地音檔代理，可複製範本建立 `config.js`：
```bash
cp config.example.js config.js
```
或直接由 `build-config.mjs` 產生：
```bash
node build-config.mjs
```

### 2. GitHub Pages 自動部署（已內建）
本專案已配置 [.github/workflows/deploy.yml](./.github/workflows/deploy.yml)，將 `build` 與 `deploy` 拆分為兩個獨立 Job，每次推送至 `main` 分支（或手動觸發 `workflow_dispatch`）時自動打包 `index.html`、`config.js` 與 `_headers` 至 `_site/` 並部署至 GitHub Pages。

若日後需要透過環境變數注入自訂代理網址，可於 GitHub 儲存庫的 **Settings → Secrets and variables → Actions → Repository secrets** 新增以下選填變數（無須加引號或逗號，未設定時自動採用官方預設端點）：

| Secret Name | 必填 | 預設值 / 說明 |
| :--- | :---: | :--- |
| `APP_GRAPHQL_URL` | 選填 | 預設為 `https://graphql.animethemes.moe/` |
| `APP_API_BASE` | 選填 | 選填之備用 REST 代理網址（預設留空） |
| `APP_MEDIA_PROXY_URL` | 選填 | 選填之音檔串流代理前綴（預設留空，由 `<audio>` 直接串流） |

---

## 📜 資料來源與聲明

- 動畫資料、封面與音訊串流皆來自社群維護的開放資料庫 **[AnimeThemes.moe](https://animethemes.moe)**。
- 主題曲音訊與封面圖像之版權歸原動畫製作委員會、唱片公司與相關權利人所有，本專案僅供個人娛樂與技術展示用途。
