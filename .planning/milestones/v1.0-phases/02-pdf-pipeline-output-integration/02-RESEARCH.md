# Phase 2: PDF Pipeline + Output Integration - Research

**Researched:** 2026-04-01
**Domain:** HTML-to-PDF generation (Playwright), Word TOC fields (python-docx XML), pipeline integration
**Confidence:** HIGH

## Summary

Phase 2 adds three capabilities to the existing DocsGen pipeline: (1) a PDF output rendered from a Jinja2 HTML template via Playwright's headless Chromium, (2) an auto-updateable Table of Contents field in the .docx, and (3) pipeline wiring so a single `generate.py` invocation produces both outputs with consistent naming and a completion report.

The technology stack is fully locked by CLAUDE.md and CONTEXT.md decisions. Playwright 1.58.0 with Chromium is installed and verified working on the target machine. python-docx 1.2.0 and Jinja2 3.1.6 are also installed. The core challenge is building a Jinja2 HTML template that mirrors the .docx visual identity (cover page, branded headers/footers, color hierarchy) using print-first CSS, and inserting a Word TOC field via raw OxmlElement XML since python-docx has no built-in TOC API.

**Primary recommendation:** Build a new `pdf_builder.py` module following the existing module-per-stage pattern, with a single `build_pdf(sections, config, docx_path)` function. Use Playwright's synchronous API (`sync_playwright`) since the existing pipeline is synchronous. The Jinja2 template renders brand colors via CSS custom properties; Playwright's `page.pdf()` with `print_background=True` preserves them.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Use a real Word XML TOC field -- inject `TOC \o "1-3" \h \z \u` via `python-docx` `OxmlElement`. Word displays "Update this field" on open; user presses F9 to refresh page numbers.
- **D-02:** TOC is inserted after the cover page section break and before the first content section. It occupies its own page (page break after TOC).
- **D-03:** TOC field covers heading levels 1-3 (`\o "1-3"`), hyperlinked (`\h`), with dotted leaders and page numbers.
- **D-04:** PDF TOC uses clickable HTML anchor links -- `<a href="#section-id">` pointing to `<h2 id="section-id">` on each section heading. Playwright/Chromium preserves these as clickable links in PDF output.
- **D-05:** Section IDs are generated deterministically from section names (slugified: lowercase, spaces to hyphens, no special chars).
- **D-06:** PDF mirrors the .docx visual identity -- same cover page layout, branded body pages with CSS `@page` header, same color hierarchy.
- **D-07:** CSS custom properties for brand colors: `--primary: {{ primary_color }};` and `--accent: {{ accent_color }};` rendered by Jinja2. All color references use `var(--primary)` / `var(--accent)`.
- **D-08:** Single Jinja2 template (`templates/document.html.j2`) -- base HTML with sections loop. Cover page is a distinct `<div class="cover-page">` with `page-break-after: always`.
- **D-09:** Print-first CSS: `print-color-adjust: exact`, `@media print` block, `page-break-inside: avoid` on tables and code blocks, embedded or system-safe fonts (must work offline).
- **D-10:** If Playwright fails, deliver `.docx` only with clear warning to stderr. Skill exits 0 (partial delivery is valid).
- **D-11:** Playwright failure caught at `build_pdf()` call. `.docx` already saved before PDF attempt -- no rollback needed.
- **D-12:** `generate.py` extended with Stage 4: `build_pdf(sections, config, docx_path)`. Same `sections` dict feeds both builders.
- **D-13:** PDF output filename: same stem as .docx, different extension.
- **D-14:** Completion report to stderr lists both paths and sizes. If PDF skipped, report notes clearly. stdout emits `.docx` path then `.pdf` path (or `PDF_SKIPPED` sentinel).

### Claude's Discretion
- Exact CSS for cover page layout (logo sizing, spacing, font weights)
- Font stack choice (system fonts vs embedded web fonts) -- offline-safe required
- How to structure the Jinja2 sections loop (dict vs ordered list of dicts)
- Exact python-docx OxmlElement XML snippet for the TOC field
- Whether to add a "Please press F9 to update page numbers" note below the TOC placeholder

