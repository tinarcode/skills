---
name: kanban
description: "Kanban multi-agent workflow: orchestrator decomposition + worker execution patterns. For orchestrator profiles (routing/fan-out) use the orchestrator section; for dispatched workers use the worker section."
version: 1.0.0
platforms: [linux, macos, windows]
environments: [kanban]
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, routing, workflow, collaboration]
    related_skills: [kanban-orchestrator, kanban-worker, kanban-codex-lane]
---

# Kanban Multi-Agent Workflow

Kanban is Hermes's built-in multi-agent task board. Orchestrator profiles decompose goals and fan out tasks; worker profiles execute them and hand off results.

The core worker lifecycle (orient → work → heartbeat → block/complete) is auto-injected as `KANBAN_GUIDANCE` in every dispatched worker's system prompt. This skill covers the deeper patterns for both roles.

---

## Orchestrator Role

*Decomposition playbook and routing rules for orchestrator profiles.*

### Discover Available Profiles First

Before creating tasks, know what profiles exist:
```bash
hermes profile list  # run via terminal tool
```

Or sanity-check one name: `kanban_list(assignee="<name>")` returns empty for unknown names.

### When to Use the Board

Create Kanban tasks when ANY of:
1. Multiple specialists needed (research + analysis + writing = 3 profiles)
2. Work must survive a crash/restart (long-running, recurring, important)
3. User might interject (human-in-the-loop at any step)
4. Independent subtasks can run in parallel
5. Review/iteration is expected (reviewer loops on drafter output)
6. Audit trail matters (board rows persist in SQLite)

If none apply — small one-shot reasoning — use `delegate_task` or answer directly.

### Anti-Temptation Rules

Your job: **route, don't execute.**
- Do NOT execute work yourself. For any concrete task, create a Kanban task and assign it.
- Split multi-lane requests before creating cards. Extract independent lanes first.
- Run independent lanes in parallel. Link only true data dependencies.
- Never create dependent work as independent ready cards — use `parents=[...]` in `kanban_create`.
- If no specialist fits available profiles, ask the user.

### Decomposition Playbook

**Step 1 — Understand the goal.** Ask clarifying questions cheaply upfront.

**Step 2 — Sketch the task graph out loud:**
1. Extract the lanes from the request
2. Map each lane to a profile from Step 0 discovery
3. Decide whether each lane is independent or gated by another
4. Create independent lanes as parallel cards with no parent links
5. Create synthesis/review/integration cards with parent links

**Step 3 — Create tasks and link:**
```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="<profile-A>",
    body="Compare infrastructure costs over 3-year window. Sources: AWS/GCP pricing, team estimates.",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="<profile-A>",  # same profile, parallel
    body="Compare query latency, throughput, scaling at ~500GB, 10k QPS peak.",
)["task_id"]

t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="<profile-B>",
    body="Read T1 (cost) and T2 (performance). Produce 1-page recommendation with trade-offs.",
    parents=[t1, t2],
)["task_id"]
```

`parents=[...]` gates promotion — children stay in `todo` until every parent reaches `done`.

**Step 4 — Complete your own task:**
```python
kanban_complete(
    summary="decomposed into T1-T3: 2 research lanes, 1 synthesis",
    metadata={"task_graph": {"T1": {"assignee": "<profile-A>", "parents": []}, "T2": {"assignee": "<profile-A>", "parents": []}, "T3": {"assignee": "<profile-B>", "parents": ["T1", "T2"]}}},
)
```

**Step 5 — Report back** with actual profile names and the task graph.

### Common Patterns

- **Fan-out + fan-in:** N research cards (no parents), one synthesis card (all as parents)
- **Parallel implementation + validation:** implementer card + explorer/researcher card, reviewer depends on both
- **Pipeline with gates:** `planner → implementer → reviewer`, each with `parents=[previous]`
- **Same-profile queue:** N tasks, same profile, no dependencies — dispatcher serializes

### Goal-Mode Cards (Persistent Workers)

For open-ended "keep going until X is true" tasks:
```python
kanban_create(
    title="Translate full docs site to French",
    body="Every page translated, no English left, links intact.",
    assignee="<translator-profile>",
    goal_mode=True,
    goal_max_turns=15,
)
```
Judge re-checks after each turn; worker keeps context. Budget exhausted → blocked for human review.

### Recovering Stuck Workers

Three actions when a worker crashes/hallucinates:
1. **Reclaim** — abort and reset to `ready` (fast path)
2. **Reassign** — switch to a different profile that exists on this setup
3. **Change profile model** — `hermes -p <profile> model`, then Reclaim to retry

### Pitfalls

