param([switch]$Project)

$ErrorActionPreference = 'Stop'

$RepoRaw = "https://raw.githubusercontent.com/d7rocket/DocsGen/master"

if ($Project) {
    $SkillDir = ".\.claude\skills\pbi-docgen"
    $CmdDir = ".\.claude\commands"
    Write-Host "Installing pbi-docgen skill (project-level)..."
} else {
    $SkillDir = "$env:USERPROFILE\.claude\skills\pbi-docgen"
    $CmdDir = "$env:USERPROFILE\.claude\commands"
    Write-Host "Installing pbi-docgen skill (user-level)..."
}

# Helper: download a skill file from GitHub
function Download-File($RelPath) {
    $uri = "$RepoRaw/.claude/skills/pbi-docgen/$RelPath"
    $outFile = Join-Path $SkillDir $RelPath
    Invoke-WebRequest -Uri $uri -OutFile $outFile -UseBasicParsing
}

# Create directory structure
Write-Host "Creating directories..."
New-Item -ItemType Directory -Force -Path (Join-Path $SkillDir "scripts") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $SkillDir "templates\prompts") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $SkillDir "references") | Out-Null
New-Item -ItemType Directory -Force -Path $CmdDir | Out-Null

# Download skill files
Write-Host "Downloading skill files..."
Download-File "SKILL.md"
Download-File "scripts\__init__.py"
Download-File "scripts\content_generator.py"
Download-File "scripts\docx_builder.py"
Download-File "scripts\generate.py"
Download-File "scripts\md_parser.py"
Download-File "scripts\pdf_builder.py"
Download-File "scripts\utils.py"
Download-File "templates\document.html.j2"
Download-File "templates\prompts\fowler_rules.j2"
Download-File "templates\prompts\grevisse_rules.j2"
Download-File "templates\prompts\section_dataflows.j2"
Download-File "templates\prompts\section_dataflows_fr.j2"
Download-File "templates\prompts\section_datamodel.j2"
Download-File "templates\prompts\section_datamodel_fr.j2"
Download-File "templates\prompts\section_maintenance.j2"
Download-File "templates\prompts\section_maintenance_fr.j2"
Download-File "templates\prompts\section_mquery.j2"
Download-File "templates\prompts\section_mquery_fr.j2"
Download-File "templates\prompts\section_overview.j2"
Download-File "templates\prompts\section_overview_fr.j2"
Download-File "templates\prompts\section_sources.j2"
Download-File "templates\prompts\section_sources_fr.j2"
Download-File "references\fr_glossary.yaml"
Download-File "references\section_heading_map.yaml"

# Download command registration
Write-Host "Installing command registration..."
Invoke-WebRequest -Uri "$RepoRaw/.claude/commands/pbi-docgen.md" -OutFile (Join-Path $CmdDir "pbi-docgen.md") -UseBasicParsing

# Install Python dependencies
Write-Host "Installing Python dependencies..."
pip install python-docx==1.2.0 Jinja2==3.1.6 playwright==1.58.0 markdown PyYAML Pillow lxml

# Install Playwright Chromium browser
Write-Host "Installing Playwright Chromium..."
playwright install chromium

# Success banner
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " pbi-docgen skill installed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
if ($Project) {
    Write-Host "Installed to: $SkillDir"
    Write-Host "Scope: this project only"
} else {
    Write-Host "Installed to: $SkillDir"
    Write-Host "Scope: all Claude Code sessions"
}
Write-Host ""
Write-Host "Usage: Type /pbi-docgen in Claude Code"
Write-Host ""
Write-Host "One-liners:"
Write-Host "  User:    irm https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.ps1 | iex"
Write-Host "  Project: & ([scriptblock]::Create((irm 'https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.ps1'))) -Project"
