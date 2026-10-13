#!/usr/bin/env python3
"""Rebuild one LobsterAI memory path in SQLite + FTS from its workspace file.

Backs up the DB, preserves rows for all other paths, uses parameterized SQL,
preflights optional markers against the workspace source, and commits only after
coverage, FTS row count, marker visibility, and SQLite integrity all verify.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", required=True, type=Path, help="Workspace markdown source")
    p.add_argument("--db", required=True, type=Path, help="LobsterAI main.sqlite")
    p.add_argument("--path", default="MEMORY.md", help="Value stored in chunks.path")
    p.add_argument("--chunk-lines", type=int, default=32)
    p.add_argument("--overlap", type=int, default=7)
    p.add_argument("--marker", help="Optional text whose presence is verified with LIKE")
    p.add_argument("--backup", type=Path, help="Optional explicit backup path")
    return p.parse_args()


def main() -> None:
    a = parse_args()
    if a.chunk_lines < 1 or a.overlap < 0 or a.overlap >= a.chunk_lines:
        raise SystemExit("Require chunk-lines >= 1 and 0 <= overlap < chunk-lines")
    if not a.workspace.is_file() or not a.db.is_file():
        raise SystemExit("Workspace source and SQLite DB must both exist")

    lines = a.workspace.read_text(encoding="utf-8").splitlines()
    workspace_text = "\n".join(lines)
    if a.marker and a.marker not in workspace_text:
        raise SystemExit(
            "Marker is not present in the workspace source; refusing to back up or modify the database"
        )

    backup = a.backup or a.db.with_name(f"{a.db.name}.pre-reindex-{int(time.time())}.bak")
    shutil.copy2(a.db, backup)

    step = a.chunk_lines - a.overlap
    now_ms = int(time.time() * 1000)
    chunks: list[tuple[object, ...]] = []
    start = 1
    while start <= len(lines):
        end = min(len(lines), start + a.chunk_lines - 1)
        text = "\n".join(lines[start - 1 : end])
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        chunks.append(
            (digest, a.path, "memory", start, end, digest[:12], "fts-only", text, "[]", now_ms)
        )
        if end == len(lines):
            break
        start += step

    con = sqlite3.connect(a.db)
    try:
        con.execute("PRAGMA busy_timeout=5000")
        con.execute("BEGIN IMMEDIATE")
        con.execute("DELETE FROM chunks WHERE path=?", (a.path,))
        con.execute("DELETE FROM chunks_fts WHERE path=?", (a.path,))
        con.executemany(
            "INSERT INTO chunks "
            "(id,path,source,start_line,end_line,hash,model,text,embedding,updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            chunks,
        )
        con.executemany(
            "INSERT INTO chunks_fts (text,id,path,source,model,start_line,end_line) "
            "VALUES (?,?,?,?,?,?,?)",
            [(c[7], c[0], c[1], c[2], c[6], c[3], c[4]) for c in chunks],
        )
        row_count = con.execute("SELECT count(*) FROM chunks WHERE path=?", (a.path,)).fetchone()[0]
        fts_count = con.execute("SELECT count(*) FROM chunks_fts WHERE path=?", (a.path,)).fetchone()[0]
        max_end = con.execute("SELECT max(end_line) FROM chunks WHERE path=?", (a.path,)).fetchone()[0]
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        marker_rows = None
        marker_fts_rows = None
        if a.marker:
            like = f"%{a.marker}%"
            marker_rows = con.execute(
                "SELECT count(*) FROM chunks WHERE path=? AND text LIKE ?", (a.path, like)
            ).fetchone()[0]
            marker_fts_rows = con.execute(
                "SELECT count(*) FROM chunks_fts WHERE path=? AND text LIKE ?", (a.path, like)
            ).fetchone()[0]
        if row_count != len(chunks) or fts_count != len(chunks):
            raise RuntimeError("Verification failed: chunk/FTS row count mismatch")
        if lines and max_end != len(lines):
            raise RuntimeError("Verification failed: indexed range does not reach workspace EOF")
        if integrity != "ok":
            raise RuntimeError("Verification failed: SQLite integrity_check is not ok")
        if a.marker and (marker_rows == 0 or marker_fts_rows == 0):
            raise RuntimeError("Verification failed: marker not present in both tables")

        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

    result = {
        "workspace": str(a.workspace),
        "workspace_lines": len(lines),
        "database": str(a.db),
        "backup": str(backup),
        "path": a.path,
        "chunk_lines": a.chunk_lines,
        "overlap": a.overlap,
        "chunks": row_count,
        "chunks_fts": fts_count,
        "max_end_line": max_end,
        "integrity_check": integrity,
        "marker_chunks": marker_rows,
        "marker_fts_rows": marker_fts_rows,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
