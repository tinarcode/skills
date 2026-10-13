#!/usr/bin/env python3
"""Recursive deep-audit of Hermes ↔ LobsterAI skill packages.

Compares every `SKILL.md`-bearing directory under both skill roots and reports:
  * shared packages that are byte-identical
  * shared packages with SHA-256 mismatches (per file + manifest)
  * packages only present on one side

Excludes metadata / implementation artifacts (.git, .archive, .hub,
.sync-backups, node_modules, __pycache__, .venv, venv, .DS_Store) so the
output stays focused on runnable / documented skill packages.

Usage:
    python3 audit-skill-packages.py [--hermes PATH] [--lobster PATH] [--json]

Default paths match the macOS deployment in `~/.hermes/skills/` and
`~/Library/Application Support/LobsterAI/SKILLs/`.

When `--json` is passed, prints the full report as JSON for machine
consumption. Otherwise prints a human summary plus the top 25 mismatches
sorted by `h_newer_days` descending.

Captured as a reusable artifact after the 2026-07-30 sync run, where the
top-level skill counts (110 vs 145) hid the real package counts (197 vs
239). Run this on every sync to catch: (a) shared same-name skill packages
with stale content on either side, and (b) LobsterAI-app-injected sub-skill
packages that should never be mirrored to Hermes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

IGNORE_PARTS = {".git", ".archive", ".hub", ".sync-backups",
                "node_modules", "__pycache__", ".venv", "venv"}
IGNORE_NAMES = {".DS_Store"}


def ignored(p: Path, root: Path) -> bool:
    rel = p.relative_to(root)
    return (any(part in IGNORE_PARTS for part in rel.parts)
            or p.name in IGNORE_NAMES)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def skill_dirs(root: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for p in root.rglob("SKILL.md"):
        if ignored(p, root):
            continue
        rel = p.parent.relative_to(root).as_posix()
        out[rel] = p.parent
    return out


def package_files(d: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for p in d.rglob("*"):
        if p.is_file() and not ignored(p, d):
            rel = p.relative_to(d).as_posix()
            files[rel] = p
    return files


def version_of(path: Path) -> str:
    text = path.read_text(errors="replace")[:4000]
    m = re.search(r"^version:\s*[\"']?([^\s\"']+)", text, re.M)
    return m.group(1) if m else ""


def build_report(hermes: Path, lobster: Path) -> dict:
    hs = skill_dirs(hermes)
    ls = skill_dirs(lobster)
    shared = sorted(set(hs) & set(ls))
    only_h = sorted(set(hs) - set(ls))
    only_l = sorted(set(ls) - set(hs))
    mismatches = []
    identical = 0
    for rel in shared:
        hf = package_files(hs[rel])
        lf = package_files(ls[rel])
        hkeys, lkeys = set(hf), set(lf)
        only_hf = sorted(hkeys - lkeys)
        only_lf = sorted(lkeys - hkeys)
        changed: list[str] = []
        for f in sorted(hkeys & lkeys):
            if sha(hf[f]) != sha(lf[f]):
                changed.append(f)
        if only_hf or only_lf or changed:
            hsmd = hs[rel] / "SKILL.md"
            lsmd = ls[rel] / "SKILL.md"
            hmtime = hsmd.stat().st_mtime
            lmtime = lsmd.stat().st_mtime
            mismatches.append({
                "skill": rel,
                "h_version": version_of(hsmd),
                "l_version": version_of(lsmd),
                "h_mtime": int(hmtime),
                "l_mtime": int(lmtime),
                "h_newer_days": round((hmtime - lmtime) / 86400, 2),
                "only_h_files": only_hf,
                "only_l_files": only_lf,
                "changed_files": changed,
                "h_file_count": len(hf),
                "l_file_count": len(lf),
            })
        else:
            identical += 1
    # sort: sync-skill first, then by largest h_newer_days gap
    mismatches.sort(key=lambda x: (x["skill"] != "devops/agent-memory-sync",
                                   -abs(x["h_newer_days"]),
                                   x["skill"]))
    return {
        "hermes_skill_packages": len(hs),
        "lobster_skill_packages": len(ls),
        "shared_packages": len(shared),
        "identical_shared_packages": identical,
        "mismatched_shared_packages": len(mismatches),
        "only_in_hermes_count": len(only_h),
        "only_in_lobster_count": len(only_l),
        "only_in_hermes": only_h,
        "only_in_lobster": only_l,
        "mismatches": mismatches,
    }


def print_human(report: dict) -> None:
    print(f"Hermes packages    : {report['hermes_skill_packages']}")
    print(f"Lobster packages   : {report['lobster_skill_packages']}")
    print(f"Shared packages    : {report['shared_packages']}")
    print(f"  identical        : {report['identical_shared_packages']}")
    print(f"  mismatched       : {report['mismatched_shared_packages']}")
    print(f"Only in Hermes     : {report['only_in_hermes_count']}")
    print(f"Only in Lobster    : {report['only_in_lobster_count']}")
    if report["only_in_lobster"]:
        print("\nOnly in Lobster (NOT import candidates, run-time injected):")
        for name in report["only_in_lobster"][:30]:
            print(f"  - {name}")
        if len(report["only_in_lobster"]) > 30:
            print(f"  ... and {len(report['only_in_lobster']) - 30} more")
    print("\nTop 25 mismatched shared packages (sorted by H_newer_days):")
    for m in report["mismatches"][:25]:
        print(f"  {m['skill']}: H={m['h_version']} L={m['l_version']} "
              f"Δdays={m['h_newer_days']:+} changed={len(m['changed_files'])}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--hermes", type=Path,
                   default=Path("/Users/user/.hermes/skills"),
                   help="Hermes skills root (default: ~/.hermes/skills)")
    p.add_argument("--lobster", type=Path,
                   default=Path("/Users/user/Library/Application Support/LobsterAI/SKILLs"),
                   help="LobsterAI skills root (default: ~/Library/Application Support/LobsterAI/SKILLs)")
    p.add_argument("--json", action="store_true",
                   help="Print full JSON report (machine-readable)")
    args = p.parse_args()
    if not args.hermes.is_dir():
        print(f"Hermes skills root not found: {args.hermes}", file=sys.stderr)
        return 2
    if not args.lobster.is_dir():
        print(f"LobsterAI skills root not found: {args.lobster}", file=sys.stderr)
        return 2
    report = build_report(args.hermes, args.lobster)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())