---
name: minimax-model-stack
description: MiniMax + SiliconFlow model routing for image / TTS / music / video generation — load when generating media or choosing fallback models.
---

# MiniMax Model Stack (2026-07-09 state)

## API Keys
- **DEPRECATED 2026-07-08:** Token Plan — do not use
- **MiniMax image-01:** `sk-cp-...` → env `MINIMAX_CN_API_KEY`, endpoint `api.minimaxi.com/v1`
- **SiliconFlow (backup):** `sk-scl...ovxl`
- **DeepSeek:** `api.deepseek.com/v1`
- **PaddleOCR:** `bc4791736f...` → `paddleocr.aistudio-app.com`

## Image Generation
- **Default:** MiniMax image-01 (api.minimaxi.com/v1/image_generation) ~22s
- **Fallback:** SiliconFlow Kwai-Kolors
- ⚠️ User confirmed 2026-07-09: do NOT re-ask for model choice

## TTS (speech-02 / speech-01 / 2.5)
- Endpoint: `api.minimaxi.com/v1/t2a_v2`
- **Mandarin:** `female-shaonv` (少女音色, default)
- **Cantonese:** `Cantonese_ProfessionalHost(F)` (default; alts: CuteGirl / GentleLady / KindWoman)
- Returns hex audio — decode before playback

## Music Generation
- Model: `music-2.6 music_generation`
- Latency: ~57s / ~104s per song
- ⚠️ **必須有 lyrics, 唔可以 instrumental**

## Video Generation
- Models: `MiniMax-Hailuo-2.3` / `video-01`
- Async — poll task_id until complete

## Chat / Reroll Model Catalog (verified 2026-10-07)
`GET https://api.minimaxi.com/v1/models` returns ONLY the public catalog:
- `MiniMax-M3` (current default, ~knowledge cutoff 2026-01)
- `MiniMax-M2.7`, `MiniMax-M2.7-highspeed`
- `MiniMax-M2.5`, `MiniMax-M2.5-highspeed`
- `MiniMax-M2.1`, `MiniMax-M2.1-highspeed`
- `MiniMax-M2`

### Preview / Internal Models
`MiniMax-M3.1-Flash-Preview` — preview reasoning model, has `thinking` blocks + cache-friendly (verified 91% cache hit on repeated prompt), uses both `/anthropic/v1/messages` and `/v1/chat/completions`.
- Catalog status moved: **as of 2026-10-13 it IS listed in `GET /v1/models`** (was absent on 2026-10-07). Never assume a model id is invalid just because the catalog omits it — some preview ids get promoted later, so probe directly.
- To verify a candidate id: POST to `/v1/chat/completions` with `{"model":"X","max_tokens":20,"messages":[{"role":"user","content":"PONG"}]}` and check `status_code: 0` in `base_resp`

### Thinking / Reasoning Models
Response includes `reasoning_content` (OpenAI-compat) or `thinking` blocks + `signature` (Anthropic-compat). Usage reports separate `reasoning_tokens` and cache_creation/cache_read tokens — useful for cost tracking on chained reasoning calls.