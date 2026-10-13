---
name: docker-github-project-setup
description: Clone a GitHub repo, configure credentials, build and run its Docker container — including interactive-CLI containers and volume permission troubleshooting.
triggers:
  - "install docker"
  - "run with docker"
  - "docker build"
  - "docker-compose run"
  - "clone and run in docker"
  - "GitHub project docker"
category: devops
---

# Docker GitHub Project Setup

Clone a GitHub repository, configure credentials/API keys, build the Docker image, and run the container — including interactive-CLI containers and volume permission fixes.

## Project Directory Convention

Custom Docker projects (not cloned from GitHub) live under `~/docker-project/<name>/`. Each project gets:
```
~/docker-project/<name>/
├── Dockerfile
├── docker-compose.yml
├── data/          # volume-mount: input files
├── output/        # volume-mount: generated output
└── README.md      # usage instructions
```

## Workflow

### 1. Clone the repo
```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>
```

### 2. Configure environment / API keys
```bash
# Check for example env file
ls -la .env* *.example

# Copy and populate
cp .env.example .env
# Edit .env with credentials (API keys, tokens, etc.)
```

### 3. Build the Docker image
```bash
docker build -t <image-name> .
```
Or via docker-compose:
```bash
docker-compose build
```

### 4. Handle volume permissions (common pitfall)
Containers running as a non-root user (e.g., `appuser` in TradingAgents) will fail with `Permission denied` on Docker volumes if the volume was initialized by root.

**Fix — pre-create volume directories with correct UID/GID:**
```bash
# Create and name the volume explicitly
docker volume create <project>_data

# Run a temporary container as root to set up directories
docker run --rm -v <project>_data:/data --user root busybox sh -c "mkdir -p /data/cache /data/memory && chown -R 1000:1000 /data"
```

**Alternative — add user override to docker-compose.yml:**
```yaml
services:
  <service-name>:
    user: "1000:1000"   # match the container's target UID
    init: true          # properly handle signals
```

Then rebuild:
```bash
docker-compose build <service-name>
```

### 5. Run the container

**Non-interactive (flags only):**
```bash
docker run --rm <image-name> --help
```

**Interactive CLI containers (TTY required):**
```bash
# Must run directly on host terminal — NOT via agent PTY
docker run --rm -it <image-name>
# or
docker-compose run --rm <service-name>
```

> ⚠️ Interactive CLIs using libraries like `questionary`, `prompt_toolkit`, or `readline` require a real TTY. They will **abort** or hang when run via piped input or agent PTY. **Run these directly on the host terminal.**

**Detached / background:**
```bash
docker run -d --name <container-name> <image-name>
docker logs -f <container-name>
```

### 6. docker-compose shortcuts
```bash
# Build and run
docker-compose up --build

# Run specific service
docker-compose run --rm <service-name>

# Rebuild
docker-compose build --no-cache
```

## Example: TradingAgents (DeepSeek)

See [`references/tradingagents-setup.md`](references/tradingagents-setup.md) for the full worked example — clone, DeepSeek API key config, volume permissions fix, and docker-compose.yml patches.

## Common Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `Permission denied: /home/appuser/.tradingagents/cache` | Volume owned by root, container runs as UID 1000 | Pre-create dirs with `chown -R 1000:1000` or add `user: "1000:1000"` to compose |
| `the input device is not a TTY` | Running interactive container via agent PTY | Use `--help` flag or run directly on host terminal |
| `Aborted.` (questionary prompt) | Pipe input to interactive CLI | Run directly on host terminal |
| `volume already exists but was not created by Docker Compose` | Manual `docker volume create` conflicts with compose-managed volume | Use `external: true` in compose or remove manual volume |
| `NotImplementedError: ConvertPirAttribute2RuntimeAttribute` (PaddlePaddle on Apple Silicon) | x86_64 PaddlePaddle wheel's OneDNN/PIR code path crashes under Rosetta 2 | Use native macOS Python or HuggingFace Transformers instead; see `local-ocr` skill |
| `libgl1-mesa-glx: has no installation candidate` (Debian Trixie/Bookworm) | Package was renamed | Use `libgl1` instead |

## Volume cleanup
```bash
docker volume rm <project>_data
docker volume create <project>_data
```
