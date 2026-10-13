# MiniMax Vision (Image Analysis)

## MCP Tool: mcp_minimax_understand_image

**Use this instead of `vision_analyze` tool.** The `vision_analyze` tool makes direct API calls that fail with 401 errors. The MCP tool `mcp_minimax_understand_image` connects to MiniMax's vision model via MCP bridge and works reliably.

### WeChat Image Cache Path
When the user sends an image via WeChat, it appears in:
```
/Users/user/.hermes/image_cache/img_*.jpg
```

### How to Analyze a WeChat Image
```python
mcp_minimax_understand_image(
    image_source="/Users/user/.hermes/image_cache/img_e10112f5ded3.jpg",
    prompt="詳細描述呢張圖片的內容：主體、風格、氛圍、顏色、所有視覺元素"
)
```

### When NOT to Use This
- If the user provides a direct URL or local file path (not from WeChat cache), use `vision_analyze` with `image_url` parameter
- This MCP tool is for MiniMax's vision model; other vision tasks (code analysis, diagram reading) may need different tools

### Session Note
- **May 9, 2026**: Confirmed that `mcp_minimax_understand_image` successfully analyzed a Hypebeast HK Instagram screenshot (UFO image) where the standard `vision_analyze` tool would have failed.
- **May 11, 2026**: Same pattern confirmed again. `vision_analyze` returned "無法看到圖片", then `mcp_minimax_understand_image` succeeded on WeChat cache image at `/Users/user/.hermes/image_cache/img_fd54cbd0f68d.jpg`. Always try MCP tool as fallback when native tool fails — it is the more reliable path for WeChat-sourced images.

### When Both Tools Fail
If `mcp_minimax_understand_image` also fails (e.g., returns "無法看到圖片"), the image may be corrupted or in an unsupported format. Try `sips -s format jpeg /path/to/input.jpg --out /tmp/recompressed.jpg` to re-encode, then analyze the recompressed version.
