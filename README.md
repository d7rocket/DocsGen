# DocsGen — PBI Documentation Skill

A Claude Code skill that turns Power BI project documentation into polished, client-ready Word (`.docx`) and PDF deliverables — with your branding, in your language.

## What it does

Takes the Markdown output from the `pbi:docs` skill and generates:
- Branded `.docx` with your logo, colors, and typography
- Unified Markdown parser (markdown-it-py) for consistent formatting across DOCX and PDF
- DigitalOcean-inspired code block styling (left-accent border pattern)
- Professional PDF output via Playwright/Chromium
- English or French output per run
- Audience-appropriate depth (executive, IT, client)

## What's New in v1.0

- **Unified parser:** markdown-it-py replaces hand-rolled `TABLE:`/`CODE_BLOCK:` markers for reliable Markdown rendering in both DOCX and PDF
- **DigitalOcean-style code blocks:** left-accent border pattern in both Word and PDF output
- **Playwright fix:** uses `wait_until="domcontentloaded"` to prevent hangs on PDF generation
- **Standard Markdown prompts:** all 12 section templates now emit standard Markdown (headings, tables, fenced code) instead of custom markers
- **Explicit heading sizes:** h1=20pt, h2=14pt, h3=12pt, h4=11pt for consistent document hierarchy

## Install

### User install (recommended)

Available in all your Claude Code sessions.

**Mac / Linux / WSL:**
```bash
curl -sL https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.ps1 | iex
```

Installs to `~/.claude/skills/pbi-docgen/` and `~/.claude/commands/`.

### Project install

Available only within the current project directory — useful for team repos where you want to commit the skill alongside the project.

**Mac / Linux / WSL:**
```bash
curl -sL https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.sh | bash -s -- --project
```

**Windows (PowerShell):**
```powershell
& ([scriptblock]::Create((irm 'https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.ps1'))) -Project
```

Installs to `.claude/skills/pbi-docgen/` and `.claude/commands/` in the current directory.

Both modes install all Python dependencies and register the `/pbi-docgen` command in Claude Code.

## Usage

1. Run `pbi:docs` on your Power BI project to generate the Markdown source docs
2. Place your logos in `docsgen-assets/logos/` (`client_logo.png`, `company_logo.png`)
3. Place your source `.md` file in `docsgen-assets/source/`
4. Type `/pbi-docgen` in Claude Code and follow the intake wizard

## Requirements

- Claude Code CLI
- Python 3.9+
- Node.js (required by Playwright for PDF generation)
- The install script handles all Python deps automatically

## Manual install (Python deps only)

```bash
pip install python-docx==1.2.0 Jinja2==3.1.6 playwright==1.58.0 markdown-it-py PyYAML Pillow lxml
playwright install chromium
```

## Asset folder structure

```
docsgen-assets/
  logos/
    client_logo.png     ← client's logo (cover page)
    company_logo.png    ← your company logo (header)
  source/
    your-pbi-docs.md    ← output from pbi:docs
```

## Stack

| Component | Technology |
|-----------|------------|
| DOCX generation | python-docx 1.2.0 |
| HTML to PDF | Playwright 1.58.0 (Chromium) |
| Markdown parsing | markdown-it-py 4.0.0 |
| Templating | Jinja2 3.1.6 |
| Skill framework | Claude Code Skills |

## Related

- [PowerBI-Skill](https://github.com/d7rocket/PowerBI-Skill) — the `pbi:docs` skill that generates the source Markdown
