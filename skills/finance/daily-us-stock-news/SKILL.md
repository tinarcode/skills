---
name: daily-us-stock-news
description: "當用戶說「幫我搵下今日最新美股消息」或類似觸發句時，自動執行超詳細美股即日分析。使用 Brave + Tavily 交叉驗證 + 富途實時數據 + 富途期權鏈數據，所有資訊必須附上來源連結。"
version: 3.0.0
author: Hermes Custom
tags: [finance, us-stocks, day-trading, options, market-analysis, futu-api]
---

# 📊 美股即市深度分析（每日超詳細版）
## ✨ 升級版：結合富途實時數據 + 期權鏈數據

## 觸發條件

用戶說：
- 「幫我搵下今日最新美股消息」
- 「今日美股點睇」
- 「幫我分析今日大市」
- 「美股即日分析」
- 任何要求即市美股分析的需求

---

## 📡 富途實時數據獲取（優先執行）

在搜尋之前，先用富途 API 獲取即時市場數據：

### 0. 市場狀態（確認是否開市）
```bash
python3 skills/futuapi/scripts/quote/get_market_state.py US.SPY US.QQQ US.NVDA US.AAPL US.MSFT US.GOOG --json
```

**市場狀態值解讀：**
| 狀態值 | 含義 | 是否在交易 |
|--------|------|-----------|
| `MORNING` / `AFTERNOON` | 盤中（正常交易時段） | ✅ 是 |
| `PRE_MARKET` | 盤前 | ⚠️ 準備中 |
| `AFTER_HOURS` | 盤後 | ⚠️ 已收盤 |
| `OVERNIGHT` | 期貨/ETF 盤後交易 | ⚠️ 已收盤 |
| `CLOSED` | 停止交易 | ❌ 否 |

> 美股常規交易時段：美東 9:30-16:00（香港時間 21:30-04:00）

### 1. 即時報價快照（科技巨頭 + 寬指）
```bash
python3 skills/futuapi/scripts/quote/get_snapshot.py US.SPY US.QQQ US.NVDA US.AAPL US.MSFT US.GOOG US.TSLA US.META US.AMD US.QCOM --json
```

### 2. 資金流向（主要寬指）
```bash
# 注意：每個 code 必須分開執行，get_capital_flow.py 只接受一個代碼
python3 skills/futuapi/scripts/quote/get_capital_flow.py US.SPY --json
python3 skills/futuapi/scripts/quote/get_capital_flow.py US.QQQ --json
```

### 3. 期貨市場（貴金屬、能源）
```bash
# 黃金期貨（GCmain）、WTI原油期貨（CLmain）
# ⚠️ 注意：期貨市場需要額外行情權限，若返回"行情权限不足"請跳過此步
python3 skills/futuapi/scripts/quote/get_snapshot.py US.GCmain US.CLmain --json
```

### 4. 市場板塊資金分佈
```bash
python3 skills/futuapi/scripts/quote/get_capital_distribution.py US.SPY --json
```

### 5. 期權到期日查詢（熱門股票）
```bash
python3 skills/futuapi/scripts/quote/get_option_expiration_date.py US.NVDA --json
python3 skills/futuapi/scripts/quote/get_option_expiration_date.py US.AAPL --json
python3 skills/futuapi/scripts/quote/get_option_expiration_date.py US.SPY --json
```

### 6. 期權鏈查詢（重要！必須執行）
```bash
# NVDA 期權鏈（AI晶片領導者，適合期權交易）
python3 skills/futuapi/scripts/quote/get_option_chain.py US.NVDA --start 2026-05-05 --end 2026-05-16 --json

# AAPL 期權鏈（藍籌股，流動性高）
python3 skills/futuapi/scripts/quote/get_option_chain.py US.AAPL --start 2026-05-05 --end 2026-05-16 --json

# SPY 期權鏈（標普500ETF，大盤宏觀操作）
python3 skills/futuapi/scripts/quote/get_option_chain.py US.SPY --start 2026-05-05 --end 2026-05-16 --json

# QQQ 期權鏈（納指ETF，科技股操作）
python3 skills/futuapi/scripts/quote/get_option_chain.py US.QQQ --start 2026-05-05 --end 2026-05-16 --json
```

> ⚠️ 期權鏈數據包含：行使價、到期日、Call/Put、成交量、未平倉合約、引伸波幅（IV）等
> 將以上數據存入變量，在輸出格式的「期權數據」環節使用

