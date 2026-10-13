---
name: nvidia-vision-backup
description: Use NVIDIA NIM with Qwen3.5-397B as vision backup when MiniMax is overloaded or primary model lacks vision support
category: mlops
triggers:
  - vision backup
  - MiniMax 529 error
  - image analysis failed
  - NVIDIA vision setup
---

# NVIDIA Vision Backup for Hermes Agent

## Overview
When MiniMax (primary model) returns 529 overload errors or DeepSeek (text-only) cannot analyze images, use **NVIDIA NIM** with **Qwen3.5-397B** as the vision backup solution.

## Prerequisites
- NVIDIA API key from https://build.nvidia.com
- Key stored in environment as `NVIDIA_API_KEY`

## Available Models on NVIDIA NIM
- `qwen/qwen3.5-397b-a17b` (recommended for vision)
- `qwen/qwen3.5-122b-a10b`
- `qwen/qwen3-next-80b-a3b-instruct`
- `qwen/qwen3-next-80b-a3b-thinking`
- `qwen/qwen2.5-coder-32b-instruct`

## Usage Pattern

### Direct API Call (Python)
```python
import json, urllib.request, base64
import os

nvidia_key = os.environ.get("NVIDIA_API_KEY")
img_path = "/path/to/image.jpg"

with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "model": "qwen/qwen3.5-397b-a17b",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            {"type": "text", "text": "Describe this image in detail"}
        ]
    }],
    "max_tokens": 1000
}

data = json.dumps(payload).encode()
req = urllib.request.Request(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    data=data,
    headers={"Authorization": f"Bearer {nvidia_key}", "Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())
    print(result["choices"][0]["message"]["content"])
```

### Via Hermes vision_analyze Tool
Once configured in config.yaml, simply call:
```python
vision_analyze(
    image_url="/path/to/image.jpg",
    question="Describe this image in detail"
)
```

## Troubleshooting

### HTTP 403 Forbidden
- Check API key is complete and valid
- Verify key format: `nvapi-<long_string>`

### HTTP 400 Invalid Request
- Ensure image is base64 encoded correctly
- Check model name matches available models on NVIDIA NIM
- Note: DeepSeek models do NOT support vision

### Model Not Found
List available models:
```python
req = urllib.request.Request(
    "https://integrate.api.nvidia.com/v1/models",
    headers={"Authorization": f"Bearer {nvidia_key}"},
    method="GET"
)
```

## Vision Backup: qwen3.6-plus (Simplest)

When MiniMax vision fails (401 Unauthorized / 529 overload), use **qwen3.6-plus** via Token Plan API which already supports vision and has a working API key:

```python
import json, urllib.request, base64

api_key = "sk-sp-djI.gEUF0EP6oSUas_s75Q3ivNVPyK_b8wn_hA2oUIV1Pzu6X_L4Y08_8pQRlQ3M9UpmJpNbbLcD8418VTomZORxeXHYQFDw-bkXSOOGVTibTcCaooimi0T6QWSkVtP_xTtR5kaUA8BliYNLkZuvPxO3GgAmHrEvRcFp7SItvt1wZ0sCTFWjhWg9SCMCe86MU_9e.MEUCIBZEAyuntYTkJ3k7qV2OlJw63Dhr_w2RISaEIFIobvgCAiEA7k95WTPb5NNvHI1hLV100c5KqZlvackn-vtAbRnbaU8"
img_path = "/path/to/image.jpg"

with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

url = "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
data = {
    "model": "qwen3.6-plus",
    "messages": [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
        {"type": "text", "text": "描述呢張圖入面有咩？"}
    ]}],
    "max_tokens": 1000
}

req = urllib.request.Request(url, data=json.dumps(data).encode(),
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())
    print(result["choices"][0]["message"]["content"])
```

## NVIDIA Qwen Vision Workaround (Absorbed from nvidia-qwen-vision-workaround)

### Problem
- `vision_analyze` tool returns 529 (MiniMax overload) or 401 (auth failed)
- Built-in vision tool does NOT auto-fallback to auxiliary.vision config

### Solution: Direct NVIDIA NIM API Call

When MiniMax fails, use `execute_code` to call NVIDIA NIM directly:

```python
import json, urllib.request, base64

nvidia_key = "YOUR_NVIDIA_API_KEY"  # nvapi-xxx format
img_path = "image_path"

with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "model": "qwen/qwen3.5-397b-a17b",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            {"type": "text", "text": "Describe this image"}
        ]
    }],
    "max_tokens": 1000
}

data = json.dumps(payload).encode()
req = urllib.request.Request(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    data=data,
    headers={"Authorization": f"Bearer {nvidia_key}", "Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())
    print(result["choices"][0]["message"]["content"])
```

### Known Limitations
- **MiniMax M2.7 does NOT support image generation** (only vision understanding)
- Image generation requires: NVIDIA FLUX / Google Gemini (imagen-3) / DALL-E

### Important Notes
- `vision_analyze` has a bug — does not use auxiliary.vision config
- MiniMax 529 overload: must use direct call to NVIDIA
- NVIDIA key format: `nvapi-xxx`

