---
name: minimax-mcp-web-search
description: Hermes MCP workaround for the minimax web_search tool.
---

# minimax-coding-plan-mcp via wrapper (Hermes workaround)

## When to use
- User asks for `mcp__minimax__web_search` / MiniMax web search
- Brave/Tavily/Firecrawl fallback chain exhausted
- Inside Hermes and `mcp__minimax__*` tool namespace unavailable (Hermes MCP client "Connection closed" on stdio)

## Why MCP fails in Hermes
- Package `minimax-coding-plan-mcp==0.0.4` requires `mcp[cli]>=1.6.0` but does `from mcp.server.fastmcp import FastMCP`
- `mcp>=2.0.0` extracted `fastmcp` to a separate package → `ModuleNotFoundError`
- Hermes uses Content-Length framing; server uses line-delimited JSON; connect probe closes stdin early

## Wrapper script (installed at `/Users/user/.local/bin/minimax-mcp-wrapper.sh`)
```bash
#!/bin/bash
exec uvx --from "minimax-coding-plan-mcp" --python 3.12 \
  --with "mcp>=1.6.0,<2" --with "httpx" \
  "minimax-coding-plan-mcp" "$@"
```

## Calling web_search via `terminal`
Write a Python script (use `write_file` + `python3 path.py`, NOT heredoc):

```python
import subprocess, json, os

env = os.environ.copy()
env["MINIMAX_API_HOST"] = "https://api.minimaxi.com"
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if line.startswith("MINIMAX_CN_API_KEY="):
            env["MINIMAX_API_KEY"] = line.strip().split("=",1)[1].strip('"').strip("'")
            break

msgs = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"hermes","version":"1.0"}}},
    {"jsonrpc":"2.0","method":"notifications/initialized","params":{}},
    {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{
        "name": "web_search",
        "arguments": {"query": "USER_QUERY_HERE"}
    }},
]
framed = "\n".join(json.dumps(m) for m in msgs) + "\n"

r = subprocess.run(
    ["/Users/user/.local/bin/minimax-mcp-wrapper.sh"],
    input=framed, capture_output=True, text=True, timeout=30, env=env,
)

for line in r.stdout.split("\n"):
    if '"id":2' in line:
        j = json.loads(line)
        result = j.get("result", {})
        for c in result.get("content", []):
            if c.get("type") == "text":
                inner = json.loads(c["text"])
                for item in inner.get("organic", []):
                    print(f"- {item['title']}\n  {item['link']}\n  {item.get('snippet','')[:200]}")
```

## understand_image
Same wrapper, but `tools/call` name = `understand_image`, args = `{ "prompt": "...", "image_source": "URL or /path" }`. Strip leading `@` from file paths. JPEG/PNG/WebP only.

## Server tool list (confirmed via uvx probe, 2026-08-12)
- `web_search(query: str)` → organic + related searches
- `understand_image(prompt: str, image_source: str)`

## Cost
Paid via MiniMax Token Plan. Key in `~/.hermes/.env` as `MINIMAX_CN_API_KEY`. Source: https://platform.minimaxi.com/docs/token-plan/mcp-guide