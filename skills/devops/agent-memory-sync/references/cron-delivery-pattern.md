# Cron-Delivery Pattern (Hermes ↔ LobsterAI)

Worked examples of the daily sync log format the agent writes, plus the exact delivery choreography when this skill is invoked from the 09:00 cron job.

## Delivery choreography (cron mode)

1. **Pre-run shell script executes** at 09:00 — `bash ~/.hermes/scripts/sync-lobsterai.sh` writes the comparison files into `~/.hermes/cron/sync/` and the basic header into `sync-YYYYMMDD.log`. The script exits 0; the agent is not yet involved.
2. **Cron job wakes the agent** with a system prompt containing the pre-run script's stdout (the basic header) and the human-written instructions ("每日記憶同步任務...").
3. **Agent's job**: read the four sync files in `~/.hermes/cron/sync/`, read its own `~/.hermes/memories/MEMORY.md` + `USER.md`, compare, decide if action is needed.
4. **Append analysis section** to `~/.hermes/cron/sync/sync-YYYYMMDD.log`.
5. **Report briefly** in the agent's final response — the system handles delivery to the user.

The agent has **no interactive channel** to ask clarifying questions. Make reasonable decisions and act.

## File: `~/.hermes/cron/sync/sync-YYYYMMDD.log`

This file is created fresh each day by the pre-run script, then appended-to by the agent. The agent's section is the durable artifact — the system may rotate or summarize the pre-run stdout, but the agent's analysis is what the user reads.

### Pre-run script writes (top of file)

```
[2026-06-04 09:05:54] === Hermes ↔ LobsterAI Sync Start ===
[09:05:54] Extracting LobsterAI memory...
[09:05:54] Listing LobsterAI skills...
  Found      101 skills
[09:05:54] Comparing skills...
  Skills only in LobsterAI:        0
  Skills only in Hermes:        0
[09:05:54] Comparing memory content...
  Hermes USER.md:       17 lines
  Hermes MEMORY.md:       45 lines
[2026-06-04 09:05:54] === Sync Complete ===
```

### Agent appends (the "stable-drift NO-OP" case — common since 2026-06-12; **zero-Hermes-only variant dominant since 2026-07-25 09:07**)

This is the **expected** pattern now that LobsterAI carries the 35-bundle corporate/PM skills. The two sides are intentionally NOT byte-identical on skills, but the drift is stable day-over-day. **Since 2026-07-25 09:07**, the Hermes-only side has been cleared (mass-sync copied all 9 previously-Hermes-only skills to LobsterAI top-level); the dominant pattern is now **zero Hermes-only + 35 LobsterAI-only** instead of the previous "1-9 Hermes-only + 35 LobsterAI-only". Use the canonical fingerprint in `references/lobsterai-stable-drift.md`:

```
### 2026-06-17 Agent-Written Sync Results (LobsterAI ↔ Hermes) ###

Sync Trigger: Daily 09:00 cron job (today, Jun 17 2026, 09:05:29 — pre-run script executed twice at 09:05:29 and 09:05:39, identical output)
Sync Script:  bash ~/.hermes/scripts/sync-lobsterai.sh (exit_code=0)

Skills (Top-Level):
  - LobsterAI: 145 skills
  - Hermes:    110 skills
  - Missing in Hermes:  35  (corporate/PM bundle, stable fingerprint — see references/lobsterai-stable-drift.md)
  - Missing in Lobster: 0   (EMPTY since 2026-07-25 09:07 mass-sync; previously 1-9 name-variant 簡版名)
  ⏸️ Zero Hermes-only drift — Hermes top-level fully aligned with LobsterAI. 35-bundle drift intentional.

Memory Diff Check:
  - Hermes MEMORY.md     : 55 lines, last modified 2026-06-14 09:06 (3 days ago, stable)
  - Hermes USER.md       : 17 lines, last modified 2026-05-20 09:07 (4 weeks ago, stable)
  - LobsterAI main.sqlite: 9 chunks, last modified 2026-06-15 09:32:54 (app-restart mtime bump, content unchanged)
  ✅ No memory content changes since previous sync run.

Action Taken This Run:
  ⏸️ NO-OP on MEMORY.md — no new concise durable facts in LobsterAI export
  ⏸️ NO-OP on USER.md — unchanged
  ⏸️ NO-OP on skill_manage — 35-bundle fingerprint unchanged, no new imports
  ⏸️ NO-OP on memory tool — no new declarative facts

Sub-skill deltas (intentionally not synced — runtime variants, bundled content, dependency trees):
  Hermes-only: (empty — since 2026-07-25 09:07 mass-sync)
  LobsterAI-only: web-search (Playwright), docx-js, ooxml, html2pptx, recalc.py, ...

🏁 Status: Top-level skills fully aligned on Hermes side; 35-bundle intentional drift on LobsterAI side.
   Skills intentionally drift by 35 (corporate/PM bundle, role-mismatch). Hermes-only = 0.
   Next sync: 2026-MM-DD 09:00 cron.
```

