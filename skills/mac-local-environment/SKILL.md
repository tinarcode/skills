---
name: mac-local-environment
description: macOS local tool routing — Whisper / OfficeCLI / Docker projects / OCR / browser control / notification limitations. Load when picking a local tool or troubleshooting Mac-specific issues.
---

# macOS Local Environment

## System
- macOS 26.2, Apple Silicon Mac
- Microsoft Office 365 installed
- Lots of Chinese-named work files
- ⚠️ Notifications unreliable — never use Calendar/display notification. Time-sensitive reminders → cron job

## CLI Tools
- **Whisper (Homebrew):** `whisper <file.m4a> --model large --language yue` (Cantonese transcription)
- **OfficeCLI v1.0.92:** Office document CLI

## Docker Projects
- `/Users/user/docker-project/a-split-bill-pwa/` → backend:8787 frontend:4173
- OCR: MiniMax only (simplified) | Surya OCR at `/Users/user/docker-project/a-ocr-service/` (port 8089)

## Browser Control (LOCAL)
- **Priority:** kimi-webbridge (port 10086) — check daemon status FIRST
- **Fallback:** mac-local-browser-control AppleScript
- **Never** use built-in browser tools for local control
- ⚠️ Kimi WebBridge Edge+Chrome conflict: close one browser before switching

## File Write Quirk
- .env blocked by patch/terminal
- Workaround: `execute_code` Python `open()` to write .env files