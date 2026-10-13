---
name: image-generation-workflow
description: "Text-to-image pipeline: MiniMax image-01 (primary) → SiliconFlow Kwai-Kolors (backup). Includes prompt engineering, meme caption overlay, and critical URL masking workarounds. Token Plan endpoint deprecated 2026-07-08."
version: 1.3.0
---

# Image Generation Workflow

Standard pipeline for generating images from text prompts, with meme caption overlay support.

**user預設風格：anime / 動漫風格**（除非指定其他風格）

## ⚠️ SESSION LEARNINGS

### What NOT to do
- **NEVER try `image_generate` tool first** — it requires `FAL_KEY` which is NOT set in this environment. It will always fail with `"FAL_KEY environment variable not set"`. Skip it entirely.
- **NEVER try arbitrary API endpoints** — endpoint guessing wastes time. Follow the verified paths below.
- **NEVER ask which model AFTER generating** — use the configured default (MiniMax image-01) unless user explicitly requests a model choice.
- **Do not use the Token Plan endpoint** — `token-plan.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation` 已 deprecated 2026-07-08。所有 qwen-image-2.0 / wan2.7-image models 都唔再用。

### Verified Working Paths (2026-07-08)
**Primary: MiniMax image-01** (~22s, presigned OSS URL → curl download)
**Backup: SiliconFlow Kwai-Kolors** (~7s, S3 download 易 timeout)

### Model Selection Reminder
The configured default is MiniMax image-01. Do not pause ordinary image generation to ask for a model; use MiniMax image-01 and fall back to SiliconFlow Kwai-Kolors if it fails. Only present model options when user explicitly asks to choose or compare models.

**IMPORTANT:** If user explicitly requests a model choice, ask before generating and wait for the answer. Otherwise proceed with the configured default.

## Model Selection Policy

- user已設定預設模型：**MiniMax image-01**。
- 一般生圖要求毋須再問模型，直接用 MiniMax image-01；失敗時自動 fallback SiliconFlow Kwai-Kolors。
- 只有user主動要求選模型、比較模型，或指定其他模型時，才列出選項。
- 同一任務嘅後續修改沿用原模型。

**user首選 Model 1 (MiniMax image-01)** — 2026-07-07 確認 ~22s 生成、URL response format、prompt_optimizer 有效。

**user options (2026-08-12 update — image-01-live 已驗證):**
| # | Model | Endpoint | 備註 |
|---|---|---|---|
| 1 | **MiniMax image-01** ⭐ (推薦 primary) | `api.minimaxi.com/v1/image_generation` | T2I + I2I (subject ref)；~22s |
| 2 | **MiniMax image-01-live** | `api.minimaxi.com/v1/image_generation` | 同 endpoint，model field 改 `"image-01-live"`；I2I / character consistency 強，T2I 都 work（2026-08-12 實測成功）；~20s |
| 6 | **SiliconFlow (Kwai-Kolors)** | SiliconFlow (`api.siliconflow.cn`) | T2I only，~7s，S3 下載易 timeout |

**Endpoint summary:**
- **MiniMax image-01 (1) PRIMARY** ⭐: `https://api.minimaxi.com/v1/image_generation` ← 用 `MINIMAX_CN_API_KEY` (sk-cp-... 格式，125 字元)
- SiliconFlow (6): `https://api.siliconflow.cn/v1/images/generations` ← 用 SiliconFlow key

⚠️ **Critical:** Token Plan endpoint (`token-plan.cn-beijing.maas.aliyuncs.com`) 已 **DEPRECATED** — 2026-07-08 user確認唔再用。`TOKEN_PLAN_API_KEY` 仍喺 config.yaml 但屬 dead config。

---

## Primary: MiniMax image-01 (Recommended)

速度最快 (~18-22秒)，質素好，**強烈推薦**。支援 base64 同 url 兩種 response。

> **Verified 2026-07-07:** MiniMax image-01 confirmed as PRIMARY per user instruction. ~22s generation (rocket launch test). See `references/minimax-image01-verified-20260707.md` for full session record (payload, response format, OSS download workaround, key attribution).

> **2026-07-08:** user確認移除所有 Token Plan models (qwen-image-2.0 / wan2.7-image) — `TOKEN_PLAN_API_KEY` endpoint 已 deprecated，唔再行。

**Endpoint:** `https://api.minimaxi.com/v1/image_generation`

