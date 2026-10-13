---
name: skill-library-maintenance
description: Audit and dedupe installed Hermes skills.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    icon: lucide:library-big
    tags:
    - Skills
    - Maintenance
    - Dedup
    - Housekeeping
    related_skills:
    - skill-creator
    - skill-vetter
---

# Skill Library Maintenance

## When to Use

- A skill appears in `skills_list` but `skill_view` refuses to resolve it
- Auditing which skills are installed, stale, or duplicated
- The active profile and worker profiles have drifted out of sync
- Pruning copies left behind by bundled installs or curator syncs

## The failure mode

Skills accumulate copies. A bundled install drops one at the tree root, a curator sync
drops one under a category directory, and both declare the same frontmatter `name:`.
The index keys on `name:`, so two directories claiming one name makes that skill
**listed but unloadable** — the only visible symptom is `skill_view` refusing to
resolve it.

## Step 1 — Scan every tree, not just the active one

```
python3 scripts/scan_duplicate_skills.py              # main + all profiles
python3 scripts/scan_duplicate_skills.py SOME/ROOT    # narrow to specific roots
```

The scanner walks each skills root, skips archival dirs, groups `SKILL.md` files by
frontmatter `name`, and exits 1 on any duplicate — so it doubles as a CI gate.

- Walk the tree in ONE Python process and run it as a standalone script. A per-file
  `terminal()` call inside a loop burns the tool-call budget and loses the aggregate
  the moment one call returns an unexpected shape.
- Profile trees are independent roots. The active profile fixing only itself is
  typically 10% of the job — scan all of them before reporting.
- Duplicate `name:` is the defect signal. Two directories with *different* names and
  overlapping content (e.g. `debugging` vs `debugging-and-error-recovery`) are NOT
  defects. Do not merge on duplicate detection alone; mention the overlap and let the
  user decide.

## Step 2 — Pick the survivor before touching anything

Newest is usually right, but verify rather than assume. Rank the evidence:

1. **Frontmatter richness** — `version:` / `platforms:` / `metadata:` / `source:` marks
   a registry- or curator-managed skill over an ad-hoc bundled copy.
2. **mtime of SKILL.md**.
3. **Architectural coherence** — do the shipped script names match what SKILL.md
   actually documents?

Compare the file sets to see what each copy uniquely carries:

```
diff <(cd OLD && find . -type f | sort) <(cd NEW && find . -type f | sort)
```

Read both "only in" lists. Files unique to OLD that SKILL.md no longer references are
dead weight. Sub-directories that each hold their own `SKILL.md` mean OLD predates a
merge into one skill.

**Trap: file count is not quality.** A stale bundled copy routinely ships *more* files
than its refactored replacement — vendor schema dumps, duplicated helper trees,
pre-consolidation sub-skill splits. Keeping the bigger directory preserves the dead
weight and drops the working refactor.

See `references/duplicate-resolution.md` for the survivor decision table by archetype.

## Step 3 — Prove the survivor is self-contained BEFORE removing the loser

```
python3 scripts/check_skill_references.py <survivor-dir>
```

Every `scripts/`, `references/`, and `templates/` path the surviving SKILL.md names
must exist on disk. A skill documenting a script it does not ship is worse than the
duplicate was: the duplicate at least resolved, and this one fails only when a task
reaches that step.

## Step 4 — Archive, don't delete — and gate cross-profile writes

Move losers to `.archive/<date-stamp>/<name>/` **inside the same skills root** so the
move is reversible and `.archive` stays skipped by the scanner.

Profile trees belong to that profile's sessions, not the active one. Report the
cross-profile findings and get explicit approval before mutating any profile other
than the active one. Users approve "fix all of them" readily — what they do not expect
is silent edits across a dozen worker trees.

## Step 5 — Verify through the real tool, not just the filesystem

1. Re-run the scanner — every root must report 0 duplicates.
2. Confirm survivor paths exist and losers are gone.
3. `skills_list` — the total must drop by exactly the number of duplicates removed. A
   count that moved by more or fewer means something else was touched.
4. `skill_view` one survivor per family, by qualified directory path, and confirm full
   content comes back with its tags/metadata.

**Verification trap:** `skill_view` returns a cached `status: unchanged` with
`content_returned: false` for a skill already loaded earlier in the same conversation.
That proves nothing about current state. Verify a skill you have NOT loaded this
session, or load it by qualified path.

## Step 6 — Purge the archive only after everything passes

Delete `.archive/<stamp>` once the survivor loads and the scan is clean. Backups of
verified-dead copies only burn disk and can confuse a later scan.

## Reporting

State: what was duplicated and why it broke, which copy was kept and the evidence
(metadata/date/coherence — not "newer" alone), the verification actually run, and
anything deliberately left alone. Never report a count the tool did not return.
