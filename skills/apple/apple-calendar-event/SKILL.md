---
name: apple-calendar-event
description: 在 macOS Apple Calendar 新增日程事件（適用於user）
---

# Apple Calendar 新增日程事件

## 觸發條件
user話「幫我加一個...日曆」、「加一個event」、「創建日程」

## 前置要求
- Calendar.app 必須喺運行中

## 流程

### 1. 確保 Calendar 運行
```python
import subprocess
subprocess.run(['open', '-a', 'Calendar'])
```

### 2. 用 Python 生成並執行 AppleScript
```python
#!/usr/bin/env python3
import subprocess
from datetime import datetime

def add_calendar_event(calendar_name, event_title, year, month, day, start_hour, start_min, duration_min=60):
    start = datetime(year, month, day, start_hour, start_min, 0)
    end = start + timedelta(minutes=duration_min)
    
    # 中文格式！呢個先work
    start_str = start.strftime("%Y年%m月%d日 下午%I:%M:%S")
    end_str = end.strftime("%Y年%m月%d日 下午%I:%M:%S")
    
    script = f'''
tell application "Calendar"
    tell calendar "{calendar_name}"
        make new event at end with properties {{summary:"{event_title}", start date:date "{start_str}", end date:date "{end_str}"}}
    end tell
end tell
'''
    with open('/tmp/add_event.applescript', 'w') as f:
        f.write(script)
    
    subprocess.run(['osascript', '/tmp/add_event.applescript'], capture_output=True, text=True)

add_calendar_event("Hermes", "去睇細B表演", 2026, 5, 1, 15, 0, 60)
```

## 注意事項

### 日期格式（重要！-trial and error 發現）
- ✅ 使用 **中文格式** `YYYY年MM月DD日 上午/下午H:MM:SS` — 例如 `2026年5月1日 下午3:00:00`、`2026年8月1日 上午10:00:00`
- ❌ `dd/mm/yyyy HH:MM:SS` 格式**唔work**，會報錯「無效的日期和時間」
- ❌ Python datetime `%d/%m/%Y %H:%M:%S` 格式**唔work**
- ❌ `May 1, 2026` 英文格式**唔work**
- ❌ 直接用 `osascript -e '...'` 單行指令，中文會引發 quote 問題

正確做法：
```python
def applescript_date(dt):
    ampm = '上午' if dt.hour < 12 else '下午'
    hour = dt.hour % 12 or 12
    return f'{dt.year}年{dt.month:02d}月{dt.day:02d}日 {ampm}{hour:02d}:{dt.minute:02d}:00'

start_str = applescript_date(start)
end_str = applescript_date(end)
# 注意：必須用中文 上午/下午 + 12小時制，上午事件（例如考試 10:00）不可硬寫「下午」。
```

### Calendar.app 必須運行
- 如果未運行，直接 `osascript` 會報錯 `應用程式不在執行中` (-600)
- 用 `open -a Calendar` 先確保佢運行

### AppleScript 寫入檔案再執行
-唔好嘗試用 `osascript -e '...'` 單行指令，中文同特殊字符會引發 quote 問題
- 寫入 .applescript 檔案再執行係最穩妥嘅方法

## 驗證
成功後會輸出 event id，例如：
```
event id D0A9F780-163F-4761-B73B-76C2AAF7A63C of calendar id 1479F399-DDD6-48FE-9BF5-F47E1898A710
```

## close_tab.scpt 預設內容
```applescript
tell application "Google Chrome"
    tell active tab of front window
        close
    end tell
end tell
```