### Agent appends (the "no action" case — common, valid)

```
### 2026-06-04 Agent-Written Sync Results (LobsterAI ↔ Hermes) ###

Sync Trigger: Daily 09:00 cron job (today, Jun 4 2026, 09:05:54)
Sync Script:  bash ~/.hermes/scripts/sync-lobsterai.sh (exit_code=0)

Skills (Top-Level):
  - LobsterAI: 101 skills
  - Hermes:    101 skills
  - Missing in Hermes:  0  (missing-in-hermes.txt: empty)
  - Missing in Lobster: 0  (missing-in-lobster.txt: empty)
  - hermes-skills.txt md5 == lobster-skills.txt md5 (e0cb27ad9f10e7fb3355a66a7ff5baf2)
  ✅ Top-level skills byte-identical (sorted set match)

Memory Diff Check:
  - Hermes MEMORY.md     : 45 lines, last modified 2026-06-01 13:09
  - Hermes USER.md       : 17 lines, last modified 2026-05-20 09:07
  - LobsterAI memory DB  : 10 chunks in main.sqlite, last modified 2026-05-31 19:12
  - No file on either side touched since the 2026-06-03 sync run

  Core facts present in BOTH (unchanged from prior syncs):
    ✅ API keys (Brave/Tavily/TokenPlan/SiliconFlow/DeepSeek/PaddleOCR/NVIDIA/Telegram/WeChat)
    ✅ Workarounds (.env blocked→execute_code, launchd gateway, skills install pipe y, vision_analyze→minimax)
    ✅ Browser control (kimi-webbridge port 10086, NOT built-in tools)
    ✅ TTS voices (female-shaonv Mandarin, Cantonese_ProfessionalHost(F))
    ✅ Pets (white hamster + Lynx Point Siamese, 「武松打虎」 style)
    ✅ Docker projects (a-split-bill-pwa :8787/:4173, a-ocr-service :8089)
    ✅ 美股分析風格 + daily-us-stock-news skill
    ✅ LobsterAI sync architecture and DB path
    ✅ Hermes Skills Index (80+ categories) + Config 重點

  LobsterAI-only content (sync log history, not new knowledge):
    - 2026-05-17, 2026-05-30 sync log entries (historical, no need to copy to Hermes)

Skills to copy: NONE
Memory to copy: NONE

Sub-skill deltas (carried over from prior runs, still intentionally not synced):
  Hermes-only: hermes-backup, a-split-bill-pwa, macos-disk-cleanup,
               baoyu-article-illustrator, kanban-codex-lane
  LobsterAI-only: web-search (Playwright), docx-js, ooxml, html2pptx, recalc.py
  -> Architecture-specific, intentionally NOT synced.

🏁 Status: 100% synchronized — no action required.
   No skills to copy. No memory chunks to transfer.
   State is stable: skill lists byte-identical, no memory file touched in 4 days.
   Next sync: 2026-06-05 09:00 cron.
```

### Agent appends (the "action" case — 2026-06-01, copy-from-Hermes)

```
### 2026-06-01 Agent-Written Sync Results ###

Skills (Top-Level):
  - LobsterAI: 101 skills
  - Hermes:    101 skills
  - Missing in Hermes:  0
  - Missing in Lobster: 0
  ✅ Top-level skills in sync

Sub-Skill Differences Found & Synced:
  ✅ Copied devops/agent-memory-sync   → LobsterAI (sync process documentation)
  ✅ Copied mlops/paddleocr-api        → LobsterAI (OCR skill)

  Not synced (architecture-specific / not relevant):
    - Hermes-only: hermes-backup, a-split-bill-pwa, macos-disk-cleanup,
                   baoyu-article-illustrator, kanban-codex-lane
    - LobsterAI-only: web-search (Playwright-based), docx-js, ooxml,
                      html2pptx, recalc.py, skill-creator sub-components

Memory:
  - Hermes MEMORY.md (46 lines) — last modified May 30 09:07
  - LobsterAI MEMORY.md (168 lines, verbose) — last modified May 31 19:11 UTC
  - Both contain same core facts (API keys, workarounds, pets, config, TTS)
  - No new information to transfer since last sync
  ✅ Memory fully in sync

  - Hermes USER.md (17 lines, compact) — last modified May 20 09:07
  - LobsterAI USER.md (56 lines, structured Markdown)
  - Same user profile content, different formatting conventions
  ✅ USER profile in sync

🏁 Status: 100% synchronized — 2 skills added to LobsterAI
```

