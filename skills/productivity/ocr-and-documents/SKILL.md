---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf)."
version: 2.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint, local-ocr, paddleocr-api]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs, scanned documents, and image screenshots that need OCR**.

## Image Screenshot OCR for WeChat / image_cache

When the user says "幫我OCR" after sending an image, first locate the newest likely image in `~/.hermes/image_cache/` or `~/.hermes/cache/` if no explicit path is given:

```bash
python3 - <<'PY'
from pathlib import Path
import time
paths=[]
for base in [Path.home()/'.hermes/image_cache', Path.home()/'.hermes/cache']:
    if base.exists():
        for p in base.rglob('*'):
            if p.is_file() and p.suffix.lower() in ['.png','.jpg','.jpeg','.webp','.heic','.pdf']:
                st=p.stat(); paths.append((st.st_mtime, st.st_size, p))
for mt,size,p in sorted(paths, reverse=True)[:10]:
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mt)), f'{size/1024:.1f}KB', p)
PY
```

For image OCR, prefer the native MCP image-understanding tool (`mcp_minimax_understand_image`) over `vision_analyze` when available, using a prompt like: "請對圖片進行高準確度OCR。保留原文語言、標題、段落、數字、日期、符號和表格結構；不要總結，不要改寫。不確定文字用【?】標示。" Then return a cleaned transcript in a code block and a short note only if useful.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## Self-Hosted OCR Models (local-ocr Variant)

For **self-hosted OCR** — particularly for Traditional/Simplified Chinese, complex layouts, or cost-sensitive use cases — `local-ocr` covers model selection, benchmarking, and deployment in depth.

### Top Recommendation: PaddleOCR-VL

| Metric | Value |
|--------|-------|
| **OmniDocBench v1.5** | **94.5%** (#1 open-source, Jan 2026) |
| **Previous (PaddleOCR-VL)** | 92.86% |
| **Languages** | 109, excellent CJK (Traditional + Simplified) |
| **Speed** | Fastest benchmarked (1x vs 0.88x MinerU, 0.28x dots.ocr) |
| **VRAM** | ~2.5 GB |
| **Self-hosted cost** | ~$0.09 / 1,000 pages |
| **HuggingFace** | `PaddlePaddle/PaddleOCR-VL-1.5` |

### Open-Source OCR Leaderboard (OmniDocBench)

| Rank | Model | OmniDoc | License |
|------|-------|---------|---------|
| 1 | **PaddleOCR-VL-1.5** | **94.5** ⭐ | Apache 2.0 |
| 2 | PaddleOCR-VL | 92.86 | Apache 2.0 |
| 3 | MinerU 2.5 | 90.67 | AGPL-3.0 |
| 4 | Qwen3-VL-235B | 89.15 | Qwen License |
| 5 | MonkeyOCR-pro-3B | 88.85 | Apache 2.0/MIT |

### Language Support Summary

| Model | 繁體中文 | 簡體中文 | English | 日文 | 韓文 |
|-------|---------|---------|---------|------|------|
| **PaddleOCR** | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ | ✅ |
| **Surya** | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ | ✅ |
| **EasyOCR** | ✅ Good | ✅ Good | ✅ Good | ✅ | ✅ |
| **Tesseract** | ✅ OK | ✅ OK | ✅ Good | ✅ | ✅ |

### Apple Silicon (M1/M2/M3/M4) Deployment

⚠️ **PaddlePaddle in Docker does NOT work on Apple Silicon** — hard crash under Rosetta 2 with `NotImplementedError: ConvertPirAttribute2RuntimeAttribute`.

**Working approaches:**
- **Surya OCR via Docker** — native ARM64, no Rosetta. See `local-ocr/references/surya-docker-arm64.md` for template
- **Surya via native venv + MPS GPU** — 2-3x faster than Docker CPU, no memory limits
- **HuggingFace Transformers + MPS** — PaddleOCR-VL via PyTorch MPS backend (Apple Silicon GPU)

**Key pitfalls:**
- Surya: pin to `a-ocr-service>=0.9.0,<0.10.0` + `transformers>=4.45.0,<4.48.0` (newer versions break)
- Surya needs `requests` explicitly added (missing dependency declaration)
- PaddleOCR 3.x API changed: use `.predict()` not `.ocr()`, constructor params removed

### How to Choose

1. **Chinese OCR + best accuracy** → PaddleOCR-VL-1.5 (self-hosted or cloud API)
2. **Complex PDF layouts + tables** → Surya or PaddleOCR PP-StructureV3
3. **No GPU / quick prototype** → EasyOCR or Tesseract
4. **Cloud API (zero install)** → PaddleOCR-VL-1.6 cloud API via `paddleocr-api` skill
5. **Any Mac, no setup** → MiniMax MCP `mcp_minimax_understand_image` (free, already configured)

**Full details:** The `local-ocr` skill (archived) contains complete benchmark data, Apple Silicon Docker templates, Surya ARM64 deployment guide, and PaddleOCR 3.x migration notes.

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)
- For Chinese-heavy OCR (Traditional or Simplified): this document's `local-ocr` variant section above covers PaddleOCR-VL — the best open-source model for CJK
- For PaddleOCR-VL-1.6 **cloud API** (zero install, no GPU needed): see the `paddleocr-api` skill — job-based API, no GPU needed, works on any Mac
