---
name: custom-wallpaper-generation
category: creative
description: Generate custom iPhone wallpapers for user with specific character preferences (cat + hamster + boy + girl in Ghibli or other styles).
---

# Custom Wallpaper Generation for user

## Trigger
User requests wallpaper generation, especially with specific character combinations (cat + hamster + boy + girl).

## User's Character Preferences (v13 - latest spec)
- **Style**: Ghibli (default), also tried sketch scan style and Baroque oil painting
- **Composition**: Cat holding hamster, boy holding girl (chain embrace), all four in one scene
- **Cat**: Lynx Point Siamese - tabby stripes, M mark on forehead, smaller size
- **Girl**: Open eyes (visible pupils), pointed chin, short hair with golden gradient highlights
- **Boy**: Squinty eyes (single line), muscular build, dark short hair with bangs
- **Size**: iPhone portrait wallpaper (720x1280 or similar)

## Workflow
1. Use SiliconFlow API (Token Plan / qwen-image-2.0) with stored API key
2. Construct detailed prompt incorporating user preferences
3. Save to `/tmp/ghibli_wallpaper_v{N}.png` (increment version)
4. Crop/resize for iPhone using ffmpeg (NOT PIL - PIL not available in execute_code sandbox):

```bash
# iPhone portrait: 1170x2532 (9:19.5 ratio)
# For square source: scale to cover, then crop from center
ffmpeg -y -i "/path/to/source.jpg" \
  -vf "scale=2532:2532,crop=1170:2532" \
  "/tmp/iphone_wallpaper.png"
```

5. Send via `MEDIA:/tmp/iphone_wallpaper.png` (WeChat accepts this format)

## Pitfalls
- **PIL not available** in execute_code sandbox — use ffmpeg via terminal instead
- WeChat send times out frequently — inform user of file path as fallback
- ffmpeg: use `-y` to overwrite, single image needs `-frames:v 1` or pattern issue
- Iterative refinement is expected - user will request specific tweaks per version
- Track version numbers to avoid overwriting
- MiniMax vision (vision_analyze) returns 401 — use mcp_minimax_understand_image instead
