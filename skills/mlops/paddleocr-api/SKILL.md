---
name: paddleocr-api
description: PaddleOCR-VL-1.6 Cloud API — OCR 文字辨識（支援本地檔案/URL，輸出 Markdown + 圖片）
category: mlops
related_skills:
  - local-ocr
  - ocr-and-documents
---

# PaddleOCR API Skill

用 PaddleOCR-VL-1.6 API 做光學字元辨識（OCR），支援：
- 本地圖片/PDF 上傳
- 遠端 URL 檔案
- 自動 polling 等候結果
- 輸出 Markdown 文件 + 內嵌圖片

## API 資訊

- **Endpoint**: `https://paddleocr.aistudio-app.com/api/v2/ocr/jobs`
- **Token**: 由用戶提供（記錄喺記憶或 `.env`）
- **Model**: `PaddleOCR-VL-1.6`

## 用法

### 前置條件

```bash
pip install requests
```

### Python Script (完整版)

```python
import json
import os
import requests
import sys
import time

JOB_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
TOKEN = "<your_token>"
MODEL = "PaddleOCR-VL-1.6"

file_path = "<local file path or file url>"

headers = {
    "Authorization": f"bearer {TOKEN}",
}

optional_payload = {
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useChartRecognition": False,
}

print(f"Processing file: {file_path}")

if file_path.startswith("http"):
    # URL Mode
    headers["Content-Type"] = "application/json"
    payload = {
        "fileUrl": file_path,
        "model": MODEL,
        "optionalPayload": optional_payload
    }
    job_response = requests.post(JOB_URL, json=payload, headers=headers)
else:
    # Local File Mode
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
        
    data = {
        "model": MODEL,
        "optionalPayload": json.dumps(optional_payload)
    }
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        job_response = requests.post(JOB_URL, headers=headers, data=data, files=files)

print(f"Response status: {job_response.status_code}")
if job_response.status_code != 200:
    print(f"Response content: {job_response.text}")

assert job_response.status_code == 200
jobId = job_response.json()["data"]["jobId"]
print(f"Job submitted successfully. job id: {jobId}")
print("Start polling for results")

jsonl_url = ""
while True:
    job_result_response = requests.get(f"{JOB_URL}/{jobId}", headers=headers)
    assert job_result_response.status_code == 200
    state = job_result_response.json()["data"]["state"]
    if state == 'pending':
        print("The current status of the job is pending")
    elif state == 'running':
        try:
            total_pages = job_result_response.json()['data']['extractProgress']['totalPages']
            extracted_pages = job_result_response.json()['data']['extractProgress']['extractedPages']
            print(f"The current status of the job is running, total pages: {total_pages}, extracted pages: {extracted_pages}")
        except KeyError:
             print("The current status of the job is running...")
    elif state == 'done':
        extracted_pages = job_result_response.json()['data']['extractProgress']['extractedPages']
        start_time = job_result_response.json()['data']['extractProgress']['startTime']
        end_time = job_result_response.json()['data']['extractProgress']['endTime']
        print(f"Job completed, successfully extracted pages: {extracted_pages}, start time: {start_time}, end time: {end_time}")
        jsonl_url = job_result_response.json()['data']['resultUrl']['jsonUrl']
        break
    elif state == "failed":
        error_msg = job_result_response.json()['data']['errorMsg']
        print(f"Job failed, failure reason：{error_msg}")
        sys.exit()

    time.sleep(5)

if jsonl_url:
    jsonl_response = requests.get(jsonl_url)
    jsonl_response.raise_for_status()
    lines = jsonl_response.text.strip().split('\n')
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    page_num = 0
    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        result = json.loads(line)["result"]
        for i, res in enumerate(result["layoutParsingResults"]):
            md_filename = os.path.join(output_dir, f"doc_{page_num}.md")
            with open(md_filename, "w", encoding="utf-8") as md_file:
                md_file.write(res["markdown"]["text"])
            print(f"Markdown document saved at {md_filename}")
            for img_path, img in res["markdown"]["images"].items():
                full_img_path = os.path.join(output_dir, img_path)
                os.makedirs(os.path.dirname(full_img_path), exist_ok=True)
                img_bytes = requests.get(img).content
                with open(full_img_path, "wb") as img_file:
                    img_file.write(img_bytes)
                print(f"Image saved to: {full_img_path}")
            for img_name, img in res["outputImages"].items():
                img_response = requests.get(img)
                if img_response.status_code == 200:
                    filename = os.path.join(output_dir, f"{img_name}_{page_num}.jpg")
                    with open(filename, "wb") as f:
                        f.write(img_response.content)
                    print(f"Image saved to: {filename}")
                else:
                    print(f"Failed to download image, status code: {img_response.status_code}")
            page_num += 1
```