**API Key:** `MINIMAX_CN_API_KEY` (in `~/.hermes/.env`，格式 `sk-cp-...` 開頭，長度 125 字元)

**Model:** `image-01`

**Verified working payload** (2026-07-07 實測):
```python
import urllib.request, json, os

# 讀 .env key（避開 masking）
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if "MINIMAX_CN_API_KEY" in line:
            api_key = line.split("=", 1)[1].strip().strip('"').strip()
            break

payload = {
    "model": "image-01",
    "prompt": "...",
    "aspect_ratio": "16:9",       # 1:1, 16:9, 9:16, 4:3, 3:4 等
    "n": 1,                       # 一次生成张数, 最多 9 張
    "response_format": "url",     # 或 "base64"
    "prompt_optimizer": True      # 自動優化提示詞
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    "https://api.minimaxi.com/v1/image_generation",
    data=data,
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req, timeout=120) as resp:
    result = json.loads(resp.read())

# url response (recommended — 避免 base64 decode 開支)
if payload["response_format"] == "url":
    image_url = result["data"]["image_urls"][0]
    import subprocess
    output_path = os.path.expanduser("~/Desktop/hermes production/output.jpeg")
    subprocess.run(["curl", "-sL", "-o", output_path, "--max-time", "120", image_url], check=True)
    print(f"✅ {output_path}")

# base64 response (alternative)
else:
    import base64
    img_data = base64.b64decode(result["data"]["image_base64"][0])
    output_path = os.path.expanduser("~/Desktop/hermes production/output.jpeg")
    with open(output_path, 'wb') as f:
        f.write(img_data)
    print(f"✅ {output_path}")
```

**Response 格式** (url mode):
```json
{
  "id": "069c01...",
  "data": {
    "image_urls": ["https://hailuo-image-algeng-data.oss-cn-wulanchabu.aliyuncs.com/...?Expires=...&Signature=..."]
  },
  "metadata": {"failed_count": "0", "success_count": "1"},
  "base_resp": {"status_code": 0, "status_msg": "success"}
}
```

⚠️ **API keys in `.env` are write-protected** — they get masked (`***`) when printed via grep/cat. Read the file in Python directly and use the value without printing.

⚠️ **HARD RULE: Do NOT use the built-in `image_generate` tool.** That tool requires `FAL_KEY` which is NOT set in user's environment — it will always fail with `"FAL_KEY environment variable not set"`. Always use the direct Python/curl approach below instead.

**For kawaii/cute style prompts**, append:
```
super kawaii cute anime, chibi proportions, big sparkling eyes, soft pastel colors, fluffy fur texture
```

---

## Attempted-but-Blocked: Poe API (sk-poe-... keys)

**Poe API supports chat completions but NOT image generation for the user's API key tier.**

- `POST /v1/chat/completions` with model `gpt-image-2`: returns empty response (no image in output)
- `POST /v1/images` (custom endpoint): returns `404 Not Found`
- `POST /v1/images/generations` (OpenAI Images API format): returns `"Images API is not enabled for this user"` (`permission_denied`)
- `GET /v1/models`: blocked by security policy

**Do NOT attempt Poe API for image generation** — use MiniMax image-01 (primary) or SiliconFlow as alternatives.

## Backup: SiliconFlow (Kwai-Kolors)

生成快 (~7秒)，但**S3下載極慢/極易timeout**，不建議優先使用。

**Endpoint:** `https://api.siliconflow.cn/v1/images/generations` (note: `.cn`, NOT `.io`)

**API Key:** `sk-scl...ovxl`

```python
import urllib.request, json, ssl
api_key = "sk-scl...ovxl"
payload = {"model":"Kwai-Kolors/Kolors","prompt":"...","image_size":"1024x1024","batch_size":1,"num_inference_steps":20}
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request("https://api.siliconflow.cn/v1/images/generations",
    data=data, headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())
url = result["images"][0]["url"]
ctx = ssl.create_default_context()
ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"}), timeout=60, context=ctx) as resp:
    with open("/tmp/output.png","wb") as f: f.write(resp.read())
```

---

## Meme Caption Overlay

```bash
SKILL_DIR=$(dirname "$(find ~/.hermes/skills -path '*/meme-generation/SKILL.md' 2>/dev/null | head -1)")
python3 "$SKILL_DIR/scripts/generate_meme.py" --image /tmp/scene.png --bars ~/Desktop/hermes\ production/meme_final.png "TOP TEXT" "BOTTOM TEXT"
```