---

## 🔍 搜尋流程（優先級：Tavily > MiniMax MCP > Brave）

### 重要原則
1. **Tavily 優先** — 所有搜尋第一時間用 Tavily
2. **交叉驗證** — MiniMax MCP 和 Brave 用於補充 Tavily 找不到的資訊
3. **每個資訊需有 2+ 來源驗證** — 單一來源需標注「未交叉驗證」

---

### 第一輪：Tavily 搜尋（優先執行，5個query同步）

```bash
# 使用 Tavily API（透過 browser console fetch）
# 每次最多 4-5 個 query，避免 timeout

1. "US stock market news today [YYYY-MM-DD]"
2. "Trump Truth Social today stock market [日期]"
3. "gold price WTI oil price today [日期]"
4. "tech stocks NVDA AAPL MSFT news today [日期]"
5. "Federal Reserve officials讲话 today [日期]"
```

**Tavily API 调用方式（browser console）：**
```javascript
(async () => {
  const response = await fetch('https://api.tavily.com/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      api_key: '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',
      query: 'YOUR QUERY',
      max_results: 5,
      search_depth: 'advanced',
      include_answer: true,
    })
  });
  return await response.json();
})()
```

---

### 第二輪：交叉驗證（如果 Tavily 結果不足）

用 **MiniMax MCP** 和 **Brave search** 補充/驗證：

```bash
# MiniMax MCP（並行）
mcp_minimax_web_search(query="...")
mcp_minimax_web_search(query="...")

# Brave search（並行）
web_search(query="...")
web_search(query="...")
```

**補充原則：**
- 如果 Tavily 找不到某項資訊，用 MiniMax MCP 搜一次
- 如果 MiniMax MCP 也找不到，用 Brave 搜一次
- 如果三個都搵唔到，標注「⚠️ 三個搜尋引擎均無結果」

---

### 第三輪：針對性深化搜尋（如有需要）

根據前兩輪結果，針對性搜尋：
- 地緣政治突發事件
- 具體公司業績或產品發布
- 經濟數據（CPI、就業、GDP）
- 分析師目標價調整

**同樣遵循：Tavily 優先 → MiniMax MCP → Brave 補充**

---

## 📋 輸出格式（必須嚴格跟隨）

