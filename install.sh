#!/usr/bin/env bash
set -e

REPO_RAW="https://raw.githubusercontent.com/d7rocket/DocsGen/master"

# Parse --project flag
PROJECT_MODE=false
for arg in "$@"; do
  [[ "$arg" == "--project" ]] && PROJECT_MODE=true
done

if $PROJECT_MODE; then
  SKILL_DIR=".claude/skills/pbi-docgen"
  CMD_DIR=".claude/commands"
  echo "Installing pbi-docgen skill (project-level)..."
else
  SKILL_DIR="$HOME/.claude/skills/pbi-docgen"
  CMD_DIR="$HOME/.claude/commands"
  echo "Installing pbi-docgen skill (user-level)..."
fi

# Helper: download a skill file from GitHub
download() {
  curl -sL "$REPO_RAW/.claude/skills/pbi-docgen/$1" -o "$SKILL_DIR/$1"
}

# Create directory structure
echo "Creating directories..."
mkdir -p "$SKILL_DIR/scripts"
mkdir -p "$SKILL_DIR/templates/prompts"
mkdir -p "$SKILL_DIR/references"
mkdir -p "$CMD_DIR"

# Download skill files
echo "Downloading skill files..."
download "SKILL.md"
download "scripts/__init__.py"
download "scripts/content_generator.py"
download "scripts/docx_builder.py"
download "scripts/generate.py"
download "scripts/md_parser.py"
download "scripts/pdf_builder.py"
download "scripts/utils.py"
download "scripts/md_renderer.py"
download "templates/document.html.j2"
download "templates/prompts/fowler_rules.j2"
download "templates/prompts/grevisse_rules.j2"
download "templates/prompts/section_dataflows.j2"
download "templates/prompts/section_dataflows_fr.j2"
download "templates/prompts/section_datamodel.j2"
download "templates/prompts/section_datamodel_fr.j2"
download "templates/prompts/section_maintenance.j2"
download "templates/prompts/section_maintenance_fr.j2"
download "templates/prompts/section_mquery.j2"
download "templates/prompts/section_mquery_fr.j2"
download "templates/prompts/section_overview.j2"
download "templates/prompts/section_overview_fr.j2"
download "templates/prompts/section_sources.j2"
download "templates/prompts/section_sources_fr.j2"
download "references/fr_glossary.yaml"
download "references/section_heading_map.yaml"

# Download command registration
echo "Installing command registration..."
curl -sL "$REPO_RAW/.claude/commands/pbi-docgen.md" -o "$CMD_DIR/pbi-docgen.md"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install python-docx==1.2.0 Jinja2==3.1.6 playwright==1.58.0 markdown-it-py PyYAML Pillow lxml

# Install Playwright Chromium browser
echo "Installing Playwright Chromium..."
python -m playwright install chromium

# Success banner
echo ""
echo -e "\033[32m========================================\033[0m"
echo -e "\033[32m pbi-docgen skill installed successfully!\033[0m"
echo -e "\033[32m========================================\033[0m"
echo ""
if $PROJECT_MODE; then
  echo "Installed to: $SKILL_DIR"
  echo "Scope: this project only"
else
  echo "Installed to: $SKILL_DIR"
  echo "Scope: all Claude Code sessions"
fi
echo ""
echo "Usage: Type /pbi-docgen in Claude Code"
echo ""
echo "One-liners:"
echo "  User:    curl -sL https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.sh | bash"
echo "  Project: curl -sL https://raw.githubusercontent.com/d7rocket/DocsGen/master/install.sh | bash -s -- --project"