---

## vision-backup-nvidia Configuration Notes (Absorbed from vision-backup-nvidia)

### Config Setup
Add to config.yaml under `auxiliary.vision`:
```yaml
provider: nvidia
model: qwen/qwen3.5-397b-a17b
base_url: https://integrate.api.nvidia.com/v1
api_key: ${NVIDIA_API_KEY}
```

### Auto-Fallback Behavior
- Primary: MiniMax-M2.7 (default)
- Vision backup: Qwen3.5-397B on NVIDIA NIM (auto-switches on 529/overload)
- System routes vision requests to backup when primary fails

---

## hermes-vision-config: Vision Provider Comparison (Absorbed)

### Vision Support by Provider

| Provider | Vision Support | Notes |
|----------|---------------|-------|
| **MiniMax-M2.7** | ⚠️ Unreliable | Returns 401/529 frequently; not trustworthy |
| **qwen3.6-plus (Token Plan)** | ✅ Yes | Works reliably, uses existing API key |
| **NVIDIA Qwen3.5-397B** | ✅ Yes | Stable, high-quality, needs separate API key |
| **Gemini** | ✅ Yes | Free tier has vision |
| **OpenAI (GPT-4o)** | ✅ Yes | Stable, needs API key |
| **Anthropic (Claude)** | ✅ Yes | Excellent quality, needs API key |
| **DeepSeek** | ❌ No | Text-only (`deepseek-chat`, `deepseek-reasoner`) |
| **Kimi (Coding)** | ❌ No | Only for coding agents, returns 403 |

### hermes-vision-config: Troubleshooting Flow (Absorbed)

When `vision_analyze` fails:

1. **Check error code**
   - `529` → Provider overloaded → switch to NVIDIA backup
   - `401` → API key invalid
   - `400` → Model doesn't support image input (DeepSeek, Kimi)
   - `403` → API key permissions insufficient (Kimi for Coding)

2. **MiniMax overload note**: vision_analyze sometimes returns generic "I can't see the image" instead of the actual 529 error. Test with a known public URL to expose the real error code.

3. **Fallback chain**: MiniMax vision (→ 401/529) → qwen3.6-plus API directly → NVIDIA Qwen3.5-397B

### hermes-vision-config: API Key Notes (Absorbed)

- Hermes parent process API keys may not be readable in `execute_code` or `terminal` subprocesses
- Keys set in `~/.hermes/auth.json` credential pool must be accessed via Hermes native methods, not direct env extraction

---

## image-analysis-qwen: qwen3.6-plus Direct API (Absorbed)

### When to Use
When MiniMax vision fails (401 Unauthorized / 529 overload), use **qwen3.6-plus** via Token Plan API.

### Quick Call
```python
import json, urllib.request, base64

api_key = "YOUR_TOKEN_PLAN_KEY"
img_path = "/path/to/image.jpg"

with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

url = "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
data = {
    "model": "qwen3.6-plus",
    "messages": [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
        {"type": "text", "text": "描述呢張圖入面有咩？"}
    ]}],
    "max_tokens": 1000
}

req = urllib.request.Request(url, data=json.dumps(data).encode(),
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())
    print(result["choices"][0]["message"]["content"])
```

### Recommended Call Order
1. **First**: `mcp_minimax_understand_image` (MCP tool — already configured and working)
2. **Fallback**: qwen3.6-plus via Python (above method)
3. **Final fallback**: NVIDIA Qwen3.5-397B direct API

### Image → Anime Style Transfer Pipeline (from image-analysis-qwen)
When user sends a photo and asks for anime/stylized version:
1. Analyze the photo with qwen3.6-plus to extract subject descriptions
2. Compose generation prompt: `Studio Ghibli anime style illustration, [subject descriptions], [style keywords], hand-drawn animation aesthetic`
3. Generate with image-generation-workflow

---

## Key Differences from Other Providers

| Provider | Vision Support | Notes |
|----------|---------------|-------|
| MiniMax-M2.7 | ⚠️ Unreliable | Returns 401/529 frequently; not trustworthy |
| qwen3.6-plus (Token Plan) | ✅ Yes | Works reliably, uses existing API key |
| DeepSeek | ❌ No | Text-only (`deepseek-chat`, `deepseek-reasoner`) |
| Kimi (Coding) | ❌ No | Only for coding agents, returns 403 |
| NVIDIA Qwen3.5 | ✅ Yes | Stable, high-quality, needs separate API key |

## Pitfalls

1. **Kimi Coding Key ≠ Moonshot Key**: Coding API keys only work for coding agents
2. **DeepSeek is Text-Only**: Available models do not accept image inputs
3. **MiniMax 529 Errors**: Common during peak hours; NVIDIA backup is more reliable
4. **API Key Format**: Must be complete `nvapi-<key>` string

## When to Use
- MiniMax returns 529 (overloaded)
- Image analysis required and primary model is text-only
- Need stable, high-quality vision without upgrading MiniMax plan
