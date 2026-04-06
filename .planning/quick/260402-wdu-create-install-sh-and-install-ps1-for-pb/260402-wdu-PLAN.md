---
phase: quick
plan: 260402-wdu
type: execute
wave: 1
depends_on: []
files_modified:
  - install.sh
  - install.ps1
  - .claude/commands/pbi-docgen.md
autonomous: true
requirements: []
must_haves:
  truths:
    - "curl -sL .../install.sh | bash installs all skill files to ~/.claude/skills/pbi-docgen/"
    - "irm .../install.ps1 | iex installs all skill files to ~/.claude/skills/pbi-docgen/"
    - "Both scripts create ~/.claude/commands/pbi-docgen.md command registration"
    - "Both scripts install Python dependencies and Playwright chromium"
    - "Both scripts print success message on completion"
  artifacts:
    - path: "install.sh"
      provides: "Bash installer for curl one-liner"
    - path: "install.ps1"
      provides: "PowerShell installer for irm one-liner"
    - path: ".claude/commands/pbi-docgen.md"
      provides: "Command registration file for /pbi-docgen"
  key_links: []
---

<objective>
Create install.sh (bash) and install.ps1 (PowerShell) installer scripts for the pbi-docgen skill, plus the command registration file.

Purpose: Enable one-liner installation of the pbi-docgen skill via curl|bash or irm|iex.
Output: Two installer scripts at repo root + command registration file.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create command registration file and install.sh</name>
  <files>
    .claude/commands/pbi-docgen.md
    install.sh
  </files>
  <action>
**Step 1 — Command registration file (.claude/commands/pbi-docgen.md):**

Create a markdown file that Claude Code will use when the user types `/pbi-docgen`. It should instruct Claude to load and follow the skill at `~/.claude/skills/pbi-docgen/SKILL.md`. Keep it simple — a short description line and a reference to the SKILL.md path. Example content:

```
---
description: Generate polished Word/PDF documentation from PBI analysis output
---

Follow the skill instructions in ~/.claude/skills/pbi-docgen/SKILL.md
```

**Step 2 — install.sh (bash installer):**

Create `install.sh` at repo root. The script must:

1. Set `REPO_RAW="https://raw.githubusercontent.com/d7rocket/DocsGen/master"` as base URL.
2. Set `SKILL_DIR="$HOME/.claude/skills/pbi-docgen"` and `CMD_DIR="$HOME/.claude/commands"`.
3. Create directory structure:
   - `$SKILL_DIR/scripts`
   - `$SKILL_DIR/templates/prompts`
   - `$SKILL_DIR/references`
   - `$CMD_DIR`
4. Download each file using `curl -sL` from raw GitHub URLs to the correct local path. The complete file list:
   - `SKILL.md`
   - `scripts/__init__.py`
   - `scripts/content_generator.py`
   - `scripts/docx_builder.py`
   - `scripts/generate.py`
   - `scripts/pdf_builder.py`
   - `templates/document.html.j2`
   - `templates/prompts/fowler_rules.j2`
   - `templates/prompts/grevisse_rules.j2`
   - `templates/prompts/section_dataflows.j2`
   - `templates/prompts/section_dataflows_fr.j2`
   - `templates/prompts/section_datamodel.j2`
   - `templates/prompts/section_datamodel_fr.j2`
   - `templates/prompts/section_maintenance.j2`
   - `templates/prompts/section_maintenance_fr.j2`
   - `templates/prompts/section_mquery.j2`
   - `templates/prompts/section_mquery_fr.j2`
   - `templates/prompts/section_overview.j2`
   - `templates/prompts/section_overview_fr.j2`
   - `templates/prompts/section_sources.j2`
   - `templates/prompts/section_sources_fr.j2`
   - `references/fr_glossary.yaml`
   - `references/section_heading_map.yaml`
   All from `$REPO_RAW/.claude/skills/pbi-docgen/{file}`.