## How to write the analysis block (worked recipe)

The block is 1–3 KB. Do **not** try to write it with a heredoc — `terminal()` may reject `cat >> file << 'EOF'` as backgrounding. Use this two-step recipe:

```python
# Step 1 (write_file tool): drop the analysis to /tmp/
content = """
### 2026-MM-DD Agent-Written Sync Results (LobsterAI ↔ Hermes) ###
...
🏁 Status: 100% synchronized — no action required.
"""
write_file("/tmp/sync-YYYYMMDD-analysis.txt", content)
```

```bash
# Step 2 (terminal tool): concatenate onto the daily log
cat /tmp/sync-YYYYMMDD-analysis.txt >> ~/.hermes/cron/sync/sync-YYYYMMDD.log
```

Then `tail -50` the log to verify the section landed correctly. Optionally `rm /tmp/sync-YYYYMMDD-analysis.txt` to keep `/tmp/` tidy.

## Tool availability in cron mode

| Tool | Available in cron? | Notes |
|------|-------------------|-------|
| `read_file` | ✅ | preferred for reading sync outputs |
| `write_file` | ✅ | for writing the analysis to `/tmp/` |
| `terminal` | ✅ | for `cat` / `md5sum` / `stat` / `sqlite3` |
| `memory` | ✅ | for new declarative facts to remember across sessions |
| `skill_manage` | ✅ | for new skills or patching this one |
| `patch` | ✅ | for editing files in place |
| `execute_code` | ❌ **BLOCKED** | runtime refuses: "Cron jobs run without a user present to approve it" |
| `delegate_task` | depends on profile config | check the cron profile's enabled toolsets |
| `clarify` | ❌ | no user present |
| `send_message` | ❌ | the system handles delivery |

## Reference timeline of daily sync outcomes

(For pattern-spotting — what does a normal week look like?)

| Date | Outcome | Action taken |
|------|---------|--------------|
| 2026-05-15 | Initial sync | Workspace files aligned, schema documented |
| 2026-05-16 | In sync | None |
| 2026-05-17 | Config updates | PaddleOCR + a-split-bill-pwa added to MEMORY.md |
| ... | In sync | None |
| 2026-05-30 | Skill updates | devops (May 30), context-engineering (May 29) updated |
| 2026-06-01 | Sub-skill diff | Copied `devops/agent-memory-sync` + `mlops/paddleocr-api` → LobsterAI |
| 2026-06-02 | In sync | None |
| 2026-06-03 | In sync | None (md5-stable since 06-01) |
| 2026-06-04 | In sync | None (md5 match: `e0cb27ad9f10e7fb3355a66a7ff5baf2`) |
| 2026-06-05..06-08 | In sync | None (md5-stable, no chunk text changes) |
| 2026-06-09 | **Memory facts propagated Hermes-ward** | Skills stable, but 8 concise facts in LobsterAI chunks (Whisper/OfficeCLI/gateway-locks/launchd plist/bot-tokens-config/image-gen endpoint/Codex 403 + DeepSeek /anthropic 404/TTS backup voices) were not in Hermes MEMORY.md — added as 1-line `- ` entries. See "propagate-concise-facts" case below. |

Two stable weeks, two actionable days. The expected ratio is heavily skewed toward "no action" — when in doubt, write the analysis showing the byte-identity proof and call it stable.

## Agent appends (the "propagate concise facts to Hermes" case — 2026-06-09)

This is a third pattern distinct from the two above. The skill counts are stable, so the "skills to copy" lines are NONE — but the *memory* comparison surfaces durable 1-2 line facts in LobsterAI chunks that aren't yet in Hermes MEMORY.md. The fix is targeted `patch` edits to add the facts (NOT to wholesale rewrite the file). Sample log section:

