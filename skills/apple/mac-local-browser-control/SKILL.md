---
name: mac-local-browser-control
description: 控制本地 macOS 瀏覽器（Chrome/Edge/Safari）播放 YouTube 影片。當用戶話「喺我電腦播」、「控制我本地瀏覽器」時使用。
version: 1.0.0
author: Hermes Custom
---

# 控制本地 macOS 瀏覽器播放 YouTube

## 核心問題

Hermes Agent 默認嘅 browser_navigate 係雲端瀏覽器，聲音唔會行到你本地電腦。需要用 kimi-webbridge 或 AppleScript 控制你 macOS 本地瀏覽器。

## 🥇 首選方法：kimi-webbridge（推薦）

如果 kimi-webbridge daemon 係 running（`~/.kimi-webbridge/bin/kimi-webbridge status` 顯示 `running:true`），**優先使用 kimi-webbridge** 而非 AppleScript 方法。kimi-webbridge 唔需要 Accessibility 權限、支援 snapshot/click/fill 等完整操作，且 session 隔離做得更好。

詳見 `kimi-webbridge` skill。


## 工作流程

### 步驟 1：確定瀏覽器

唔同瀏覽器用唔同 AppleScript：

```applescript
-- Chrome
tell application "Google Chrome" to open location "URL"

-- Microsoft Edge  
tell application "Microsoft Edge" to open location "URL"

-- Safari
tell application "Safari" to open location "URL"
```

### 步驟 2：開 URL

```applescript
-- 寫 script 到 /tmp
tell application "BROWSER_NAME"
    activate
    delay 0.3
    open location "https://www.youtube.com/watch?v=VIDEO_ID"
end tell
```

### 步驟 3：播放（需要 Accessibility 權限）

YouTube 按 `k` 係 play/pause。

```applescript
tell application "Microsoft Edge"
    activate
    delay 1
    tell application "System Events"
        keystroke "k"
    end tell
end tell
```

## ⚠️ macOS 權限限制

### 問題
`System Events` 發送 keystroke 需要 **Accessibility 權限**，否則會報錯：
```
「System Events」發生錯誤：不允許以osascript傳送按鍵。 (1002)
```

### 解決方法
用戶需要手動開啟：
1. **System Settings** → **Privacy & Security** → **Accessibility**
2. 撳 **+** 添加
3. 搵並添加 **Terminal** 或相關 app
4. 打剔 ✅ 允許

### 暫時解決
如果用戶唔想設定權限，最簡單係叫佢自己去瀏覽器撳 `k` 或 `空格鍵` 播放。

## 查找瀏覽器 Script

### 檢查邊個瀏覽器有 YouTube 開緊：
```applescript
-- Chrome
tell application "Google Chrome" to tell front window to tell active tab to return title & " | " & URL

-- Edge
tell application "Microsoft Edge" to tell front window to tell active tab to return title & " | " & URL

-- Safari
tell application "Safari" to tell front document to return name & " | " & URL
```

## 重要：Browserbase 雲端瀏覽器 ≠ 本地 Chrome

`browser_navigate` / `browser_console` 係行喺 **Browserbase 雲端瀏覽器**，聲音唔會到你本地電腦，同時亦睇唔到你本地 Chrome 嘅內容。

**確認方法**：如果 user 話「冇播」，好可能係因為我哋喺Browserbase播，但user睇緊自己本地 Chrome。

**解決**：所有播放操作都必須用 AppleScript 行本地 Chrome。

## Chrome Apple Event JavaScript 權限

用戶開咗 `Chrome → View → Developer → Allow JavaScript from Apple Events` 之後，理论上可以喺 AppleScript 入面行 JavaScript，但 shell  escaping 問題令到呢個好難用：

```bash
# 呢個會失敗（escaping 衝突）
osascript -e 'tell application "Google Chrome" to do JavaScript "document.querySelector(\"video\").play()" in active tab of front window'
```

**建議替代方案**：叫 user 手动撳 `Space` 或 `k` 播放影片。

## Auto-Close Tab Timer

喺影片開始播放後，設定計時器自動刪除 tab：

```bash
# 片長秒數 + 5 秒緩衝
sleep 280 && osascript -e 'tell application "Google Chrome" to close active tab of front window'
```

## 完整工作流程（推薦）

1. `osascript -e 'tell application "Google Chrome" to open location "URL"'` — 開 URL
2. `osascript -e 'tell application "Google Chrome" to activate'` — 切換 focus 到 Chrome
3. 叫 user 撳 `Space` 或 `k` 播放
4. 計時後自動關閉：`sleep DURATION && osascript -e 'tell application "Google Chrome" to close active tab of front window'`

## 查找 YouTube 影片時長

用 browser_navigate 開 YouTube page 之後：
```javascript
document.querySelector('video')?.duration // 返回秒數（float）
```

但要注意：呢個係 Browserbase 入面嘅時長，搵到之後再用喺本地 Chrome 嘅計時器。

## 注意事項

- Chrome/Edge 可能同時開著多個 tab，要確認係邊個有 YouTube
- `open location` 會喺front window開新tab，唔會alert舊tab
- 如果 user 話「byejack」咁嘅名，要先 web_search 搵正確 video URL
- 權限問題係無解的，這是 macOS 安全限制，沒有 command-line 繞過方法
- **千其唔好依賴 browser_console/play() 來播放音樂** — 雲端瀏覽器冇聲到你本地電腦

## 附：macOS 本地 Web Server 注意事項

### Streamlit / Flask / FastAPI 等本地伺服器

macOS 上用 Python 3.14 時要注意 PATH 問題：

```
# streamlit 安裝到非標準位置
/Library/Frameworks/Python.framework/Versions/3.14/bin/streamlit

# 直接打 streamlit 會 command not found
# 要先 export PATH
export PATH="/Library/Frameworks/Python.framework/Versions/3.14/bin:$PATH"
streamlit run app.py
```

**實用做法**：每次起本地伺服器前，都行 `which streamlit` 確認有冇嘢，若空行就主動 export PATH。

### 驗證伺服器已啟動

```bash
curl -s --max-time 3 http://localhost:8501 | head -3
```

見到 HTML 輸出（如 `<!-- Copyright (c) Streamlit`）就係成功。

---

## 觸發條件

用戶話：
- 「喺我本地電腦播」
- 「控制我本地瀏覽器」
- 「打開 YouTube 播...」
- 「幫我開 localhost」
- 「起個 web server」
- 任何需要喺 local browser 睇片/聽歌的情況，或喺 local 起 web server 的情況

⚠️ **觸發後第一件事**：檢查 kimi-webbridge 有冇 running。如果 running，直接使用 kimi-webbridge（本 skill 只做 fallback 用）。