---

## Absorbed: multi-image-generation (Cantonese Trigger Variant)

### Trigger
For ordinary image generation, use the configured default MiniMax image-01 without asking for model selection. If user explicitly asks to choose a model, present MiniMax image-01 and SiliconFlow options before generating and wait for the choice.

**Available models (2026-07-08 update; Token Plan deprecated):**
1. **MiniMax image-01** ⭐ (推薦 primary) — `api.minimaxi.com/v1/image_generation`
2. SiliconFlow (Kwai-Kolors) — `api.siliconflow.cn`

### user的倉鼠圖偏好（記憶）
- 白色倉鼠：純白毛、粉紅耳朵、黑豆眼、冇花紋
- 虎斑暹羅貓：奶油色身體、淺灰虎斑紋、藍眼睛
- 倉鼠大小：極細小，如貓隻爪咁大（符合現實比例）
- 姿勢：倉鼠坐喺貓身上、手拎逗貓棒指向隻貓
- 風格偏好：Studio Ghibli吉卜力風格

生成倉鼠圖時自動套用以上描述，無需重複說明。

---

## Absorbed: text-to-image (English Trigger Variant)

### English Trigger Patterns
Activate when the user says: "draw", "generate", "create an image", "text-to-image"

### ⚠️ PITFALL: User Sends Image + Style Instruction = GENERATION Request

**CRITICAL INTERPRETATION RULE:** When a user sends a reference image AND says something like:
- "新成吉卜力風格" (new Ghibli style)
- "X風格嘅版本"
- "幫我轉做Y風格"