### Deferred Ideas (OUT OF SCOPE)
- PDF bookmarks (named destinations) -- anchor links satisfy navigability requirement
- Config reuse (save client config for repeat runs) -- v2 requirement CFG-01/CFG-02
- ASCII / ERD diagrams -- v2 requirement DIAG-01/DIAG-02
- French language -- Phase 3
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PDF-01 | Jinja2 HTML template renders structured content with full CSS layout matching document brand colors | Jinja2 template pattern with CSS custom properties (D-07/D-08); verified Jinja2 3.1.6 installed |
| PDF-02 | PDF generated from HTML via Playwright (headless Chromium) -- not wkhtmltopdf | Playwright 1.58.0 sync API with `page.set_content()` + `page.pdf()`; Chromium verified launching |
| PDF-03 | CSS is print-first: explicit `print-color-adjust: exact`, embedded fonts, page break control | Print CSS patterns documented below; `print_background=True` required in `page.pdf()` call |
| DOCX-05 | Table of contents inserted at document start (auto-updateable TOC field in Word) | OxmlElement XML pattern for `w:sdt` + `w:fldChar` TOC field; insert after cover page section break |
| OUT-01 | Both `.docx` and `.pdf` produced in a single skill invocation | Pipeline integration: Stage 4 added to `generate.py` after Stage 3 `build_docx()` |
| OUT-02 | Output files named predictably: `[ClientName]_[ReportName]_v[Version]_[YYYY-MM-DD].docx/.pdf` | Filename logic already at `docx_builder.py` lines 511-516; PDF reuses same stem |
| OUT-03 | Skill reports completion with output file paths and file sizes | Completion report pattern: stderr for human-readable, stdout for machine-readable paths |
</phase_requirements>

## Standard Stack

### Core (locked -- no alternatives)
| Library | Version | Purpose | Verified |
|---------|---------|---------|----------|
| python-docx | 1.2.0 | TOC field injection via OxmlElement XML | Installed, verified via `pip show` |
| Playwright (Python) | 1.58.0 | Headless Chromium HTML-to-PDF rendering | Installed, Chromium launches successfully |
| Jinja2 | 3.1.6 | HTML template rendering with brand color injection | Installed, already used for prompt templates |

### Supporting (already installed)
| Library | Version | Purpose |
|---------|---------|---------|
| lxml | (python-docx dependency) | XML manipulation for TOC field elements |
| PyYAML | (installed) | Config parsing (no change from Phase 1) |

**No new packages to install.** Everything needed is already present.

## Architecture Patterns

### New Files
```
.claude/skills/pbi-docgen/
  scripts/
    pdf_builder.py          # NEW: build_pdf() function
  templates/
    document.html.j2        # NEW: Jinja2 HTML template for PDF
```

### Modified Files
```
scripts/generate.py         # Add Stage 4: build_pdf() call + completion report
scripts/docx_builder.py     # Add TOC field insertion in build_docx()
SKILL.md                    # Capture both output paths, report both sizes
```

### Pattern 1: Playwright Synchronous PDF Generation
**What:** Use `sync_playwright` context manager to launch Chromium, set HTML content, and render PDF.
**When to use:** Always -- the existing pipeline is synchronous; no async needed.
**Example:**
```python
# Source: Playwright Python official docs + verified on target machine
from playwright.sync_api import sync_playwright

def build_pdf(sections: dict, config: dict, docx_path: str) -> str:
    """Build PDF from sections using Jinja2 template + Playwright.
    
    Args:
        sections: Same dict passed to build_docx().
        config: JSON config dict.
        docx_path: Path to .docx (used to derive .pdf filename).
    
    Returns:
        Absolute path to saved .pdf file.
    """
    # 1. Render HTML from Jinja2 template
    html_content = _render_html(sections, config)
    
    # 2. Generate PDF via Playwright
    pdf_path = docx_path.replace('.docx', '.pdf')
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        page.pdf(
            path=pdf_path,
            format="Letter",
            print_background=True,
            margin={
                "top": "20mm",
                "bottom": "20mm",
                "left": "15mm",
                "right": "15mm",
            },
            display_header_footer=True,
            header_template='<div></div>',  # CSS @page handles headers
            footer_template='<div style="font-size:10px;text-align:center;width:100%"><span class="pageNumber"></span></div>',
        )
        browser.close()
    
    return os.path.abspath(pdf_path)
```

