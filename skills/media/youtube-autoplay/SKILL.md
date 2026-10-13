---
name: youtube-autoplay
description: 用 Chrome AppleScript 播放 YouTube 影片，自動計時關閉分頁
version: 3.0.0
author: Hermes Custom
---

# 🎬 YouTube 自動播放並關閉

## 觸發條件
用戶叫你「播放XXX」

## 完整工作流程（已驗證成功）

### 步驟 1：搜尋 YouTube URL
```
web_search query: "youtube 歌名" 或 "youtube 藝術家 歌名"
取第一個結果 URL
```

### 步驟 2：開 Chrome 並取得片長

**方法 A（推薦）：寫 AppleScript 檔案**
```python
# write_file /tmp/open_yt.scpt
content = '''tell application "Google Chrome"
    activate
    delay 1
    open location "https://www.youtube.com/watch?v=VIDEO_ID"
end tell'''
```

```bash
osascript /tmp/open_yt.scpt
```

**方法 B（直接 shell）：**
```bash
open -a "Google Chrome" "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 步驟 3：讀取片長
browser_snapshot 入面會顯示：
```
button "0 Minutes 0 Seconds of 3 Minutes 19 Seconds" [ref=e8]: 0:00 / 3:19
```
讀取 `3:19` 轉換為秒：`3 * 60 + 19 = 199`

### 步驟 4：建立自動關閉脚本並 Set Timer
```python
# write_file /tmp/close_tab.scpt
close_script = '''tell application "Google Chrome"
    close active tab of front window
end tell'''

# 計時後自動關閉（片長秒數 + 10秒緩衝）
# sleep [秒數] && osascript /tmp/close_tab.scpt &
```
⚠️ **唔需要等用戶確認！Timer 到了就自動關。**

### 步驟 5：提醒用戶
告知片長，已 set timer

## AppleScript 參考

**開 Chrome + YouTube（推薦寫檔案執行）：**
```applescript
-- /tmp/open_yt.scpt
tell application "Google Chrome"
    activate
    delay 1
    open location "https://www.youtube.com/watch?v=VIDEO_ID"
end tell
```
```bash
osascript /tmp/open_yt.scpt
```

**確認 Chrome 開到：**
```applescript
tell application "Google Chrome" to name of window 1
-- 返回分頁名稱，有 🔊 符號表示正在播放
```

**關閉當前分頁（寫檔案）：**
```applescript
-- /tmp/close_tab.scpt
tell application "Google Chrome"
    close active tab of front window
end tell
```
```bash
osascript /tmp/close_tab.scpt
```

## 注意事項
- **`open location` 係最穩妥嘅方法**，唔使用 `make new tab`（容易出 window 索引錯誤）
- browser tool 係另一個隔離嘅 browser，唔係你本機 Chrome
- 播放係靠 YouTube 預設行為（可能需要用戶撳 k），Chrome 視窗出現即係成功
- 🔊 符號表示片正在播放