## 快捷用法（terminal 直接 run）

將上面 script 保存做 `paddleocr_run.py`，然後：

```bash
# URL mode
python paddleocr_run.py "https://example.com/document.pdf"

# Local file mode
python paddleocr_run.py ~/Desktop/scan.jpg
```

## 從 Agent 內呼叫

```python
# 用 execute_code 直接呼叫
from hermes_tools import terminal

# URL mode
result = terminal(f"python paddleocr_run.py https://example.com/doc.pdf")

# Local mode 
result = terminal(f"python paddleocr_run.py ~/Desktop/scan.pdf")
```

## 注意事項

- **Token** 需要由用戶提供，建議 save 去 memory
- API 支援嘅 file formats：圖片（JPEG, PNG, TIFF）同 PDF
- Polling interval：5秒
- Output 預設放喺 `./output/` 目錄
- `useDocOrientationClassify`：自動校正文件方向
- `useDocUnwarping`：文件展平（彎曲文件矯正）
- `useChartRecognition`：圖表辨識
- 以上 optional 參數預設關閉，需要可自行開啟

## 整合入現有專案時必須小心（Pitfall）

> **⚠️ 整合新 OCR provider 入現有 pipeline 時，改完一定要先 test 現有 providers，確認冇 regressions。**

- 改 `run_ocr_pipeline()` 嘅 shared return value（例如 `raw_ocr_text` ternary expression）會影響所有 providers，唔係淨係新加嗰個
- 每個 provider 行獨立 code path 但共享同一個 return block — 看似安全嘅改動可能引入 subtle break
- 加新 vars、expand conditionals、改 dict 都屬於「共享改動」
- 建議 step-by-step commit / backup：先加 provider function → rebuild test → 再改 pipeline → rebuild test
- 如果出事：即刻 revert 所有改動，`docker compose up -d --build` rebuild
- Lunch-split 架構細節、surya 依賴、debugging techniques 見 `references/lunch-split-integration.md`

### Debugging: OCR returns "未識別店舖" (silent failure)

當所有 providers 都 output 「未識別店舖」+ 1 個 item「請手動輸入食物 $0.0」+ `raw_ocr_text: ""`，
表示 OCR pipeline 完全冇文字產出。按以下順序排查：

1. **Check provider 本身**：直接 call OCR function（見 `references/lunch-split-integration.md` Debugging 一節）
2. **Check API key**：MiniMax MCP 用 truncated key（有 `...`）會 silent fail，MCP response 有 "login fail" error 但 UI 唔會 show
3. **Check fallback**：`needs_surya` 決定 provider 有冇文字 fallback。冇 fallback + provider fail = 空結果
4. **Check Surya**：`docker exec lunch-split-api python -c "import httpx; print(httpx.get('http://host.docker.internal:8089/health').json())"`
5. **Check Docker logs**：`docker logs lunch-split-api | tail -20`
6. **OCR jobs 係 in-memory**：container restart 會清走 running jobs，receipt 留低空 data → `curl -X DELETE http://localhost:8787/api/receipts`

## Post-Processing／Cleanup（關鍵！）

PaddleOCR-VL-1.6 嘅 `layoutParsingResults[].markdown.text` 輸出係 **layout-aware markdown**，
每個文字 box 獨立成行，夾雜 HTML `<div><img>` placeholder tags。直接餵入 downstream parser
會出錯 — 必須做以下 cleanup pipeline：

### 1. Strip HTML tags
```python
import re

cleaned = re.sub(r"<div[^>]*>.*?</div>", "", raw_text, flags=re.DOTALL)
cleaned = re.sub(r"<img[^>]*/?>", "", cleaned)
cleaned = re.sub(r"<[^>]+>", "", cleaned)      # any remaining HTML
```

### 2. Clean superscript noise
PaddleOCR markdown 有時會出 `$ ^{①}`, `$ ^{i}` 等 superscript artifacts：
```python
cleaned = re.sub(r"\$ ?\^?\{?[①②③④⑤⑥⑦⑧⑨⑩iI]+\}?", "", cleaned)
```

### 3. Merge adjacent name + price lines
Layout parser 將 item name 同 price 分拆成兩個 box，中間仲有 blank lines。
必須 collapse blanks 同 merge 相鄰行：