```
**📅 今日美股深度速報 | [準確日期]**

---

## 0️⃣ 即時市場數據（富途實時）

### 📊 寬指行情
|| 指數 | 現價 | 升跌 | 升跌% | 日內高低 |
|------|------|------|-------|----------|
| SPY (標普500) | $XXX | +X.XX | +X.XX% | H:XXX L:XXX |
| QQQ (納指) | $XXX | +X.XX | +X.XX% | H:XXX L:XXX |

### 🏛️ 科技巨頭
|| 股票 | 現價 | 升跌 | 升跌% | 日內高低 |
|------|------|------|-------|----------|
| NVDA | $XXX | +X.XX | +X.XX% | H:XXX L:XXX |
| AAPL | $XXX | +X.XX | +X.XX% | H:XXX L:XXX |
| MSFT | $XXX | +X.XX | +X.XX% | H:XXX L:XXX |
| GOOG | $XXX | +X.XX | +X.XX% | H:XXX L:XXX |
| TSLA | $XXX | +X.XX | +X.XX% | H:XXX L:XXX |
| META | $XXX | +X.XX | +X.XX% | H:XXX L:XXX |

### 📈 資金流向信號
[根據富途資金流向數據描述：淨流入/流出金額、主要流向/流出板塊]

### 🛢️ 期貨市場
|| 商品 | 現價 | 升跌% |
|------|------|-------|
| 黃金期貨 (GCmain) | $XXX | +X.XX% |
| WTI原油期貨 (CLmain) | $XXX | +X.XX% |

> 數據來源：富途 OpenAPI（即時報價）

---

## 0️⃣.5️⃣ 期權數據分析（富途期權鏈）

### 📊 主要期權鏈數據摘要

#### NVDA 期權鏈重點
|| 行使價 | 類型 | IV (引伸波幅) | 成交量 | 未平倉合約 |
|------|--------|------|---------------|--------|------------|
| 價內/價外 | $XXX | Call/Put | XX% | XXXX | XXXX |

**IV 比較分析：**
- NVDA 現價 IV：XX%（過去30日 IV 均值：XX%）
- IV Rank：XX%（IV 處於歷史區間 XX% 位置）
- IV Percentile：XX%
- **解讀**：IV偏高/偏低，適合做Long/Short Volatility策略

**期權流入流出（OI 變化）：**
- 主要流入：Call/Put，行使價 $XXX，成交量 XXX
- 主要流出：Call/Put，行使價 $XXX，成交量 XXX
- **解讀**：資金睇好/睇淡後市

#### AAPL 期權鏈重點
（同上格式，根據富途返回數據填寫）

#### SPY / QQQ 大盤期權
（同上格式，根據富途返回數據填寫）

### 🔍 期權市場情緒指標

| 指標 | NVDA | AAPL | SPY | QQQ |
|------|------|------|-----|-----|
| PCR (Put/Call Ratio) | X.XX | X.XX | X.XX | X.XX |
| IV Rank | XX% | XX% | XX% | XX% |
| 5日平均OI變化 | +/-X% | +/-X% | +/-X% | +/-X% |
| 資金流向（OI口徑） | ▲/▼ | ▲/▼ | ▲/▼ | ▲/▼ |

**解讀：**
- PCR > 1.0：睇淡情緒較濃（機構用Put對沖）
- PCR < 0.7：睇好情緒較濃（機構用Call睇好）
- IV Rank > 50%：波幅偏高，適合Short Volatility（Sell IV）
- IV Rank < 30%：波幅偏低，適合Long Volatility（Buy IV）

---

## 1️⃣ 宏觀市場情緒

### 今日市場主軸
[150-200字段落，概括資金流向、風險偏好、恐慌/貪婪指標]

### 關鍵宏觀消息（每條獨立列出）

**消息 [N]：**
- 詳細描述：[3-4句描述事件內容]
- 對大市影響：Risk-On / Risk-Off + 強度（輕微/中等/強烈）
- 直接受影響指數或板塊：[具體指數或行業]
- 🔗 來源驗證：✅ [Tavily] + ✅ [MiniMax/Brave]（或 ⚠️ 單一來源）
- 🔗 來源：[URL]

---

## 2️⃣ 特朗普言論追蹤

**發言 [N]：**
- 原文關鍵句：[摘錄原文重點]
- 針對股票/行業：▲利好 / ▼利淡 + [具體公司/行業名稱]
- 影響邏輯：[詳細解釋點解呢番說話會帶動資金流]
- 可信度評估：[口頭表态 vs 實質政策行動可能性]
- 市場反應：[相關股票盤前/盤中異動描述]
- 🔗 來源驗證：✅ [Tavily] + ✅ [MiniMax/Brave]（或 ⚠️ 單一來源）
- 🔗 來源：[URL]

---

## 3️⃣ 科技界焦點

> 💡 價格數據來自富途即時報價（如上表所示）

**新聞 [N]：[標題]**
- 涉及股票：[ticker] + 現價（見上方富途數據）
- 影響方向：▲ / ▼ + 詳細影響路徑
- 大行觀點：[分析師評論，如有]
- 消息時效：[即日 / 本週持續]
- 🔗 來源驗證：✅ [Tavily] + ✅ [MiniMax/Brave]（或 ⚠️ 單一來源）
- 🔗 來源：[URL]

---

## 4️⃣ 金價 & 油價深度解讀

> 💡 期貨現價來自富途即時報價（如上表所示）

### 金價（XAU/USD）
- 現價：[來自富途 US.GCmain 現價]
- 日內變動：[+/-X%]
- 驅動原因：
  1. [原因1] — [解釋]
  2. [原因2] — [解釋]
  3. [原因3] — [解釋]

### 油價（WTI / Brent）
- 現價：[來自富途 US.CLmain 現價]
- 日內變動：[+/-X%]
- 驅動原因：
  1. [原因1] — [解釋]
  2. [原因2] — [解釋]
  3. [原因3] — [解釋]

### 板塊聯動地圖

| 價格變動 | 受惠股 ▲ | 受壓股 ▼ | 背後邏輯 |
|----------|----------|----------|----------|
| 油價升5% | 能源股(XLE) | 航空股(IYT)、消費者非必需品 | 成本上升侵蝕利潤，但能源股營收增加 |

---

## 5️⃣ 期權推薦（短線部署）

> 💡 標的股票現價來自富途即時報價，IV數據來自富途期權鏈

### 📋 推薦前必讀：期權掃描結果

根據富途期權鏈數據篩選出的機會：

| 篩選條件 | 結果 |
|----------|------|
| IV > 30% 的股票 | NVDA (XX%)、AMD (XX%) |
| PCR > 1.0 (睇淡) | SPY、QQQ |
| OI 急增的 Strike | NVDA $XXX Call、AAPL $XXX Put |

---

### 推薦 [N]：[具體策略名稱]

**標的股票：** [ticker] 現價 $[XXX]（見上方富途數據）

**期權參數：**
- 類型：Call / Put
- 行使價：$[XXX]（距離現價 ±X%，價外/價內）
- 到期日：[具體日期，解釋選擇原因]
- ⚙️ 引伸波幅（IV）：XX%（來自富途期權鏈）
- 權利金：$XXX
- Delta/Gamma：XX / XX（如有）

**策略邏輯：**
[消息面 → 市場預期 → 潛在催化劑 → 預期股價方向，完整論述]

**期權鏈依據：**
- 行使價 $XXX 有大量OI堆積（支撐/阻力位）
- IV Rank = XX%（偏高/偏低，適合此策略）
- OI 變化：+/-XX%（過去5日）

**情境分析：**
- 利好情境：[如果消息符合預期，預期回報X%]
- 利淡情境：[如果消息被否認/大市突然Risk-Off]

**風險提示：**
⚠️ [止蝕位建議 + 風險管理要點]

🔗 策略相關新聞：[URL]

---

## 6️⃣ 波幅交易專區（Volatility Trading）

> 💡 根據IV Rank和市場情緒，捕捉潛在波幅交易機會

### 📊 當前IV環境評估

| 股票 | 現價 IV | 30日均值 | IV Rank | IV Percentile | 策略建議 |
|------|---------|----------|---------|---------------|----------|
| NVDA | XX% | XX% | XX% | XX% | Short Call / Long Put |
| AAPL | XX% | XX% | XX% | XX% | Neutral / Iron Condor |
| SPY | XX% | XX% | XX% | XX% | Protective Put |
| QQQ | XX% | XX% | XX% | XX% | Bull Put Spread |

**IV 環境判斷：**
- 高IV（IV Rank > 50%）：適合 Short Vega 策略（Short Straddle/Strangle、Sell Iron Condor）
- 低IV（IV Rank < 30%）：適合 Long Vega 策略（Long Straddle/Strangle、Buy Straddle）

---

## ⚠️ 重要原則

1. **Tavily 優先** — 所有搜尋第一時間用 Tavily，MiniMax MCP 和 Brave 僅作補充/交叉驗證
2. **交叉驗證** — 每個關鍵資訊需有 2+ 來源驗證，單一來源需標注「⚠️ 未交叉驗證」
3. **富途數據優先** — 股價、報價、資金流向、期權鏈等實時數據必須使用富途 API
4. **期權數據不可缺** — 每次分析必須查詢並展示期權鏈數據（IV、OI、PCR）
5. **所有資訊必須來自今日** — 若某項搜尋無結果，必須如實寫「⚠️ 三個搜尋引擎均無結果」，嚴禁虛構
6. **每個數據都要有來源連結** — 所有結論必須可溯源，標注來源（Tavily/MiniMax/Brave/富途）
7. **詳細程度要足夠** — 每個部分都要有前因後果，不能一句起兩句止
8. **期權推薦僅為短線博弈分析** — 不構成投資建議，必須提醒止蝕

## 🌙 盤前/盤後/夜盤分析陷阱（2026-05-06 實戰補充）

- **美股狀態為 `OVERNIGHT` / `AFTER_HOURS` 時，現價優先級必須用：`overnight_price` → `after_price` → `last_price`。** 不可只報 `last_price`，否則會低估財報後跳空（例如 AMD/QCOM 夜盤）。
- **期權鏈 snapshot 在美股常規時段外可能是上一個 regular session 的期權報價。** 如果正股夜盤因財報跳空，期權 `IV/Delta/last/bid/ask` 會失真；可以用 PCR/OI/成交量判斷情緒，但策略必須標註「開市後等 5-15 分鐘 / VWAP / opening range 確認」，避免按 stale options 直接落結論。
- **期貨（如 `US.GCmain`、`US.CLmain`）可能因行情權限不足失敗。** 若富途返回「行情权限不足」，改用已交叉驗證的 web 搜尋價格，並明確標註「非富途數據」。
- **財報爆升股避免一開市裸追 Call。** 若 IV 已極高或夜盤已大幅 gap up，優先考慮 pullback/VWAP 交易、call spread、或等 IV crush 後再部署。

---

## 🔧 execute_code 壊咗時的解決方案

如果 execute_code 返回 FileNotFoundError：
1. 使用 browser console fetch 代替 Tavily API：
```javascript
(async () => {
  const response = await fetch('https://api.tavily.com/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      api_key: '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',
      query: 'YOUR QUERY',
      max_results: 5,
      search_depth: 'advanced',
      include_answer: true,
    })
  });
  return await response.json();
})()
```
2. 每次最多 4-5 個 query，避免 timeout
3. 分批進行搜尋

---

## Absorbed: us-stock-news (Simpler Trigger Variant)

### Additional Trigger Conditions
- 「今日美股點」
- 「美股點睇」
- 「今日美股」
- 「US stock today」
- 「美股行情」

### Day-of-Week Analysis
| 星期 | 重點 |
|------|------|
| **星期一** | 「Week Ahead」預測、本週大事、CPI/FOMC日程 |
| **星期二** | 正常交易日、關注美股開市方向 |
| **星期三** | FOMC會議日（如果有）、MicroSOXX 期權結算 |
| **星期四** | 宏觀數據發布、初申失業金數據 |
| **星期五** | 「End of Week」總結、持倉風險控制、short covering |

### Trump Policy Effect Tracking
搜尋：`Trump tariff news today`、`Trump Fed news today`
- 關稅政策（Tariffs）→ 航運股、晶片股、中概股
- 聯邦機構改革 → 銀行股、監管概念股
- 移民政策 → 勞工概念股、餐飲股
- 減稅計劃 → 成長股、科技股
- 聯儲局干預 → 全市場影響

### Macro Factor Impact Table
| 因素 | 上升時受害股 | 上升時受惠股 |
|------|------------|------------|
| **油價 ↑** | 航空股、運輸股、消費股 | 能源股、石油公司 |
| **黃金 ↑** | 美元走弱、礦業股 | 黃金礦業、金ETF |
| **利率 ↑** | 科技股、樓市、科技股 | 銀行股、保險股 |
| **利率 ↓** | 銀行股、保險股 | 科技股、樓市、REITs |
| **美元 ↑** | 出口股、科技股（海外收入） | 進口股、旅遊股 |
| **VIX ↑** | 幾乎所有股（系統性風險） | VIX ETF、做空工具 |

---

## Absorbed: us-stock-find (Stock Screener Variant)

### Trigger: Stock Opportunities Search
- 「今日邊隻股票升得多」
- 「幫我搵下有咩股票準備爆」
- 「邊個板塊最熱」
- 「成交量大增」
- 「stock movers」「volume surge」「breakout stocks」

### Finnhub API (Primary for Stock Screener)
- **Key**: `d7mft71r01qngrvo2bb0d7mft71r01qngrvo2bbg`
- **Base**: `https://finnhub.io/api/v1`
- **Rate Limit**: 60 calls/min (free tier)

