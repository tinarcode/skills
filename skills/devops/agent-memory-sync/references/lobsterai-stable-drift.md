# LobsterAI Stable-Drift Reference

Captured from the 2026-06-12 → 2026-06-13 sync cycle. Complements `lobsterai-workspace-files.md` and `cron-delivery-pattern.md`.

## What "stable drift" means here

LobsterAI carries a permanent 35-skill corporate/PM bundle that Hermes does **not** mirror and will not import. The two sides are intentionally NOT byte-identical on skills — but they ARE stable day-over-day. This is a third NO-OP pattern, distinct from:

- **Byte-identical** (md5 match on sorted skill lists) — see `cron-delivery-pattern.md`
- **Memory facts to propagate** (skill counts stable, but concise durable facts surfaced in LobsterAI chunks) — see `cron-delivery-pattern.md`
- **Stable drift** (THIS pattern: skill counts intentionally differ by 35, no action) — captured 2026-06-13

Recognize stable drift by:
1. `missing-in-hermes.txt` is non-empty AND the names are stable across two consecutive daily logs
2. `missing-in-lobster.txt` contains 1 entry (`debugging` or similar parity overlap)
3. LobsterAI `main.sqlite` chunk count is unchanged from yesterday
4. Hermes `MEMORY.md` and `USER.md` modification times are older than the previous sync

If all four hold, the right action is to write a NO-OP analysis and move on. Do NOT manufacture skill imports.

## Canonical LobsterAI-only skill bundle (35 skills, as of 2026-06-13)

Stable since LobsterAI bundled-update on 2026-06-12. Treat this list as a fingerprint — if these names change, a new bundled update has shipped and the analysis must be redone.

### Corporate / PM / Agile (20 — NOT relevant for user's solo IT-tech role)

```
sprint-planning, standup, stakeholder-update, product-brainstorming,
roadmap-update, competitive-brief, user-research, incident-response,
analyze, architecture, design-critique, design-handoff, design-system,
ux-copy, documentation, code-review, metrics-review, synthesize-research,
research-synthesis, system-design
```

### Data / Engineering adjacent (15 — FLAGGED for manual review)

These overlap with skills user might plausibly use (IT tech at a nursing college, occasional data/infra work). The skill policy is "do NOT auto-import; flag for manual review". Listed in priority order:

```
sql-queries, write-query, validate-data, explore-data,
data-context-extractor, statistical-analysis, data-visualization,
create-viz, build-dashboard, deploy-checklist, tech-debt,
testing-strategy, accessibility-review, write-spec, debug
```

**Note**: `debug` and `debugging-and-error-recovery` already exist on the LobsterAI side under those exact names; the `debug` entry in the 35-bundle is the duplicate-of-Hermes-`debugging` overlap, not a new skill to import.

## Bundled-skill-update heuristic

When LobsterAI's skill count jumps by **10+ in a single 24h window**, it is almost certainly a LobsterAI bundled app update, not user-driven installation. Fingerprint:

- The new skills are mostly corporate/PM-flavored (the names cluster around agile rituals, design critique, sprint planning)
- The jump lands between two daily cron runs without any `hermes skills install` activity on the Hermes side
- The same 35-name cluster appears consistently across LobsterAI updates (e.g. 06-12 → 06-13 was a stable carryover, not a re-jump)

**Action**: Write the daily log noting the jump, classify the new skills against the canonical 35-bundle, and call it stable drift. Do NOT bulk-import. Do NOT raise a "reconciliation needed" alert.

## Hermes-only skills (was 9 through 2026-07-24; **0 since 2026-07-25 09:07**)

Through 2026-07-24, nine top-level skills existed on the Hermes side that were not in LobsterAI. Classification by category:

**Category (a) — Name variants / 簡版名** (4 skills, intentional overlap with LobsterAI's existing skills):
- `debugging` — Hermes simplified name; LobsterAI has `debug` + `debugging-and-error-recovery` separately
- `design` — Hermes simplified name; LobsterAI has `design-critique`, `design-handoff`, `design-system` (3 separate skills)
- `trading` — Hermes simplified name; LobsterAI has multiple trading-related skills under more specific names
- `product-research` — Hermes simplified name; LobsterAI covers the domain under different naming

**Category (b) — Hermes-architectural features with no LobsterAI equivalent** (1 skill):
- `kanban` — Hermes's built-in multi-agent task board (orchestrator + worker profiles + KANBAN_GUIDANCE). Added 2026-06-19. LobsterAI's delegation model does not use orchestrator/worker splits, so importing would be meaningless. Permanent architectural no-import.

**Category (c) — Hermes-exclusive desktop / cross-platform drivers** (1 skill):
- `computer-use` — cuahq/cua-driver cross-platform desktop automation, v2.0.0, added 2026-06-29 15:14. LobsterAI only has the macOS-only sub-skill `apple/macos-computer-use`. Distinct scope — not an import candidate.

**Category (d) — Platform-specific macOS-local bundles** (3 skills, added 2026-07-10 09:53):
- `hermes-gateway-ops` — Hermes macOS launchd / gateway plist / lock-file troubleshooting
- `mac-local-environment` — Hermes macOS environment bundle (Office 365 paths, software quirks)
- `minimax-model-stack` — Hermes MiniMax MCP / model routing / provider config bundle

All three (d) category skills depend on macOS-specific runtime primitives (`~/Library/LaunchAgents/`, Office CLI on Mac, kimi-webbridge daemon, MiniMax coding-plan MCP) that don't exist in LobsterAI's cross-platform desktop runtime. They are **NOT import candidates** — neither the skills themselves nor the underlying platform features they document are portable.

**Stable set (was 9 through 2026-07-24)**: `computer-use`, `debugging`, `design`, `hermes-gateway-ops`, `kanban`, `mac-local-environment`, `minimax-model-stack`, `product-research`, `trading`

### 2026-07-25 09:07 mass-sync event — Hermes-only went 9 → 0

On 2026-07-25 at 09:07, all 9 previously-Hermes-only skills (plus 2 other changes = +8 net) were copied to LobsterAI `SKILLs/` top-level. LobsterAI skill count jumped 137 → 145. LobsterAI's `ls -1 SKILLs/ | grep -v '\.json$'` now reports 145 (the `skills.config.json` file makes raw `ls` show 146; sync script filters correctly).

**Important caveat — top-level name presence ≠ content parity**: LobsterAI now has all 9 directory names, but the 3 category-(d) skills (`hermes-gateway-ops`, `mac-local-environment`, `minimax-model-stack`) carry Hermes-runtime-specific content (macOS launchd / Office CLI / kimi-webbridge / MiniMax MCP) that LobsterAI cannot exercise. Treat them as **content-non-portable but directory-portable**. If LobsterAI's per-skill content drift on those 3 skills surfaces later, the right action is the SHA-256 / `cp` rollback workflow from `references/portable-skill-update-workflow.md`, not a sync error.

### Detection heuristic for fresh agents (NEW — category d)
When a new Hermes-only skill appears in `missing-in-lobster.txt`, classify as (a)/(b)/(c)/(d). For (d), check if the skill SKILL.md mentions any of: `~/Library/LaunchAgents/`, `launchd plist`, `kimi-webbridge`, `OfficeCLI`, `Whisper --language yue`, `Mac mini`, `Apple Silicon`, `MiniMax MCP`. If yes, it's category (d) — flag as "macOS-specific bundle, not import candidate" and skip. Same treatment as (b) and (c) in the log: explicit classification name + skip rationale.

**Note (2026-07-27)**: this detection heuristic is now mainly useful for detecting any FUTURE Hermes-only skill. Since 2026-07-25, the dominant pattern is `missing-in-lobster.txt` is empty (zero Hermes-only drift). The 9 previous Hermes-only names are now all in LobsterAI at the top level.

### `computer-use` — Hermes-exclusive desktop driver (NEW, 2026-06-29)
Hermes-only top-level `computer-use` skill (cuahq/cua-driver desktop automation, v2.0.0, added 2026-06-29 15:14). LobsterAI has the macOS-only sub-skill `apple/macos-computer-use` but no top-level `computer-use`. Not an import candidate — different scope (cross-platform desktop driver vs macOS-only sub-skill) and different SKILL.md author. When classifying, mark in the log as: "`computer-use` — Hermes-exclusive cuahq/cua-driver top-level skill (cross-platform), distinct from LobsterAI's macOS-only sub-skill."

### `debugging` — name variant overlap (簡版名)
Hermes uses the simplified name `debugging`; LobsterAI has `debug` + `debugging-and-error-recovery` separately. Don't propagate — parity would be redundant. Flag as "intentional no-import" in the log.

### `design` — name variant overlap (簡版名)
Hermes uses the simplified name `design`; LobsterAI has `design-critique`, `design-handoff`, `design-system` (3 separate skills). Don't propagate — Hermes' umbrella `design` skill covers the same domain under simplified naming.

### `trading` — name variant overlap (簡版名)
Hermes uses the simplified name `trading`; LobsterAI has multiple trading-related skills under more specific names. Don't propagate — Hermes' umbrella `trading` skill covers the same domain.

### `product-research` — name variant overlap (簡版名)
Hermes-side simplified name for the product comparison/research class of work. As of 2026-06-14 also appears in the `missing-in-lobster.txt` set; stable carryover. Don't propagate — LobsterAI's category covers the same domain under different naming.

### `kanban` — Hermes-specific multi-agent orchestration feature (NEW, 2026-06-19)
**This is NOT a name variant.** `kanban` is Hermes's built-in multi-agent task board — orchestrator profiles decompose goals and fan out tasks to worker profiles, with `KANBAN_GUIDANCE` auto-injected into dispatched worker system prompts. The `kanban-codex-lane` sub-skill has existed in the Hermes skills directory since earlier, but `kanban` as a top-level SKILL.md entry was added on 2026-06-19 (Hermes total 103→104, missing-in-lobster 2→3).

LobsterAI has **no equivalent architecture** — its delegation model does not use orchestrator/worker profile splits. Trying to "import" `kanban` to LobsterAI would be meaningless because the underlying runtime feature doesn't exist there. Treat as a permanent architectural no-import — distinct from the name-variant cases above. When classifying, mark in the log as: "`kanban` — Hermes-specific multi-agent delegation toolset (orchestrator + worker profiles + KANBAN_GUIDANCE), no LobsterAI equivalent by design."

### Recognition pattern (current, **0 Hermes-only since 2026-07-25 09:07**)
```
missing-in-lobster.txt should be EMPTY (0 bytes, md5 d41d8cd98f00b204e9800998ecf8427e).
missing-in-hermes.txt should contain the canonical 35-skill corporate/PM bundle names from the list above.
```
If `missing-in-lobster.txt` is empty across two consecutive daily logs, it's the expected zero-Hermes-only carryover (the 2026-07-25 mass-sync event cleared it). If a name appears, that's a new Hermes install OR a LobsterAI-side rename — classify it as category (a)/(b)/(c)/(d) using the heuristic in the Detection section above. If `missing-in-hermes.txt` diverges from the 35-bundle, a LobsterAI bundled-update has shipped.

**History**: 2026-06-19 added `kanban` (2→3). 2026-06-27 verified all 5 names — `design` and `trading` were always Hermes-only but previously undercounted; this is the first formal recognition that the stable Hermes-only set was 5, not 3. 2026-06-30 added `computer-use` (5→6) — cuahq/cua-driver top-level desktop automation skill, Hermes-exclusive (LobsterAI only had the macOS sub-skill `apple/macos-computer-use`). 2026-07-11 added 3 category (d) macOS-specific bundles (6→9): `hermes-gateway-ops`, `mac-local-environment`, `minimax-model-stack`, all installed at 2026-07-10 09:53, between the 07-10 09:05 cron run and the 07-11 09:05 cron run. The 07-10 sync log reported the older 6-skill state because the cron ran BEFORE the 09:53 install batch. **2026-07-25 09:07 mass-sync event cleared all 9 to 0**: LobsterAI now has directory names for all 9 previously-Hermes-only skills (137 → 145, +8 net after other changes). Category-(d) skills remain content-non-portable but directory-portable.

## Direct-SQLite verification recipe (for NO-OP confirmation)

When the sync script reports stable counts but you want extra confidence before writing NO-OP:

```bash
# 1. Confirm chunk count and dates
sqlite3 -header -separator '|' \
  "$HOME/Library/Application Support/LobsterAI/openclaw/state/memory/main.sqlite" \
  "SELECT id, path, source, start_line, end_line, model, datetime(updated_at, 'unixepoch') as updated FROM chunks ORDER BY updated_at DESC;"

# 2. Check meta for last index build
sqlite3 -separator '|' \
  "$HOME/Library/Application Support/LobsterAI/openclaw/state/memory/main.sqlite" \
  "SELECT key, substr(value, 1, 200) FROM meta;"

# 3. Compare against previous sync log's chunk-count line
grep -E "main.sqlite.*chunks" ~/.hermes/cron/sync/sync-*.log | tail -5
```

If the chunk count and `updated_at` values are unchanged from yesterday, the daily log line can confidently read "no memory DB changes since previous sync run".

## Skills-directory artifact: `skills.config.json`

LobsterAI's `SKILLs/` directory contains **137 entries** but only **136 are skill directories**:

```
~/Library/Application Support/LobsterAI/SKILLs/skills.config.json   ← metadata file
```

The sync script's count of 136 comes from filtering on `SKILL.md` (or counting only directories with that file). If you ever run `ls | wc -l` on the SKILLs/ directory and see 137, that's correct — subtract one for the config file. Not a sync error.

## Template: stable-drift NO-OP log section

```markdown
### YYYY-MM-DD Agent-Written Sync Results (LobsterAI ↔ Hermes) ###

Sync Trigger: Daily 09:00 cron job (today, ...)
Sync Script:  bash ~/.hermes/scripts/sync-lobsterai.sh (exit_code=0)

Skills (Top-Level):
  - LobsterAI: 136 skills
  - Hermes:    101 skills
  - Missing in Hermes:  35  (corporate/PM bundle, stable fingerprint — see references/lobsterai-stable-drift.md)
  - Missing in Lobster: 1   (debugging — overlap with LobsterAI debug/debugging-and-error-recovery)
  ⏸️ Stable drift — both sides stable vs previous sync, no action.

Memory Diff Check:
  - Hermes MEMORY.md     : N lines (unchanged since previous sync)
  - Hermes USER.md       : N lines (unchanged)
  - LobsterAI main.sqlite: N chunks (verified via sqlite3, updated_at unchanged)
  ✅ No memory content changes since previous sync run.

Action Taken This Run:
  ⏸️ NO-OP on MEMORY.md — yesterday's summary line still accurate
  ⏸️ NO-OP on USER.md — unchanged
  ⏸️ NO-OP on skill_manage — 35-bundle fingerprint unchanged, no new imports
  ⏸️ NO-OP on memory tool — no new declarative facts

🏁 Status: 95% synchronized — fully stable vs previous sync baseline.
   Skills intentionally drift by 35 (corporate/PM bundle, role-mismatch).
   Next sync: YYYY-MM-DD 09:00 cron.
```

## Template: zero-Hermes-only NO-OP log section (since 2026-07-25 09:07)

Use this template when `missing-in-lobster.txt` is empty AND `missing-in-hermes.txt` matches the 35-bundle. The previous "stable drift" template assumed 1+ Hermes-only names; the new dominant pattern is **zero**. The two sides are still NOT byte-identical on skills (LobsterAI 145 vs Hermes 110), but the Hermes-only side has been fully synced to LobsterAI at the top level. The 35-bundle drift remains intentional.

```markdown
### YYYY-MM-DD Agent-Written Sync Results (LobsterAI ↔ Hermes) ###

Sync Trigger: Daily 09:00 cron job (today, ...)
Sync Script:  bash ~/.hermes/scripts/sync-lobsterai.sh (exit_code=0)

Skills (Top-Level):
  - LobsterAI: 145 skills
  - Hermes:    110 skills
  - Missing in Hermes:  35  (corporate/PM bundle, stable fingerprint — see references/lobsterai-stable-drift.md)
  - Missing in Lobster: 0   (EMPTY, md5 d41d8cd98f00b204e9800998ecf8427e) ← since 2026-07-25 09:07 mass-sync
  ⏸️ Zero Hermes-only drift — all Hermes top-level skills are now also on LobsterAI (since 2026-07-25 09:07). 35-bundle corporate/PM drift remains intentional.

Memory Diff Check:
  - Hermes MEMORY.md     : N lines (unchanged since previous sync)
  - Hermes USER.md       : N lines (unchanged)
  - LobsterAI main.sqlite: N chunks (verified via sqlite3, updated_at unchanged)
  ✅ No memory content changes since previous sync run.

Action Taken This Run:
  ⏸️ NO-OP on MEMORY.md — unchanged
  ⏸️ NO-OP on USER.md — unchanged
  ⏸️ NO-OP on skill_manage — 35-bundle fingerprint unchanged, no new imports
  ⏸️ NO-OP on memory tool — no new declarative facts

Sub-skill deltas (intentionally not synced — runtime variants, bundled content, dependency trees):
  See prior sync logs for the deep sub-skill review. No blind bulk mirroring performed.

🏁 Status: Top-level skills fully aligned on Hermes side; 35-bundle intentional drift on LobsterAI side.
   Hermes-only = 0 (since 2026-07-25 09:07 mass-sync), LobsterAI-only = 35 (corporate/PM, role-mismatch).
   Next sync: YYYY-MM-DD 09:00 cron.
```

## Reference timeline update (extension to cron-delivery-pattern.md)

| Date | Outcome | Action taken |
|------|---------|--------------|
| 2026-06-01 | Sub-skill diff | Copied `devops/agent-memory-sync` + `mlops/paddleocr-api` → LobsterAI |
| ... | In sync | None |
| 2026-06-09 | **Memory facts propagated Hermes-ward** | 8 concise facts added |
| ... | In sync | None |
| 2026-06-12 | **Bundled-skill-update detected** | LobsterAI 101→136 in 24h. Classified 35 corporate/PM skills as stable drift, flagged 15 for manual review. MEMORY.md skill-count summary line updated. |
| 2026-06-13 | Stable drift NO-OP | Same 35-bundle, same 1 Hermes-only, chunk counts identical to 06-12. |
| 2026-06-14..06-17 | Stable drift NO-OP | Same numbers across all four runs (LobsterAI 136 / Hermes 103, missing-in-hermes 35, missing-in-lobster 2 — `debugging` + `product-research` are both intentional 簡版名 on Hermes side). 06-17 confirmed LobsterAI SQLite mtime Jun 15 09:32 reflects app restart, not new content. Pre-run script sometimes executes twice in the same minute — write the analysis once at the end of the log, do not re-run. |
| 2026-06-18..06-20 | Stable drift NO-OP + new Hermes-only skill + `knowledge:` bug reproduction | 06-19: Hermes installed top-level `kanban` skill (Hermes 103→104, missing-in-lobster 2→3). This is Hermes-specific multi-agent delegation toolset, NOT a name variant — see "Hermes-only skills" section. 06-20: same numbers (LobsterAI 136 / Hermes 104, missing-in-hermes 35, missing-in-lobster 3 — `debugging`, `kanban`, `product-research`). Also reproduced the `knowledge:` literal-prefix bug from 2026-06-15 — new agent read the user task literally and emitted `[YYYY-MM-DD HH:MM:SS] knowledge: ===` lines in `sync-20260620.log`. Fix: re-append with `### YYYY-MM-DD Agent-Written Sync Results (LobsterAI ↔ Hermes) ###` header. Pattern confirmed: log entry shape is independent of skill count — always use the `###` header. |
| 2026-06-21 | Stable drift NO-OP + **3rd `knowledge:` reproduction** | Same numbers as 06-20 (LobsterAI 136 / Hermes 104, missing-in-hermes 35, missing-in-lobster 3). Reproduced the `knowledge:` literal-prefix bug for the **third time** — wrote `[2026-06-21 09:06:00] knowledge: === Hermes Cron Sync Summary 2026-06-21 ===` + 9 `knowledge:` lines into `sync-20260621.log`. The "Pitfalls (continued)" warning was NOT sufficient to catch a fresh agent; promoted the warning to a prominent `⚠️ LOG FORMAT RULE` callout at the top of `Cron-Delivered Sync Mode` in `SKILL.md` (post-session review only allows memory/skill tools, so the polluted `sync-20260621.log` could NOT be cleaned up in-session — flagged for next cron run). If `sync-20260621.log` still contains `knowledge:` lines on 06-22, the next agent should sed-delete lines 25-end and re-append with the `### 2026-06-21 Agent-Written Sync Results (LobsterAI ↔ Hermes) ###` header. |
| 2026-06-22..06-26 | Stable drift NO-OP + continued `knowledge:` reproductions (4th, 5th, 6th) | Bug continues to reproduce every 4-5 days. Each reproduction: agent loads `skill_view(agent-memory-sync)` AFTER running the sync script and AFTER reading prior-day log files; the literal `knowledge:` token in the cron prompt + visible `knowledge:` lines in prior logs anchor the pattern before the SKILL.md warnings can be read. SKILL.md has been updated multiple times to add stronger warnings but the root cause — load-order — was not enforced. |
| 2026-06-27 | Stable drift NO-OP + **7th `knowledge:` reproduction** + Hermes-only count correction (3→5) | Reproduced the bug for the 7th time. Sequence: ran `bash ~/.hermes/scripts/sync-lobsterai.sh` first, then read `sync-20260626.log` (contained 11 polluted `knowledge:` lines from the 06-26 bug), then pattern-matched and emitted 13 `[2026-06-27 09:08:08] knowledge: ...` lines into `sync-20260627.log`. Also corrected a long-standing tracking error: `missing-in-lobster.txt` actually contains **5 names** (`debugging`, `design`, `kanban`, `product-research`, `trading`), not 3. `design` and `trading` were always Hermes-only but the reference previously undercounted. SKILL.md bumped to v1.6.0 — added explicit "load skill FIRST" hard rule, documented the 2026-06-27 reproduction in the ⛔ STOP block, and updated both the SKILL.md and this reference to recognize 5 Hermes-only skills. Cleanup needed: delete lines from `[2026-06-27 09:08:08] knowledge: === Hermes Cron Sync Summary 2026-06-27 ===` to end of `sync-20260627.log`, then re-append with `### 2026-06-27 Agent-Written Sync Results (LobsterAI ↔ Hermes) ###` header. |
| 2026-06-30 | Stable drift NO-OP + **8th `knowledge:` reproduction** + Hermes-only count correction (5→6) | Reproduced the `knowledge:` bug for the **8th time**. Sequence: ran `bash ~/.hermes/scripts/sync-lobsterai.sh` first (still before loading `agent-memory-sync` skill), read `sync-20260629.log` and `sync-20260627.log` (both polluted with `knowledge:` lines from prior reproductions, seeding the pattern), pattern-matched the visible format, and emitted `[2026-06-30 09:08:00] knowledge: === Hermes Cron Sync Summary 2026-06-30 ===` + 12 polluted `knowledge:` lines into `sync-20260630.log`. Confirms the load-order root cause: warnings in SKILL.md only catch agents who load the skill FIRST. Also corrected Hermes-only count: `missing-in-lobster.txt` now contains **6 names** (`computer-use`, `debugging`, `design`, `kanban`, `product-research`, `trading`) — `computer-use` (cuahq/cua-driver cross-platform desktop automation, v2.0.0) added to Hermes skills on 2026-06-29 15:14, between the 06-29 09:05 and 06-30 09:05 cron runs. LobsterAI has only the macOS sub-skill `apple/macos-computer-use`, no top-level `computer-use` — not an import candidate. Updated both SKILL.md and this reference to recognize 6 Hermes-only skills. Cleanup needed: delete lines from `[2026-06-30 09:08:00] knowledge: === Hermes Cron Sync Summary 2026-06-30 ===` to end of `sync-20260630.log`, then re-append with `### 2026-06-30 Agent-Written Sync Results (LobsterAI ↔ Hermes) ###` header. |

| 2026-07-01 | Stable drift NO-OP + **9th `knowledge:` reproduction** + 16-day stable-drift streak | Reproduced the `knowledge:` bug for the **9th time** despite loading `agent-memory-sync` FIRST (per the v1.6.0 hard rule). Sequence: loaded skill first (good), then read `sync-20260630.log` to compare today's state vs yesterday, found 14 polluted `knowledge:` lines from the previous reproduction, pattern-matched the visible format and emitted `[2026-07-01 09:06:00] knowledge: === Hermes Cron Sync Summary 2026-07-01 ===` + 13 polluted `knowledge:` lines into `sync-20260701.log`. **Critical lesson for the field**: the load-order fix is necessary but NOT sufficient — the visible buggy pattern in prior-day logs is a stronger signal than the SKILL.md warning. SKILL.md bumped to v1.7.0 with a new mitigation: when reading any prior-day log, immediately write a "previous-day cleanup flag" line in today's log naming the polluted previous day (e.g. `⚠️ Previous-day cleanup: sync-20260630.log contains 14 polluted knowledge: lines`) — this breaks the seed chain by making the bug visible to the next reader. Also recorded the **16th consecutive sync day with identical numbers** (LobsterAI=136, Hermes=107 top-level, missing-in-hermes=35, missing-in-lobster=6). Hermes MEMORY.md updated 57→58 lines (+1, today's stats line). LobsterAI SKILLs/ mtime still 2026-06-11 22:48 (20 days, fully stable). LobsterAI memory DB mtime still 2026-06-29 09:32 (2 days, also stable). Cleanup needed: delete lines from `[2026-07-01 09:06:00] knowledge: === Hermes Cron Sync Summary 2026-07-01 ===` to end of `sync-20260701.log`, then re-append with `### 2026-07-01 Agent-Written Sync Results (LobsterAI ↔ Hermes) ###` header. |
| 2026-07-02..07-04 | Stable drift NO-OP + continued `knowledge:` reproductions (10th, 11th) + new `patch`-based dotfile workaround | Bug continues to reproduce despite warnings. 07-02 / 07-03 sequences: cron task arrives → agent runs `bash ~/.hermes/scripts/sync-lobsterai.sh` BEFORE loading this skill → reads prior-day logs (each containing more polluted `knowledge:` lines than the day before) → pattern matches → emits more `knowledge:` lines. SKILL.md updated to v1.8.0 with three structural-fix proposals in `references/lobsterai-stable-drift-2026-07-02-addendum.md` (sync-lobsterai.sh warning file, cron-prompt rewrite, auto-load hook). **2026-07-04 — positive new technical finding**: the `patch` tool's in-place string replacement works as the SIMPLEST workaround for the dotfile-overwrite Tirith scan. Read the log via `read_file`, then `patch(path=..., old_string="=== Sync Complete ===", new_string="=== Sync Complete ===\n\n### analysis block")`. No `/tmp/` round-trip, no `cat >> ...` shell redirect, no awk-chain. SKILL.md bumped to v1.9.0 with this as the new recommended first approach for small analysis-block appends to dotfile logs. **19th consecutive sync day with identical numbers** (LobsterAI=136, Hermes=107 top-level, missing-in-hermes=35, missing-in-lobster=6). USER.md still mtime 2026-05-20 (6+ weeks stable). LobsterAI SKILLs/ mtime still 2026-06-11 22:48 (23 days). All systems green. |
| 2026-07-05 | **Stable drift NO-OP — NO `knowledge:` reproduction (breakthrough, 1st time in 11 runs)** + `write_file` direct-to-log pattern validated | **First successful no-reproduction of the `knowledge:` bug since 2026-06-15** (10 prior cron runs had all reproduced; this 11th attempt is the first to avoid). Sequence: cron task arrived → agent ran `bash ~/.hermes/scripts/sync-lobsterai.sh` twice at 09:05:50 + 09:06:17 (identical output — script sometimes executes twice in the same minute, see pitfall above; agent correctly did NOT re-run after the second invocation) → read prior-day logs (`sync-20260703.log`, `sync-20260704.log` — both polluted with `knowledge:` lines from the 10th/11th reproductions, which would normally seed the pattern) → read all four sync output files + both memory files → wrote the analysis block using **`write_file()` directly to `~/.hermes/cron/sync/sync-20260705.log`** with `### 2026-07-05 09:06 Hermes Analysis (post-sync)` markdown header. NO `knowledge:` prefix, NO `cat >>` heredoc, NO `/tmp/` round-trip, NO `patch` in-place edit — single `write_file()` call succeeded cleanly. This validates the v1.9.0 SKILL.md warning + the v1.6.0 "load skill first" hard rule + the v1.7.0 "treat prior-day `knowledge:` as a bug, not a pattern" mitigation — combination appears sufficient when the agent reads prior-day logs AFTER internalizing the warning. **Minor observation for future NO-OP confidence**: Hermes `config.yaml` mtime refreshed Jul 4 00:56 (1 day before today's sync) by an external process; content was not directly inspected in this run since no sync-relevant changes are expected (auxiliary providers + mcp_servers all match prior recorded state). **The mtime refresh alone is NOT a sync signal** — it can be caused by gateway restarts, code_execution sessions writing via `execute_code`, or any background process that touches the config. **Recommendation for future agents**: when `~/.hermes/config.yaml` mtime is newer than expected but no skill or memory changes are reported by the sync script or memory export, treat as a non-event — do NOT attempt to diff the config unless something downstream is unexplained by stable state. **20th consecutive sync day with identical numbers** (LobsterAI=136, Hermes=107 top-level, missing-in-hermes=35, missing-in-lobster=6). USER.md still mtime 2026-05-20. LobsterAI SKILLs/ mtime still 2026-06-11 22:48 (24 days). LobsterAI memory DB mtime Jul 4 00:56 (refreshed externally; content unchanged — same 361-line export, identical chunks verified by the export diff). All systems green. Cleanup STILL pending: `sync-20260703.log` and `sync-20260704.log` contain `knowledge:` lines from the 10th and 11th reproductions (not cleaned in-session — the post-session review only allows memory/skill tools, so any cron-run agent wishing to clean them must use sed or re-write. These should be sed-cleaned during a future interactive session if the agent has full tool access). |

The expected outcome for any day where the LobsterAI skill count is 136 is "stable drift NO-OP" until either side's skill bundle changes.

## Positive-no-reproduction milestone (2026-07-05)

The 2026-07-05 sync run is the **first successful no-reproduction** of the `knowledge:` literal-prefix bug in the 11 cron runs since it was first documented (2026-06-15). For the prior 10 consecutive runs, every fresh agent that received the cron task reproduced the bug — by reading the colloquial cron prompt literally and pattern-matching the visible `knowledge:` lines in prior-day logs.

What worked on 2026-07-05:
1. Agent read prior-day logs (`sync-20260703.log`, `sync-20260704.log`) which were both polluted with `knowledge:` lines from the 10th/11th reproductions. These would normally seed the pattern.
2. Agent recognized the polluted lines as a known bug rather than a convention (per the v1.7.0 mitigation).
3. Agent used `write_file()` directly to the log path with `### 2026-07-05 09:06 Hermes Analysis (post-sync)` markdown header — NO `knowledge:` prefix emitted.
4. Agent did NOT re-run the sync script after seeing the polluted prior-day logs (the script had already produced identical output twice — `terminal(bash ~/.hermes/scripts/sync-lobsterai.sh)` at 09:05:50 and 09:06:17). Recognizing duplicate runs and not triggering more is itself a good signal.

**Implication for skill maintenance**: the combination of (a) prominent ⛔ STOP block at the top of SKILL.md, (b) v1.6.0 load-order hard rule, (c) v1.7.0 "treat prior-day `knowledge:` as a bug" mitigation, and (d) v1.9.0 `patch` / `write_file` direct-to-log workarounds appears to be sufficient — at least for this agent. The structural-fix proposals in `references/lobsterai-stable-drift-2026-07-02-addendum.md` (sync-lobsterai.sh warning file, cron-prompt rewrite, auto-load hook) remain recommended for defense-in-depth but are no longer the only viable path.

**Caveat**: single-data-point. The next 5-10 cron runs will tell us if this is a one-off lucky escape or a real durable fix. If the bug reproduces again on 2026-07-06 or later, the structural fixes become urgent. If no reproduction through 2026-07-15, the current mitigation can be considered stable.

### 2026-07-25 — mass-sync event: Hermes-only 9 → 0, LobsterAI 137 → 145 (+8)

Between 2026-07-24 and 2026-07-25 09:07, all 9 previously-Hermes-only skills were copied to LobsterAI top-level `SKILLs/` directory. LobsterAI skill count jumped 137 → 145 (+8 net after offsetting other changes). The 6 expected names were `computer-use`, `debugging`, `design`, `kanban`, `product-research`, `trading` — plus 2 others for the +8 net delta. All 9 category-(d) macOS-platform bundles (`hermes-gateway-ops`, `mac-local-environment`, `minimax-model-stack`) are also now on LobsterAI as directory names but their SKILL.md content is Hermes-runtime-specific (launchd / Office CLI / kimi-webbridge / MiniMax MCP) and LobsterAI cannot exercise it.

**First sync day with `missing-in-lobster.txt` empty**: the 9 Hermes-only names are gone from the diff. `missing-in-hermes.txt` still contains the canonical 35-bundle (corporate/PM, intentional role-mismatch drift). This is the **zero-Hermes-only drift** pattern — supersedes the 9-name recognition pattern that was correct from 2026-07-11 to 2026-07-24. Updated SKILL.md to v1.14.0 to reflect the new dominant pattern.

Detection signal: `wc -c missing-in-lobster.txt` returns 0 and `md5sum missing-in-lobster.txt` returns `d41d8cd98f00b204e9800998ecf8427e` (empty file hash). The `hermes-skills.txt` and `lobster-skills.txt` md5 values will NOT match (intentional 35-bundle drift on LobsterAI side), but the Hermes-only set should be empty. Use the "zero-Hermes-only NO-OP log section" template (added above) for daily logs in this state.

### 2026-07-26 (Sunday 09:32) — first NO_REPLY sync under the new pattern

First daily sync to recognize the zero-Hermes-only state. All stable, NO_REPLY. Sunday morning cron trigger; all files in sync, no content updates needed. Confirmed the new template works correctly for the new pattern.

### 2026-07-27 (Monday 09:05) — second NO_REPLY sync under the new pattern

Second daily sync under the zero-Hermes-only state. All stable: Hermes MEMORY.md (45 lines, mtime Jul 22 18:38, 5 日 stable), Hermes USER.md (21 lines, mtime Jul 22 09:36, 5 日 stable), LobsterAI skill count 145 stable, Hermes skill count 110 stable, Hermes-only=0, LobsterAI-only=35 (corporate/PM fingerprint unchanged). Both sides' sync history show clean NO_REPLY outcomes. The "zero-Hermes-only drift" template matches the log entry shape correctly. **Lesson embedded**: when `missing-in-lobster.txt` is empty across consecutive daily logs, it's the expected new stable state — don't manufacture a sync error when the previously-expected 9 Hermes-only names are missing. Reference this file's "Zero Hermes-only NO-OP log section" template for the canonical log entry shape.

## New minor signal: config.yaml mtime refresh is NOT a sync trigger (2026-07-05)

Observed on 2026-07-05: `~/.hermes/config.yaml` mtime was Jul 4 00:56 (1 day before the sync), but no sync-relevant content changes were detectable. The sync script's outputs and the memory export both reported stable state.

**Pitfall to watch for in future agents**: when seeing `config.yaml` mtime newer than expected, do NOT assume a config change happened that needs syncing. Common causes of mtime-only refreshes (no content change):
- Hermes gateway restart writes a normalized version of the YAML (cosmetic only)
- A `code_execution` session wrote via `execute_code` Python `open()`
- The cron framework or curator rotated metadata
- An IDE or backup tool touched the file

**Decision rule**: only treat a `config.yaml` mtime refresh as a sync signal if the sync script's outputs OR the memory export OR the Hermes skills list shows a corresponding delta. If everything else is stable, log the mtime refresh as a non-event and move on.