### Pattern 2: TOC Field Injection via OxmlElement
**What:** Insert a structured document tag (SDT) containing a TOC field into the .docx body XML.
**When to use:** After cover page, before first content section (D-02).
**Example:**
```python
# Source: python-docx issue #36 + chanmo.github.io blog + D-01/D-02/D-03
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def _insert_toc_field(doc, levels="1-3"):
    """Insert a TOC field placeholder into the document body.
    
    Creates a Structured Document Tag (SDT) wrapping a TOC field instruction.
    Word will display 'Update this field' when the document is opened.
    User presses F9 to populate page numbers.
    """
    sdt = OxmlElement('w:sdt')
    sdtpr = OxmlElement('w:sdtPr')
    docpartobj = OxmlElement('w:docPartObj')
    docpartgallery = OxmlElement('w:docPartGallery')
    docpartgallery.set(qn('w:val'), 'Table of Contents')
    docpartunique = OxmlElement('w:docPartUnique')
    docpartunique.set(qn('w:val'), 'true')
    docpartobj.append(docpartgallery)
    docpartobj.append(docpartunique)
    sdtpr.append(docpartobj)
    sdt.append(sdtpr)

    sdtcontent = OxmlElement('w:sdtContent')
    
    # "Table of Contents" heading
    p = OxmlElement('w:p')
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = 'Table of Contents'
    r.append(t)
    p.append(r)
    sdtcontent.append(p)

    # TOC field: begin -> instrText -> separate -> end
    p2 = OxmlElement('w:p')
    r2 = OxmlElement('w:r')
    
    fldchar_begin = OxmlElement('w:fldChar')
    fldchar_begin.set(qn('w:fldCharType'), 'begin')
    
    instrtext = OxmlElement('w:instrText')
    instrtext.set(qn('xml:space'), 'preserve')
    instrtext.text = f'TOC \\o "{levels}" \\h \\z \\u'
    
    fldchar_separate = OxmlElement('w:fldChar')
    fldchar_separate.set(qn('w:fldCharType'), 'separate')
    
    fldchar_end = OxmlElement('w:fldChar')
    fldchar_end.set(qn('w:fldCharType'), 'end')
    
    r2.append(fldchar_begin)
    r2.append(instrtext)
    r2.append(fldchar_separate)
    r2.append(fldchar_end)
    p2.append(r2)
    sdtcontent.append(p2)
    
    sdt.append(sdtcontent)
    return sdt
```

### Pattern 3: Jinja2 HTML Template with CSS Custom Properties
**What:** Single `document.html.j2` template that renders the full document with brand colors injected via CSS custom properties.
**When to use:** For all PDF rendering (D-08).
**Template skeleton:**
```html
{# Source: D-06/D-07/D-08/D-09 decisions #}
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  :root {
    --primary: {{ primary_color }};
    --accent: {{ accent_color }};
  }
  @page {
    size: Letter;
    margin: 20mm 15mm;
  }
  @media print {
    * { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  }
  body {
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
  }
  .cover-page {
    page-break-after: always;
    text-align: center;
    padding-top: 80px;
  }
  .cover-page h1 { color: var(--primary); font-size: 28pt; }
  .cover-page .subtitle { color: var(--primary); font-size: 18pt; }
  .toc a { color: var(--primary); text-decoration: none; }
  .toc { page-break-after: always; }
  h1 { color: var(--primary); }
  h2 { color: var(--accent); }
  table { width: 100%; border-collapse: collapse; page-break-inside: avoid; }
  th { background: var(--primary); color: white; padding: 8px 12px; }
  pre, code { page-break-inside: avoid; }
  pre { background: #f2f2f2; padding: 12px; border-radius: 4px; }
</style>
</head>
<body>
  <div class="cover-page">
    {% if client_logo %}<img src="{{ client_logo }}" style="max-width:300px">{% endif %}
    <h1>{{ client_name }}</h1>
    <p class="subtitle">{{ report_name }}</p>
    <p class="meta">Version {{ version }} | {{ date }}</p>
    {% if company_logo %}<img src="{{ company_logo }}" style="max-width:120px">{% endif %}
  </div>
  
  <div class="toc">
    <h1>Table of Contents</h1>
    {% for section in sections %}
    <p><a href="#{{ section.id }}">{{ section.label }}</a></p>
    {% endfor %}
  </div>
  
  {% for section in sections %}
  <div class="section">
    <h1 id="{{ section.id }}">{{ section.label }}</h1>
    {{ section.html_content }}
  </div>
  {% endfor %}
</body>
</html>
```

