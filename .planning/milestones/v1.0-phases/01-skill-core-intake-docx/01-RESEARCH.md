# Phase 1: Skill Core + Intake + DOCX - Research

**Researched:** 2026-04-01
**Domain:** Claude Code Skills, python-docx document generation, Markdown parsing, LLM-driven content generation
**Confidence:** HIGH

## Summary

Phase 1 builds the entire DocsGen skill from scratch: a Claude Code skill (SKILL.md) that drives an intake wizard conversation, hands off to a Python generation script (`generate.py`), which parses source Markdown, calls `claude -p` for section prose, and assembles a branded `.docx` via python-docx. The skill must work from any directory, auto-create asset folders, validate prerequisites, and produce client-ready output.

The technology stack is fully locked by CONTEXT.md decisions: python-docx 1.2.0 for DOCX, Jinja2 3.1.6 for prompt templates, `claude -p` subprocess for LLM prose generation. The critical technical risk is python-docx's lack of high-level APIs for cell shading, paragraph backgrounds, and code block borders -- these require direct XML manipulation via `OxmlElement` and `parse_xml`. The skill architecture splits cleanly: SKILL.md handles all user interaction (intake wizard), then invokes `scripts/generate.py` with a JSON payload via Bash tool.

**Primary recommendation:** Build the pipeline in strict order -- scaffolding first, then MD parser, then LLM content generation, then DOCX builder -- because each layer depends on the output shape of the previous one.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: LLM-generated prose via `claude -p` subprocess with section-specific prompts
- D-02: Quality bar requires LLM prose, not templates
- D-03: Audience awareness in LLM prompt (M Query switches between plain-English and annotated code)
- D-04: Each of 6 sections is a separate LLM call
- D-05: Asset-first flow -- check `docsgen-assets/` before asking questions
- D-06: Sequential one-field-at-a-time prompts on first run
- D-07: Language always asked, never cached
- D-08: Pre-generation validation -- all assets checked before Python launches
- D-09: `docsgen-assets/` auto-created with `logos/` and `source/` subdirectories
- D-10: Heading-based section detection from `##` headings
- D-11: Section mapping uses heading keyword matching
- D-12: Sections with no content silently skipped
- D-13: Source MD can be single or multiple files, concatenated before parsing
- D-14: Built-in Word styles + run-level color overrides (never style mutation)
- D-15: Run-level formatting locked from day one
- D-16: Table header shading via XML-level OxmlElement
- D-17: Cover page as dedicated section with NEW_PAGE
- D-18: Header/footer with different_first_page_header_footer
- D-19: Code style: Courier New 9pt, light grey background, 1pt border
- D-20: SKILL.md handles intake, calls `scripts/generate.py` via Bash
- D-21: `generate.py` is single entry point with pipeline stages
- D-22: JSON config via stdin or temp file
- D-23: Skill at `~/.claude/skills/pbi-docgen/`
- D-24: Fowler compliance via LLM prompt instructions
- D-25: Prose generated fresh each run

### Claude's Discretion
- Exact Jinja2 prompt template structure for each section type
- Specific RGBColor values for "light tint" alternating table rows
- python-docx paragraph spacing (before/after pt values)
- How to handle very long M Query code blocks in .docx
- Whether to use `add_paragraph` or `add_run` chaining for mixed-format paragraphs