```
### 2026-06-09 Agent-Written Sync Results (LobsterAI ↔ Hermes) ###

Sync Trigger: Daily 09:00 cron job (today, Jun 9 2026, 09:05:39 — script ran twice at 09:05:39 and 09:05:52, identical output)
Sync Script:  bash ~/.hermes/scripts/sync-lobsterai.sh (exit_code=0)

Skills (Top-Level):
  - LobsterAI: 101 skills
  - Hermes:    101 skills
  - Missing in Hermes:  0  (missing-in-hermes.txt: empty, 0 bytes)
  - Missing in Lobster: 0  (missing-in-lobster.txt: empty, 0 bytes)
  - hermes-skills.txt == lobster-skills.txt (sort diff = 0 lines, exit 0)
  ✅ Top-level skills byte-identical (sorted set match — stable for 8+ days)

Memory Diff Check:
  - Hermes MEMORY.md     : 45 → 54 lines (AGENT-EDITED this run, see below)
  - Hermes USER.md       : 17 lines, last modified 2026-05-20 09:07 (unchanged 20 days)
  - LobsterAI memory DB  : 9 chunks in main.sqlite, MAX(updated_at) = 2026-06-07 22:11:57 HKT

Action Taken This Run:
  ✅ Hermes MEMORY.md UPDATED (45 → 54 lines, 2084 → 2863 bytes)
  - Skipped USER.md (unchanged from 06-05, no new user facts in LobsterAI export)
  - Skipped skills (101/101 already in sync)

  New facts propagated from LobsterAI export to Hermes MEMORY.md:
    1. ## CLI 工具 section (NEW)
       - Whisper (Homebrew): `whisper <file.m4a> --model large --language yue` (粵語轉錄)
       - OfficeCLI v1.0.92: Office 文件 CLI
    2. ## Workarounds section (3 new entries)
       - Gateway lock files path: ~/.local/state/hermes/gateway-locks/ — 「token already in use」錯誤來源
       - No allowlist = ALL users denied by default (silent bot); allowlist via launchd plist at ~/Library/LaunchAgents/ai.hermes.gateway.plist
       - Bot tokens → config.yaml `platforms.telegram.token` (唔放入 .env)
    3. ## Model Routing section (2 new entries)
       - image_gen payload: size=1024*1024; endpoint: token-plan.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
       - ❌ Codex CLI: 403 expired | ❌ DeepSeek /anthropic endpoint: 404 dead
    4. ## TTS section (1 new entry)
       - 備選 voices: Cantonese_CuteGirl, Cantonese_GentleLady, Cantonese_KindWoman

  Deliberately NOT propagated (verbose historical detail, per 06-08 convention):
    - Full Hermes Skills Index (163 SKILL.md files enumeration)
    - Full Hermes Config yaml dump
    - Historical sync log entries
    - Hermes config metadata (reasoning_effort, config_version)

Sub-skill deltas (architecture-specific, intentionally NOT synced, same as 06-06/06-07/06-08):
  Hermes-only: hermes-backup, a-split-bill-pwa, macos-disk-cleanup, baoyu-article-illustrator, kanban-codex-lane
  LobsterAI-only: web-search (Playwright), docx-js, ooxml, html2pptx, recalc.py

🏁 Status: 100% synchronized.
   - Skills: 101/101, byte-identical
   - Memory: Hermes 54 lines (condensed summary), LobsterAI 9 chunks (raw historical)
   - All durable environment facts from LobsterAI now present in Hermes MEMORY.md
   - USER.md unchanged (no new user profile facts in either direction)

Next sync: 2026-06-10 09:00 cron.
```

### How to apply this case

1. Read both sides, then look for **concise durable facts in LobsterAI export that aren't in Hermes MEMORY.md**. The LobsterAI export text is *noisy* (chunk overlap of ~80 tokens causes apparent duplication), so don't dismiss the whole export as "verbose historical detail" — extract the 1-2 line nuggets.
2. Heuristic for "propagate vs skip":
   - **Propagate**: 1-2 line technical facts that won't go stale in a week (CLI command, error code meaning, lock file path, dead endpoint, backup voice name).
   - **Skip**: config YAML dumps, full skills index, sync log history, per-day archive entries.