1. Analyze the image briefly to understand its content (what's in it)
2. Immediately offer to generate a style-transferred version
3. Describe the scene in text → use as prompt for generation

**Wrong:** User sends image + "新成吉卜力風格" → You describe the image in detail → User says "我係要你生成"

**Correct:** User sends image + "新成吉卜力風格" → You say "收到！等我幫你生成吉卜力風格版本！" → Describe the scene → Generate

**Trigger:** Reference image + a style keyword means style-transfer generation, not description. Use the configured MiniMax image-01 default unless user explicitly requests a model choice.

### Reference-Based Image Generation (Photo/Style → Anime/Style Pipeline)
When user wants a stylized version (anime, Ghibli, kawaii, etc.) of a reference image they send:

1. **Analyze the photo** using the available vision tool (Minimax MCP vision via `mcp_minimax_understand_image` or qwen3.6-plus):
   ```python
   import urllib.request, json, base64
   img_path = "/path/to/photo.jpg"
   with open(img_path, "rb") as f:
       img_b64 = base64.b64encode(f.read()).decode()
   api_key = "MOONSHOT_API_KEY"
   payload = {
       "model": "qwen3.6-plus",
       "messages": [{"role": "user", "content": [
           {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
           {"type": "text", "text": "描述呢張圖入面有咩？"}
       ]}],
       "max_tokens": 300
   }
   req = urllib.request.Request("https://api.moonshot.cn/v1/chat/completions",
       data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
   with urllib.request.urlopen(req, timeout=30) as resp:
       result = json.loads(resp.read())
   description = result["choices"][0]["message"]["content"]
   ```
2. **Generate anime version** using the description in the prompt, with anime style keywords.

### Iterative Refinement Tips
- **Eye shape**: "小眼" may not work — use explicit descriptors like "eyes drawn as thin horizontal lines"
- **Hair details**: Specify "PROMINENT blonde/golden highlights", "only on the hair tips/ends" for subtle highlights
- **Body type**: "Slim" may be subtle — use "very slim build with V-shaped face and sharp chin"
- **Hair parting**: "center part/middle part hairstyle (hair parts in the middle, swept to both sides)"
- **Size relationships**: Emphasize "noticeably smaller than the humans, petite"
- **Facial simplicity**: If user says "簡單啲", switch to minimalist Ghibli style
- **See also:** `references/session-20260512-slim-vface-prompts.md` for verified prompt modifiers
- **Color corrections:** Use comparative phrasing — "not dark, just subtle shading" works better than just "lighter". "Completely [X], no [Y]" works better than just "more [X]".
- **Spatial corrections:** Anchor height to the other character — "her head reaches below the guy's shoulder" works better than just "shorter".
- **See also:** `references/session-20260514-ghibli-refinement.md` for spatial/color correction patterns

---

## Absorbed: siliconflow-image-gen (SiliconFlow-Specific Details)

### SiliconFlow Telegram Sending (Bot API)
⚠️ send_message(to=telegram, message="/tmp/image.png") only sends the file path, NOT the actual image!
To truly send image to Telegram, use Bot API:
```bash
curl -s "https://api.telegram.org/bot<TOKEN>/sendPhoto" \
  -F "chat_id=<CHAT_ID>" -F "photo=@/tmp/image.jpg"
```

### SiliconFlow S3 URL Download (execute_code workaround)
Python urllib in execute_code sandbox times out on SiliconFlow S3 URLs — use terminal curl:
```bash
curl -s -L --max-time 120 -A "Mozilla/5.0" -o ~/Desktop/hermes\ production/output.png $(cat ~/Desktop/hermes\ production/sf_url.txt)
```

---

## WeChat Sending

```bash
sips -s format jpeg -s formatOptions 70 ~/Desktop/hermes production/output.png --out ~/Desktop/hermes production/output.jpg
## ⚠️ WeChat Media Sending — CRITICAL

**`send_message(target="weixin", message="/path/to/file.jpg")` SUCCEEDS but the image does NOT appear in WeChat.** This is a known issue — WeChat requires the `MEDIA:` prefix in the message body.

**Correct:**
```
send_message(target="weixin", message="MEDIA:~/Desktop/hermes production/gaming_girl.jpg")
```

Always compress to 100-300KB before sending:
```bash
sips -s format jpeg -s formatOptions 70 ~/Desktop/hermes production/output.png --out ~/Desktop/hermes production/output.jpg
```

### 🚨 NEVER FORGET THE MEDIA: PREFIX (HARD STOP)

**Pitfall observed 2026-07-09 (MagSafe SSD session):** Generated V2 image successfully (116KB JPEG saved to `~/Desktop/hermes production/magsafe_ssd_v2.jpeg`), explained in detail what the image contained, but **forgot to actually send the image to user via WeChat**. User had to explicitly say "你冇send過嚟WeChat 我睇唔到".

**Lesson**: After generating ANY image, the final message **MUST include `MEDIA:<absolute_path>`** as the last line. Do NOT just describe what the image contains — the user wants to SEE it, not read about it.

**Workflow enforcement**:
1. Generate image → save to `~/Desktop/hermes production/`
2. Compress with sips to <300KB JPEG
3. Verify file exists and is readable
4. **Always end response with**: `MEDIA:/absolute/path/to/compressed.jpg`
5. For WeChat delivery (this user's primary platform), the `MEDIA:` prefix in the message body is what makes the image actually render — a bare path silently fails.
---

## execute_code Sandbox Quirks

**execute_code sandbox does NOT auto-import `os`** — you MUST explicitly `import os` in every script, or `os.path.expanduser()` will raise `NameError: name 'os' is not defined`.

```python
# Always include os even if you think it's built-in
import os, urllib.request, json, ssl
```

Also: execute_code jobs can be interrupted by new user messages. For multi-step image gen (generate → save URL → download), prefer terminal commands for stability, or accept that intermediate steps may need to be re-run.

---

## ⚠️ WeChat Media Sending — CRITICAL

**`send_message(target="weixin", message="/path/to/file.jpg")` SUCCEEDS but the image does NOT appear in WeChat.** This is a known issue — WeChat requires the `MEDIA:` prefix in the message body.

**Correct:**
```
send_message(target="weixin", message="MEDIA:~/Desktop/hermes production/gaming_girl.jpg")
```

Always compress to 100-300KB before sending:
```bash
sips -s format jpeg -s formatOptions 70 ~/Desktop/hermes production/output.png --out ~/Desktop/hermes production/output.jpg
```

### 🚨 NEVER FORGET THE MEDIA: PREFIX (HARD STOP)

**Pitfall observed 2026-07-09 (MagSafe SSD session):** Generated V2 image successfully (116KB JPEG saved to `~/Desktop/hermes production/magsafe_ssd_v2.jpeg`), explained in detail what the image contained, but **forgot to actually send the image to user via WeChat**. User had to explicitly say "你冇send過嚟WeChat 我睇唔到".

**Lesson**: After generating ANY image, the final message **MUST include `MEDIA:<absolute_path>`** as the last line. Do NOT just describe what the image contains — the user wants to SEE it, not read about it.

**Workflow enforcement**:
1. Generate image → save to `~/Desktop/hermes production/`
2. Compress with sips to <300KB JPEG
3. Verify file exists and is readable
4. **Always end response with**: `MEDIA:/absolute/path/to/compressed.jpg`
5. For WeChat delivery (this user's primary platform), the `MEDIA:` prefix in the message body is what makes the image actually render — a bare path silently fails.

---

## FAL_KEY — DO NOT MENTION

**Never mention FAL_KEY to the user.** If the image_generate tool fails, do not explain why or what FAL_KEY is. Simply use the direct Python/curl approach via MiniMax as described above. The user does not need to know about this infrastructure detail.

---

## Session Learnings
- `references/minimax-image01-verified-20260707.md` — 2026-07-07 verified payload, response format, OSS curl workaround
- `references/minimax-image-01-verified-20260707.md` — full session record
- `references/session-20250512-hair-highlights.md` — concrete example: hair highlights only on tips (發尾), cat style preferences, model selection reminder
- `references/session-20260512-slim-vface-prompts.md` — V-face/slim body/center part prompt modifiers (qwen-image-2.0-pro, deprecated endpoint)
- `references/session-20260514-ghibli-refinement.md` — spatial/color correction patterns
- `references/session-20260514-style-transfer-intent.md` — style transfer interpretation rules
- `references/session-20260708-macau-senado.md` — 2026-07-08 Macau Senado Square session: cinematic dusk prompt, verified 22s gen / 379KB raw / 233KB compressed, **user decision to deprecate Token Plan models**, memory-overflow pitfall lesson
- ~~`references/token-plan-verified-20250512.md`~~ — **DEPRECATED 2026-07-08**, archived to `references/deprecated-20260708/` (Token Plan endpoint 唔再用)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| SiliconFlow DNS fail (`api.siliconflow.io`) | Use `.cn` domain not `.io` |
| WeChat media send timeout | Switch to Telegram immediately as fallback |
| SiliconFlow S3 download timeout | Switch to MiniMax image-01 with base64 format |
| `ModuleNotFoundError: No module named 'PIL'` | `python3 -m pip install Pillow` |
| `NameError: name 'os' is not defined` in execute_code | Always `import os` explicitly |
| Image gen interrupted by new user message | Re-run generation; keep URL file for re-download |
| Token Plan endpoint 404 / "Model not exist" | 唔好再用 — 已 deprecated，行 MiniMax image-01 |

## Cross-Session Pitfalls (Lessons That Spilled Beyond This Skill)

### ⚠️ Memory tool char limit (2,200) — batch condense, don't atomically replace
When removing deprecated entries (e.g. Token Plan qwen/wan), surrounding stale entries (e.g. daily LobsterAI sync stats) can push the result past 2,200 chars even when the individual remove+add looks small. **Always batch-condense in ONE call** — the memory tool checks the FINAL state, not per-operation, so a single `operations` array with multiple removes and one add succeeds where 2 separate calls each fail.

Rule of thumb: before any memory edit, mentally compute (current_chars - chars_to_remove + chars_to_add). If close to 2,200, include `replace` on the longest surrounding entries in the same batch.

### ⚠️ Sync-time audit: SKILL.md wording can drift from the latest user directive
On 2026-07-22 the v1.2.0 of this skill still said "HARD STOP 必須問模型" while user had moved to "default MiniMax image-01, no model-selection question" on 2026-07-09. The sync agent caught the contradiction and bumped to v1.3.0 with corrected wording before copying. **Any user-facing workflow skill that contains a MUST / HARD STOP / NEVER directive should be re-audited at sync time against the latest durable user directive** (`~/.hermes/memories/USER.md` + `MEMORY.md` on Hermes, or the equivalent on the destination). The audit lives in the `devops/agent-memory-sync` workflow under the portable-skill-update-workflow reference.

Detection heuristic: `grep -nE 'MUST|HARD STOP|NEVER|必須' "$SKILL/SKILL.md"` and ask "does this absolute wording still match the user's most recent expressed preference?" If not, fix the source first, bump the version, then copy. This is a separate concern from a content-hash mismatch on the same skill — a same-name skill with byte-different content can be a legitimate update OR a sign that the destination carries a runtime-specific variant that should not be overwritten.