### Deferred Ideas (OUT OF SCOPE)
- Config reuse (save client config for repeat runs) -- v2 CFG-01/CFG-02
- ASCII / ERD diagrams -- v2 DIAG-01/DIAG-02
- Table of contents in .docx -- Phase 2 DOCX-05
- PDF output -- Phase 2 entirely
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SCAF-01 | Skill works from any directory | SKILL.md stored in `~/.claude/skills/pbi-docgen/`; `${CLAUDE_SKILL_DIR}` substitution for script paths |
| SCAF-02 | Auto-create `docsgen-assets/` with `logos/`, `source/` | Python `os.makedirs()` or SKILL.md Bash mkdir; guide user via conversation |
| SCAF-03 | Follows Claude Code skill conventions | SKILL.md frontmatter format documented; `scripts/`, `templates/`, `references/` directories |
| SCAF-04 | Detect missing Python deps and surface install instructions | `importlib` check or `subprocess` pip check in generate.py entry point |
| INTAK-01 | Step-by-step intake for all required inputs | SKILL.md conversation flow; 10 fields per D-06 |
| INTAK-02 | Language asked every run | SKILL.md always includes language prompt; D-07 |
| INTAK-03 | Validate all assets before generation | Pre-flight checklist in SKILL.md before Bash call to generate.py |
| INTAK-04 | Auto-create output folder | `docsgen-output/` created by generate.py |
| PARSE-01 | Read source MD from pbi:docs | Python file I/O; heading-based parsing per D-10 |
| PARSE-02 | Section auto-detection for 6 categories | Keyword matching on `##` headings per D-11 |
| PARSE-03 | Skip sections with no content | D-12; parser returns only matched sections |
| CONT-01 | Section 1: Project overview | LLM prompt template via Jinja2 + `claude -p` |
| CONT-02 | Section 2: Source systems & architecture | LLM prompt template via Jinja2 + `claude -p` |
| CONT-03 | Section 3: Dataflows (skip if absent) | LLM prompt + PARSE-03 skip logic |
| CONT-04 | Section 4: M Query (audience-aware) | Audience-switching prompt per D-03 |
| CONT-05 | Section 5: Data model / SSAS | LLM prompt template via Jinja2 + `claude -p` |
| CONT-06 | Section 6: Troubleshooting & maintenance | LLM prompt template via Jinja2 + `claude -p` |
| CONT-07 | English follows Fowler's guidelines | Fowler rules embedded in each LLM prompt per D-24 |
| DOCX-01 | .docx with all sections, headings, paragraphs, tables, code blocks | python-docx Document API + custom Code style |
| DOCX-02 | Cover page with client info and logos | Dedicated section with NEW_PAGE per D-17 |
| DOCX-03 | Brand colors via run-level formatting | RGBColor on runs per D-14/D-15; XML shading for tables per D-16 |
| DOCX-04 | Header/footer with page numbers and different first page | different_first_page_header_footer per D-18 |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| python-docx | 1.2.0 | .docx creation and manipulation | Only serious Python library for programmatic Word generation. Supports styles, runs, images, headers/footers, sections, tables. Latest release. |
| Jinja2 | 3.1.6 | LLM prompt template rendering | Standard Python template engine. Used for section-specific `claude -p` prompts, not for docx templates. Already installed. |
| PyYAML | 6.0.3 | Color config file parsing | Reads `docsgen-assets/colors.yaml`. Already installed. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pillow | 12.1.0 | Logo image processing | Resize/validate logos before embedding. Already installed. |
| lxml | (transitive) | XML manipulation for python-docx | Cell shading, paragraph backgrounds, code block borders. Comes with python-docx. |
| markdown | 3.10.2 | Markdown parsing | Optional -- may not be needed if using regex-based heading extraction (see Architecture Patterns). |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Raw regex MD parsing | `markdown` library | `markdown` is heavier but more robust for edge cases; regex is simpler for heading-only extraction. Decision: start with regex, add `markdown` only if edge cases appear. |
| `claude -p` subprocess | Claude SDK (Python) | SDK adds dependency; subprocess is simpler, well-documented, and sufficient for one-shot calls. |

**Installation:**
```bash
pip install python-docx==1.2.0 Jinja2==3.1.6 PyYAML Pillow
```

**Version verification:** python-docx 1.2.0 confirmed as latest via PyPI (2026-04-01). Jinja2 3.1.6 confirmed as latest.

## Architecture Patterns

