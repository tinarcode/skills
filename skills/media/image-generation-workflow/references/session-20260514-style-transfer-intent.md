# Style Transfer Intent — Session Learning (2025-05-14)

## The Mistake
User sent an image (anime-style couple with tabby Siamese cat and white hamster) and said "新成吉卜力風格". I described the image in detail instead of generating a Ghibli-style version.

User then corrected: "我係要你生成一張吉卜力風格嘅版本"

## The Lesson
**When user = reference image + style keyword = generation request, not analysis request.**

Signal keywords that trigger generation intent:
- "X風格嘅版本" / "X風格的版本" (style's version)
- "新X風格" (new X style)
- "幫我轉做X" (help me convert to X)
- "生成X風格" (generate X style)

## Correct Workflow
1. Acknowledge: "收到，幫你生成X風格版本"
2. Ask model (per HARD STOP rule): "請問想用邊個模型？"
3. Analyze image content briefly (using vision tool)
4. Describe the scene in text for the prompt
5. Generate with the target style keywords appended

## Example
User sends image of a couple with pets + "新成吉卜力風格"
→ "收到user！等我幫你生成吉卜力風格版本！請問想用邊個模型？（6個選項）"

Then prompt template:
```
[detailed scene description from image], Studio Ghibli style, Hayao Miyazaki anime art style, hand-drawn watercolor aesthetic, warm nostalgic colors, soft lighting, [pets described], [people described]
```
