# Example: macmini cleanup (2026-05-24)

## Before
- Disk: 228GB total, 17GB used, 4.3GB available (80% capacity)
- APFS snapshots: 3 (com.apple.os.update-* x2, MSUPrepareUpdate x1)

## Findings

### Top consumers
| Path | Size |
|------|------|
| `~/Library/Containers/com.docker.docker/` | 69GB |
| `~/Library/Application Support/Claude-3p/` | 10GB |
| `~/Library/Caches/` | 9.3GB |
| `~/Pictures/` | 8GB |
| `~/Library/Application Support/Google/` | 5GB |

### Docker breakdown
- Images: 67.8GB (26 images, 46.5GB reclaimable)
- Build cache: 37.4GB (20.3GB reclaimable)
- Containers: 1.38GB
- Volumes: 396MB

## Cleanup executed
1. `docker system prune -a -f --volumes` → reclaimed **44.92GB**
   - Deleted images: ai-hedge-fund, cms-app-frontend/backend, paddleocr, busybox, postgres:16-alpine, nginx:alpine, tradingagents, a-ocr-service, futu-api
   - Deleted 4 containers, 1 volume, build cache
2. User caches cleaned: Homebrew (2GB), pip, Go build, Raspberry Pi (1.2GB), Electron ShipIt (790MB), Ollama, node-gyp, GeoServices
3. APFS snapshots: attempted but requires sudo — user must run `sudo tmutil deletelocalsnapshots /`
4. Claude 3p (10GB): identified but not deleted (user decision pending)

## After
- Disk: 228GB total, 17GB used, 75GB available (19% capacity)
- Total reclaimed: ~50GB (44.92 Docker + ~5GB caches)
