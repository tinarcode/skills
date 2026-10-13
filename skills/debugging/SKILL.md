---
name: debugging
description: "Complete debugging suite: systematic root-cause analysis, Python pdb/debugpy, and Node.js inspect. All debugging workflows for Hermes agents."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, python, nodejs, pdb, debugpy, breakpoints]
    related_skills: []
---

# Debugging — Complete Workflow Suite

This skill is the umbrella for all debugging approaches. Load any section as needed.

---

## Section A: Systematic Root-Cause Analysis

**The Iron Law:** NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.

### The 4 Phases

**Phase 1 — Root Cause Investigation:**
- Read error messages carefully (don't skip stack traces)
- Reproduce consistently
- Check recent changes (`git log`, `git diff`)
- Trace data flow upstream to find the source
- Add diagnostic instrumentation at component boundaries

**Phase 2 — Pattern Analysis:**
- Find working examples in the same codebase
- Compare against references completely (don't skim)
- Identify every difference, however small

**Phase 3 — Hypothesis & Testing:**
- Form one specific hypothesis: "X is the root cause because Y"
- Make the smallest possible change to test
- Verify before continuing

**Phase 4 — Implementation:**
- Create a failing test case FIRST (regression)
- Fix the root cause, not the symptom
- If 3+ fixes failed: question the architecture

### Phase 1 Completion Checklist
- [ ] Error messages fully read and understood
- [ ] Issue reproduced consistently
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Root cause hypothesis formed

### Red Flags — STOP if you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "I don't fully understand but this might work"
- **"One more fix attempt" after 3+ failures** → architectural problem

### With Hermes Tools
- `search_files` — Find error strings, trace function calls
- `read_file` — Read source code with line numbers
- `terminal` — Run tests, check git history, reproduce bugs
- `web_search`/`web_extract` — Research error messages, library docs

---

## Section B: Python Debugging (python-debugpy)

Three tools, picked by situation:

| Tool | When |
|------|------|
| `breakpoint()` + pdb | Local, interactive, simplest. Add in source, run normally. |
| `python -m pdb` | Launch script under pdb, no source edits needed. |
| `debugpy` | Remote/headless — attach to already-running process. |

### pdb Quick Reference

| Command | Action |
|---------|--------|
| `n` / `s` | next line / step into |
| `r` | return from current function |
| `c` | continue |
| `l` / `ll` | list source around current line / full function |
| `w` | where (stack trace) |
| `u` / `d` | move up / down in the stack |
| `p expr` / `pp expr` | print / pretty-print expression |
| `display expr` | auto-print expr on every stop |
| `b file:line` | set breakpoint |
| `interact` | drop into full Python REPL in current scope |
| `q` | quit |

### Recipe 1: Local breakpoint
Edit the file:
```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()  # drops into pdb here
    return result + y
```
Run normally. **Don't forget to remove `breakpoint()` before committing.**

### Recipe 2: pytest under pdb
```bash
pytest tests/test_file.py::test_name --pdb -p no:xdist
# xdist (parallel) is incompatible with pdb — use -p no:xdist
```

### Recipe 3: Post-mortem on any exception
```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

### Recipe 4: Remote debug with debugpy
```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
debugpy.wait_for_client()
debugpy.breakpoint()
```
Or launch without source edit:
```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client script.py
```

### Common Pitfalls
1. **pdb under pytest-xdist silently does nothing** — always use `-p no:xdist`
2. **`PYTHONBREAKPOINT=0`** disables all `breakpoint()` — check `echo $PYTHONBREAKPOINT`
3. **`breakpoint()` in CI/non-TTY hangs** — never commit it
4. **`debugpy.listen` blocks only if you also call `wait_for_client()`**

---

## Section C: Node.js Debugging (node-inspect-debugger)

Two tools, pick one:
- **`node inspect`** — built-in, zero install, CLI REPL
- **`ndb` / CDP via `chrome-remote-interface`** — scriptable automation

### node inspect Quick Reference

| Command | Action |
|---------|--------|
| `c` / `cont` | continue |
| `n` / `s` | next / step into |
| `o` / `out` | step out |
| `sb('file.js', 42)` | set breakpoint at file.js line 42 |
| `bt` | backtrace (call stack) |
| `repl` | drop into REPL in current scope (Ctrl+C to exit) |

### Attaching to Running Process
```bash
kill -SIGUSR1 <pid>  # Enable inspector
node inspect -p <pid>  # Attach debugger
```

### Programmatic CDP Driver
```javascript
const CDP = require('chrome-remote-interface');
const client = await CDP({ port: 9229 });
const { Debugger, Runtime } = client;
Debugger.paused(async ({ callFrames, reason }) => {
    // Walk scopes, evaluate expressions, capture state
    await Debugger.resume();
});
await Runtime.enable();
await Debugger.enable();
```

### Common Pitfalls
1. **Wrong line numbers in TS** — breakpoints hit emitted JS, not `.ts` (unless sourcemaps enabled)
2. **`--inspect` vs `--inspect-brk`** — `-brk` pauses on first line; plain `--inspect` may race past your breakpoint
3. **Port collisions** — default 9229; use `--inspect=0` for random port
4. **Background kills** — `Ctrl+C` out of `node inspect` leaves target paused; `cont` first or `kill` target explicitly

---

## Quick Reference by Trigger

| User says | Use |
|-----------|-----|
| "debug this systematically" | Section A: systematic-debugging |
| "python debugger / pdb / breakpoint" | Section B: python-debugpy |
| "node debugger / --inspect" | Section C: node-inspect-debugger |
| "debug a running process" | Section B (debugpy) or C (SIGUSR1) |
| "this test is failing" | Section A + B (pytest --pdb) |
