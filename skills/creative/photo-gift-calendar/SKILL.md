---
name: photo-gift-calendar
description: "Photo calendar/photobook PDF. Use on gift calendar."
version: 1.0.0
author: Hermes Agent (auto-saved)
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [photo, calendar, gift, photobook, pdf, pillow, opencv, chinese-typography]
    category: creative
    related_skills: [pdf]
---

# Photo Gift Calendar / Photobook Pipeline

Turn a folder of N photos (typically 12 = months, or any small number) into a print-ready PDF — magazine-style layout, Chinese calendar grid, optional oil-paint stylization, A5/A4 paper sizes. Output is one PDF per style variant.

## When to Use

- 「做個日曆送畀女朋友/男朋友」 / 「12 張相做月曆」 / 「紀念日禮物」
- 「相簿」 / 「photobook」 / 「N 張相印出嚟」
- 「我哋嘅旅行相整本 print-ready」
- 「每月一張相 + 日曆格」 — classic use case
- Any deliverable: photos → magazine grid → print PDF

## Pre-flight: 4 Questions Before Coding

**Don't start rendering until you have these answers** — every missing answer costs a re-render:

1. **Layout** — traditional grid (each month shows the full date matrix) vs magazine (big photo + dates underneath)
2. **Paper size** — A4 / A5 / B5 / Square (210×210mm). A5 300 DPI = 1748×2480 px.
3. **Style variants** — original only? oil-paint? watercolor? Multiple variants = multiple PDFs.
4. **Language** — 全繁中 / 中英 / 中文+數字

Also worth asking if not given:
- Which month maps to which photo (user often has a meaningful order — anniversary month, etc.)
- Any caption / quote per page, or image-only?
- Holidays to mark (default: CN/HK holidays for the target year)

**Stop rule**: if the photo folder is missing files or files don't match naming (e.g. asked for 1-12, only finds 1-6), **stop and ask user to re-confirm**. Don't auto-infer the missing photos from a folder of mismatched names — that creates the wrong mapping.

## Recipe: PIL + OpenCV Pipeline

This is the working recipe verified 2026-09-19 on a 12-photo A5 Chinese calendar. The key bits:

```python
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
import cv2
import calendar

# A5 300 DPI
A5_W, A5_H = 1748, 2480
MARGIN = 100

# macOS Chinese fonts (verified paths)
FONT_HEAVY = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"

# Holidays (year-specific, hard-code)
HOLIDAYS_2027 = {
    (1,1):"元旦", (2,14):"情人節", (3,8):"婦女節",
    (4,5):"清明節", (5,1):"勞動節", (5,9):"母親節",
    (6,1):"兒童節", (6,20):"父親節", (7,1):"回歸",
    (9,25):"中秋節", (10,1):"國慶日", (10,15):"重陽節",
    (11,25):"感恩節", (12,24):"平安夜", (12,25):"聖誕節", (12,31):"除夕",
}
```

### Auto-rotate via EXIF (best-effort)

```python
def auto_rotate(img):
    try:
        from PIL.ExifTags import ORIENTATION
        exif = img._getexif() or {}
        for tag_id, value in exif.items():
            if ORIENTATION.get(tag_id) == 'Orientation':
                if value == 3: img = img.rotate(180, expand=True)
                elif value == 6: img = img.rotate(-90, expand=True)
                elif value == 8: img = img.rotate(90, expand=True)
                break
    except Exception: pass
    return img
```

**Pitfall**: Files with NO EXIF (PNGs, HEIC conversions, hand-edited JPEGs) → auto-rotate does nothing. **Fallback**: ask user to manually rotate in Preview/Finder. Don't try OpenCV face-angle detection — too slow and unreliable for this.

### Cover-crop (smart_crop_to_fit)

```python
def smart_crop_to_fit(img, target_w, target_h):
    iw, ih = img.size
    target_ratio = target_w / target_h
    img_ratio = iw / ih
    if img_ratio > target_ratio:
        new_w = int(ih * target_ratio)
        left = (iw - new_w) // 2
        img = img.crop((left, 0, left + new_w, ih))
    else:
        new_h = int(iw / target_ratio)
        top = (ih - new_h) // 2
        img = img.crop((0, top, iw, top + new_h))
    return img.resize((target_w, target_h), Image.LANCZOS)
```

**Pitfall**: Cover-crop can chop off a face. For portrait photos, the crop is from top/bottom — if subject is at the top, they get cut. Warn the user that portrait photos are the riskiest.

### Oil-paint effect (cv2.stylization)

```python
def apply_oil_paint(img):
    arr = np.array(img)
    arr = cv2.bilateralFilter(arr, 5, 30, 30)
    arr = cv2.stylization(arr, sigma_s=30, sigma_r=0.45)  # KEY: 30, not 60
    arr = arr.astype(np.float32)
    arr[:,:,0] *= 1.03   # slight warm tint
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)
```

**Critical pitfall — sigma_s**:
- `sigma_s=60` → too aggressive, comic-book outlines + RGB noise (red/green pixels)
- `sigma_s=30` → sweet spot, looks like real oil paint
- `sigma_s=10` → barely visible

