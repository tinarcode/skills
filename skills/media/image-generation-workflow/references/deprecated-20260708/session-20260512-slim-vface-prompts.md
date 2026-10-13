# 2026-05-12 Session: Slim Body / V-Face / Hair Highlights Prompts

## SESSION CONTEXT
user wanted a kawaii anime illustration based on a couple photo.
Iteration went: slim → slimmer → V-face → center part → tips-only highlights

## VERIFIED PROMPT MODIFIERS (qwen-image-2.0-pro)

### Body/Face — Slim V-face (works well)
```
both characters are very slim and thin with V-shaped faces (sharp chin and jawline)
very slim build with V-face
very slim build with V-shaped face and sharp chin
```

### Hair — Center part with tips highlights (works well)
```
short black hair with center part/middle part hairstyle (hair parts in the middle, swept to both sides)
golden blonde highlights only on the hair tips/ends
```

### Hamster size (small scale)
```
tiny small white dwarf hamster — pure white fur, pink ears, round black eyes, no markings, very small in size
```

## MODEL SELECTION PATTERN
- First gen: askeduser, he chose option 2 (qwen-image-2.0-pro)
- All subsequent iterations: did NOT re-ask, reused qwen-image-2.0-pro
- user did not object to not being asked again after the first choice

## IMAGE FORMATTING FOR WECHAT
```bash
# Generate → curl download → sips compress
curl -sL -o <path> <url> --max-time 120
sips -s format jpeg -s formatOptions 85 <input> --out <output>
sips -z 600 600 <input> --out <small>
# Send: send_message with MEDIA: prefix
```

## KEY FILE PATHS (updated format)
~/Desktop/hermes production/couple_v5_small.jpg