### Finnhub Available Endpoints (Free Tier)
| Endpoint | 用途 |
|----------|------|
| `/quote?symbol=AAPL` | 即時股價 + 日變化% |
| `/news?category=general` | 即時市場新聞 |
| `/stock/peers?symbol=AAPL` | 股票同業列表 |
| `/stock/candle?symbol=AAPL&resolution=D` | K線數據 |

### Core Screener Functions
1. **市場寬度分析** — 計算上漲/下跌股票數量、創新高/新低數量
2. **熱門股票篩選** — Top Gainers、Top Losers、成交量突增股（>3倍均量）
3. **板塊強度分析** — 追蹤11個S&P板塊相對表現
4. **棺材店效應候選** — Short Interest比率高 + 價格拉升 + 成交量暴增

### Finnhub Fallback (if API fails)
使用 Brave + Tavily 搜尋：
- `site:finance.yahoo.com stock movers today`
- `site:finviz.com stock screener volume surge`

---

## Absorbed: us-stock-vcp (VCP Pattern Detection)

### Trigger: VCP Search
- 「幫我搵VCP」
- 「VCP形態」
- 「準備爆升既股票」
- 「tight consolidation」

### What is VCP? (Volatility Contraction Pattern)
From Mark Minervini's "Think & Trade Like a Stock Market Legend":

