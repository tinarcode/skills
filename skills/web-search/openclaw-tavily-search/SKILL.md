---
name: openclaw-tavily-search
description: Web search via Tavily API — used together with Brave web_search for cross-validation. When user asks to search/look up, run BOTH sources and compare results. Requires TAVILY_API_KEY.
version: 0.2.0
author: Xiaoran Li (@jacky1n7)
license: MIT-0
---

## Cross-Validation Workflow

**When to use:** User asks to search, look up, find links, or verify information. user prefer cross-validation with multiple sources simultaneously.

**Workflow:**
1. Run `mcp_minimax_web_search` (MiniMax MCP) — primary source (用戶主要搜尋工具)
2. Run `brave_web_search` (built-in tool) — secondary source
3. Run `tavily_search` (this skill) — tertiary source for cross-check
4. Compare results: identify agreements, conflicts, and unique findings
5. Present consolidated answer with source verification

**Note:** If one source fails or returns poor results, the other two should compensate. All three sources should be run in parallel for best coverage.

**Output format:**
```
## 搜尋結果：{query}

### ✅ 三者一致（已驗證）
- [item confirmed by all three sources]

### ✅ 兩者一致（已驗證）
- [item confirmed by two sources, noting which ones]

### ⚠️ 有衝突（需留意）
- Brave/MiniMax/Tavily 結果：A
- Brave/MiniMax/Tavily 結果：B

### 🔍 單一來源（僅供參考）
- [unique finding with single source citation]

### 總結
[consolidated answer with source attribution]
```

**Always cite sources:** "According to [Brave/MiniMax/Tavily/Both/etc]"

# Tavily Search

Use the bundled script to search the web with Tavily.

## Requirements

- **TAVILY_API_KEY** — Stored in `~/.hermes/.env` (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)
- Alternative: Set env var `TAVILY_API_KEY` or add to `~/.openclaw/.env`

## Commands

Run from the skill workspace:

```bash
# raw JSON (default)
python3 {baseDir}/scripts/tavily_search.py --query "..." --max-results 5

# include short answer (if available)
python3 {baseDir}/scripts/tavily_search.py --query "..." --max-results 5 --include-answer

# stable schema (closer to web_search): {query, results:[{title,url,snippet}], answer?}
python3 {baseDir}/scripts/tavily_search.py --query "..." --max-results 5 --format brave

# human-readable Markdown list
python3 {baseDir}/scripts/tavily_search.py --query "..." --max-results 5 --format md
```

## Output

### raw (default)
JSON: query, optional answer, results: [{title,url,content}]

### brave
JSON: query, optional answer, results: [{title,url,snippet}]

### md
A compact Markdown list with title/url/snippet.

## Notes

- Keep `max-results` small by default (3–5) to reduce token/reading load.
- Prefer returning URLs + snippets; fetch full pages only when needed.
- For certification/course 「含金量」 questions, search both the local course name and the global credential name, then extract official issuer/course pages before scoring value. See `references/certification-course-value-assessment.md` for the HCIP-Datacom vs EC-Council CCT pattern and answer template.
- For ISO/IT course eligibility questions (e.g. whether ISO 27001 training satisfies an ISO20000 or IT-related certificate requirement), extract the course page and compare exact wording vs broader category wording. See `references/iso-it-course-eligibility.md`.
- For course/certificate eligibility questions (「讀完算唔算符合…要求」), extract the official course page, compare exact credential/standard names against the stated requirement, and answer conditionally without overclaiming. See `references/certification-course-eligibility-assessment.md`.