**Critical pitfall — pre-filtered photos**: Photos with cartoon/anime filter baked in (line outlines, cel shading) → don't apply oil-paint on top. It compounds and looks grotesque. Render those pages in "original" variant only.

### Chinese calendar grid

```python
def draw_calendar_grid(draw, year, month, x0, y0, grid_w, grid_h, font_path):
    cal = calendar.Calendar(firstweekday=6)  # Sun-start
    weeks = cal.monthdayscalendar(year, month)
    cell_w = grid_w / 7
    cell_h = grid_h / (len(weeks) + 1)
    
    f_wd = ImageFont.truetype(font_path, int(cell_h * 0.32))
    f_day = ImageFont.truetype(font_path, int(cell_h * 0.50))
    f_event = ImageFont.truetype(font_path, int(cell_h * 0.18))
    
    for i, wd in enumerate(["日","一","二","三","四","五","六"]):
        cx = x0 + i * cell_w + cell_w / 2
        color = (180, 60, 60) if i == 0 else (50, 50, 50)
        bbox = draw.textbbox((0,0), wd, font=f_wd)
        draw.text((cx - bbox[2]/2, y0 + cell_h/2 - bbox[3]/2 - bbox[1]), wd, font=f_wd, fill=color)
    
    grid_y0 = y0 + cell_h
    for r, week in enumerate(weeks):
        for c, day in enumerate(week):
            if day == 0: continue
            cx = x0 + c * cell_w + cell_w / 2
            cy = grid_y0 + r * cell_h + cell_h / 2
            color = (180, 60, 60) if c == 0 else (30, 30, 30)
            bbox = draw.textbbox((0,0), str(day), font=f_day)
            draw.text((cx - bbox[2]/2, cy - bbox[3]/2 - bbox[1] - cell_h*0.08), str(day), font=f_day, fill=color)
            holiday = HOLIDAYS_2027.get((month, day))
            if holiday:
                bbox = draw.textbbox((0,0), holiday, font=f_event)
                draw.text((cx - bbox[2]/2, cy + cell_h*0.13), holiday, font=f_event, fill=(140, 90, 60))
```

### PDF assembly (PIL only, no reportlab)

```python
from PIL import Image as PILImage
def make_pdf(prefix, out_name, dir_):
    images = [PILImage.open(f"{dir_}/{prefix}_{m:02d}.jpg").convert("RGB") for m in range(1, 13)]
    images[0].save(out_name, save_all=True, append_images=images[1:], resolution=300.0, quality=92)
```

Quality=92 keeps file size sane (~7-9 MB for A5 12 pages).

## Layout: Magazine Style

```
┌─────────────────────────────┐
│       [BIG PHOTO 58%]       │
├─────────────────────────────┤
│ 三月         2027           │   ← month big, year small
│ 日 一 二 三 四 五 六        │
│   calendar grid 42%         │
└─────────────────────────────┘
```

- Photo area: 58% of A5 height
- Title row: ~150px below photo
- Calendar grid: fills remaining space
- Outer border: 2px warm gray (180,170,155) at margin-40

## Pitfalls

1. **EXIF-less PNGs**: rotate by hand, re-upload. Don't try face detection.
2. **cv2.stylization sigma_s**: must be 30. 60 produces RGB glitch noise.
3. **Pre-filtered photos + oil-paint**: looks grotesque. Skip those pages in oil variant.
4. **Portrait photos in horizontal slot**: subject can get chopped. Warn user.
5. **Cover-crop on square photos**: no chop zone — upscale to fill, looks soft. OK for sentimental photos.
6. **Default PIL font rendering Chinese**: produces tofu boxes. MUST specify `.ttc` font path.
7. **PDF quality=95**: file balloons to 30+ MB for A5 photos. Use quality=92 for 7-9 MB.
8. **Forgetting which version the user asked for**: confirm variant count and filenames BEFORE rendering.

## Verification

After rendering:
1. **Visual spot-check 2-3 pages** with `vision_analyze`: pick 1 landscape, 1 portrait, 1 text-heavy grid.
2. **Check oil-paint for RGB noise** — zoom into high-detail area (foliage, fabric). Red/green pixel dots = sigma_s too high.
3. **PDF page count** = number of photos (12 for a 12-month calendar).
4. **File size**: A5 12-page at quality=92 → 5-10 MB per PDF. Larger means photos weren't downsampled.

## Output Convention

```
~/Desktop/calendar_<year>/
├── original_<01-12>.jpg
├── oil_<01-12>.jpg
├── <year>日曆_原相版.pdf
└── <year>日曆_油畫版.pdf
```

Send PDFs back to user with `MEDIA:` prefix on WeChat (per image-generation-workflow pitfall — bare paths silently fail).

## Future Variants

This pipeline extends to:
- **Polaroid wall** (grid of N photos, no calendar)
- **Photobook** (chapter pages, photo + caption)
- **Custom birthday card** (1 photo + Chinese calligraphy + cover-crop)
- **Anniversary poster** (12 photos → 1 large composite, no grid)

For polaroid/photobook, drop the calendar grid code and use a `multi_cell_grid(image_list, cols=4)` helper.

## References

- `references/session-20260919-calendar-pipeline.md` — full session record