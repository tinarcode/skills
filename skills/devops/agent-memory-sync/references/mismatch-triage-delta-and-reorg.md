# Mismatch triage: Δ predicts nothing, and big line deltas are often reorganization

Captured 2026-10-12, after the recursive audit on 2026-10-11 produced a **false NO-OP**.

## 1. The failure this file prevents

On 2026-10-11 the mismatch list was triaged by `h_newer_days` and the whole large-Δ group was written off in one line:

> "Δ≈146 cluster (`finance/daily-us-stock-news` etc.) = install-timestamp artifact + long-standing intentional variants → stable noise"

Nothing in that group was diffed. The next day, diffing all of them found **8 real portable corrections**, four of which were commands that fail outright if executed:

| Skill | Version | What was actually wrong on the destination |
|---|---|---|
| `mlops/huggingface-hub` | 1.0.0 → **1.0.1** | `hf upload-large-folder` is **[Deprecated]** → use `hf upload`; `hf papers list` → `hf papers ls` |
| `mlops/evaluation/weights-and-biases` | 1.0.0 → **1.0.1** | sweep `distribution: log_uniform` → **`log_uniform_values`** (2 sites) |
| `smart-home/openhue` | 1.0.0 → **1.0.1** | releases ship **tarballs, not bare binaries** — old `curl …/openhue-linux-amd64` silently 404s |
| `productivity/nano-pdf` | 1.0.0 | added `related_skills` cross-refs (`pdf`, `ocr-and-documents`) for structural/scan work |
| `productivity/ocr-and-documents` | 2.3.0 | missing PaddleOCR-VL self-hosted OCR section + `paddleocr-api` cross-ref |
| `media/image-generation-workflow` | 1.3.0 | options table stale at 2026-07-08; missing `image-01-live` (verified 2026-08-12) |
| `finance/daily-us-stock-news` | 3.0.0 | missing futu OpenD interactive-relogin fallback (cron can never open port 11111) |
| `context-engineering` | — | missing `references/memory-management.md` file entirely (not just the link to it) |

Meanwhile the small-Δ group (Δ<7 days, 12 skills) was genuinely all noise. **Small Δ was noise; a 145-day Δ was a critical fix.** The delta magnitude carried zero information.

## 2. The only reliable discriminator

`h_newer_days` is a *sort key*, not a *verdict*. Sort by `abs(h_newer_days)` so nothing hides in the tail, then **`diff` every single element** before writing a triage sentence.

Cheap fingerprints that predict a real correction (vs. noise):

- **`h_version` and `l_version` disagree** — a version bump on the source is the author saying "I changed something". In the 2026-10-12 batch, all four command-breaking fixes carried a version bump.
- The diff touches a **command, endpoint, flag, deprecation notice, or config key** — not a path constant and not a metadata line.
- The diff has **real added prose** (a new section, a new reference file), not just `version:`/`description:` in frontmatter.

Fingerprint that predicts noise: the diff is 1–2 lines of `official: true`, a runtime path constant (`HERMES_SKILLS_ROOT` vs `LOBSTERAI_SKILLS_ROOT`), a set-vs-tuple rewrite, or `changed_files: []` (hash granularity, nothing actually differs).

## 3. A large line delta can be reorganization, not content

`research/research-paper-writing` looked like Hermes had **lost 758 lines** of paper-drafting craft. It had not — Hermes had extracted the inline `## Phase 5: Paper Drafting` block into `references/phase5-paper-drafting.md` (757 lines) with byte-identical section titles.

Check before concluding "the destination is richer, copy it":

```bash
grep -E "^#{2,3} " "$HERMES/$p/SKILL.md" | tail -25
grep -E "^#{2,3} " "$LOBSTER/$p/SKILL.md" | tail -25   # compare section titles, not line counts
diff <(cd "$HERMES/$p" && find . -type f | sort) <(cd "$LOBSTER/$p" && find . -type f | sed "s|^$p/||" | sort)
```

If the titles match and the file inventory differs by one extracted reference file, it is the **same content in a different shape** → do not copy either direction. This applies to the reverse direction too.

## 4. Overlap with a destination-native skill is also a reason not to copy

`software-development/plan` on Hermes is v2.0.0 with +283 lines of plan-authoring craft. It looked like a clear upgrade. But LobsterAI already ships `software-development/writing-plans` v1.1.0 (297 lines) whose section titles match almost one-for-one, *plus* a separate `create-plan`. Copying `plan` v2.0.0 would have created a third overlapping plan skill on the destination. Check whether the destination already covers the capability under a different name before mirroring:

```bash
find "$LOBSTER_SKILLS" -maxdepth 3 -type d \( -name "writing-plans" -o -name "create-plan" -o -name "plan" \) -not -path "*/.sync-backups/*"
```

## 5. Stale flattened duplicates on the destination

LobsterAI carries **both** `devops/agent-memory-sync/` (current, v1.22.0, 689 lines) and a top-level `devops-agent-memory-sync/` (mtime Aug 12, **v1.19.0**, 638 lines). The flattened name is the long-standing "1 renamed variant" in `missing-in-hermes.txt`.

- Do **not** delete it during sync. Deleting on the destination is destructive and outside the copy recipe (backup-then-copy only ever *adds or overwrites*).
- Record it as a finding for user to decide.
- When classifying one-sided names, first ask whether the name is a **flattened stale copy** of a nested current package rather than a genuine rename.

```bash
find "$LOBSTER_SKILLS" -maxdepth 3 -type d -name "agent-memory-sync" -not -path "*/.sync-backups/*"
grep -m1 '^version:' "$LOBSTER_SKILLS/devops-agent-memory-sync/SKILL.md" "$LOBSTER_SKILLS/devops/agent-memory-sync/SKILL.md"
```

## 6. Verifying a copied skill carries no new runtime pollution

After copying Hermes SKILL.md files to the destination, check that any runtime-specific tokens (`~/.hermes`, `HERMES_`, `minimax-mcp`) were **already present in the backup**, i.e. pre-existing, not newly introduced by the copy:

```bash
B="$LOBSTER_SKILLS/.sync-backups/<stamp>"
grep -cE "HERMES_|~/.hermes|minimax-mcp" "$B/productivity/ocr-and-documents/SKILL.md"   # before
grep -cE "HERMES_|~/.hermes|minimax-mcp" "$LOBSTER_SKILLS/productivity/ocr-and-documents/SKILL.md"  # after
```

Equal counts = no new pollution. Higher count = the copy brought Hermes-only paths, which is a signal to reconsider.