### Recommended Project Structure
```
~/.claude/skills/pbi-docgen/
  SKILL.md                    # Intake wizard + orchestration
  scripts/
    generate.py               # Single entry point: parse -> generate -> build
    docx_builder.py            # python-docx document assembly
    md_parser.py               # Markdown section detection and extraction
    content_generator.py       # claude -p calls for each section
    utils.py                   # Shared helpers (color parsing, file validation)
  templates/
    prompts/
      section_overview.j2      # Jinja2 prompt for Section 1
      section_sources.j2       # Jinja2 prompt for Section 2
      section_dataflows.j2     # Jinja2 prompt for Section 3
      section_mquery.j2        # Jinja2 prompt for Section 4 (audience-aware)
      section_datamodel.j2     # Jinja2 prompt for Section 5
      section_maintenance.j2   # Jinja2 prompt for Section 6
    fowler_rules.j2            # Shared Fowler compliance instructions (included in all prompts)
  references/
    section_heading_map.yaml   # Heading keywords -> section category mapping
    fowler_guidance.md         # Fowler's rules reference for prompt engineering
```

### Pattern 1: SKILL.md Intake Wizard
**What:** SKILL.md handles the entire user conversation, collecting inputs one at a time, validating, then invoking generate.py.
**When to use:** Always -- this is the skill entry point.
**Example:**
```yaml
---
name: pbi-docgen
description: Generate branded Word documents from PBI documentation. Use when the user wants to create client-ready .docx deliverables from pbi:docs Markdown output.
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Glob
---

# PBI Documentation Generator

You are the DocsGen intake wizard. Guide the user through document generation.

## Step 1: Asset Directory Setup
Check if `docsgen-assets/` exists in the current working directory.
If not, create it with subdirectories:
```
mkdir -p docsgen-assets/logos docsgen-assets/source
```
...
```

### Pattern 2: JSON Config Handoff (SKILL.md -> generate.py)
**What:** SKILL.md collects all inputs, writes a JSON config to a temp file, invokes generate.py.
**When to use:** At the transition from intake to generation.
**Example:**
```python
# Config schema (D-22)
{
    "client_name": "Acme Corp",
    "client_logo": "docsgen-assets/logos/acme-logo.png",
    "company_logo": "docsgen-assets/logos/company-logo.png",
    "primary_color": "#1B365D",
    "accent_color": "#4A90D9",
    "language": "EN",
    "audience": "client",  # "client" | "internal" | "IT"
    "report_name": "Sales Dashboard",
    "version": "1.0",
    "source_files": ["docsgen-assets/source/overview.md", "docsgen-assets/source/model.md"],
    "output_dir": "docsgen-output"
}
```

### Pattern 3: Run-Level Color Application (NOT Style Mutation)
**What:** Apply brand colors by setting `run.font.color.rgb` on individual runs, never by modifying style definitions.
**When to use:** Every heading, every colored text element.
**Why critical:** python-docx style mutations can fail silently -- a heading may appear to have a color in the API but render as black in Word. Run-level formatting is the only reliable method.
**Example:**
```python
from docx.shared import RGBColor, Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_colored_heading(doc, text, level, color_hex):
    """Add a heading with brand color applied at run level."""
    heading = doc.add_heading(level=level)
    run = heading.add_run(text)
    r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
    run.font.color.rgb = RGBColor(r, g, b)
    return heading
```

### Pattern 4: Table Cell Shading via XML
**What:** Apply background color to table cells using OxmlElement XML manipulation.
**When to use:** Table header rows (primary color) and alternating body rows (light accent tint).
**Example:**
```python
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

def set_cell_background(cell, color_hex):
    """Set background color on a table cell via XML shading element."""
    # color_hex without '#', e.g. "1B365D"
    shading_elm = parse_xml(
        f'<w:shd {nsdecls("w")} w:fill="{color_hex}" w:val="clear"/>'
    )
    cell._tc.get_or_add_tcPr().append(shading_elm)
```

