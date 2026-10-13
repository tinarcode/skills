# TradingAgents Docker Setup Reference

## Quick Start
```bash
cd ~/TradingAgents
docker-compose run --rm tradingagents
```

## Environment Config (~/TradingAgents/.env)
```
DEEPSEEK_API_KEY=sk-<key>
LLM_PROVIDER=deepseek
```
> ⚠️ Both `DEEPSEEK_API_KEY` AND `LLM_PROVIDER=deepseek` are required. The CLI selects the provider from `LLM_PROVIDER`, not from which API key is set.

## Smoke test before interactive run
```bash
docker run --rm --env-file .env tradingagents --help
# Should print usage/options. Confirms image is built and env is wired correctly.
```

## Interactive CLI note (critical)
TradingAgents CLI uses `questionary` (prompt_toolkit) for arrow-key menus. Must run directly on host terminal:
```bash
docker-compose run --rm tradingagents
```
`docker run --rm -it` produces `"the input device is not a TTY"` in agent PTY. `docker-compose run --rm` at least renders the welcome banner before aborting at the prompt — useful for verifying config loads without entering the full flow.

## docker-compose.yml patches applied
- `user: "1000:1000"` — matches container's appuser UID
- `init: true` — proper signal handling
- Named volume `tradingagents_data` with pre-set ownership

## Volume fix (critical)
```bash
docker volume rm tradingagents_tradingagents_data 2>/dev/null
docker volume create tradingagents_tradingagents_data
docker run --rm -v tradingagents_tradingagents_data:/data --user root busybox sh -c "mkdir -p /data/cache /data/memory && chown -R 1000:1000 /data"
```

## Interactive CLI note
TradingAgents uses `questionary` for interactive prompts. Must run directly on host terminal:
```bash
docker-compose run --rm tradingagents
# NOT: docker run --rm -it (fails with "input device is not a TTY" in agent PTY)
```

## Supported LLM Providers
- deepseek, openai, anthropic, google, xai, qwen, glm, openrouter, ollama, azure_openai

## Key files
- Entrypoint: `tradingagents` CLI (installed as package entry point)
- Config: `tradingagents/default_config.py`
- Graph: `tradingagents/graph/trading_graph.py`
- CLI main: `cli/main.py`
