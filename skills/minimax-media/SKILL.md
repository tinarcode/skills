---
name: minimax-media
description: "MiniMax media generation suite: TTS (text-to-speech via t2a_v2), music generation (music-2.6), and video generation (Hailuo). All three share api.minimaxi.com + MINIMAX_CN_API_KEY. Trigger: any MiniMax audio/song/video generation request. Verified 2026-07-08 against real API."
version: 2.0.0
---
---

# MiniMax Media Generation

Unified skill for MiniMax TTS (speech synthesis) and video generation (Hailuo). Both tools share the same API endpoint (`api.minimaxi.com`) and API key (`MINIMAX_CN_API_KEY`).

## ⚠️ CRITICAL: Correct Endpoint

`api.minimax.io` and `api.minimaxi.com` are DIFFERENT endpoints with DIFFERENT API keys!
- `api.minimax.io` → requires separate key, returns `invalid api key`
- `api.minimaxi.com` → use `MINIMAX_CN_API_KEY` (configured in `~/.hermes/.env`)

---

## Image Analysis (Vision)

> 📁 See `references/minimax-vision.md` for WeChat image cache paths and the `mcp_minimax_understand_image` MCP tool (use this instead of `vision_analyze` which fails with 401).

---

## Section: TTS (Text-to-Speech)

### Trigger
User asks to convert text to speech / 文字轉語音

### API
- **Endpoint:** `https://api.minimaxi.com/v1/t2a_v2`
- **Key:** `MINIMAX_CN_API_KEY`
- **Verified Models (2026-07-08 real API probe):**
  - `speech-01-hd` / `speech-01-turbo` (older)
  - `speech-02-hd` ⭐ / `speech-02-turbo` (recommended, 99% voice similarity)
  - `speech-2.5-hd-preview` / `speech-2.5-turbo-preview` (latest preview)
  - ❌ `speech-2.6-hd` / `speech-2.8-hd` — these model IDs are NOT valid (returns error). 6 models above are the verified working set.

### ⚠️ CRITICAL: Audio is HEX, not base64

`result["data"]["audio"]` is **hex-encoded** bytes (not base64!). Decode with `bytes.fromhex()`, NOT `base64.b64decode()`.

```python
# CORRECT:
audio_data = bytes.fromhex(result["data"]["audio"])

# WRONG — will fail:
# audio_data = base64.b64decode(result["data"]["audio"])
```

### Python Call (verified 2026-07-08)
```python
import urllib.request, json, os

with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if "MINIMAX_CN_API_KEY" in line:
            api_key = line.split("=", 1)[1].strip().strip('"').strip()
            break

url = "https://api.minimaxi.com/v1/t2a_v2"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

payload = {
    "model": "speech-02-hd",       # ⭐ recommended
    "text": "<文字>",
    "stream": False,
    "voice_setting": {
        "voice_id": "female-shaonv",  # 普通話 少女音色 (預設)
        "speed": 1, "vol": 1, "pitch": 0
    },
    "audio_setting": {
        "sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1
    }
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())

# Hex decode (NOT base64)
audio_data = bytes.fromhex(result["data"]["audio"])
with open(os.path.expanduser('~/Desktop/hermes production/output.mp3'), 'wb') as f:
    f.write(audio_data)
```

### Voice Preferences

**user預設：**
| 語言 | Voice ID | 名稱 |
|------|----------|------|
| 普通話 | `female-shaonv` | 少女音色（預設）|
| 粵語 | `Cantonese_ProfessionalHost(F)` | 專業女主持（預設）|

**其他可用音色（已 verify 2026-07-08）：**
- 普通話: `female-shaonv` (少女, 預設)
- 粵語: `Cantonese_ProfessionalHost(F)` (專業女主持, 預設), `Cantonese_GentleLady` (溫柔女聲), `Cantonese_CuteGirl` (可愛女孩), `Cantonese_KindWoman` (善良女聲), `Cantonese_PlayfulMan` (活潑男聲)