5. Download command registration: `curl -sL "$REPO_RAW/.claude/commands/pbi-docgen.md" -o "$CMD_DIR/pbi-docgen.md"`
6. Install Python deps: `pip install python-docx==1.2.0 Jinja2==3.1.6 playwright==1.58.0 markdown PyYAML Pillow lxml`
7. Install Playwright chromium: `playwright install chromium`
8. Print success banner with green text:
   ```
   pbi-docgen skill installed successfully!
   
   Usage: Type /pbi-docgen in Claude Code
   
   One-liner install:
     curl -sL https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.sh | bash
   ```

Use `set -e` at top for fail-fast. Use a helper function for downloads to reduce repetition (e.g., `download() { curl -sL "$REPO_RAW/.claude/skills/pbi-docgen/$1" -o "$SKILL_DIR/$1"; }`). Add echo statements showing progress (e.g., "Downloading skill files...", "Installing Python dependencies...").
  </action>
  <verify>
    <automated>bash -n "C:/Users/DeveshD/Documents/Claude Projects/DocsGen/install.sh" && echo "install.sh syntax OK" && test -f "C:/Users/DeveshD/Documents/Claude Projects/DocsGen/.claude/commands/pbi-docgen.md" && echo "command file exists"</automated>
  </verify>
  <done>install.sh passes bash syntax check, .claude/commands/pbi-docgen.md exists with skill reference</done>
</task>

<task type="auto">
  <name>Task 2: Create install.ps1 (PowerShell installer)</name>
  <files>install.ps1</files>
  <action>
Create `install.ps1` at repo root. Mirror the exact same logic as install.sh but in PowerShell idioms:

1. Set variables: `$RepoRaw`, `$SkillDir` (using `$env:USERPROFILE\.claude\skills\pbi-docgen`), `$CmdDir`.
2. Create directories using `New-Item -ItemType Directory -Force`.
3. Download files using `Invoke-WebRequest -Uri ... -OutFile ...` (or the shorter `irm` alias with output redirect). Use the same complete file list as install.sh (all 23 skill files + command registration).
4. Use a helper function: `function Download-File($RelPath) { Invoke-WebRequest -Uri "$RepoRaw/.claude/skills/pbi-docgen/$RelPath" -OutFile "$SkillDir\$RelPath" }`
5. Install Python deps: `pip install python-docx==1.2.0 Jinja2==3.1.6 playwright==1.58.0 markdown PyYAML Pillow lxml`
6. Install Playwright chromium: `playwright install chromium`
7. Print success banner using `Write-Host` with `-ForegroundColor Green`.
8. Include the one-liner reminder: `irm https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.ps1 | iex`

Use `$ErrorActionPreference = 'Stop'` at top for fail-fast. Add Write-Host progress messages.
  </action>
  <verify>
    <automated>powershell -NoProfile -Command "Get-Content 'C:/Users/DeveshD/Documents/Claude Projects/DocsGen/install.ps1' | Out-Null; Write-Host 'install.ps1 readable'" 2>/dev/null; echo "install.ps1 exists and is valid"</automated>
  </verify>
  <done>install.ps1 exists with matching logic to install.sh, uses PowerShell idioms (Invoke-WebRequest, New-Item, Write-Host)</done>
</task>

</tasks>

<verification>
- `bash -n install.sh` passes (no syntax errors)
- `.claude/commands/pbi-docgen.md` exists and references SKILL.md
- `install.ps1` exists and contains matching file download list
- Both scripts reference all 23 skill files
- Both scripts include pip install and playwright install chromium steps
</verification>

<success_criteria>
Three files created at correct paths: install.sh, install.ps1, .claude/commands/pbi-docgen.md. Both installer scripts download all skill files, install deps, register the command, and print success messages.
</success_criteria>

<output>
After completion, create `.planning/quick/260402-wdu-create-install-sh-and-install-ps1-for-pb/260402-wdu-SUMMARY.md`
</output>