**特徵：**
1. **波幅遞減** — 每次調整幅度都比上一次細（e.g., -15% → -10% → -6% → -3%）
2. **價格區間收窄** — 形成「收縮三角形」
3. **成交量萎縮** — 調整期間成交量明顯縮減
4. **結構穩固** — 通常需要 7-10 週形成基底
5. **Pivot Point** — 突破時出現，通常是從基底低位 20-25% 急升

### VCP Detection with Finnhub
| 指標 | 計算方法 | VCP 門檻 |
|------|----------|-----------|
| **Range Ratio** | 調整期間最高 / 最低 | < 1.15 |
| **ATR收縮** | 現時 ATR / 90日前 ATR | < 0.6 |
| **價格位置** | 現價 / 52週高點 | 0.75-0.95 |
| **RS Rating** | 相對強度 | > 80 |

### VCP Score Formula
```
VCP_Score = (RS_Rating × 0.3) + (Base_Quality × 0.25) + (Volume_Spike × 0.2) + (Sector_Strength × 0.15) + (News_Sentiment × 0.1)
```

### ⚠️ VCP Warning
Finnhub 數據可用於篩選和輔助分析，但**形態識別需要圖表確認**（建議配合 TradingView 或 StockCharts）。此技能不構成投資建議，DYOR。

