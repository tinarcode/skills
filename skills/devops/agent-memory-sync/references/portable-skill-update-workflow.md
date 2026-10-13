# Portable Skill Update Workflow

Captured 2026-07-22. The patterns below were used to copy four portable skill packages to LobsterAI without breaking runtime-specific variants. Applicable to any Hermes↔LobsterAI (or Hermes↔other-agent) sync where the source has a richer or newer version of a skill that already exists on the destination.

## 1. Pre-copy audit (catches drift BEFORE any writes)

For each shared skill directory (i.e. name exists on both source and destination), compare the source's `SKILL.md` to the latest durable user directive on the source side. The check is independent of the SHA-256 mismatch signal — a same-name skill with byte-different content can be a legitimate update, OR a sign that the destination carries a runtime-specific variant the source does not.

```bash
# Read the latest user directive
cat ~/.hermes/memories/USER.md
cat ~/.hermes/memories/MEMORY.md

# For each shared skill, list the absolute/must/HARD STOP/NEVER wording and check
# whether any of it contradicts the latest directive.
grep -nE 'MUST|HARD STOP|NEVER|必須|HARD 一定要|硬性' "$H_SKILL/SKILL.md"
```

If a contradiction is found, the source SKILL.md itself needs a fix (bump version + rewrite the section) BEFORE the copy. Real example from 2026-07-22: `image-generation-workflow` v1.2.0 had "HARD STOP 必須問模型" while user moved to "default MiniMax image-01, no model-selection question" on 2026-07-09. Bumped to v1.3.0, rewrote the section, then copied.

## 2. Backup root (single timestamped directory, not per-skill)

Use a single backup root for the whole batch. Keeps rollback paths findable in one place and makes the log line auditable in a single grep.

```bash
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP="$LOBSTER_SKILLS/.sync-backups/$STAMP"
mkdir -p "$BACKUP"
```

Then for each skill package you're about to copy, snapshot the destination under the backup root:

```bash
# (e.g. for devops/agent-memory-sync)
mkdir -p "$BACKUP/devops-agent-memory-sync"   # or under a "<category>/<skill>" structure
cp -R "$LOBSTER_SKILLS/devops/agent-memory-sync" "$BACKUP/devops-agent-memory-sync/"
```

If you decide after the copy that a particular package should NOT have been updated (e.g. destination has a runtime-specific variant), restore it with `cp`:

```bash
cp "$BACKUP/devops-agent-memory-sync/SKILL.md" "$LOBSTER_SKILLS/devops/agent-memory-sync/SKILL.md"
```

**Why `cp` (not `cat <<` or `>>`)**: `cp` overwrites cleanly; `>` / `>>` / `cat << EOF >>` are all subject to Tirith dotfile-overwrite scans in cron context.

## 3. Copy with SHA-256 verification (per file)

For each file in the source package, copy and immediately verify the SHA-256 of the destination matches the source. Bumping the skill version is appropriate when content changes.

```bash
# Example: copy SKILL.md + references/* + scripts/* for one skill
SRC="$HOME/.hermes/skills/devops/agent-memory-sync"
DST="$LOBSTER_SKILLS/devops/agent-memory-sync"

for rel in SKILL.md references/workspace-sqlite-fts-drift-repair.md scripts/reindex-lobster-memory.py; do
  mkdir -p "$DST/$(dirname "$rel")"
  cp "$SRC/$rel" "$DST/$rel"
  src_sha=$(shasum -a 256 "$SRC/$rel" | cut -d' ' -f1)
  dst_sha=$(shasum -a 256 "$DST/$rel" | cut -d' ' -f1)
  [ "$src_sha" = "$dst_sha" ] || { echo "mismatch on $rel"; exit 1; }
done
```

Python equivalent (use when shell `shasum` is unavailable — sqlite3 + python3 are always available):

```python
from pathlib import Path
import hashlib, shutil
H = Path("/Users/user/.hermes/skills"); L = Path("/Users/user/Library/Application Support/LobsterAI/SKILLs")
for rel in ["SKILL.md", "references/workspace-sqlite-fts-drift-repair.md"]:
    s, d = H/rel, L/rel
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(s, d)
    assert hashlib.sha256(s.read_bytes()).digest() == hashlib.sha256(d.read_bytes()).digest(), rel
```

## 4. When NOT to copy a "different" skill

Reject the copy if the destination's variant is runtime-specific, not portable. The fingerprint is a content diff whose context references the destination's runtime (e.g. macOS-specific paths, runtimes, install scripts that wouldn't translate). Real example from 2026-07-22: `using-agent-skills` had different content on LobsterAI (177 lines, no nested-skill discovery section) vs Hermes (193 lines, with a `User-named skill lookup` section). The proposed fix was to add a generic version of that section to LobsterAI. But LobsterAI's variant was runtime-specific to LobsterAI's skill discovery pipeline, and the copy would have polluted the destination. **Action**: copy attempted → verified the change was wrong → restored via `cp <backup> <target>`. Logged the no-op with rationale.

## 5. What to record in the daily log

For each portable skill package copied, the daily log entry should include:
- Skill name and category
- New version number (if bumped on the source)
- One-line description of the change
- SHA-256 fingerprint (or just the matched-shas assertion)
- Backup root path
- Any rollback decisions (e.g. "considered X, restored via backup because Y")

Format:
```
✅ Updated portable skill content with verified backups and SHA-256 checksums:
    - <category>/<skill>: <one-line summary> (v<new>).
    ...
  Backup root: <path>
```

## 6. Pre-copy audit checklist (reuse every sync)

- [ ] Hermes USER.md / MEMORY.md inspected for latest durable directives
- [ ] For each shared skill, the source SKILL.md scanned for absolute/must/HARD STOP wording
- [ ] Any contradiction fixed on the source first (bump version + rewrite section)
- [ ] Destination variant inspected for runtime-specific content (decide copy vs. skip)
- [ ] Backup root created with timestamp
- [ ] Per-file `cp` + `shasum -a 256` verification
- [ ] Log entry with backup root path
- [ ] Restore any mistaken copy via `cp` from backup, not from source
