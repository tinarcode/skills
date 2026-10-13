# Correct Sync Analysis Block — Copy & Modify

**STOP.** If your analysis block starts with anything other than `### ` (markdown header), you have reproduced the `knowledge:` bug. See the skill's ⛔ STOP — PRE-FLIGHT CHECK.

---

### YYYY-MM-DD Agent-Written Sync Results (LobsterAI ↔ Hermes) ###

Sync Trigger: Daily 09:00 cron job
Sync Script:  bash ~/.hermes/scripts/sync-lobsterai.sh (exit_code=0)

Skills (Top-Level):
  - LobsterAI: <N> skills
  - Hermes:    <N> skills
  - Missing in Hermes:  <N>
  - Missing in Lobster: <N>
  ✅ Top-level skills in sync (or note delta)

Memory Diff Check:
  - Hermes MEMORY.md     : <N> lines, last modified YYYY-MM-DD HH:MM
  - Hermes USER.md       : <N> lines, last modified YYYY-MM-DD HH:MM
  - LobsterAI memory DB  : <N> chunks in main.sqlite, last modified YYYY-MM-DD HH:MM
  - Note any file modification since previous sync run

  Core facts present in BOTH (unchanged from prior syncs):
    ✅ API keys, workarounds, browser, TTS, pets, Docker, US-stock, skills index

  LobsterAI-only content (sync log history, not new knowledge):
    - <date> sync log entries (historical, no need to copy to Hermes)

Skills to copy: NONE
Memory to copy: NONE

Sub-skill deltas (intentionally not synced):
  Hermes-only: (empty — since 2026-07-25 09:07 mass-sync, all Hermes top-level skills are also on LobsterAI)
  LobsterAI-only: web-search (Playwright), docx-js, ooxml, html2pptx, ...

🏁 Status: 100% synchronized — no action required.   (or note actual outcome)
   Next sync: YYYY-MM-DD 09:00 cron.

---

## Usage

1. `cp templates/correct-sync-analysis.md /tmp/$(date +%Y-%m-%d)-analysis.md`
2. Replace placeholders (`<N>`, dates, names).
3. Verify FIRST line is `### ` not `knowledge:`.
4. Append via `terminal()`: `cat /tmp/$(date +%Y-%m-%d)-analysis.md >> /Users/user/.hermes/cron/sync/sync-$(date +%Y%m%d).log`
5. Verify with a second read that no `knowledge:` lines snuck in.

## Forbidden first-line patterns

- ❌ `knowledge: === Hermes Cron Sync Summary ...`
- ❌ `Knowledge:` (any case)
- ❌ `[YYYY-MM-DD HH:MM:SS] knowledge: ...`
- ❌ Any line that does not start with `### `

If your output contains `knowledge:` lines, delete them and re-append from this template.
