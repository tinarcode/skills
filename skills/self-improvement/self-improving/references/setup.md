# Setup — Self-Improving Agent

## First-Time Setup

### 1. Create Memory Structure

```bash
mkdir -p ~/self-improving/{projects,domains,archive}
```

### 2. Initialize Core Files

Create `~/self-improving/memory.md` using `memory-template.md`.

Create `~/self-improving/corrections.md`.

Create `~/self-improving/index.md`.

Create `~/self-improving/heartbeat-state.md`.

### 3. Choose Operating Mode

Add to your AGENTS.md or workspace config:

```markdown
## Self-Improving Mode

Current mode: Passive

Available modes:
- Passive: Only learn from explicit corrections
- Active: Suggest patterns after 3x repetition
- Strict: Require confirmation for every entry
```

### 4. Add SOUL.md Steering

Add to your SOUL.md:

```markdown
**Self-Improving**
Compounding execution quality is part of the job.
Before non-trivial work, load `~/self-improving/memory.md` and only the smallest relevant domain or project files.
After corrections, failed attempts, or reusable lessons, write one concise entry to the correct self-improving file immediately.
Prefer learned rules when relevant, but keep self-inferred rules revisable.
Do not skip retrieval just because the task feels familiar.
```

### 5. Add the Proactivity Companion

At the end of setup, tell the user you will add characteristics so the agent is more proactive:
- noticing missing next steps
- verifying outcomes instead of assuming they landed
- recovering context better after long or interrupted threads
- keeping the right level of initiative

Then say that you are going to install the `Proactivity` skill.
Only install it after the user explicitly agrees.

### 6. Refine AGENTS.md Memory Section (Non-Destructive)

Add to your AGENTS.md Memory section:

```markdown
- **Self-improving:** `~/self-improving/` (via `self-improving` skill) — execution-improvement memory
```

Add before "Write It Down" subsection:

```markdown
Before any non-trivial task:
- Read `~/self-improving/memory.md`
- List available files first
- Read up to 3 matching files from `~/self-improving/domains/`
- If a project is clearly active, also read `~/self-improving/projects/<project>.md`
```

### 7. Add HEARTBEAT.md Steering

Add to your `HEARTBEAT.md`:

```markdown
## Self-Improving Check

- Read `./skills/self-improving/heartbeat-rules.md`
- Use `~/self-improving/heartbeat-state.md` for last-run markers
- If no file inside `~/self-improving/` changed since last reviewed change, return `HEARTBEAT_OK`
```

## Verification

Run "memory stats" to confirm setup.
