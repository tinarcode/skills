---
name: opendataloader-pdf
category: data-science
description: OpenDataLoader PDF — #1 benchmark PDF parser for AI-ready data extraction and PDF accessibility auto-tagging. Convert PDFs to Markdown/JSON/HTML with bounding boxes, reading order (XY-Cut++), table detection. Requires Java 21+.
trigger: pdf parsing, pdf extraction, opendataloader, convert pdf to markdown, pdf to json, pdf accessibility
---

# OpenDataLoader PDF Skill

## Overview

[OpenDataLoader PDF](https://github.com/opendataloader-project/opendataloader-pdf) — #1 benchmarked PDF parser (0.907 overall accuracy). Extracts structured Markdown, JSON (with bounding boxes), HTML, and Tagged PDF from any PDF.

**Requirements:**
- Java 21+ (`/opt/homebrew/opt/openjdk@21/bin/java`)
- Python 3.10+
- `opendataloader-pdf` pip package (v2.4.3 installed)

**Critical:** Java is keg-only via Homebrew. Always export PATH before using:
```bash
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
```

## Quick Start (Python API)

```python
import opendataloader_pdf

# Convert single PDF to Markdown + JSON
opendataloader_pdf.convert(
    input_path=["document.pdf"],
    output_dir="output/",
    format="markdown,json"
)

# Batch convert all PDFs in a folder
opendataloader_pdf.convert(
    input_path=["/path/to/pdfs/"],
    output_dir="output/",
    format="markdown,json"
)

# With images embedded
opendataloader_pdf.convert(
    input_path=["document.pdf"],
    output_dir="output/",
    format="markdown-with-images",
    image_format="jpeg"
)

# Specific pages only
opendataloader_pdf.convert(
    input_path=["document.pdf"],
    output_dir="output/",
    format="markdown",
    pages="1,3,5-7"
)

# Use PDF structure tree for better reading order
opendataloader_pdf.convert(
    input_path=["document.pdf"],
    output_dir="output/",
    format="markdown,json",
    use_struct_tree=True
)

# Preserve original line breaks
opendataloader_pdf.convert(
    input_path=["document.pdf"],
    output_dir="output/",
    format="markdown",
    keep_line_breaks=True
)

# Sanitize sensitive data (emails, phones, IPs, CC numbers, URLs)
opendataloader_pdf.convert(
    input_path=["document.pdf"],
    output_dir="output/",
    format="json",
    sanitize=True
)

# Tagged PDF output (accessibility auto-tagging)
opendataloader_pdf.convert(
    input_path=["document.pdf"],
    output_dir="output/",
    format="tagged-pdf"
)

# Parallel processing (experimental)
opendataloader_pdf.convert(
    input_path=["document.pdf"],
    output_dir="output/",
    format="markdown",
    threads="4"
)
```

## CLI Usage (direct Java jar)

```bash
export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"
opendataloader-pdf --help
opendataloader-pdf -i document.pdf -o output/ -f markdown,json
```

## Output Formats

| Format | Description |
|--------|-------------|
| `json` | JSON with bounding boxes for every element |
| `markdown` | Clean Markdown |
| `markdown-with-html` | Markdown with HTML for tables |
| `markdown-with-images` | Markdown with embedded image references |
| `html` | HTML output |
| `text` | Plain text |
| `tagged-pdf` | Accessibility-tagged PDF output |

## Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_path` | str or list | One or more PDF paths or directories |
| `output_dir` | str | Output directory (default: input file dir) |
| `format` | str | Comma-separated output formats |
| `password` | str | Password for encrypted PDFs |
| `pages` | str | Page range e.g. "1,3,5-7" |
| `use_struct_tree` | bool | Use PDF structure tree for reading order |
| `reading_order` | str | "xycut" (default) or "off" |
| `table_method` | str | "default" (border-based) or "cluster" |
| `image_output` | str | "external" (default), "embedded", or "off" |
| `image_format` | str | "png" (default) or "jpeg" |
| `keep_line_breaks` | bool | Preserve original line breaks |
| `sanitize` | bool | Replace sensitive data with placeholders |
| `include_header_footer` | bool | Include page headers/footers |
| `detect_strikethrough` | bool | Detect ~~strikethrough~~ text |
| `content_safety_off` | str | Disable safety filters: "all", "hidden-text", "off-page", "tiny", "hidden-ocg" |
| `quiet` | bool | Suppress console logging |
| `threads` | str | Worker threads (1=sequential, >1=parallel experimental) |

## Hybrid Mode (AI-enhanced)

Requires a running hybrid backend server:
```bash
pip install "opendataloader-pdf[hybrid]"
opendataloader-pdf-hybrid --port 5002
```

Then in Python:
```python
opendataloader_pdf.convert(
    input_path=["complex_document.pdf"],
    output_dir="output/",
    format="markdown",
    hybrid="docling-fast",        # or "hancom-ai"
    hybrid_mode="auto",           # "auto" (triage) or "full" (all pages to AI)
    hybrid_fallback=True          # fallback to Java on AI error
)
```

## Python Package Info

- Installed at: `opendataloader_pdf` (v2.4.3)
- Main function: `convert()` (replaces deprecated `run()`)
- Backend: Java JAR launched via subprocess per call

## Pitfalls

1. **Java PATH required**: Java is keg-only. Always run `export PATH="/opt/homebrew/opt/openjdk@21/bin:$PATH"` first, or the Python wrapper won't find the JVM.
2. **Each convert() spawns a JVM**: Batch all files in one call (`input_path=["file1.pdf", "file2.pdf", "folder/"]`). Repeated single-file calls are slow.
3. **Threads > 1 is experimental**: Output may vary slightly on some PDFs. Capped at available CPU cores.
4. **Hybrid mode needs separate server**: Not included in base pip install. Install extra: `pip install "opendataloader-pdf[hybrid]"`.
5. **Content safety is ON by default**: Some invisible/hidden text elements are filtered out. Use `content_safety_off="all"` to disable.
