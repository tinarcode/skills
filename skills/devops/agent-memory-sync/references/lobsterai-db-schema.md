# LobsterAI Memory DB Schema

Source of truth discovered during 2026-05-30 sync session.

## Database Location

```
~/Library/Application Support/LobsterAI/openclaw/state/memory/main.sqlite
```

## Tables

### `chunks` — Primary memory store

```sql
CREATE TABLE chunks (
  id TEXT PRIMARY KEY,          -- sha256(hex) of chunk text
  path TEXT NOT NULL,            -- 'MEMORY.md' (or 'memory/YYYY-MM-DD.md')
  source TEXT NOT NULL DEFAULT 'memory',
  start_line INTEGER NOT NULL,   -- 1-indexed first line
  end_line INTEGER NOT NULL,     -- 1-indexed last line
  hash TEXT NOT NULL,            -- first 12 hex chars of sha256
  model TEXT NOT NULL,           -- always 'fts-only'
  text TEXT NOT NULL,            -- actual chunk content
  embedding TEXT NOT NULL,       -- always '[]' (empty JSON array, never a real vector)
  updated_at INTEGER NOT NULL    -- epoch milliseconds (e.g. 1780053117447)
);

CREATE INDEX idx_chunks_path ON chunks(path);
CREATE INDEX idx_chunks_source ON chunks(source);
```

### `chunks_fts` — FTS5 full-text search (STANDALONE, not content-sync'd)

```sql
CREATE VIRTUAL TABLE chunks_fts USING fts5(
  text,
  id UNINDEXED,
  path UNINDEXED,
  source UNINDEXED,
  model UNINDEXED,
  start_line UNINDEXED,
  end_line UNINDEXED
);
```

This is NOT an `content=` table — it does NOT auto-sync with `chunks`. You must manage both tables on insert/delete.

### Other tables

- `chunks_fts_config`, `chunks_fts_content`, `chunks_fts_data`, `chunks_fts_docsize`, `chunks_fts_idx` — FTS5 internal tables, auto-maintained
- `embedding_cache` — cache table (not relevant for sync)
- `files` — file tracking table
- `meta` — empty, no configuration stored

## Original Chunking Strategy (LobsterAI's import)

The 207-line verbose MEMORY.md was chunked into 7 chunks, each ~25-30 lines with ~5-10 line overlaps between adjacent chunks (for context continuity at chunk boundaries). Each chunk is a standalone excerpt from the larger document, not a clean section boundary.

## New Condensed Chunking Strategy (as of 2026-05-30)

The 47-line condensed MEMORY.md is chunked into 3 non-overlapping chunks of ~15-16 lines each, split at `§` section marker boundaries:

| Chunk | Lines | Content |
|-------|-------|---------|
| 1 | 1-16 | Environment + API Keys |
| 2 | 17-32 | Workarounds + Model Routing + TTS |
| 3 | 33-47 | Pets + LobsterAI config + a-split-bill-pwa |

## Chunk ID Generation

```python
import hashlib
chunk_id = hashlib.sha256(chunk_text.encode()).hexdigest()
hash_prefix = chunk_id[:12]
```

## Update Pattern

```sql
BEGIN TRANSACTION;

-- Delete old
DELETE FROM chunks WHERE path='MEMORY.md';
DELETE FROM chunks_fts WHERE path='MEMORY.md';

-- Insert new chunks
INSERT INTO chunks (id, path, source, start_line, end_line, hash, model, text, embedding, updated_at)
VALUES ('<sha256>', 'MEMORY.md', 'memory', <start>, <end>, '<hash12>', 'fts-only', '<escaped text>', '[]', <epoch_ms>);

INSERT INTO chunks_fts (id, path, source, model, start_line, end_line, text)
VALUES ('<sha256>', 'MEMORY.md', 'memory', 'fts-only', <start>, <end>, '<escaped text>');

COMMIT;
```

**Important**: Single quotes in chunk text must be escaped as `''` in SQL statements.
