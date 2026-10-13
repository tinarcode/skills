# MiniMax API Probe Results — 2026-07-08

Verified via direct API calls against `api.minimaxi.com/v1` using `MINIMAX_CN_API_KEY`.

## Endpoint Inventory

| Endpoint | Method | Status |
|----------|--------|--------|
| `/v1/models` | GET | ✅ returns 8 chat LLMs only (M2 / M2.1 / M2.5 / M2.7 / M3 + highspeed variants) |
| `/v1/t2a_v2` | POST | ✅ works for 6 TTS models |
| `/v1/music_generation` | POST | ✅ works for music-2.6 (lyrics only) |
| `/v1/video_generation` | POST | ✅ works for Hailuo-2.3 + video-01 |
| `/v1/voices` | GET | ❌ 404 |
| `/v1/voice` | GET | ❌ 404 |
| `/v1/voice/voices` | GET | ❌ 404 |
| `/v1/voice/list` | GET | ❌ 404 |
| `/v1/voice/available` | GET | ❌ 404 |
| `/v1/voice/clone` | GET | ❌ 404 |
| `/v1/music/voices` | GET | ❌ 404 |
| `/v1/music` | GET | ❌ 404 |

## TTS Models — All Verified

| Model | Audio returned | Status |
|-------|----------------|--------|
| `speech-01-hd` | 18420 bytes | ✅ |
| `speech-01-turbo` | 16692 bytes | ✅ |
| `speech-02-hd` | 15540 bytes | ✅ recommended |
| `speech-02-turbo` | 14964 bytes | ✅ |
| `speech-2.5-hd-preview` | 18996 bytes | ✅ |
| `speech-2.5-turbo-preview` | 13812 bytes | ✅ |

All returned valid mp3 with ID3 header. Test text: "test".

❌ **`speech-2.6-hd`, `speech-2.8-hd` etc. — DO NOT EXIST**. The `minimax-media` SKILL.md previously listed these (incorrectly). Real model family is 01 / 02 / 2.5-preview.

## Music Models — Verified Only `music-2.6` Works

| Model | Mode | Status | Time | Output |
|-------|------|--------|------|--------|
| `music-2.6` | lyrics | ✅ | 56.6s | 1.6MB / 103824ms mp3 |
| `music-2.6` | instrumental | ❌ | timeout >60s | hang |
| `music-2.6-free` | instrumental | ❌ | timeout >60s | hang |
| `music-01` | any | ❌ | <1s | 2013 "cannot use music-02 params on music-01 model" |
| `music-02` | any | ❌ | <1s | 2013 "invalid model" |
| `music-1.5` / `music-2.0` | any | ❌ | timeout | hang |

Successful payload (lyrics mode):
```json
{
  "model": "music-2.6",
  "prompt": "slow Cantonese ballad, melancholic, emotional, solo piano with soft strings, 65 BPM",
  "lyrics": "[verse]\n夜深咗 街燈照住我\n[chorus]\n回憶太重 寂寞太濃",
  "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3"}
}
```

⚠️ **Instrumental mode hangs server-side**. Always provide actual lyrics.

## Video Models — Only `MiniMax-Hailuo-2.3` and `video-01` Work

| Model | Status |
|-------|--------|
| `MiniMax-Hailuo-2.3` | ✅ returns task_id |
| `video-01` | ✅ returns task_id |
| `hailuo-02` | ❌ 2013 "incorrect model param input" |
| `MiniMax-Video-01` | ❌ 2013 "incorrect model param input" |

Polling endpoint NOT YET VERIFIED — based on common pattern, likely:
- `GET /v1/query/video_generation?task_id=<task_id>`

## Response Format Quirks

### TTS response
```json
{
  "data": {"audio": "4944330400000000086a54585858..."},
  "trace_id": "069cd9afdb5bbf3c982eb23db688f5d8",
  "base_resp": {"status_code": 0, "status_msg": "success"}
}
```
- `audio` is **hex-encoded bytes** (NOT base64)
- Use `bytes.fromhex()` to decode

### Music response
```json
{
  "data": {"audio": "hex...", "status": 2},
  "trace_id": "069cd9d49ace1aa6ade3b1b8c284fdf0",
  "extra_info": {
    "music_duration": 103824,
    "music_sample_rate": 32000,
    "music_channel": 2,
    "bitrate": 128000,
    "music_size": 1662900
  },
  "base_resp": {"status_code": 0, "status_msg": "success"}
}
```

### Video response
```json
{
  "task_id": "417410834858279",
  "base_resp": {"status_code": 0, "status_msg": "success"}
}
```

## Known Voice IDs (verified to work)

- `female-shaonv` (普通話 少女)
- `Cantonese_ProfessionalHost(F)` (粵語 專業女主持)
- `Cantonese_GentleLady` (粵語 溫柔女聲)
- `Cantonese_CuteGirl` (粵語 可愛女孩)
- `Cantonese_KindWoman` (粵語 善良女聲)
- `Cantonese_PlayfulMan` (粵語 活潑男聲)

Other voice IDs must be sourced from the MiniMax Audio web UI (https://hailuoai.com/audio) since no list endpoint exists.