⚠️ **Voice list endpoint NOT exposed** — `GET /v1/voices`, `/v1/voice`, `/v1/voice/available` all return 404. Voice IDs must be hard-coded from the MiniMax Audio web UI (https://hailuoai.com/audio). When in doubt, use the verified defaults above.

### Delivery
```python
send_message(target="weixin", message=os.path.expanduser("~/Desktop/hermes production/output.mp3"))
```

### Pitfalls
- **Hex encoding, not base64** — `bytes.fromhex()` is the ONLY correct decoder.
- **Empty `voice_id`** → error 2013. Always set `voice_setting.voice_id`.
- **Streaming mode (`stream: true`)** requires hex output_format; can't combine with `url`.
- **`.env` key is masked** by `cat`/`grep` — always read with Python `open()` and never echo.
- **Long text (>10K chars)** — use async t2a_async endpoint with file upload, NOT sync t2a_v2.

---

## Section: Video Generation (Hailuo)

### Trigger
User asks to generate a video / 生成影片

### API
- **Endpoint:** `https://api.minimaxi.com/v1/video_generation`
- **Key:** User's MiniMax API key (starts with `sk-cp-`)
- **Poll:** `https://api.minimaxi.com/v1/query/video_generation?task_id=...`
- **File retrieve:** `https://api.minimaxi.com/v1/files/retrieve?file_id=...`

### Models
| Model | Status (2026-07-08) | Duration | Resolution | Notes |
|-------|---------------------|----------|------------|-------|
| MiniMax-Hailuo-2.3 | ✅ verified | 6 or 10s | 768P (default), 1080P | Best for text-to-video, returns task_id |
| video-01 | ✅ verified | TBD | TBD | Returns task_id (also works) |
| MiniMax-Hailuo-02 | ❌ invalid | — | — | Returns 2013 "incorrect model param input" |
| MiniMax-Video-01 | ❌ invalid | — | — | Returns 2013 "incorrect model param input" |
| T2V-01-Director | unverified | 6 or 10s | 768P | Camera movement via [command] syntax |
| T2V-01 | unverified | 6 or 10s | 768P | Basic model |

### Generate Video (Text-to-Video)
```python
import json, urllib.request, os, time

api_key = "USER_API_KEY"
url = "https://api.minimaxi.com/v1/video_generation"

data = {
    "model": "MiniMax-Hailuo-2.3",
    "prompt": "Your video description here",
    "duration": 6,
    "resolution": "768P"
}

req = urllib.request.Request(
    url, data=json.dumps(data).encode(),
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read())
    task_id = result['task_id']
    print(f"Task submitted: {task_id}")
```

### ⚠️ Critical: Correct Parameter Format
**WRONG (will fail "prompt can't be empty"):**
```json
{"model": "...", "input": {"prompt": "..."}, "parameters": {...}}
```
**CORRECT:**
```json
{"model": "...", "prompt": "...", "duration": 6, "resolution": "768P"}
```
The prompt goes at the top level, NOT wrapped in `input` object.

### Poll for Status
```python
for attempt in range(30):
    status_url = f"https://api.minimaxi.com/v1/query/video_generation?task_id={task_id}"
    req = urllib.request.Request(status_url, headers={"Authorization": f"Bearer {api_key}"}, method="GET")
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
        status = result.get('status')
        
        if status == 'Success':
            file_id = result['file_id']
            break
        elif status == 'Fail':
            print(f"Failed: {result}")
            break
        # status_code 12002 = still processing
    time.sleep(5)
```

### Download Video
```python
retrieve_url = f"https://api.minimaxi.com/v1/files/retrieve?file_id={file_id}"
req = urllib.request.Request(retrieve_url, headers={"Authorization": f"Bearer {api_key}"}, method="GET")
with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read())
    download_url = result['file']['download_url']

video_req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(video_req, timeout=180) as vr:
    with open(os.path.expanduser('~/Desktop/hermes production/output_video.mp4'), 'wb') as f:
        f.write(vr.read())
```

### Common Errors
| Error | Cause | Fix |
|-------|-------|-----|
| 2013 "prompt can't be empty" | Wrong JSON format | Use top-level `prompt` not `input.prompt` |
| 2049 "invalid api key" | Wrong endpoint | Use `api.minimaxi.com` not `api.minimax.io` |
| 12002 | Still processing | Keep polling |

### Reference-Based Character Generation
When generating videos of specific characters (user's hamster, cat, etc.), describe them in detail:
```
A cute cartoon hamster and a tiger-stripe Siamese cat standing together.
Hamster: round chubby body, cream/beige colored fur with subtle grey stripe between ears, tiny round pinkish-grey ears, round black shiny eyes with catchlight...
Cat: Lynx Point Siamese, light beige body, dark grey-brown tabby stripes on ears and forehead, ice blue almond-shaped eyes...
Both raising one paw in a 'yeah' gesture, cartoon 3D animation style.
```

### WeChat Delivery
```python
send_message(target="weixin", message="MEDIA:~/Desktop/hermes production/output_video.mp4")
```

---

## Section: Music Generation (music-2.6)

### Trigger
User asks to generate a song / 音樂生成 / 生成歌曲

### API
- **Endpoint:** `https://api.minimaxi.com/v1/music_generation`
- **Key:** `MINIMAX_CN_API_KEY`

### Verified Models (2026-07-08)
| Model | Status | Notes |
|-------|--------|-------|
| `music-2.6` | ✅ (lyrics mode) | 56-67s generation time, ~104s song (~1.6MB mp3, 32000Hz mono) |
| `music-2.6` | ❌ (instrumental mode) | Read timeout >60s — server hangs |
| `music-2.6-free` | ❌ (instrumental mode) | Same hang as paid |
| `music-cover` | unverified | For voice-cloning / cover generation (requires audio_url) |
| `music-cover-free` | unverified | Free tier of music-cover |
| `music-01` / `music-02` | ❌ | Returns 2013 "cannot use music-02 params on music-01 model" — these are LEGACY, do NOT use |

### ⚠️ CRITICAL: Must provide `lyrics`

Instrumental mode (`is_instrumental: true`) **hangs** — server returns no response, times out after 60s+. Always provide actual lyrics, even simple ones like `[verse]\nla la la`.

### Working Payload (verified 2026-07-08)
```python
import urllib.request, json, os

with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if "MINIMAX_CN_API_KEY" in line:
            api_key = line.split("=", 1)[1].strip().strip('"').strip()
            break

payload = {
    "model": "music-2.6",
    "prompt": "slow Cantonese ballad, melancholic, emotional, solo piano with soft strings, 65 BPM",
    "lyrics": "[verse]\n夜深咗 街燈照住我\n獨自行 腳步好沉重\n[chorus]\n回憶太重 寂寞太濃\n點解偏偏係你走",
    "audio_setting": {
        "sample_rate": 32000,
        "bitrate": 128000,
        "format": "mp3"
    }
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    "https://api.minimaxi.com/v1/music_generation",
    data=data,
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    method="POST"
)

# ⏱️ Music gen takes 50-70s — use 120s timeout
with urllib.request.urlopen(req, timeout=120) as resp:
    result = json.loads(resp.read())

if result["base_resp"]["status_code"] == 0:
    # Hex decode (same as TTS)
    audio_data = bytes.fromhex(result["data"]["audio"])
    output = os.path.expanduser("~/Desktop/hermes production/song.mp3")
    with open(output, "wb") as f:
        f.write(audio_data)
    duration_ms = result["extra_info"]["music_duration"]
    print(f"✅ {output} ({len(audio_data)/1024/1024:.2f} MB, {duration_ms/1000:.1f}s)")
```

### Lyrics Format
Supports structure tags (newline-separated):
```
[Intro] / [Verse] / [Pre Chorus] / [Chorus] / [Interlude] / [Bridge] / [Outro]
[Post Chorus] / [Transition] / [Break] / [Hook] / [Build Up] / [Inst] / [Solo]
```
Length: 1-3500 chars.

### Prompt Format
Style + mood + scene + instrumentation + BPM:
```
"indie folk, melancholic, introspective, walking alone at night, 75 BPM"
```
Max 2000 chars.

### Response Format
```json
{
  "data": {
    "audio": "49443304...",  // hex-encoded mp3
    "status": 2
  },
  "trace_id": "069cd9d49ace1aa6ade3b1b8c284fdf0",
  "extra_info": {
    "music_duration": 103824,    // ms
    "music_sample_rate": 32000,
    "music_channel": 2,
    "bitrate": 128000,
    "music_size": 1662900        // bytes
  },
  "base_resp": {"status_code": 0, "status_msg": "success"}
}
```

### Pitfalls
- **Hex encoding, not base64** — same as TTS, use `bytes.fromhex()`.
- **~60s latency** — set `timeout=120` minimum.
- **Instrumental hangs** — never use `is_instrumental: true`.
- **No empty lyrics** — always include at least 1 char of lyrics (server returns 2013).
- **`music-01` / `music-02` are legacy** — return 2013. Use `music-2.6` only.

### Cover Mode (music-cover / music-cover-free) — NOT YET TESTED
For voice cloning / cover generation:
- Pass `audio_url` (max 50MB, 6s-6min, mp3/wav/flac) OR `audio_base64`
- Set `prompt` describing target style (10-300 chars)
- Optional `lyrics` (10-1000 chars)
- `cover_feature_id` from preprocess endpoint for 2-step flow
- ❌ Not verified — flag for future testing.
