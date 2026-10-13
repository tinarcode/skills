#!/usr/bin/env python3
"""Scan Hermes skills trees for duplicate frontmatter `name:` values.

The skill index keys on the frontmatter `name:`, so two directories declaring
the same name make that skill listed but unloadable via skill_view.

Usage:
    python3 scan_duplicate_skills.py            # main + every profile
    python3 scan_duplicate_skills.py /some/root # narrow to specific roots

Exits 1 if any duplicate name is found, so it doubles as a CI gate.
"""
import os
import re
import sys
import collections

# Archival / bookkeeping dirs are never live skill trees.
SKIP = {".archive", ".curator_backups", ".hub", ".locks", "node_modules", ".git"}
NAME_RE = re.compile(r"^name:\s*(.+)$", re.M)


def default_roots():
    base = os.path.expanduser("~/.hermes")
    roots = []
    main = os.path.join(base, "skills")
    if os.path.isdir(main):
        roots.append((main, "main"))
    profiles = os.path.join(base, "profiles")
    if os.path.isdir(profiles):
        for profile in sorted(os.listdir(profiles)):
            skills = os.path.join(profiles, profile, "skills")
            if os.path.isdir(skills):
                roots.append((skills, "profiles/" + profile))
    return roots


def scan(root):
    names = collections.defaultdict(list)
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        if "SKILL.md" not in filenames:
            continue
        total += 1
        path = os.path.join(dirpath, "SKILL.md")
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                head = handle.read(2000)
        except OSError:
            continue
        match = NAME_RE.search(head)
        rel = os.path.relpath(dirpath, root)
        # Key unnamed skills by their own path so they never collide with each other.
        key = match.group(1).strip() if match else "<noname:{0}>".format(rel)
        names[key].append(rel)
    return total, {k: v for k, v in names.items() if len(v) > 1}


def main(argv):
    if argv:
        roots = [(os.path.abspath(p), os.path.basename(os.path.abspath(p))) for p in argv]
    else:
        roots = default_roots()

    bad = 0
    for root, label in roots:
        if not os.path.isdir(root):
            print("SKIP {0}: {1} not found".format(label, root))
            continue
        total, dups = scan(root)
        if dups:
            bad += 1
            print("DUP  {0}: {1} skills, {2} duplicate name(s)".format(label, total, len(dups)))
            for name, paths in sorted(dups.items()):
                print("      {0}".format(name))
                for path in paths:
                    print("        - {0}".format(path))
        else:
            print("OK   {0}: {1} skills, 0 duplicates".format(label, total))

    print("")
    print("trees with duplicate names: {0}".format(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
