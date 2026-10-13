# Hermes Memory Management Patterns

## How Memory Entries Work

The Hermes `memory` tool stores entries as individual blocks. Each `add` call creates one entry. The `remove` action with `old_text` matches the **entire entry content** — not a substring search within entries.

## The Single-Bloc Pitfall

If all memories are stored as one large entry (common when the char limit is exceeded and you keep appending), calling `remove` with a partial `old_text` match will delete the **entire entry**, wiping all memories at once.

**How it happens:**
1. Memory grows to 2,200+ chars as one continuous block
2. You call `memory(action='remove', old_text='some subsection header')`
3. The tool matches the entry's leading text and removes the **whole block**

**Prevention:**
- Keep memory entries short and focused (one topic per entry)
- Use separate entries for: environment, API keys, workarounds, model config, user preferences
- When restoring after a wipe, re-create as multiple small entries, not one big block

**Recovery after accidental wipe:**
- User profile (USER.md) survives separately — it's a different store
- Rebuild from: what you can recall from the current session, user profile data, and the conversation transcript

## Entry Size Budget

With a 2,200 char limit for MEMORY.md:
- Aim for 4–7 entries max
- Each entry ~300–500 chars
- Trim sync logs, session artifacts, and transient task progress — these belong in session search, not memory
