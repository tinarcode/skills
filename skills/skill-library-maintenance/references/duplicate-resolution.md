# Deciding Which Duplicate Survives

Applies after `scripts/scan_duplicate_skills.py` reports two directories sharing one
frontmatter `name:`. Never delete before this is settled.

## Archetype table

| Archetype | How to recognize it | Survivor |
|---|---|---|
| **Stale bundled copy** | Root-level, no `version:`/`platforms:`/`metadata:`, carries vendor schema dumps (`.xsd`, bundled locale data), duplicated helper trees, or sub-directories that each hold their own `SKILL.md` | The categorized / registry-managed copy |
| **Registry-managed copy** | Frontmatter carries `version:`, `platforms:`, `metadata.hermes.icon`, `tags:`, `source:` | Always the survivor over a root-level copy |
| **Refactored successor** | Script names follow one convention (`docx_read.py`, `docx_edit.py`) while the other follows a pre-merge one (`check_bounding_boxes.py`, `extract_form_structure.py`) | The refactored one, even if it ships fewer files |
| **Both plausible** | Comparable metadata, comparable dates, comparable coherence | Ask. Never guess when two copies are genuinely equal in quality |

## Evidence order

1. Frontmatter richness
2. `SKILL.md` mtime
3. Script/reference naming coherence against what SKILL.md documents
4. Self-containment (`scripts/check_skill_references.py`)

**File count is not evidence.** A stale bundled copy usually ships *more* files than
its refactored replacement — vendor schema dumps, duplicated helpers, sub-skills that
were since merged. Preferring the bigger directory preserves dead weight and drops the
working version.

## Reading the file-set diff

```
diff <(cd OLD && find . -type f | sort) <(cd NEW && find . -type f | sort)
```

- Files unique to OLD that SKILL.md no longer references → dead weight, safe to archive.
- Sub-directories in OLD each holding a `SKILL.md` → OLD predates a merge into one skill.
- Files unique to NEW with no counterpart in OLD → OLD is functionally incomplete.
- Anything unique to OLD that looks load-bearing (a script OLD documents and NEW omits) →
  stop and port it into NEW before archiving OLD. That is a merge, not a cleanup.

## Distinct names that overlap are not duplicates

`debugging` vs `debugging-and-error-recovery`, or `create-plan` vs `plan` vs
`writing-plans`, are separate skills with separate scopes. Overlapping subject matter
is a consolidation candidate for the curator, not a defect to fix during a dedup pass.
Report the overlap and move on.
