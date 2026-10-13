# Token Plan API - Verified Working (2025-05-12)

## Confirmed Working Configuration

**Endpoint:**
```
https://token-plan.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
```

**API Key:** `TOKEN_PLAN_API_KEY` from `~/.hermes/.env`

**Model:** `qwen-image-2.0`

**Payload format (two wrapping styles, both work):**

Style A — flat messages (simpler):
```json
{
  "model": "qwen-image-2.0",
  "messages": [{"role": "user", "content": [{"type": "text", "text": "<PROMPT>"}]}],
  "size": "1024*1024"
}
```

Style B — input-wrapped (as of 2025-05-12):
```json
{
  "model": "qwen-image-2.0",
  "input": {
    "messages": [{"role": "user", "content": [{"type": "text", "text": "<PROMPT>"}]}]
  },
  "parameters": {"size": "1024*1024"}
}
```

⚠️ **CRITICAL:** `content` MUST be a list of objects with `"type": "text"` and `"text": "..."` keys. A bare string `"content": "prompt text"` returns `InvalidParameter: Input should be a valid list: input.messages.0.content`.

**Auth header:** `Bearer <TOKEN_PLAN_API_KEY>`

**Response:** URL in `output.choices[0].message.content[0].image`

## Failed Approaches Tried (2025-05-12)

### 1. FAL API (`image_generate` tool)
```
Error: FAL_KEY environment variable not set
```
**Lesson:** NEVER try FAL. It requires a key that doesn't exist in this environment.

### 2. Wrong Token Plan endpoints
Tried these and got `"Model not exist"` errors:
- `/images/generations` with various model names (qwen-vl-plus, qwen-vl-max, qwen-image-v1, wanx-v1)
- `/services/aigc/text2image/image-synthesis`
- `/v1/images/generations`

**Lesson:** Only `/api/v1/services/aigc/multimodal-generation/generation` works with qwen-image-2.0.

### 3. urllib download failures
`urllib.request.urlopen()` on Token Plan's OSS presigned URLs returns HTTP 403 in the execute_code sandbox.

**Lesson:** Use `curl -sL -o <path> <url>` instead.

### 4. Presigned URL expiry
The URL in the JSON response contains a signature that expires quickly. Must download immediately.

**Lesson:** Never do generate → wait → download in separate steps.

## Complete Working Script

```python
import subprocess, json, os, urllib.request

env_path = os.path.expanduser("~/.hermes/.env")
api_key = None
with open(env_path) as f:
    for line in f:
        if 'TOKEN_PLAN_API_KEY' in line:
            api_key = line.split('=')[1].strip().strip('"')
            break

url = "https://token-plan.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

prompt = "your prompt here"

payload = {
    "model": "qwen-image-2.0",
    "input": {"messages": [{"role": "user", "content": [{"text": prompt}]}]},
    "parameters": {"size": "1024*1024"}
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}, method="POST")

with urllib.request.urlopen(req, timeout=120) as response:
    result_json = json.loads(response.read().decode("utf-8"))

image_url = result_json["output"]["choices"][0]["message"]["content"][0]["image"]

# Download immediately with curl
output_path = os.path.expanduser("~/Desktop/hermes production/output.png")
subprocess.run(["curl", "-sL", "-o", output_path, "--max-time", "120", image_url], check=True)

# Compress and resize
jpg_path = os.path.expanduser("~/Desktop/hermes production/output.jpg")
subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", output_path, "--out", jpg_path])
subprocess.run(["sips", "-z", "600", "600", jpg_path, "--out", jpg_path])
```

## WeChat Send
```python
send_message(target="weixin", message="MEDIA:~/Desktop/hermes production/output.jpg")
```
