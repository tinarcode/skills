# Historical log: `knowledge:` reproductions + 2026-07 drift incidents

Extracted from `SKILL.md` (was v1.23.0) on 2026-10-13 to keep SKILL.md under the 100,000-char limit. Nothing here was deleted — it is the long-form history behind the rules that are still stated inline in SKILL.md.

Read this if: you are about to append to a sync log and want to understand *why* the format rules exist, or you are diagnosing a drift pattern first seen in 2026-07.

---

## Part 1 — ✅ Positive milestone — 2026-07-05 first no-reproduction in 11 runs

The 2026-07-05 cron run was the **first time since 2026-06-15** that the `knowledge:` literal-prefix bug was successfully avoided. The agent read prior-day logs that were polluted with `knowledge:` lines from the 10th and 11th reproductions, recognized them as known bugs (per the v1.7.0 mitigation), and emitted the analysis block with a `### ... ###` markdown header. Single `write_file()` call to the log path; no `/tmp/` round-trip, no `cat >>` heredoc, no `patch` in-place edit. This validates the current ⛔ STOP block + load-order hard rule + "treat prior-day `knowledge:` as a bug" mitigation — the combination is sufficient. If you are an agent reading this after a previous reproduction, **know that the current mitigation has worked at least once** — follow it and you will likely also avoid the bug.

### ✅ 2026-07-06 → 2026-07-22 — 17 consecutive no-reproduction days (mitigation proven durable, addendum prediction disproven)

After the 2026-07-05 first success, the next 16 consecutive cron runs (2026-07-06 through 2026-07-21) all successfully avoided the `knowledge:` bug; the 2026-07-22 run is the 17th consecutive clean run. The mitigation remains durable across multiple agents and days; the structural-fix proposals remain optional defense-in-depth.

**2026-07-28 detail (action-class run with two structural fixes)**: pre-run output was canonical; agent skipped the redundant `bash ~/.hermes/scripts/sync-lobsterai.sh` re-run. Verified three reconciliation actions:

1. **Recursive sync-skill gap fix** — deep sub-skill audit showed `devops/agent-memory-sync` was Hermes' most-out-of-date portable package (LobsterAI's copy was v1.13.0, Hermes had v1.14.0 with 10+ pitfall warnings including 4 new `knowledge:` reproduction details). Copied the full 10-file package (SKILL.md + 7 references + 1 script + 1 template) using the portable-skill-update-workflow.md recipe; SHA-256 verified per file; backup root `/Users/user/Library/Application Support/LobsterAI/SKILLs/.sync-backups/20260728-090911/devops-agent-memory-sync`. Without this fix, a future agent loading the skill from LobsterAI would only see v1.13.0 warnings and miss the latest `knowledge:` reproductions — **the rules that protect us from the bug were themselves unprotected**.

2. **FTS indexing lag fix** — workspace MEMORY.md mtime 2026-07-27 09:33 vs SQLite `MAX(updated_at)` 2026-07-23 09:11 (4-day gap) triggered a reindex using the packaged `reindex-lobster-memory.py` with a workspace-present marker ("2026-07-27 (Monday 09:32) LobsterAI Sync"). Result: 25 chunks + 25 FTS rows (was 22), coverage 1–608 (was 1–552), marker FTS 6 hits, `PRAGMA integrity_check=ok`, `PRAGMA wal_checkpoint(FULL)` returned `0|90|90` (all WAL frames cleanly checkpointed). Auto-backup at `main.sqlite.pre-reindex-1785200910.bak`.

3. **No memory edit needed** — Hermes MEMORY.md (45 lines, Jul 22) and USER.md (21 lines, Jul 22) had no new durable facts absent from LobsterAI.

---

## Part 2 — ⚠️ 2026-07-10 21:00 — Hermes MEMORY.md auto-curator prune anomaly (NEW PITFALL)

On 2026-07-10 at ~21:00, the Hermes `~/.hermes/memories/MEMORY.md` was truncated from 33 lines → 3 lines (modified mtime confirmed by `stat -f "%Sm"`). No backup in `~/.hermes/.archive/` or `~/.hermes/.curator_backups/`.

The lesson: a Hermes-side curator can shrink `MEMORY.md` outside of any sync tick. If a sync run finds `MEMORY.md` suddenly much shorter than the last known content, do **not** treat it as "nothing to sync" — compare line counts and re-read; the pruning happened outside the sync cycle and needs manual recovery or a targeted re-sync from the LobsterAI side.

## Part 3 — 📦 2026-07-10 09:53 — Hermes-only skills grew 6 → 9 (3 new macOS-specific bundles, NEW CATEGORY)

Three new Hermes-only top-level skills appeared at Jul 10 09:53 (between the 07-10 09:05 cron run and the 07-11 09:05 cron run):

- `hermes-gateway-ops` — Hermes-specific macOS launchd / gateway plist / lock-file operations
- `mac-local-environment` — macOS local tool routing
- `minimax-model-stack` — MiniMax + SiliconFlow routing

These three are **content-non-portable** (they describe Hermes' own launchd/gateway internals), but their *directory names* were later mirrored to LobsterAI by the 2026-07-25 mass-sync, so they no longer register as Hermes-only. They remain the canonical example of "a skill can be name-present on both sides and still non-portable in content".

---

## Part 4 — 2026-07-02 reproduction (10th) — structural fix needed, not just wording

The tenth reproduction showed that wording-level mitigation was not sufficient on its own: the trigger is structural (a colloquial prompt that reads like a syntax directive, sitting next to a directory of prior logs that contain the literal token). The three structural fixes proposed (and their trade-offs) remain optional defense-in-depth:

1. Emit a warning from `sync-lobsterai.sh` into the sync directory itself.
2. Rewrite the cron prompt so it does not contain the literal token next to the word "log".
3. Add an auto-load hook for this skill at cron start.

## Part 5 — 2026-06-27 reproduction (7th) — same pattern, fresh failure

This session was itself a reproduction. Sequence:

1. Cron prompt arrived with literal `knowledge:` token ("用 knowledge: 保持到呢個 cron …").
2. Agent read prior-day log files which contained the same polluted lines.
3. Agent treated the visible prior-day pattern as the convention and emitted `knowledge:`-prefixed lines.
4. Remediation required stripping the polluted lines from `[2026-06-27 09:08:08] knowledge: === Hermes Cron Sync Summary 2026-06-27 ===` to end of file, then re-appending using the `### 2026-06-27 Agent-Written Sync Results (LobsterAI ↔ Hermes) ###` template from Step 9.

**The generalizable failure mode**: reading a directory where a previous agent made a mistake, and pattern-matching the mistake instead of the intent. The `knowledge:` token in the prompt is the *concept* ("save the knowledge summary to the log"), never a syntax marker.