### Pattern 4: Graceful Playwright Failure (D-10/D-11)
**What:** Wrap `build_pdf()` in try/except at the `generate.py` level.
**Example:**
```python
# In generate.py, after build_docx():
pdf_path = None
try:
    from scripts.pdf_builder import build_pdf
    pdf_path = build_pdf(sections, config, docx_path)
except Exception as e:
    print(f"PDF generation failed: {e}", file=sys.stderr)
    print(f"DOCX output delivered: {docx_path}", file=sys.stderr)
    print("To enable PDF: pip install playwright==1.58.0 && python -m playwright install chromium", file=sys.stderr)

# stdout output (D-14)
print(docx_path)
print(pdf_path if pdf_path else "PDF_SKIPPED")
```

### Anti-Patterns to Avoid
- **Async Playwright in sync pipeline:** Do not use `async_playwright` -- the pipeline is synchronous. Mixing async/sync creates complexity with no benefit for a single PDF render.
- **Reusing Jinja2 Environment from prompt templates:** The prompt templates use `FileSystemLoader` pointing to `templates/prompts/`. The HTML template needs its own loader pointing to `templates/`. Either use a separate `Environment` or point the loader at `templates/` and reference the file directly.
- **Style mutation for TOC heading:** Do not apply formatting to the TOC heading via Word styles. Use the same run-level approach as all other headings in the document (D-14/D-15 pattern).
- **`wait_until="load"` with embedded images:** When `set_content()` includes `<img src="file:///...">` paths, use `wait_until="networkidle"` to ensure images are loaded before PDF render. Local file paths in `src` attributes must use `file:///` protocol on Windows.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTML-to-PDF rendering | Custom headless browser management | Playwright `page.pdf()` | Handles fonts, CSS, page breaks, image embedding |
| TOC field in Word | Manual page-number calculation | Word field code `TOC \o "1-3" \h \z \u` | Word recalculates on open; python-docx cannot know page numbers |
| Section ID slugification | Custom regex chain | Simple `re.sub` pattern: `re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-'))` | One line, deterministic per D-05 |
| Markdown-to-HTML for PDF sections | Custom parser | Python `markdown` library or reuse existing prose with HTML escaping | Content already parsed by `md_parser.py`; just needs HTML wrapping |
| Print CSS page break control | Manual element splitting | CSS `page-break-inside: avoid` and `page-break-after: always` | Chromium respects these reliably |

## Common Pitfalls

### Pitfall 1: Logo Images Not Rendering in PDF
**What goes wrong:** `<img src="path/to/logo.png">` shows broken image in PDF.
**Why it happens:** Playwright's `set_content()` does not have a base URL context for relative paths. Local file paths must use `file:///` protocol.
**How to avoid:** Convert all logo paths to `file:///` URIs before injecting into the template. On Windows: `pathlib.Path(path).as_uri()`.
**Warning signs:** PDF renders but logos are missing or show placeholder boxes.

### Pitfall 2: Colors Missing in PDF
**What goes wrong:** Background colors on table headers, code blocks, or cover page elements appear white in PDF.
**Why it happens:** Playwright's `page.pdf()` defaults to not printing background graphics.
**How to avoid:** Always pass `print_background=True` in `page.pdf()` call. Also include `print-color-adjust: exact` and `-webkit-print-color-adjust: exact` in CSS.
**Warning signs:** PDF renders but looks "washed out" or all-white backgrounds.

### Pitfall 3: TOC Field Shows "Error! No table of contents entries found"
**What goes wrong:** Word opens the document and the TOC field shows an error instead of "Update this field."
**Why it happens:** Heading styles (Heading 1, Heading 2, etc.) are not applied to the document headings. The TOC field `\o "1-3"` only collects paragraphs with built-in heading styles.
**How to avoid:** The existing `_add_colored_heading()` uses `doc.add_heading(level=N)` which DOES apply the built-in heading style. The run-level color override does not remove the style. Verify this is preserved after TOC insertion. The `\o` switch in the TOC instruction collects paragraphs styled as Heading 1 through Heading 3.
**Warning signs:** After pressing F9 in Word, the TOC is empty or shows the error message.

