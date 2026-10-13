# MiniMax image-01 — Verified Working (2026-07-07)

Session-verified end-to-end generation of a 16:9 rocket launch scene.
Use this reference whenever MiniMax is the chosen model — it captures
the exact payload, response shape, download workaround, and timing.

## Endpoint

```
POST https://api.minimaxi.com/v1/image_generation
Authorization: Bearer <MINIMAX_CN_API_KEY>   # sk-cp-...  format, 125 chars
Content-Type: application/json
```

## Verified Request Payload

```json
{
  "model": "image-01",
  "prompt": "A dramatic rocket launch scene, ...",
  "aspect_ratio": "16:9",
  "n": 1,
  "response_format": "url",
  "prompt_optimizer": true
}
```

Field notes (all confirmed 2026-07-07):

| Field | Allowed | Notes |
|-------|---------|-------|
| `model` | `image-01` | only model currently exposed for image gen |
| `prompt` | string | natural-language, ~free length |
| `aspect_ratio` | `1:1`, `16:9`, `9:16`, `4:3`, `3:4` (etc.) | affects output canvas |
| `n` | 1–9 | batch of N images returned |
| `response_format` | `url` (recommended) / `base64` | `url` saves base64 decode + is faster downstream |
| `prompt_optimizer` | `true` / `false` | `true` improves simple prompts; safe default |

## Verified Response (url mode)

```json
{
  "id": "069c01...",
  "data": {
    "image_urls": [
      "https://hailuo-image-algeng-data.oss-cn-wulanchabu.aliyuncs.com/image_inference_output%2F...aigc.jpeg?Expires=...&OSSAccessKeyId=...&Signature=..."
    ]
  },
  "metadata": {"failed_count": "0", "success_count": "1"},
  "base_resp": {"status_code": 0, "status_msg": "success"}
}
```

`base_resp.status_code == 0` is the success marker. Anything else → abort.

**OSS URL is presigned but expires fast.** Download within the same script.
`urllib.request.urlopen` → **403 Forbidden** on these URLs.
Always use `curl -sL` (or `urllib.request.urlretrieve` on a fresh URL, with
fallback to curl if the file comes back <10 KB).

## End-to-End Template

```bash
cat > /tmp/img_gen/gen.py << 'PYEOF'
import urllib.request, json, os, subprocess, time

api_key = None
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if "MINIMAX_CN_API_KEY" in line and not line.strip().startswith("#"):
            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
assert api_key and api_key.startswith("sk-cp-")

payload = {
    "model": "image-01",
    "prompt": "<YOUR PROMPT>",
    "aspect_ratio": "16:9",
    "n": 1,
    "response_format": "url",
    "prompt_optimizer": True,
}

req = urllib.request.Request(
    "https://api.minimaxi.com/v1/image_generation",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Authorization": f"Bearer {api_key}",
             "Content-Type": "application/json"},
    method="POST",
)
t0 = time.time()
with urllib.request.urlopen(req, timeout=120) as resp:
    result = json.loads(resp.read())
print(f"Generate: {time.time()-t0:.1f}s, status={result['base_resp']}")

url = result["data"]["image_urls"][0]
out = os.path.expanduser("~/Desktop/hermes production/<NAME>.jpg")
os.makedirs(os.path.dirname(out), exist_ok=True)
subprocess.run(["curl", "-sL", "-o", out, "--max-time", "120", url], check=True)
print(f"OK: {out} ({os.path.getsize(out)//1024} KB)")

# Optional: WeChat-friendly compressed JPEG
wechat = out.replace(".jpg", "_wechat.jpg")
subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "75",
                out, "--out", wechat], check=True, capture_output=True)
print(f"WeChat: {wechat} ({os.path.getsize(wechat)//1024} KB)")
PYEOF
python3 /tmp/img_gen/gen.py
```

## Measured Performance (2026-07-07, Mac Mini M-series, .cn region)

| Stage | Time |
|-------|------|
| Generate POST | ~21.9 s |
| URL → local JPG via curl | ~1 s |
| sips compress to WeChat size | ~0.5 s |
| **Total** | **~24 s for 1 image (316 KB JPG)** |

## Gotchas

- **`image_generate` built-in tool requires `FAL_KEY`** which is NOT set.
  Skip it and use this direct Python path. Don't mention `FAL_KEY` to the
  user (per image-generation-workflow pitfalls).
- **`MINIMAX_CN_API_KEY` masking**: `grep`/`cat` of `.env` returns
  `sk-cp-TX...***` — read the file in Python directly and never print the
  key. Same masking applies inside `execute_code` sandbox.
- **MiniMax API key (`sk-cp-...`) ≠ Token Plan key (`sk-sp-...`)** and
  ≠ SiliconFlow key (`sk-scl...`). Pick the wrong key for the wrong
  endpoint → 401. Endpoint summary table is in the parent SKILL.md.

## Sanity Check

After saving the JPG, validate:
```python
assert os.path.getsize(out) > 50_000, "Image suspiciously small"
with open(out, "rb") as f:
    head = f.read(4)
    assert head[:3] == b"\xff\xd8\xff", "Not a valid JPEG"  # JPEG magic
```

If `head[:8] == b"\x89PNG\r\n\x1a\n"` → it's a PNG instead (some prompts
return PNG); sips `--out` still works either way.