- Never invent profile names — dispatcher silently drops unknown assignees
- Don't bundle independent lanes into one card
- Don't over-link because of wording — "finally check X" may be parallel if X is static
- Use `parents=[...]` during `kanban_create`, not linking afterward
- If `HERMES_TENANT` is set, pass it on every `kanban_create` call

---

## Worker Role

*Pitfalls, examples, and edge cases for dispatched workers.*

### Workspace Handling

| Kind | What it is | How to work |
|------|-----------|-------------|
| `scratch` | Fresh tmp dir, yours alone | Read/write freely; GC'd when task archived |
| `dir:<path>` | Shared persistent directory | Other runs will read your output — treat as long-lived |
| `worktree` | Git worktree at resolved path | If `.git` missing, run `git worktree add <path> ${HERMES_KANBAN_BRANCH:-wt/$HERMES_KANBAN_TASK}` first |

### Good Handoff Shapes

**Coding task:**
```python
kanban_complete(
    summary="shipped rate limiter — token bucket, keys on user_id with IP fallback, 14 tests pass",
    metadata={"changed_files": ["rate_limiter.py", "tests/test_rate_limiter.py"], "tests_run": 14, "tests_passed": 14, "decisions": ["user_id primary, IP fallback for unauthenticated"]},
)
```

**Needs human review:**
```python
kanban_comment(body="review-required handoff:\n" + json.dumps({"changed_files": [...], "tests_run": 14, "tests_passed": 14}, indent=2))
kanban_block(reason="review-required: rate limiter shipped, 14/14 tests pass — needs eyes on the user_id/IP fallback choice")
```

**Research task:**
```python
kanban_complete(
    summary="3 competing libraries reviewed; vLLM wins on throughput, SGLang on latency, Tensorrt-LLM on memory",
    metadata={"sources_read": 12, "recommendation": "vLLM", "benchmarks": {"vllm": 1.0, "sglang": 0.87, "trtllm": 0.72}},
)
```

**Review task:**
```python
kanban_complete(
    summary="reviewed PR #123; 2 blocking issues (SQL injection in /search, missing CSRF on /settings)",
    metadata={"pr_number": 123, "findings": [{"severity": "critical", "file": "api/search.py", "issue": "raw SQL concat"}, {"severity": "high", "file": "api/settings.py", "issue": "missing CSRF middleware"}], "approved": False},
)
```

### Claiming Cards You Created

Pass `created_cards=[...]` with ids from successful `kanban_create` return values only. Kernel verifies each id exists and was created by your profile — phantom ids block completion.

```python
# GOOD
c1 = kanban_create(title="remediate SQL injection", assignee="security-worker")
kanban_complete(summary="...", created_cards=[c1["task_id"]])

# BAD — invented ids → gate rejects
kanban_complete(summary="Created t_a1b2c3d4", created_cards=["t_a1b2c3d4"])
```

### Block Reasons That Get Answered Fast

Bad: `"stuck"` — no context. Good: one sentence naming the specific decision needed.

```python
kanban_comment(body="Full context: I have user IPs from Cloudflare but some behind NATs...")
kanban_block(reason="Rate limit key: IP (NAT-unsafe) or user_id (requires auth)?")
```

### Heartbeats Worth Sending

Good: `"epoch 12/50, loss 0.31"`, `"scanned 1.2M/2.4M rows"`. Bad: `"still working"`, sub-second intervals.

### Retry Diagnostics

When reopening a task, check prior runs' `outcome`:
- `timed_out` → chunk the work or shorten it
- `crashed` → reduce memory footprint
- `spawn_failed` → usually profile config issue, ask human via block
- `reclaimed` + `archived` → task was pulled out; check status before continuing

### Do NOT

- Call `delegate_task` as a substitute for `kanban_create` — delegate is for short in-run subtasks
- Call `clarify` to ask the human — you're running headless, it times out. Use `kanban_comment` + `kanban_block`
- Modify files outside `$HERMES_KANBAN_WORKSPACE` unless the task body says to
- Complete a task you didn't actually finish — block it instead

### Pitfalls

- Task state can change between dispatch and your startup — always `kanban_show` first
- `dir:` and `worktree` workspaces can have stale artifacts from prior runs
- Don't rely on CLI (`hermes kanban ...`) in containerized backends — use the tools instead

---

## Shared Reference

### Tool ↔ CLI Equivalents

| Tool | CLI |
|------|-----|
| `kanban_show` | `hermes kanban show <id> --json` |
| `kanban_complete` | `hermes kanban complete <id> --summary "..."` |
| `kanban_block` | `hermes kanban block <id> "reason"` |
| `kanban_create` | `hermes kanban create "title" --assignee <profile> [--parent <id>]` |

Use tools from inside an agent; CLI exists for the human operator.