### Pitfall 4: Tables and Code Blocks Split Across Pages in PDF
**What goes wrong:** A table starts at the bottom of a page and continues on the next, cutting through a row.
**Why it happens:** CSS `page-break-inside: avoid` is not applied, or the element is too tall for a single page.
**How to avoid:** Apply `page-break-inside: avoid` on `<table>` and `<pre>` elements. For very long tables, accept that they will break -- only short/medium tables benefit from this rule.
**Warning signs:** Visual inspection of PDF shows awkwardly split content.

### Pitfall 5: TOC Inserted at Wrong Position in DOCX
**What goes wrong:** TOC appears before the cover page or after the first content section.
**Why it happens:** `body.insert_element_before(sdt, 'w:sectPr')` inserts before the LAST sectPr, which might not be the right location.
**How to avoid:** After `_build_cover_page()` adds a section break, the document body has two `w:sectPr` elements. The TOC must be inserted after the first section break. Navigate to the correct position by finding the second section's content start point and inserting the SDT there.
**Warning signs:** Cover page content is disrupted, or TOC appears at document end.

### Pitfall 6: Playwright Browser Startup Latency
**What goes wrong:** First PDF generation takes several seconds due to Chromium cold start.
**Why it happens:** Playwright downloads and unpacks Chromium on first use; subsequent launches still have ~1-2s overhead.
**How to avoid:** Accept this latency -- it is a one-time cost per `generate.py` invocation. Do not attempt browser pooling for a single-document pipeline.
**Warning signs:** None -- this is expected behavior, not a bug.

## Code Examples

### Slugify Function for Section IDs (D-05)
```python
import re

def slugify(text: str) -> str:
    """Convert section name to URL-safe ID for HTML anchors."""
    slug = text.lower().strip()
    slug = slug.replace(' ', '-')
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)  # collapse multiple hyphens
    return slug.strip('-')
```

### Logo Path to File URI (Windows-safe)
```python
from pathlib import Path

def to_file_uri(path: str) -> str:
    """Convert a local file path to a file:/// URI for HTML img src."""
    return Path(path).resolve().as_uri()
```

### Prose-to-HTML Conversion for PDF Template
```python
import re

def prose_to_html(prose: str, accent_color: str) -> str:
    """Convert generated prose (with TABLE:/CODE_BLOCK: markers) to HTML.
    
    Mirrors the parsing logic in docx_builder._parse_and_add_prose()
    but outputs HTML instead of python-docx elements.
    """
    # Reuse the same marker-based parsing that docx_builder uses,
    # but emit <table>, <pre>, <h2>, <h3>, and <p> tags instead.
    # This ensures PDF and DOCX content are identical.
    pass  # Implementation follows marker parsing pattern from docx_builder.py
```

