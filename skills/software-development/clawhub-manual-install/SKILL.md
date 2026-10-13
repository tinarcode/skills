---
name: clawhub-manual-install
description: Manually install skills from ClawHub when the web download fails. Use browser to read skill files, then skill_manage to create them locally.
version: 1.0.0
---

# ClawHub Manual Install

When `curl` or browser download fails for a ClawHub skill, manually extract and install.

## When to Use

- Browser detects "Download is starting" but file doesn't appear in expected location
- `execute_code` can't write files (FileNotFoundError)
- Skill download URL returns a file instead of rendering in browser

## Steps

### 1. Navigate to ClawHub skill page
```
https://clawhub.ai/{author}/{slug}
```

### 2. Identify all files
Look for "X total" in Files section and tab through to see all files (SKILL.md + supporting files in references/, scripts/, etc.)

### 3. Read SKILL.md first
Use browser_console to extract main content:
```js
const main = document.querySelector('main');
main.innerText.substring(0, 20000);
```

### 4. Read each supporting file
Click file buttons in the Files section, then extract content:
```js
const main = document.querySelector('main');
const content = main.innerText;
const idx = content.indexOf('FILENAME.md');
content.substring(idx, idx + LENGTH);
```

### 5. Create skill via skill_manage

**SKILL.md** (create action):
```
skill_manage(action='create', name='{slug}', content='...', category='...')
```

**Supporting files** (write_file action):
```
skill_manage(action='write_file', name='{slug}', file_path='{path}', file_content='...')
```

Valid file paths: `references/`, `scripts/`, `templates/`, `assets/`

### 6. Verify installation
```
skill_view(name='{slug}')
```

## Files needed per skill type

| Skill type | Files needed |
|------------|--------------|
| Basic | SKILL.md only |
| With scripts | SKILL.md + scripts/*.py |
| With templates | SKILL.md + references/*.md |

## Common Issues

- **execute_code fails with FileNotFoundError**: Use delegate_task with terminal toolset, or ask user to run command
- **Browser download triggers but file missing**: Read content via JS and manually create files
- **File path not allowed**: Must be under references/, scripts/, templates/, or assets/

## Install LobeHub/Community Skills via CLI

The Hermes Skills Hub website install button often fails for LobeHub/Community skills (button click doesn't trigger download). **Use the CLI instead:**

```bash
# Search for a skill
hermes skills search <skill-name>

# Install it (add --yes for non-interactive)
hermes skills install lobehub/<skill-name> --yes
```

Example — installing english-news-translator:
```bash
hermes skills install lobehub/english-news-translator --yes
# Output: Installed: english-news-translator, Files: SKILL.md
```

After install, verify with:
```bash
skill_view(name='<skill-name>')
```

## Example: openclaw-tavily-search

1. Read SKILL.md content from page
2. Create skill with skill_manage action='create'
3. Read scripts/tavily_search.py via file button click
4. Write to scripts/tavily_search.py
5. Verify with skill_view
