#!/usr/bin/env python3
"""Verify a skill ships every support file its SKILL.md names.

Run this BEFORE deleting a duplicate: the survivor must be self-contained,
otherwise removing the other copy trades a resolvable-but-wrong skill for one
that fails only later, when a task reaches the missing step.

Usage:
    python3 check_skill_references.py <skill-dir> [<skill-dir> ...]

Exits 1 if any referenced file is missing.
"""
import os
import re
import sys

REF_RE = re.compile(r"(?:scripts|references|templates|assets)/[A-Za-z0-9_./-]+")
# Strip prose punctuation that follows a path in markdown/inline code.
TRAILING = ".,;:)`'\""


def check(skill_dir):
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        print("FAIL {0}: no SKILL.md".format(skill_dir))
        return False

    with open(skill_md, encoding="utf-8", errors="replace") as handle:
        text = handle.read()

    present = set()
    for dirpath, _, filenames in os.walk(skill_dir):
        for filename in filenames:
            present.add(os.path.relpath(os.path.join(dirpath, filename), skill_dir))

    mentioned = {ref.rstrip(TRAILING) for ref in REF_RE.findall(text)}
    missing = sorted(ref for ref in mentioned if ref not in present)

    scripts = sorted(f for f in present if f.startswith("scripts/") and f.endswith(".py"))
    if missing:
        print("FAIL {0}: {1} referenced file(s) missing".format(skill_dir, len(missing)))
        for ref in missing:
            print("        - {0}".format(ref))
        return False

    print("OK   {0}: {1} support file(s), {2} script(s), no dangling refs".format(
        skill_dir, len(present), len(scripts)))
    return True


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    results = [check(d) for d in argv]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