```python
price_re = re.compile(r"^\$?(\d+(?:\.\d{1,2})?)$")
lines = [l.strip() for l in cleaned.split("\n") if l.strip()]
merged = []
for line in lines:
    stripped = line
    # Skip "x1" quantity markers and lone "$"
    if re.match(r"^x\d+$", stripped, re.I) and merged:
        continue
    if stripped == "$":
        continue
    # Handle "$XX $YY" dual price (use discounted second price)
    dual = re.match(r"^\$(\d+(?:\.\d{1,2})?)\s+\$(\d+(?:\.\d{1,2})?)$", stripped)
    if dual and merged and merged[-1]:
        merged[-1] = f"{merged[-1]} ${dual.group(2)}"
        continue
    # Merge single price with previous line (item name)
    if price_re.match(stripped) and merged and merged[-1]:
        prev = merged[-1]
        prev_words = prev.split()
        last_word = prev_words[-1] if prev_words else ""
        if not price_re.match(last_word) and not last_word.startswith("$"):
            merged[-1] = f"{prev} ${stripped.lstrip('$')}"
            continue
    merged.append(stripped)
cleaned = "\n".join(merged)
```

### Complete pipeline
```python
raw_text = "\n".join(all_text_parts).strip()
if raw_text:
    cleaned = re.sub(r"<div[^>]*>.*?</div>", "", raw_text, flags=re.DOTALL)
    cleaned = re.sub(r"<img[^>]*/?>", "", cleaned)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = re.sub(r"\$ ?\^?\{?[①②③④⑤⑥⑦⑧⑨⑩iI]+\}?", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    # ... merge logic above ...
    return clean_ocr_text(cleaned)
```

唔做呢個 cleanup 嘅話，heuristic parser（expects `name $price` per line）會搵唔到 item，
因為名同行分開唔同行。

## 整合入現有專案（Provider Pattern）

將 PaddleOCR 加入現有 FastAPI OCR pipeline 嘅標準步驟（參考 `references/lunch-split-integration.md`）：

1. **Env vars**：`PADDLEOCR_API_TOKEN`, `PADDLEOCR_API_URL`, `PADDLEOCR_MODEL`
2. **Provider registry**：加入 `OCR_PROVIDERS` set
3. **Async wrapper**：`call_paddleocr_ocr(path)` — job submit → poll → parse JSONL → return text
4. **Pipeline integration**：加入 `run_ocr_pipeline()`，set `needs_surya`（fallback），同其他 providers 一樣 pattern（call → heuristic_parse → error handling）
5. **Frontend**：加 provider label 入 dropdown

關鍵設計決定：
- PaddleOCR 需要 Surya 做 fallback（API 可能 timeout/fail）
- 最長等待 5 分鐘（60×5s polling）
- Error 用 dict `{"error": "..."}`返回，pipeline 用 `isinstance(result, str)` 判斷成功/失敗
- Markdown text 從 `layoutParsingResults[].markdown.text` 抽取
- 可同其他 sync/async OCR providers 並存同一條 pipeline

### PaddleOCR + MiniMax 組合（推薦！）

PaddleOCR layout-parsed text 就算 cleanup 後仍然有 noise（name/price 分開行、量詞混入等）。
**最佳方案**：PaddleOCR 做 OCR 文字提取 → MiniMax MCP 做結構化 JSON parsing。

```python
# In run_ocr_pipeline():
if should_paddleocr:
    paddleocr_text = await call_paddleocr_ocr(path)
    if isinstance(paddleocr_text, str) and paddleocr_text.strip():
        paddleocr_raw_text = paddleocr_text
        # Use MiniMax for structured parsing with PaddleOCR text as hint
        if bool(minimax_key):
            minimax_structured = await call_minimax_mcp_understand_image(path, paddleocr_text)
            if minimax_structured and isinstance(minimax_structured, dict) and not minimax_structured.get("error"):
                minimax_structured["notes"] = f"PaddleOCR-VL-1.6 + MiniMax 解析。{minimax_structured.get('notes', '')}"
                paddleocr_receipt = minimax_structured
        # Fallback: heuristic parse if MiniMax unavailable or failed
        if not paddleocr_receipt:
            candidate = heuristic_parse(paddleocr_text)
            if has_real_items(candidate):
                paddleocr_receipt = candidate
```

呢個 pattern 嘅 output quality 同純 MiniMax 一致（乾淨 item names、正確分類、冇 noise），
而 PaddleOCR 提供額外嘅 raw text 作 cross-reference。Notes 會標明「PaddleOCR-VL-1.6 + MiniMax 解析」。

### 結算 discount 計算

預設 codebase 會 skip 所有 `item_type == "discount"`。如需要計入優惠但排除積分：

```python
if item["item_type"] == "discount":
    if "積分" in item["name"]:
        continue  # skip loyalty points
    shared_items.append(item_total)  # discount is negative, shared among all
    continue
```
