<!-- GSD:project-start source:PROJECT.md -->
## Project

**DocsGen — PBI Documentation Skill**

A Claude Code skill that takes Power BI project documentation (Markdown files from the existing `pbi:docs` skill) plus branding assets and generates polished formal deliverables — `.docx` and HTML→PDF — for internal teams, client stakeholders, and IT. The skill handles everything from intake (logos, colors, language) to structured multi-section output, eliminating the gap between raw PBI analysis and presentation-ready documentation.

**Core Value:** Turn structured PBI Markdown docs into client-ready Word/PDF deliverables with correct branding, language, and audience-appropriate depth — in one skill invocation.

### Constraints

- **Dependency:** Requires existing PBI Markdown docs as input — skill is not standalone without them
- **Python:** Output generation requires Python (python-docx) and Node (Playwright) or equivalent — skill must check for these and surface clear errors
- **Asset folder:** User must populate `docsgen-assets/` before generation; skill guides them through what's needed
- **Language:** Per-run language selection — EN or FR, not both simultaneously
- **Quality bar:** Output must look clean and professional — suitable for direct client delivery without post-processing in Word. Typography, spacing, color application, and layout must be intentional and polished.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Document Generation (DOCX)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| python-docx | 1.2.0 | Core .docx creation and manipulation | Industry standard for programmatic Word file creation in Python. Supports styles, colors (RGBColor), headers/footers, images, tables. Released June 2025, actively maintained. Requires Python >=3.9. |
| Jinja2 | 3.1.6 | Template rendering for document content | Powers dynamic content insertion. Used standalone (not via docxtpl) because we need fine-grained control over python-docx formatting that template-based approaches obscure. |
### HTML to PDF Conversion
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Playwright (Python) | 1.58.0 | Headless Chromium for HTML-to-PDF | Fastest option: 3ms warm / 42ms cold for simple docs, 13ms warm / 119ms cold for complex docs. Full modern CSS support (Grid, Flexbox, custom properties). JavaScript execution if needed. Microsoft-backed, actively maintained. Python >=3.9. |
| Criterion | Playwright | WeasyPrint (68.1) | wkhtmltopdf |
|-----------|------------|-------------------|-------------|
| Speed (warm) | 3ms simple, 13ms complex | 227ms simple, 629ms complex | N/A |
| CSS support | Full modern CSS (Grid, Flexbox, etc.) | CSS Paged Media L3 only, no Grid complex layouts | Ancient WebKit, frozen CSS |
| JS execution | Yes (Chromium engine) | No | Limited |
| Maintenance | Active (Microsoft) | Active (Kozea) | Abandoned / EOL |
| Output size | 16-125 KB | 8-21 KB (more compact) | Varies |
| Warm mode | Yes (browser reuse, 14x speedup) | No | No |
### Claude Code Skill Structure
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Claude Code Skills | Current | Skill framework (SKILL.md + supporting files) | Native Claude Code extension mechanism. Skills are SKILL.md files with YAML frontmatter + markdown instructions, stored in `~/.claude/skills/`. |
| Claude Code Subagents | Current | Specialized agents for isolated tasks | Optional: a subagent could handle the document generation step in isolation. Defined in `.claude/agents/` with YAML frontmatter. |
### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| lxml | Latest | XML manipulation for python-docx internals | When applying theme colors at the XML level (python-docx exposes OxmlElement/qn for direct XML access). Pulled in as python-docx dependency. |
| Pillow | Latest | Image processing for logos | Resizing/converting logo images before embedding in .docx headers. Not strictly required if logos are pre-sized. |
| markdown | Latest | Markdown parsing | Parsing source .md files from pbi:docs output into structured data for document generation. |
| PyYAML | Latest | YAML parsing | Reading color scheme configuration files from docsgen-assets/. |
## Stack Architecture Overview
## Skill Directory Structure
### SKILL.md Frontmatter Pattern
## Custom Color Themes and Logos in .docx
### Color Application Strategy
### Implementation Pattern
# Apply heading color from config
# Table header shading
# Logo in header
### Color Config File Format (docsgen-assets/colors.yaml)
### Logo Placement
- **Cover page:** Client logo (centered, large) + company logo (bottom or top-right)
- **Header:** Company logo (left-aligned, small ~1 inch width) on all pages after cover
- **Footer:** Optional client logo (small) or text-only footer
## Alternatives Considered
| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| DOCX generation | python-docx | docxtpl | No pre-existing Word template to fill; need programmatic control over dynamic sections |
| DOCX generation | python-docx | Spire.Doc | Commercial license required; python-docx covers all needed features |
| HTML-to-PDF | Playwright | WeasyPrint | Slower (75x in warm mode), limited CSS support for complex layouts |
| HTML-to-PDF | Playwright | wkhtmltopdf | Abandoned/EOL, frozen WebKit engine, security vulnerabilities |
| HTML-to-PDF | Playwright | Puppeteer | Node.js only (no native Python bindings); Playwright has official Python SDK |
| HTML-to-PDF | Playwright | xhtml2pdf | Limited CSS support, no JavaScript, poor table rendering |
| Skill framework | Claude Code Skills | Standalone CLI | Skills integrate with Claude's conversation context; CLI would lose the intake wizard UX |
## Installation
# Core document generation
# HTML to PDF
# Supporting
# Optional: for advanced Markdown parsing
### Prerequisites Check (skill should verify on run)
# Python 3.9+
# Playwright browsers installed
# python-docx available
## Version Pinning Strategy
## Sources
- [python-docx PyPI](https://pypi.org/project/python-docx/) -- v1.2.0, released June 2025
- [python-docx Documentation](https://python-docx.readthedocs.io/en/latest/) -- styles, headers/footers, font colors
- [docxtpl PyPI](https://pypi.org/project/docxtpl/) -- v0.20.2, released November 2025
- [Playwright Python PyPI](https://pypi.org/project/playwright/) -- v1.58.0, released January 2026
- [WeasyPrint PyPI](https://pypi.org/project/weasyprint/) -- v68.1, released February 2026
- [HTML to PDF Benchmark 2026](https://pdf4.dev/blog/html-to-pdf-benchmark-2026) -- Playwright vs Puppeteer vs WeasyPrint performance data
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) -- SKILL.md structure, frontmatter, supporting files
- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents) -- agents.md format, configuration
- [wkhtmltopdf EOL Advisory](https://doc.doppio.sh/article/wkhtmltopdf-is-now-abandonware) -- deprecated, no longer maintained
- [python-docx Font Color API](https://python-docx.readthedocs.io/en/latest/dev/analysis/features/text/font-color.html) -- RGBColor and theme color support
- [MSO_THEME_COLOR_INDEX](https://python-docx.readthedocs.io/en/latest/api/enum/MsoThemeColorIndex.html) -- theme color enumeration
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