### Pattern 5: Paragraph Background Shading for Code Blocks
**What:** Apply light grey background to code block paragraphs using XML.
**When to use:** M Query code blocks and any code-formatted content.
**Example:**
```python
def set_paragraph_shading(paragraph, color_hex):
    """Set background shading on a paragraph via XML."""
    shading_elm = parse_xml(
        f'<w:shd {nsdecls("w")} w:fill="{color_hex}" w:val="clear"/>'
    )
    paragraph._element.get_or_add_pPr().append(shading_elm)
```

### Pattern 6: Cover Page as Separate Section
**What:** Create cover page in the document's first section, then add a new section for body content with different header/footer.
**When to use:** Document start.
**Example:**
```python
from docx.enum.section import WD_SECTION_START

def setup_cover_page(doc):
    """Configure first section as cover page with distinct header."""
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    # Cover page content goes here (client name, logos, etc.)
    # ...
    # Add section break for body content
    new_section = doc.add_section(WD_SECTION_START.NEW_PAGE)
    return new_section
```

### Pattern 7: Header with Logo Image
**What:** Add company logo to header on all non-cover pages.
**When to use:** Body content section setup.
**Example:**
```python
def add_header_logo(section, logo_path):
    """Add logo to section header."""
    header = section.header
    header.is_linked_to_previous = False
    paragraph = header.paragraphs[0]
    run = paragraph.add_run()
    run.add_picture(logo_path, width=Inches(1.0))
```

### Pattern 8: claude -p Subprocess for Content Generation
**What:** Call `claude -p` with a rendered Jinja2 prompt to generate section prose.
**When to use:** Each of the 6 sections.
**Example:**
```python
import subprocess
import json

def generate_section_prose(prompt_text):
    """Call claude -p to generate professional prose from source content."""
    result = subprocess.run(
        ["claude", "-p", prompt_text, "--output-format", "text"],
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p failed: {result.stderr}")
    return result.stdout.strip()
```

### Anti-Patterns to Avoid
- **Style mutation for colors:** Never do `style.font.color.rgb = ...` on built-in heading styles. Use run-level formatting only (D-14/D-15).
- **Positional CLI args:** Never use positional args for generate.py. Use JSON config (D-22).
- **Single monolithic LLM call:** Never send all sections to one `claude -p` call. Use separate calls per section (D-04).
- **Caching language selection:** Never cache or infer language. Always ask (D-07/INTAK-02).
- **Generating blank sections:** Never output headings for sections with no source content (D-12/PARSE-03).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Word document creation | Custom XML assembly | python-docx | Thousands of edge cases in OOXML spec |
| Template rendering | String concatenation for prompts | Jinja2 | Variable escaping, includes, conditionals handled correctly |
| YAML parsing | Regex or custom parser | PyYAML | Standard, handles all YAML edge cases |
| Image resizing | Manual pixel math | Pillow | Handles DPI, format conversion, aspect ratio |
| Cell shading | Full custom XML builder | `parse_xml` + `nsdecls` helper from python-docx | python-docx provides XML helpers even for unsupported features |
| Hex color parsing | Regex | Simple int() slicing | `int(hex_str[1:3], 16)` is sufficient; no library needed |

**Key insight:** python-docx handles ~80% of Word generation needs through its high-level API. The remaining ~20% (cell shading, paragraph backgrounds, borders) requires dropping to XML via the library's own `parse_xml`/`nsdecls` helpers -- not building a separate XML layer.

## Common Pitfalls

### Pitfall 1: Silent Style Color Failures
**What goes wrong:** Setting `style.font.color.rgb` on a built-in heading style appears to work in the API but renders as black in Word.
**Why it happens:** Word's style inheritance and theme color precedence can override programmatic style changes.
**How to avoid:** Always use run-level formatting: `run.font.color.rgb = RGBColor(r, g, b)`. This is D-14/D-15.
**Warning signs:** Headings appear uncolored when opened in Word despite color being set in code.

