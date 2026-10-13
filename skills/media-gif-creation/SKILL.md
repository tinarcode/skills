---
name: media-gif-creation
description: "Convert images or videos to animated GIFs using ffmpeg. Covers Ken Burns zoom effect for photos, PIL-based frame extraction for videos, and Telegram delivery tips."
category: media
---

# Media GIF Creation

Create animated GIFs from static images (Ken Burns zoom effect) or videos (frame extraction). Both workflows use ffmpeg as the core engine.

## Section: Image to GIF (Ken Burns Zoom Effect)

### Trigger
User says: 「將呢個變成GIF」、「整GIF」、「做GIF」(for photos)

### Recommended: Ken Burns Zoom Effect
```bash
ffmpeg -y -loop 1 -i INPUT.jpg \
  -vf "scale=W:-1:flags=lanczos,zoompan=z='min(zoom+0.003,1.2)':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=N:s=WxH:fps=N" \
  -t SECONDS -loop 0 OUTPUT.gif
```

**Example (960px wide, 5 seconds, 10fps):**
```bash
ffmpeg -y -loop 1 -i INPUT.jpg \
  -vf "scale=960:-1:flags=lanczos,zoompan=z='min(zoom+0.003,1.2)':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=50:s=960x1280:fps=10" \
  -t 5 -loop 0 /Users/user/Desktop/output.gif
```

### Parameter Reference
| Parameter | Description |
|-----------|-------------|
| `scale=W:-1:flags=lanczos` | Width W, auto height, Lanczos quality |
| `zoompan=z='min(zoom+0.003,1.2)'` | Slow zoom in (1.0→1.2), 0.003 controls speed |
| `x=iw/2-(iw/zoom/2)` | Center horizontally during zoom |
| `y=ih/2-(ih/zoom/2)` | Center vertically during zoom |
| `d=N` | Total frames = fps × seconds |
| `s=WxH` | Output resolution |
| `fps=N` | Frames per second |
| `-t SECONDS` | Total GIF duration |

### Simple Version (No Animation)
```bash
ffmpeg -y -loop 1 -i INPUT.jpg -vf "scale=960:-1:flags=lanczos" -t 5 -loop 0 OUTPUT.gif
```

### Common Issues
| Problem | Solution |
|---------|----------|
| `zoompan` error `-22 invalid argument` | Ensure `d=N` and `s=WxH` are separate: `:d=N:s=WxH` |
| fade causes all-black output | fade out `st` must be `total_seconds - fade_duration`, e.g., 3s GIF fade out 1s → `fade=t=out:st=2:d=1` |
| palettegen timeout | Don't force palettegen, output directly is more stable |
| GIF too large (10MB+) | Lower fps (10), smaller scale (720), shorter duration (3-5s) |

---

## Section: Video to GIF (PIL Frame Extraction)

### Trigger
User says: 「整GIF」、「做GIF」(for video) / video-to-GIF

### Recommended: PIL Method (for Telegram)
Telegram GIFs don't animate in chat — they only play when opened directly. For guaranteed animation, send MP4 instead.

#### Step 1: Extract Frames
```python
import subprocess, os
temp_dir = '/tmp/gif_frames'
os.makedirs(temp_dir, exist_ok=True)

subprocess.run([
    'ffmpeg', '-y', '-i', 'INPUT.mov',
    '-vf', 'scale=480:-1:flags=lanczos,fps=10',
    '-q:v', '3',
    f'{temp_dir}/frame_%03d.jpg'
])
```

#### Step 2: Generate GIF with PIL
```python
from PIL import Image
import os

frames_dir = sorted([f for f in os.listdir(temp_dir) if f.endswith('.jpg')])
frames = []
for fname in frames_dir:
    img = Image.open(f'{temp_dir}/{fname}')
    img = img.resize((240, 426), Image.LANCZOS)
    img = img.convert('P', palette=Image.ADAPTIVE, colors=128)  # Reduce colors
    frames.append(img.copy())
    img.close()

frames[0].save(
    '/Users/user/Desktop/output.gif',
    save_all=True,
    append_images=frames[1:],
    duration=100,  # 10fps = 100ms/frame
    loop=0,
    optimize=True
)
```

#### Step 3: Compress for Delivery
```bash
sips -s format jpeg -s formatOptions 60 /tmp/final_meme.png --out /tmp/final_meme.jpg
```

### Quick Command (ffmpeg Direct Output)
```bash
ffmpeg -y -i INPUT.mov \
  -vf "scale=480:-1:flags=lanczos,fps=10" \
  -t 7 -loop 0 OUTPUT.gif
```
**Note**: Direct ffmpeg output produces large files (10MB+). PIL method recommended for compression.

### Recommended Settings
| Setting | Recommended |
|---------|-------------|
| scale width | 320-480px |
| fps | 10-15 |
| duration | 3-7 seconds |
| colors | 64-128 |
| target size | <5MB |

### Telegram GIF Limitation (Session Discovery)
Telegram does NOT animate GIFs inline in chat — they appear static until opened. For guaranteed animation, send MP4 format which plays inline in Telegram.

### Output Location
`/Users/user/Desktop/output.gif` or `output_anim.gif`
