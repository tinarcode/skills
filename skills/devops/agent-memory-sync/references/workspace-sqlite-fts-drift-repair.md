# Workspace vs SQLite/FTS Drift Repair

## Signal

LobsterAI's workspace `MEMORY.md` can be newer than `main.sqlite`. A successful workspace-file sync does not prove searchable memory is current.

Verify all three independently:

1. Workspace source contains the new durable fact.
2. `chunks` covers the workspace through its final line and contains the fact.
3. `chunks_fts` has the same row count and can retrieve the fact.

A typical stale-index signature is:

- workspace `MEMORY.md` mtime is newer than `main.sqlite`;
- `max(end_line)` in `chunks` is less than the workspace line count;
- a distinctive marker appears in the workspace but returns zero rows in both SQLite tables.

## Safe repair

Use the packaged script rather than hand-writing SQL:

```bash
python3 ~/.hermes/skills/devops/agent-memory-sync/scripts/reindex-lobster-memory.py \
  --workspace "$HOME/Library/Application Support/LobsterAI/openclaw/state/workspace-main/MEMORY.md" \
  --db "$HOME/Library/Application Support/LobsterAI/openclaw/state/memory/main.sqlite" \
  --path MEMORY.md \
  --marker 'a distinctive synced phrase'
```

The script:

- creates a timestamped SQLite backup first;
- deletes/replaces only rows for the selected `path`;
- preserves daily memory rows and unrelated paths;
- writes both `chunks` and standalone `chunks_fts` in one transaction;
- uses SHA-256 IDs, `fts-only`, and literal `[]` embeddings;
- verifies row-count parity, EOF coverage, marker visibility, and `PRAGMA integrity_check`.

## Marker preflight and retry safety

Choose the marker from the **workspace source being indexed**, not from Hermes memory, USER.md, or a planned sync note. Before any backup or transaction, the packaged script now checks that the exact marker occurs in the workspace file. If it is absent, the script exits without creating a backup or modifying SQLite.

Prefer a distinctive, durable phrase already present in the workspace. Avoid broad phrases that may occur in many overlapping chunks. After a successful run, expect one or more matches in both tables because chunk overlap can legitimately duplicate the marker.

If verification still fails after a transaction (for example, due to a future schema/tokenization change):

1. Restore the database with `cp <auto-backup> <main.sqlite>` — do not reconstruct it by hand.
2. Verify the restored database with row counts, EOF coverage, and `PRAGMA integrity_check`.
3. Re-read the workspace, select a marker known to be present there, then rerun once.
4. Report the final successful backup, not the discarded attempt, in the daily log; record the failed attempt only as an operational note.

## Verification semantics

`chunks_fts` is a standalone FTS5 table, not content-synchronized with `chunks`. Updating one table alone leaves search inconsistent.

For CJK or punctuation-heavy markers, the script's marker verification deliberately uses `LIKE` in both tables. After that structural verification, run a real `MATCH` query separately with a simple tokenizer-friendly term where practical.

## Pitfalls

- Do not replace the whole DB; replace only `WHERE path='MEMORY.md'`.
- Do not call workspace memory and searchable memory collectively “in sync” until both tables are verified.
- Backups and checksum verification are mandatory before writing an external agent's state.
- An empty WAL file with a fresh mtime is not itself evidence of pending content.
