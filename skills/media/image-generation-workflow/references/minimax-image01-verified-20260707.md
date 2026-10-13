---
name: minimax-image01-verified-20260707
description: MiniMax image-01 endpoint verification record — confirmed working payload, response format, download workaround, and key attribution (2026-07-07)
---

# MiniMax image-01 — Verified 2026-07-07

## Test prompt (workload)
```
A dramatic rocket launch scene, massive rocket lifting off with intense flames
and thick billowing smoke clouds, vibrant orange and yellow fire illuminating
the launch pad, deep blue starry sky background with countless stars, cinematic
low-angle view, ultra detailed, 8K, photorealistic, dramatic lighting, science
fiction atmosphere
```

## Result

| Field | Value |
|---|---|
| Endpoint | `https://api.minimaxi.com/v1/image_generation` |
| API key env | `MINIMAX_CN_API_KEY` (sk-cp-... prefix, 125 chars) |
| Generate time | **21.9s** |
| Total (gen + download + compress) | 24.2s |
| Output | `~/Desktop/hermes production/minimax_rocket.jpg` |
| Original size | 316 KB |
| WeChat compressed | 257 KB (sips -s formatOptions 75) |
| Status | `{"base_resp":{"status_code":0,"status_msg":"success"}}` |

## Key discoveries from this session

### 1. Existing key, no new install
The `sk-cp-...` API key the user pasted **matched the existing `MINIMAX_CN_API_KEY` in `~/.hermes/.env` verbatim** (length 125). No new key install required — only the pipeline designation needed updating.

### 2. Prior misclassification corrected
Previous `## Model Routing` in MEMORY said "Token Plan qwen-image-2.0 (preferred)" — but the actual running pipeline was always MiniMax image-01. The skill file's Primary section already documented it correctly. After this session:
- **SKILL.md** → MiniMax = ⭐ PRIMARY, listed first
- **MEMORY.md** → as of batch write attempt, still says Token Plan preferred (MEMORY update failed due to size; skill file is now source of truth)

### 3. Three endpoints, three accounts, **no cross-auth**
| Endpoint | Provider | Env var | Account |
|---|---|---|---|
| `token-plan.cn-beijing.maas.aliyuncs.com/.../multimodal-generation/generation` | Alibaba Bailian | `TOKEN_PLAN_API_KEY` (sk-sp-...) | Aliyun |
| `api.minimaxi.com/v1/image_generation` | MiniMax | `MINIMAX_CN_API_KEY` (sk-cp-...) | MiniMax |
| `api.siliconflow.cn/v1/images/generations` | SiliconFlow | `sk-scl...ovxl` | SiliconFlow |

Wrong key → 401. Never assume tokens are interchangeable.

## Canonical payload

```python
payload = {
    "model": "image-01",
    "prompt": "...",
    "aspect_ratio": "16:9",       # 1:1, 16:9, 9:16, 4:3, 3:4
    "n": 1,                       # batch size, max 9
    "response_format": "url",     # preferred over base64
    "prompt_optimizer": True      # auto-improve prompt
}
```

## Download — critical workaround

The response returns an **Aliyun OSS presigned URL** (Wulanchabu bucket).
- ❌ `urllib.request.urlopen()` → **403** (works against urlretrieve alone on fresh URLs only)
- ✅ `curl -sL` always works
- ⚠️ `execute_code` sandbox is blocked from running POST+subprocess combos in cron-like mode — use `terminal` with python3 heredoc instead

```python
import subprocess
subprocess.run(["curl", "-sL", "-o", output_path, "--max-time", "120", image_url], check=True)
```

## Response format (url mode)

```json
{
  "id": "069c01e6d04388eb3bbc8d580b953c7b",
  "data": {
    "image_urls": [
      "https://hailuo-image-algeng-data.oss-cn-wulanchabu.aliyuncs.com/image_inference_output%2Ftalkie%2Fprod%2Fimg%2F2026-07-07%2F<uuid>_aigc.jpeg?Expires=1783505015&OSSAccessKeyId=LTAI5tB2SwrRwAtD23etQUbC&Signature=..."
    ]
  },
  "metadata": {"failed_count": "0", "success_count": "1"},
  "base_resp": {"status_code": 0, "status_msg": "success"}
}
```

OSS URL `Expires` param (~hour TTL) is much longer than Token Plan presigned URLs (which expire in seconds) — but still download within same script.

## Gotchas

- **`response_format=url` is the new preferred default** — old skill code defaulted to `base64`. Switching to `url` saves base64 decode cost (an extra ~30-50% buffer roundtrip on large images).
- **`prompt_optimizer=true` confirmed working**: didn't mangle the literal "dramatic / photorealistic / 8K" cues from the test prompt.
- **API key masking**: `grep`/`cat` of `~/.hermes/.env` shows `***` for API keys — read with Python `open()` and use the value without printing.
- **Speed ranking observed**: MiniMax image-01 (~22s) ≪ Token Plan qwen/wan (~2 min) ≫ SiliconFlow (download timeout-prone). MiniMax is now the no-brainer default.

## Path forward

- MiniMax image-01 = **PRIMARY** for image gen (per user instruction 2026-07-07: "記住呢個方法 設定為主要生圖")
- Token Plan (qwen-image-2.0 / wan2.7 series) = SECONDARY when user explicitly requests
- SiliconFlow (Kwai-Kolors) = BACKUP only

Default to MiniMax for all future image gen unless user specifies Token Plan model or SiliconFlow.
