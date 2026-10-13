# Ghibli Style Generation — Session 2025-05-14

## Workflow

1. User sent reference image (anime-style couple + Lynx Point Siamese + white hamster)
2. User said "新成吉卜力風格" → **generation request** (NOT analysis — see `session-20260514-style-transfer-intent.md`)
3. Asked model → user chose #3 `wan2.7-image`
4. Generated with detailed scene description + Ghibli style keywords
5. Downloaded immediately with `urllib.request.urlretrieve()` (worked fine on fresh presigned URLs)
6. Compressed with `sips`, sent via WeChat with `MEDIA:` prefix

## Full Iteration History (V2 → V3 → V4)

### V1 → V2: 3 corrections in single message
User said: "女仔要矮啲 去到男仔膊頭以下 倉鼠係純白色 隻貓塊面冇咁黑"

| Correction | Prompt addition |
|---|---|
| Girl shorter | `Height difference: the girl is shorter, her head reaches below the guy's shoulder` |
| Pure white hamster | `pure white hamster (completely white, no brown spots)` |
| Lighter cat face | `very light beige face mask and ears and paws (not dark, just subtle shading)` |

### V2 → V3: Single correction + approval signal
User said: "女仔要再矮啲，**其他都好好**"

- **Signal:** "其他都好好" = approval of everything EXCEPT this one thing
- Keep all previous corrections unchanged, only amplify the height difference
- Prompt: `Significant height difference: the girl is much shorter, her head barely reaches the guy's shoulder level`
- Do NOT re-ask model selection on iterative refinements (reuse previously chosen model)

### V3 → V4: Two related corrections
User said: "再矮啲同埋大家黐埋一齊嘅"

- **Signal:** "再矮啲" (even shorter) — same axis, pushed further
- **Signal:** "黐埋一齊" (closer together) — new but related axis
- Prompt: `Very significant height difference: the girl is very short, her head only reaches the guy's upper arm/shoulder pit level. The couple standing very close together, tightly snuggling, their bodies touching closely`

## Prompt Adjustment Patterns

### Height/Spatial Progressions
```
V2: "the girl is shorter, her head reaches below the guy's shoulder"
V3: "the girl is much shorter, her head barely reaches the guy's shoulder level"
V4: "the girl is very short, her head only reaches the guy's upper arm/shoulder pit level"
```
Pattern: escalate adverbs (shorter → much shorter → very short) + refine reference point (below shoulder → barely shoulder level → upper arm level)

### Closeness Progressions
```
V2: (no explicit closeness mention)
V4: "very close together, tightly snuggling, their bodies touching closely"
```

## Key Takeaway

When user gives corrections about spatial relationships (height, position) or colors (pet fur shades, facial features), include explicit comparative descriptors in the prompt:

- Height: use specific reference points ("below shoulder", "chin height", "upper arm level")
- Colors: set expectations explicitly ("not dark, just subtle shading", "completely white, no spots")
- Avoid relative terms like "lighter" or "shorter" alone — anchor to the other character/object
- On iterative refinements: amplify the same axis by escalating adverbs and refining reference points
- "其他都好好" means all previous corrections are correct — only push the stated axis further