### Pitfall 2: Header/Footer Inheritance Between Sections
**What goes wrong:** Adding a new section inherits the previous section's header/footer, leading to cover page logos appearing on body pages or vice versa.
**Why it happens:** By default, sections in python-docx link to the previous section's header/footer.
**How to avoid:** Set `header.is_linked_to_previous = False` on each new section's header and footer before adding content.
**Warning signs:** Same header content appearing on all pages despite different section configurations.

### Pitfall 3: Cell Shading XML Elements Must Be Unique
**What goes wrong:** Reusing the same shading XML element across multiple cells causes only the last cell to be shaded.
**Why it happens:** XML elements can only have one parent in lxml. Appending to a new parent silently removes from the old parent.
**How to avoid:** Create a new `parse_xml()` shading element for every cell. Never cache and reuse the element.
**Warning signs:** Only the last cell in a row is shaded; previous cells lose their background.

### Pitfall 4: claude -p Subprocess Timeout and Encoding
**What goes wrong:** LLM calls hang or return garbled text on Windows.
**Why it happens:** Large prompts with source MD content can take 30-60+ seconds. Windows subprocess encoding defaults to cp1252.
**How to avoid:** Set `timeout=120` on subprocess.run. Use `encoding='utf-8'` and `errors='replace'`. Consider `--bare` flag for faster startup.
**Warning signs:** Subprocess timeouts, UnicodeDecodeError, or mojibake in generated prose.