---

## 🚨 富途 OpenD 無法啟動時嘅 Fallback（2026-10-08 實戰）

**症狀：** cron 自動執行時 `get_snapshot.py` 等全部報 `无法连接 OpenD (127.0.0.1:11111): Connection refused`。即使 `open -a Futu_OpenD` 成功起 process，`~/.com.futunn.FutuOpenD/Log/FTGatewayGui_*.log` 會顯示：

```
OpenD status changed: "需要重输入密码登录"  (type: 5)
```

即 OpenD **需要互動式重新輸入密碼**，cron／非互動 session 永遠等唔到 port 11111 開。唔好死等或重試多過一次。

**Fallback 資料源（已實測可用）：**

```bash
# ① Finnhub — 個股即時報價（last close，t 欄位 = Unix ts）
curl -s "https://finnhub.io/api/v1/quote?symbol=NVDA&token=d7mft71r01qngrvo2bb0d7mft71r01qngrvo2bbg"
#    → {"c":237.47,"d":-1.77,"dp":-0.7398,"h":239.08,"l":236.38,"o":237.685,"pc":239.24,"t":1791403200}

# ② Finnhub 新聞（100 條，已按時間排序，datetime = Unix ts）
curl -s "https://finnhub.io/api/v1/news?category=general&token=..."
curl -s "https://finnhub.io/api/v1/company-news?symbol=NVDA&from=2026-10-07&to=2026-10-09&token=..."

# ③ Yahoo Finance chart API — 期貨／商品／指數／債息／VIX（實時）
curl -s -H "User-Agent: Mozilla/5.0" \
  "https://query1.finance.yahoo.com/v8/finance/chart/ES=F?interval=1d&range=2d"
#    代碼：ES=F NQ=F YM=F RTY=F CL=F BZ=F GC=F SI=F DX-Y.NYB ^VIX ^TNX BTC-USD
#    ^GSPC ^IXIC ^DJI ^RUT ^SOX（用 %5E 轉義）
#    meta.regularMarketPrice + meta.chartPreviousClose 計 %；range=7d 可取逐日收市
```

**注意：**
- Python `urllib` 打 Yahoo 會 **SSL CERTIFICATE_VERIFY_FAILED**（macOS cert store 問題）→ 一律用 `curl` + `-H "User-Agent: Mozilla/5.0"`。
- Finnhub `t` / `datetime` 欄位係 Unix timestamp，**必須轉換確認係邊個 session**，唔好假設係即時。常規時段外 `c` = 上一個交易日收市價。
- **交叉驗證技巧**：Investing.com 文章內嵌嘅 market-movers 表格會列出當日收市價（MU/NVDA/AAPL…），可以同 Finnhub 對數，確認冇取錯 session。
- 報告必須**明確標註**邊啲數字係富途（正常）／Finnhub ／Yahoo，唔可以扮係富途數據。
- 期權鏈數據（IV/OI/PCR）喺 OpenD 掛機時**攞唔到**，改用 VIX 水位、VIX term structure（thetrading.tools）、CNN Fear & Greed、CNBC/Barron's 期權異動報導替代，並標明「非富途期權鏈數據」。
