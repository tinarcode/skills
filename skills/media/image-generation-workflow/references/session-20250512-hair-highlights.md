# Session Learning: 2025-05-12 — Hair Highlights & Pet Preferences

## What Happened
User sent a couple photo → asked to generate anime version with pets → I generated but forgot to ask for model selection → user called me out ("你應該要問我用邊個模型") → I found the skill which already had all the rules.

## Key Corrections (User-Style Preferences)

### Hair Highlights
- User said: "女仔個伯母要有啲金色嘅挑染"
- User clarified: "淨係發尾要挑染" (highlights ONLY on hair tips/ends, not throughout)
- Prompt adjustment needed: `golden blonde highlights only on the hair tips/ends (only the bottom tips of her hair are dyed golden blonde)`

### Cat Preference
- User said: "隻貓都係第一版好啲"
- This means: when iterating, the user may prefer elements from earlier versions
- Always note what version elements the user liked when iterating

## Workflow Reminder
The skill's HARD STOP rule (asking for model before generation) was already in the SKILL.md. The failure was in APPLYING it, not knowing it.
- Future agents: when user says "generate image", immediately present 6 model options BEFORE any code
- If you forget and generate without asking, apologize and present options retroactively

## This Session's Generation Details
- Model used: qwen-image-2.0-pro (option 2)
- Couple description: boy in black/white striped shirt + black vest, round silver glasses; girl in light gray hoodie, short black hair
- Pets: Lynx Point Siamese cat (cream body, dark gray tabby points, blue eyes) + tiny white dwarf hamster (pure white, pink ears, black eyes)
- Style: kawaii anime, chibi, soft pastel colors
- Output path: ~/Desktop/hermes production/couple_v3_small.jpg
