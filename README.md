# DocsGen — PBI Documentation Skill

A Claude Code skill that turns Power BI project documentation into polished, client-ready Word (`.docx`) and PDF deliverables — with your branding, in your language.

## What it does

Takes the Markdown output from the `pbi:docs` skill and generates:
- Branded `.docx` with your logo, colors, and typography
- PDF via Playwright/Chromium
- English or French output per run
- Audience-appropriate depth (executive, IT, client)

## Install

**Mac / Linux / WSL:**
```bash
curl -sL https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.ps1 | iex
```

This installs the skill to `~/.claude/skills/pbi-docgen/`, registers the `/pbi-docgen` command in Claude Code, and installs all Python dependencies.

## Usage

1. Run `pbi:docs` on your Power BI project to generate the Markdown source docs
2. Place your logos in `docsgen-assets/logos/` (`client_logo.png`, `company_logo.png`)
3. Place your source `.md` file in `docsgen-assets/source/`
4. Type `/pbi-docgen` in Claude Code and follow the intake wizard

## Requirements

- Claude Code CLI
- Python 3.9+
- The install script handles all Python deps automatically

## Manual install (Python deps only)

```bash
pip install python-docx==1.2.0 Jinja2==3.1.6 playwright==1.58.0 markdown PyYAML Pillow lxml
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
| HTML → PDF | Playwright 1.58.0 (Chromium) |
| Templating | Jinja2 3.1.6 |
| Skill framework | Claude Code Skills |

## Related

- [PowerBI-Skill](https://github.com/d7rocket/PowerBI-Skill) — the `pbi:docs` skill that generates the source Markdown