### Pitfall 5: Markdown Heading Detection False Positives
**What goes wrong:** Lines inside code blocks that start with `##` are incorrectly detected as section headings.
**Why it happens:** Naive regex `^##\s+` matches inside fenced code blocks.
**How to avoid:** Track fenced code block state (count ``` markers) when scanning for headings. Skip any `##` lines inside a fenced block.
**Warning signs:** Spurious sections appearing in output, or section boundaries in wrong places.

### Pitfall 6: Image Path Resolution Across Directories
**What goes wrong:** Logo paths fail because generate.py resolves relative paths from its own location, not the user's working directory.
**Why it happens:** Skill runs from `~/.claude/skills/pbi-docgen/` but assets are in the user's CWD.
**How to avoid:** JSON config should contain absolute paths (resolved by SKILL.md before handoff). generate.py should validate all paths exist before starting.
**Warning signs:** FileNotFoundError on logo paths that work from the user's terminal.

### Pitfall 7: add_heading() Returns Paragraph, Not Run
**What goes wrong:** Attempting to set color on the return value of `doc.add_heading("text", level=1)` -- it returns a Paragraph, not a Run.
**Why it happens:** API confusion. `add_heading` creates a paragraph with a run inside it.
**How to avoid:** Use `heading = doc.add_heading(level=1)` (no text), then `run = heading.add_run("text")`, then `run.font.color.rgb = ...`. Or access `heading.runs[0]` after creation with text.
**Warning signs:** AttributeError when trying to access `.font` on a Paragraph object.

## Code Examples

### Complete Custom Code Style Creation
```python
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt, RGBColor

def create_code_style(document):
    """Create a 'Code' paragraph style for M Query and code blocks (D-19)."""
    styles = document.styles
    code_style = styles.add_style('Code', WD_STYLE_TYPE.PARAGRAPH)
    code_style.base_style = styles['Normal']
    code_style.font.name = 'Courier New'
    code_style.font.size = Pt(9)
    code_style.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    # Background shading must be applied per-paragraph via XML
    # Border must also be applied via XML on each paragraph
    return code_style
```

### Paragraph Border via XML (for Code Blocks)
```python
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

def add_paragraph_border(paragraph, color_hex="D0D0D0"):
    """Add a thin border around a paragraph (for code block styling)."""
    pPr = paragraph._element.get_or_add_pPr()
    borders = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="4" w:space="4" w:color="{color_hex}"/>'
        f'  <w:left w:val="single" w:sz="4" w:space="4" w:color="{color_hex}"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="4" w:color="{color_hex}"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="4" w:color="{color_hex}"/>'
        f'</w:pBdr>'
    )
    pPr.append(borders)
```

### Section Heading Map (references/section_heading_map.yaml)
```yaml
# Maps ## heading keywords to section categories (D-11)
sections:
  - id: overview
    label: "Project Overview"
    keywords: ["overview", "summary", "introduction", "about"]
  - id: sources
    label: "Source Systems & Architecture"
    keywords: ["data source", "gateway", "connection", "source system", "architecture"]
  - id: dataflows
    label: "Dataflows"
    keywords: ["dataflow", "data flow", "refresh", "pipeline"]
  - id: mquery
    label: "M Query Business Logic"
    keywords: ["m query", "power query", "m code", "query", "transformation"]
  - id: datamodel
    label: "Data Model"
    keywords: ["data model", "ssas", "relationship", "table", "measure", "dax", "column"]
  - id: maintenance
    label: "Troubleshooting & Maintenance"
    keywords: ["parameter", "troubleshooting", "maintenance", "configuration", "setting"]
```

### Jinja2 Prompt Template Example (Section 4 - M Query)
```jinja2
{# templates/prompts/section_mquery.j2 #}
{% include 'fowler_rules.j2' %}

You are writing Section 4: M Query Business Logic for a Power BI documentation deliverable.

**Client:** {{ client_name }}
**Report:** {{ report_name }}
**Audience:** {{ audience }}

{% if audience == "client" %}
Write a plain-English summary of what each M Query does in business terms.
Do NOT include raw M code. Explain transformations as business operations
(e.g., "filters sales data to the current fiscal year" not "Table.SelectRows(Source, each [Year] >= 2024)").
{% else %}
For each M Query, provide:
1. A one-sentence business purpose
2. The annotated M code with inline comments explaining each step
3. Any dependencies on other queries or parameters
{% endif %}

**Source content to transform:**
{{ source_content }}

Write the section content now. Output only the section body text (no heading -- that is added programmatically).
```

### Fowler Rules Include Template
```jinja2
{# templates/fowler_rules.j2 #}
**Writing quality rules (Fowler's Modern English Usage):**
1. Prefer active voice. "The report filters data" not "Data is filtered by the report."
2. No nominalization padding. "Using" not "the utilization of." "Analyzing" not "the analysis of."
3. No corporate filler. Never use: leverage, synergy, optimize, utilize, facilitate, streamline.
4. Keep sentences under 25 words. Split long sentences.
5. Be direct. State what something does, not what it "aims to" or "seeks to" do.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| docxtpl (template-based) | python-docx (programmatic) | Project decision | Full control over dynamic sections; no pre-existing .docx template needed |
| Style-level color | Run-level color (RGBColor) | Known pitfall | Prevents silent color rendering failures in Word |
| Monolithic LLM calls | Per-section LLM calls | D-04 | Avoids context overflow, enables section-specific prompt tuning |

## Open Questions

1. **Long M Query code blocks in .docx**
   - What we know: Word handles long code blocks poorly -- no horizontal scrolling, text wraps or gets cut off.
   - What's unclear: Best approach for very wide M code (150+ char lines).
   - Recommendation: Use Courier New 9pt (D-19), set narrow page margins for code sections, and wrap lines at 100 characters in the prompt instructions. If code is too wide, the LLM prompt should instruct line breaking.

2. **claude -p warm startup time on Windows**
   - What we know: `claude -p` loads skills, hooks, MCP servers on each invocation. With 6 section calls, this adds up.
   - What's unclear: Exact cold-start overhead per call on this Windows machine.
   - Recommendation: Use `claude -p --bare` to skip auto-discovery for faster execution. Each call only needs the prompt and text output.

3. **Markdown tables in source content**
   - What we know: Source MD from pbi:docs may contain Markdown tables. These need to become Word tables.
   - What's unclear: How consistently pbi:docs formats tables.
   - Recommendation: The LLM prompt should instruct Claude to output structured content (e.g., "TABLE:" markers) that generate.py can parse into python-docx table calls. Alternatively, pass table content through and let the DOCX builder detect pipe-delimited table syntax.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All generation | Yes | 3.13.12 | -- |
| claude CLI | Content generation (claude -p) | Yes | (installed at /c/Users/DeveshD/.local/bin/claude) | -- |
| Node.js | claude CLI runtime | Yes | v24.13.1 | -- |
| python-docx | DOCX generation | No (not installed) | -- | Install: `pip install python-docx==1.2.0` |
| Jinja2 | Prompt templates | Yes | 3.1.6 | -- |
| PyYAML | Color config | Yes | 6.0.3 | -- |
| Pillow | Logo processing | Yes | 12.1.0 | -- |
| markdown | MD parsing (optional) | No (not installed) | -- | Use regex-based heading extraction |

**Missing dependencies with no fallback:**
- python-docx 1.2.0 -- must be installed before any DOCX generation work

**Missing dependencies with fallback:**
- markdown library -- regex-based `##` heading extraction is sufficient for section detection

## Project Constraints (from CLAUDE.md)

- **python-docx 1.2.0** pinned (CLAUDE.md Technology Stack)
- **Jinja2 3.1.6** pinned (CLAUDE.md Technology Stack)
- **Run-level formatting only** for colors -- never style mutation (CLAUDE.md Color Application Strategy)
- **Table header shading via OxmlElement** at XML level (CLAUDE.md Implementation Pattern)
- **Cover page:** client logo centered large + company logo bottom-right (CLAUDE.md Logo Placement)
- **Header:** company logo left-aligned ~1 inch on non-cover pages (CLAUDE.md Logo Placement)
- **colors.yaml** for color configuration (CLAUDE.md Color Config File Format)
- **Quality bar:** output must be suitable for direct client delivery without post-processing (CLAUDE.md Constraints)
- **GSD workflow enforcement:** all file changes through GSD commands (CLAUDE.md GSD Workflow Enforcement)

## Sources

### Primary (HIGH confidence)
- [python-docx PyPI](https://pypi.org/project/python-docx/) -- v1.2.0 confirmed as latest via `pip index versions`
- [python-docx Font Color docs](https://python-docx.readthedocs.io/en/latest/dev/analysis/features/text/font-color.html) -- RGBColor API
- [python-docx Header/Footer docs](https://python-docx.readthedocs.io/en/latest/user/hdrftr.html) -- different_first_page_header_footer
- [python-docx Sections docs](https://python-docx.readthedocs.io/en/latest/user/sections.html) -- WD_SECTION_START
- [python-docx Styles docs](https://python-docx.readthedocs.io/en/latest/user/styles-using.html) -- add_style API
- [Claude Code Skills docs](https://code.claude.com/docs/en/skills) -- SKILL.md format, frontmatter, supporting files, invocation
- [Claude Code Headless docs](https://code.claude.com/docs/en/headless) -- claude -p usage, --bare, --output-format

### Secondary (MEDIUM confidence)
- [python-docx cell shading issue #146](https://github.com/python-openxml/python-docx/issues/146) -- OxmlElement cell background pattern
- [python-docx cell shading issue #434](https://github.com/python-openxml/python-docx/issues/434) -- unique XML elements per cell
- [python-docx header image issue #407](https://github.com/python-openxml/python-docx/issues/407) -- run.add_picture in headers
- [WD_STYLE_TYPE docs](https://python-docx.readthedocs.io/en/latest/api/enum/WdStyleType.html) -- custom style creation
- [OOXML table cell shading spec](http://officeopenxml.com/WPtableCellProperties-Shading.php) -- XML shading element format

### Tertiary (LOW confidence)
- None -- all findings verified against official docs or GitHub issues

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- versions verified against PyPI, APIs verified against official docs
- Architecture: HIGH -- skill structure verified against Claude Code official docs, python-docx patterns verified against issues and docs
- Pitfalls: HIGH -- cell shading, style mutation, and header inheritance issues well-documented in python-docx GitHub issues

**Research date:** 2026-04-01
**Valid until:** 2026-05-01 (stable libraries, no fast-moving concerns)
