# Hermes Agent Skills

A personal library of 159 agent skills for [Hermes](https://github.com/NousResearch/hermes) — covering software development workflow, ML ops, media generation, document processing, research, trading tools, and macOS automation.

## What's here

```
skills/
├── <name>/                     top-level skills
├── design/                     UI/UX design skills
├── productivity/               docx, pdf, xlsx, pptx, OCR, email
├── software-development/       github, plans, git workflow
├── mlops/                      training, inference, evaluation
├── media/                      image/video/audio generation pipelines
├── creative/                   generative art, memes, wallpapers
├── research/                   search, monitoring, markets
└── trading/                    stock + options analysis
```

Every skill is a directory containing a `SKILL.md` with YAML frontmatter
(`name`, `description`) plus optional `scripts/`, `references/`, and `templates/`.

## Usage

Skills are auto-discovered by Hermes from `~/.hermes/skills/`. To use this repo:

```bash
git clone https://github.com/tinarcode/skills.git
cp -R skills/skills/. ~/.hermes/skills/
```

Some skills require API keys — set them in `~/.hermes/.env` (see the `Setup`
section of each `SKILL.md`).

## A note on this mirror

This is the **public, sanitized** mirror. Personal and employer-identifying content
has been redacted:

- Real names, honorifics, and user profile details → `[user]`
- Employer, vendor, and signatory names → `[vendor]` / `[signatory]` / `ORG`
- Personal side-project names and regional organization names → generic descriptions
- A skill that was entirely employer-procurement-specific was removed

Historical snapshots (`.archive/`, `.curator_backups/`) and curator bookkeeping
are **not** included here — they live in a separate private backup.

No API keys or tokens are present; token-like strings are documentation
placeholders.

## License

Skills are a mix of original work and third-party sources (Anthropic's skill
collection, addyosmani, HuggingFace, etc.). Per-skill `LICENSE` files apply where
present; check each `SKILL.md` frontmatter for attribution.