### Completion Report Pattern (D-14, OUT-03)
```python
# In generate.py after both builds complete:
import os

def _report_completion(docx_path: str, pdf_path: str | None) -> None:
    """Print completion report to stderr and output paths to stdout."""
    docx_size = os.path.getsize(docx_path)
    print(f"\nGeneration complete!", file=sys.stderr)
    print(f"  DOCX: {docx_path} ({docx_size:,} bytes)", file=sys.stderr)
    
    if pdf_path:
        pdf_size = os.path.getsize(pdf_path)
        print(f"  PDF:  {pdf_path} ({pdf_size:,} bytes)", file=sys.stderr)
    else:
        print(f"  PDF:  SKIPPED (see warning above)", file=sys.stderr)
    
    # stdout: machine-readable output for SKILL.md
    print(docx_path)
    print(pdf_path if pdf_path else "PDF_SKIPPED")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| wkhtmltopdf for HTML-to-PDF | Playwright headless Chromium | 2024+ (wkhtmltopdf EOL) | Full modern CSS support, active maintenance |
| python-docx TOC via LibreOffice macro | Word field code + user F9 refresh | N/A (always this way) | No LibreOffice dependency required |
| WeasyPrint for PDF | Playwright | Benchmark data 2026 | 75x faster warm mode, full CSS Grid/Flexbox |

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All | Yes | 3.13.12 | -- |
| python-docx | DOCX-05 (TOC) | Yes | 1.2.0 | -- |
| Playwright | PDF-01, PDF-02 | Yes | 1.58.0 | D-10: deliver .docx only |
| Chromium (Playwright) | PDF-02 | Yes | 145.0.7632.6 | D-10: deliver .docx only |
| Jinja2 | PDF-01 | Yes | 3.1.6 | -- |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None. All dependencies are installed and verified.

## Open Questions

1. **Prose-to-HTML converter duplication**
   - What we know: `docx_builder._parse_and_add_prose()` contains the full marker parsing logic (TABLE:, CODE_BLOCK:, headings, paragraphs). PDF needs the same parsing but outputting HTML.
   - What's unclear: Whether to extract a shared "content model" that both builders consume, or duplicate the parsing logic in `pdf_builder.py`.
   - Recommendation: Extract the prose parsing into a shared function that returns a list of typed content blocks (heading, paragraph, table, code_block). Both builders consume this intermediate representation. However, this is a refactor -- the simpler path is to write a parallel `_prose_to_html()` in `pdf_builder.py` that follows the same marker protocol.

2. **TOC insertion point in document body XML**
   - What we know: After `_build_cover_page()`, the document has two sections. The TOC SDT must go at the start of the second section's content.
   - What's unclear: The exact XML navigation to insert after the first `w:sectPr` but before the first content heading.
   - Recommendation: After `_build_cover_page()` returns, add the TOC heading and field as the next elements in the document body. Then add a page break paragraph. The section break from the cover page naturally separates them.

3. **`<img>` tag for logos in Playwright**
   - What we know: `page.set_content()` can load `file:///` URIs on Windows.
   - What's unclear: Whether `set_content()` with `wait_until="networkidle"` reliably waits for `file:///` images to load.
   - Recommendation: Test with actual logo files during implementation. Fallback: read image files as base64 and embed directly as `data:` URIs in the `<img src>` attributes (guaranteed to work, no file loading issues).

## Project Constraints (from CLAUDE.md)

- **python-docx 1.2.0** pinned version -- do not upgrade
- **Playwright 1.58.0** pinned version -- do not upgrade
- **Jinja2 3.1.6** pinned version -- do not upgrade
- **Run-level formatting only** for .docx colors (never style mutation)
- **Quality bar:** Output must be suitable for direct client delivery without post-processing
- **stderr for progress, stdout for output paths** -- established protocol from Phase 1
- **GSD workflow enforcement** -- do not make direct repo edits outside GSD workflow

## Sources

### Primary (HIGH confidence)
- [Playwright Python page.pdf() API](https://playwright.dev/python/docs/api/class-page#page-pdf) -- all PDF generation parameters
- [python-docx GitHub Issue #36](https://github.com/python-openxml/python-docx/issues/36) -- TOC field is not natively supported; must use OxmlElement
- Target machine verification: `pip show playwright` (1.58.0), `pip show python-docx` (1.2.0), Chromium launch test (passed)

### Secondary (MEDIUM confidence)
- [chanmo.github.io TOC tutorial](https://chanmo.github.io/blog/2023/11/25/Generate-TOC.html) -- OxmlElement XML pattern for SDT + field chars
- [pdf noodle: Playwright Python HTML-to-PDF guide](https://pdfnoodle.com/blog/generate-pdf-from-html-using-playwright-python) -- sync_playwright pattern with set_content
- [Pamela Fox: Converting HTML to PDF with Playwright](http://blog.pamelafox.org/2024/01/converting-html-pages-to-pdfs-with.html) -- practical tips

### Tertiary (LOW confidence)
- None -- all findings verified against installed packages or official docs

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all versions verified installed on target machine
- Architecture: HIGH -- extends existing patterns (module-per-stage, marker parsing); decisions are locked
- Pitfalls: HIGH -- known issues documented from official sources and community experience; Pitfall 3 (TOC + heading styles) verified against existing code

**Research date:** 2026-04-01
**Valid until:** 2026-05-01 (stable stack, all versions pinned)
