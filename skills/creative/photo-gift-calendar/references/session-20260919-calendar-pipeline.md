# Session 2026-09-19 — 12-Photo A5 Chinese Calendar

**user**: user（Tin）
**Project**: 「送畀女朋友嘅手作禮物」 → 12 張相做 2027 月曆
**Style choices**: 雜誌風（每月大相+底下日期）、A5、繁中
**Variants**: 兩個版本（原相版 + 油畫版）
**Output**: 
- `/Users/user/Desktop/calendar_2027/2027日曆_原相版.pdf` (7.3 MB)
- `/Users/user/Desktop/calendar_2027/2027日曆_油畫版.pdf` (9.1 MB)

## Source photos

`~/Desktop/photo/` with naming `1.JPG`-`12.jpeg` (mixed extensions):
- 1.JPG: square (1536²) — 合照，餅乾工作坊
- 2.jpeg: 3088×2316 landscape — 霓虹燈夜景合照
- 3.jpeg: 5712×4284 landscape — **花田+人，橫拍，無 EXIF** → EXIF auto-rotate 無效
- 4.PNG: 1290×2796 portrait — 直向手機相（女友+user+貓+倉鼠）
- 5.jpeg: 5712×4284 landscape — 風景
- 6.jpg: 1280×1707 portrait
- 7.jpeg: 4032×2268 wide landscape
- 8.jpeg: 2268×4032 portrait
- 9.JPG: 1536×2048 portrait
- 10.jpeg: 5712×4284 landscape
- 11.jpeg: 3088×2316 landscape
- 12.jpeg: 5712×4284 landscape

## Iteration Journey

### v1 (failed)
- cv2.stylization `sigma_s=60` → produced RGB noise artifacts in oil variant
- No auto-rotate (3.jpeg stayed sideways in 3月 page)
- Holiday table missing 清明節 date

### v2 (shipped)
- `sigma_s=30, sigma_r=0.45` → clean oil paint look
- Added EXIF auto-rotate helper (worked for 9/12 photos; 3.jpeg still sideways)
- Pre-filtered photos (4.PNG had cartoon-style outlines) → oil variant looks grotesque; documented as known limitation

### Untried / proposed
- OpenCV face-angle detection for 3.jpeg — skipped because slow + unreliable
- Manual rotate-by-hand then re-upload — recommended for next session if user reports more sideways photos

## Bugs Surfaced (kept as pitfalls in SKILL.md)

1. **EXIF-less files don't auto-rotate** — most common failure mode for screenshots, PNG exports, hand-edited JPEGs.
2. **cv2.stylization sigma_s=60 too high** — visible RGB speckles. 30 is the verified sweet spot.
3. **Pre-filtered photos + oil-paint = compound grotesque** — 4.PNG already had cartoon outline filter; oil on top made it look haunted.
4. **Portrait photos cover-cropped into horizontal slots risk chopping faces** — 6月、8月、9月 three portrait photos, 8月 risk highest (subject near top).
5. **First session missed files 1, 3, 5, 6, 7, 8, 9** — user had renamed/added files mid-conversation; on second `ls` all 12 were present. Lesson: don't render until folder is verified complete twice.

## What Worked Well

- Stopping to ask 4 questions (layout, size, style, language) before rendering
- Generating both variants (original + oil) in one pass, same render code
- vision_analyze spot-check on 2-3 pages caught the cv2 sigma_s bug before print
- Stating file paths clearly in the final delivery so user could preview without hunting

## Verification

- vision_analyze on oil_03.jpg → caught sideways photo + RGB noise → triggered v2 fix
- vision_analyze on oil_04.jpg + original_04.jpg → confirmed pre-filter issue → documented limitation
- File size: 7.3 MB + 9.1 MB → quality=92 + LANCZOS resize was right

## Output paths user can find

```
ls ~/Desktop/calendar_2027/
  2027日曆_原相版.pdf
  2027日曆_油畫版.pdf
  original_01-12.jpg   (12 files)
  oil_01-12.jpg        (12 files)
```