3. Use `patch` to add `- ` bullet lines into the appropriate existing section (or create a new section header if the topic is new). Do NOT rewrite the whole file.
4. **CRITICAL pitfall**: `read_file()` output is `LINE_NUM|CONTENT`. When you copy that into `patch` `new_string`, the leading `|` becomes part of the file and produces stray `|-` / `||` lines. Strip the `read_file` line-number pipe — actual bullets are `- ` (hyphen-space), not `|-`. Verify with `grep -nE '^\|-' MEMORY.md` after patching.
5. Append a log section that lists each new entry under "New facts propagated", and explicitly notes what was *deliberately* NOT propagated (to head off the next agent from second-guessing the choice).
6. Report `Hermes MEMORY.md : N → M lines` in the "Memory Diff Check" so the next day's sync can see what changed this run.

### Agent appends (the "sync-the-sync-skill" action case — 2026-07-28)

A distinct fourth pattern: top-level skill names are aligned, no Hermes memory delta, but a **shared package on LobsterAI is materially older than its Hermes source** — and that package happens to be the sync workflow itself. The destination's stale SKILL.md does not contain the latest pitfall warnings, so the next agent's load doesn't protect them. Sample log section:

```
### 2026-07-28 Agent-Written Sync Results (LobsterAI ↔ Hermes) ###

Sync trigger: scheduled daily cron; used the pre-run collection (09:05:54), no redundant script execution.

Skills:
- LobsterAI 145; Hermes 110; LobsterAI-only 35 (the established corporate/PM bundle, intentionally not imported).
- Hermes-only 0 (`missing-in-lobster.txt` empty; MD5 `d41d8cd98f00b204e9800998ecf8427e`). This is the expected post-2026-07-25 state.
- Deep package audit found the LobsterAI copy of `devops/agent-memory-sync` stale. Updated the complete 10-file package from Hermes; all SHA-256 checks passed. Backup: `/Users/user/Library/Application Support/LobsterAI/SKILLs/.sync-backups/20260728-090911/devops-agent-memory-sync`.

Memory:
- Hermes MEMORY.md (45 lines, Jul 22) and USER.md (21 lines, Jul 22) contain no new durable facts absent from LobsterAI; no Hermes memory edits needed.
- Detected LobsterAI workspace/SQLite indexing drift: workspace MEMORY.md was 608 lines (Jul 27), while SQLite/FTS covered only lines 1–552 (22 rows, Jul 23).
- Reindexed `MEMORY.md` with the packaged repair script. Result: 25 `chunks` + 25 FTS rows, coverage 1–608, marker searchable (6 FTS hits), `integrity_check=ok`; auto-backup: `/Users/user/Library/Application Support/LobsterAI/openclaw/state/memory/main.sqlite.pre-reindex-1785200910.bak`.

Status: stable intentional skill drift; actionable package freshness and FTS indexing lag repaired successfully. Next sync: 2026-07-29 09:00.
```

**Why this matters**: the `devops/agent-memory-sync` skill contains the v1.13.0+ `knowledge:` reproduction warnings. If the destination copy is from v1.5.0, a fresh agent loads the skill and sees "1 reproduction" instead of "10+ reproductions" — the load gives false confidence. The recursive audit (shared-package mtime diff) is the only way to catch this; relying on `missing-in-hermes.txt` / `missing-in-lobster.txt` cannot detect it because the *name* is identical on both sides.

### How to detect this case (recipe)

1. After the standard top-level name check, run a deep package audit: for every shared category-skill, compare `H_mtime` and `L_mtime` for the `SKILL.md` file. List the top N by `max(H_mtime, L_mtime) - min(H_mtime, L_mtime)` — the entries with the largest gap are the most stale.
2. **Always include `devops/agent-memory-sync` in the audit even if it does not appear in the diff** — the destination rarely auto-updates, so mtime lag is the normal state. Treat it as a quarterly check (run a hash compare every 30 days minimum).
3. For each shared package with `H_mtime > L_mtime + 7d`, follow the portable-skill-update-workflow.md recipe: single backup root → per-file `cp` → SHA-256 verification. Bump the version on the source if the audit surfaces a contradiction with the latest user directive.
4. Verify the FTS lag in the same run: `stat -f "%Sm" workspace_main/MEMORY.md` vs SQLite `MAX(updated_at) WHERE path='MEMORY.md'`. If the gap is >1 day and the workspace file is larger than the FTS `MAX(end_line)`, run the reindex script with a workspace-present marker. Always run `PRAGMA wal_checkpoint(FULL);` after reindex and confirm `0|N|N` (zero busy, all frames checkpointed).
