---
name: autonomous-ai-agents
description: "Delegate coding tasks to autonomous coding agent CLIs (Claude Code, Codex, OpenCode). Covers common orchestration patterns, provider-specific quirks, PTY handling, worktree isolation, parallel execution, and PR review workflows."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Codex, OpenCode, Autonomous, Delegation, PTY, Worktrees, Code-Review]
    related_skills: [claude-code, codex, opencode, hermes-agent]
---

# Autonomous Coding Agents — Common Orchestration

Delegate coding, review, and refactoring tasks to external autonomous coding agents (Claude Code, OpenAI Codex, OpenCode). All three are CLI-based coding agents that can read files, write code, run commands, and manage git workflows.

## When to Use This Skill

Use when the user asks to delegate a coding task to an external agent, wants an autonomous coding session, or needs parallel code implementation/review across multiple worktrees.

**Jump to your agent:**
- [Claude Code](#claude-code) — most comprehensive, best for Claude/Anthropic integration
- [Codex](#codex-openai) — OpenAI's agent, sandbox model, git-required
- [OpenCode](#opencode) — provider-agnostic, best for multi-model flexibility

## Common Orchestration Patterns

All three agents share these patterns:

### Two Modes: Print vs Interactive

| Mode | Use when | PTY needed |
|------|----------|------------|
| **One-shot / print** | Single task, bounded diff, CI scripts | No |
| **Interactive / background** | Multi-turn iteration, exploratory work | Yes (TTY required) |

### Print Mode (Preferred for Automation)

```
# Claude Code
terminal(command="claude -p 'Add error handling' --max-turns 10", workdir="/path", timeout=120)

# Codex
terminal(command="codex exec 'Add error handling'", workdir="~/project")

# OpenCode
terminal(command="opencode run 'Add error handling'", workdir="~/project")
```

### Interactive PTY via tmux (Multi-Turn)

```bash
# Start session
terminal(command="tmux new-session -d -s agent-work -x 140 -y 40")

# Launch agent
terminal(command="tmux send-keys -t agent-work 'cd /path && <agent-cmd>' Enter")

# Wait for startup
terminal(command="sleep 5 && tmux send-keys -t agent-work Enter")  # trust dialog

# Send task
terminal(command="tmux send-keys -t agent-work 'Refactor auth module' Enter")

# Monitor
terminal(command="sleep 15 && tmux capture-pane -t agent-work -p -S -50")

# Exit
terminal(command="tmux send-keys -t agent-work '/exit' Enter")
```

### Worktree Isolation for Parallel Tasks

```bash
# Create isolated worktrees
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main

# Run agents in parallel (one per worktree)
terminal(command="<agent-cmd> 'Fix #78' --full-auto", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="<agent-cmd> 'Fix #99' --full-auto", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# Push and cleanup after acceptance
git worktree remove /tmp/issue-78
```

### Background Monitoring

```bash
terminal(command="<agent-cmd> 'Refactor auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

process(action="poll", session_id="<id>")
process(action="log", session_id="<id>", limit=100)

# Send input if agent asks
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

### PR Review Pattern

```bash
# Clone to temp dir for isolation
REVIEW=$(mktemp -d)
git clone https://github.com/user/repo.git $REVIEW
cd $REVIEW && gh pr checkout 42

# Run review
<agent-cmd> review --base origin/main
```

### Session Continuation

```bash
# Claude Code
terminal(command="claude -p 'Continue refactoring' --resume <session_id> --max-turns 5", workdir="/project")

# OpenCode
terminal(command="opencode run 'Continue refactoring' --continue", workdir="~/project")
```

---

## Claude Code

The most comprehensive coding agent. Best for deep Anthropic model integration, slash commands, hooks, MCP servers, and multi-agent teams.

**Quick start:**
```bash
npm install -g @anthropic-ai/claude-code
claude  # first-run: browser OAuth or --console for API key
```

**Key patterns from `claude-code` skill:**
- **Print mode:** `claude -p 'task' --max-turns 10 --allowedTools 'Read,Edit'`
- **Structured output:** `--output-format json --json-schema '<schema>'`
- **Session resumption:** `--resume <session_id>` or `--continue`
- **Worktree mode:** `claude -w feature-x --tmux`
- **Custom subagents:** `.claude/agents/security-reviewer.md`
- **Hooks for automation:** PostToolUse, PreToolUse, Stop events
- **MCP server integration:** `claude mcp add github -- npx @modelcontextprotocol/server-github`

**Distinctive capabilities:**
- Built-in slash commands: `/review`, `/security-review`, `/plan`, `/compact`
- Settings hierarchy: CLI flags → local → project → user
- CLAUDE.md project memory files
- Auto-mode for classifier inspection
- Plugin ecosystem

**Key pitfalls:**
- Interactive mode REQUIRES tmux — Claude Code is a full TUI app
- `--dangerously-skip-permissions` permission dialog defaults to "No, exit" — must send Down+Enter
- `--max-budget-usd` minimum is ~$0.05 (cache creation cost)
- Context degrades above 70% window — use `/compact` proactively

**Full reference:** The original `claude-code` skill (archived) contains the complete CLI flag reference, slash command catalog, hook types, MCP integration guide, and settings configuration.

---

## Codex (OpenAI)

OpenAI's coding agent with sandbox-based execution. Requires a git repository.

**Quick start:**
```bash
npm install -g @openai/codex
# Auth: OPENAI_API_KEY or CLI OAuth via `codex auth login`
```

**Key patterns from `codex` skill:**
- **One-shot:** `codex exec 'Add dark mode'`
- **Sandboxed:** `codex exec --full-auto 'Refactor auth'` (auto-approves workspace changes)
- **PR review:** `codex review --base origin/main`
- **Background:** `codex exec --full-auto 'task'`, background=true, pty=true

**Distinctive capabilities:**
- Sandbox modes: `--full-auto` (sandboxed, auto-approve), `--yolo` (no sandbox), `--sandbox danger-full-access` (no bubblewrap)
- Git-required: refuses to run outside a git directory (use `mktemp -d && git init` for scratch)
- Batch PR reviews with worktrees

**Key pitfalls:**
- **Always use `pty=true`** — Codex hangs without a PTY
- **Git repo required** — won't run outside git
- Gateway/service context: bubblewrap sandboxing may fail with `uid map: Permission denied` — use `--sandbox danger-full-access` in that case
- Parallel worktrees need separate git worktree directories

**Full reference:** The original `codex` skill (archived) contains the complete flag reference, parallel worktree patterns, and batch review workflows.

---

## OpenCode

Provider-agnostic, open-source coding agent. Best for multi-model flexibility and custom agent workflows.

**Quick start:**
```bash
npm i -g opencode-ai@latest  # or: brew install anomalyco/tap/opencode
opencode auth login  # configure provider (OpenRouter, Anthropic, etc.)
opencode auth list   # verify auth
```

**Key patterns from `opencode` skill:**
- **One-shot:** `opencode run 'Add retry logic'`
- **With context files:** `opencode run 'Review config' -f config.yaml -f .env.example`
- **Interactive background:** `opencode`, background=true, pty=true
- **Custom agents:** `opencode agent create --description '...' --mode primary`
- **Session management:** `opencode session list`, `opencode stats`

**Distinctive capabilities:**
- **VS Code Tunnel / remote SSH PATH issue:** npm global binaries not in restricted PATH — use `npx opencode run` or `$(npm root -g)/bin/opencode`
- Custom agent creation via CLI (LLM-generated agent configs)
- Multi-agent mode (build/plan tabs with `Tab` key)
- Session stats and cost tracking per model
- `Ctrl+C` to exit (not `/exit` — that opens agent selector)

**Key pitfalls:**
- `/exit` is NOT valid — opens agent selector dialog. Use `Ctrl+C` (`\x03`) or `process(action="kill")`
- PATH mismatch between local terminal and Hermes can resolve different binaries
- Enter may need to be pressed twice to submit in TUI
- `opencode agent create` is interactive (2min LLM gen + permissions TUI) — handle via background PTY

**Full reference:** The original `opencode` skill (archived) contains the complete TUI keybinding reference, custom agent file format, binary resolution strategies, and smoke test procedure.

---

## Selection Guide

| Criterion | Claude Code | Codex | OpenCode |
|-----------|-------------|-------|----------|
| **Best model** | Anthropic (Sonnet, Opus) | OpenAI models | Any (OpenRouter, Anthropic, etc.) |
| **Git required** | No | Yes | Recommended |
| **PTY needed** | Yes (interactive) | Yes | Yes (interactive) |
| **Slash commands** | ✅ Rich set | ❌ | ❌ |
| **Hooks/automation** | ✅ Extensive | ❌ | ❌ |
| **MCP integration** | ✅ Native | ❌ | ❌ |
| **Custom agents** | ✅ Via files | ❌ | ✅ Native CLI |
| **Multi-turn sessions** | ✅ tmux | ✅ tmux | ✅ background PTY |
| **Cost tracking** | Per-session JSON | Basic | Per-model stats |
| **Remote/VS Tunnel** | Works | Works | Needs npx workaround |

**Recommendation:** Use Claude Code for the richest integration (Anthropic models, hooks, MCP, slash commands). Use OpenCode for multi-provider flexibility. Use Codex for OpenAI ecosystem work with sandbox isolation.
