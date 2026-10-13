# Weixin (WeChat) inbound media + session troubleshooting

Adapter source: `~/.hermes/hermes-agent/gateway/platforms/weixin.py` — read it before guessing at behaviour; the doc page and the code drift apart.

## Inbound message shape

Long-poll `getupdates` returns messages carrying `item_list`. Each entry has an integer `type`, and the adapter dispatches on it via `_INBOUND_MEDIA`:

| type | item key | download timeout | cached as |
|---|---|---|---|
| 1 | `text_item` | — | text |
| 2 | `image_item` | 30 s | `.jpg` |
| 3 | `voice_item` | 60 s | `.silk`, then central STT re-transcribes |
| 4 | `file_item` | 60 s | original filename preserved |
| 5 | `video_item` | 120 s | `video.mp4` |

`ref_msg` (quoted/replied-to) media is collected too, so a reply-to-image gives context.

For images the adapter accepts EITHER a hex `aeskey` sitting beside the media block OR `media.aes_key` base64 — prefer whichever is present. A hex `aeskey` on `image_item` is a real shape, not a typo.

Voice is always downloaded raw and re-transcribed locally; Tencent's own `voice_item.text` STT is unreliable for non-Chinese audio. Do not treat that field as the transcript.

## Media is AES-128-ECB over the CDN

Fetch path is `WEIXIN_CDN_BASE_URL` (default `https://novac2c.cdn.weixin.qq.com/c2c`)/download?encrypted_query_param=... , then AES-128-ECB decrypt with the item's key. Outbound uses `ilink/bot/getuploadurl`. Needs the `cryptography` package.

## Reading the diagnosis from the log

The single inbound log line settles which layer broke:

```
[Weixin] inbound from=<id> type=dm media=N
```

- `media=0` on a text-only message → the upstream delivered no attachment item. Protocol-layer limitation, not a Hermes bug, not a decrypt problem, not a user-side Android setting. Escalating to Android settings wastes the user's time.
- `media=N>0` alongside `image download failed: <exc>` → item arrived, CDN fetch or decrypt failed. Check `cryptography` is installed and that `novac2c.cdn.weixin.qq.com` is reachable.

Search the same window for `download failed` (search_files against `~/.hermes/logs/gateway.log`) to get the exception text.

## Stale `context_token` on proactive sends

Symptom, in `gateway.log` and `errors.log`:

```
[Weixin] session expired for <id>; retrying without context_token
[Weixin] send failed to=<id>: iLink sendmessage session not ready: ret=-2 errcode=None
        errmsg=prepare failed — the user must send the bot a message first (or re-pair)
```

Cause: iLink requires a `context_token` echoed back per peer, sourced from that peer's latest inbound message. Tokens persist to `~/.hermes/weixin/accounts/<account_id>.context-tokens.json`. When no inbound message has arrived recently (idle TTL, or the only traffic is a cron push), the token is stale.

The adapter retries once without the token, and `weixin: restored N context token(s)` appears in the log. So a stray `restored` line is normal and self-healing — **do not report it as an error the user needs to act on**. It only becomes a real problem when the retry also fails, which happens on a never-paired bot. Cron deliveries show this as a delivery error followed by a `falling back to standalone` warning.

## Rerunning QR login

Only needed for `errcode=-14` (session expired) or a genuinely unpaired bot: `hermes gateway setup`. Requires `aiohttp` + terminal QR support from the `messaging` extra, otherwise install with `python -c "import pm; pm.sync_venv(['messaging'], explicit=True)"`.

## What does not work

- Group messages from a QR-login `...@im.bot` identity are generally not delivered by iLink at all; `group_policy` changes have no effect. Missing raw inbound group events means the limitation is upstream, so don't debug Hermes config.
- If media never arrives on Weixin from a phone client, do not keep hunting Android send-mode variations. Move the payload to a channel that carries it.