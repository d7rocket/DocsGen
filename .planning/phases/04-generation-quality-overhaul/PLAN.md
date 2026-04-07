# Phase 4: Generation Quality Overhaul — Execution Plan

**Phase goal:** Replace two diverged hand-rolled parsers with a single unified Markdown parser (markdown-it-py), fix the Playwright PDF hang, redesign the HTML template to a DigitalOcean-inspired style, and update all prompt templates and the pbi:docs output contract to emit standard Markdown.

---

## Success Criteria (UAT)

1. A prose string containing a fenced code block with interior blank lines renders correctly in both DOCX and PDF — blank lines are preserved, not truncated
2. Pipe tables render identically in DOCX and PDF (correct header shading, column count, alternating rows)
3. Bold (`**text**`) and italic (`*text*`) render as formatted runs — no asterisks leak into output
4. `build_pdf()` completes without hanging — no `networkidle` timeouts
5. PDF visual output matches the DigitalOcean-inspired CSS: left-accent code blocks, distinct heading hierarchy (h1/h2/h3), clean tables with primary-color headers
6. No literal `TABLE:`, `CODE_BLOCK:`, or `END_TABLE` strings appear in DOCX or PDF output after running with updated prompts
7. Both `.claude/skills/pbi-docgen/` and `skills/pbi-docgen/` (repo copy) are in sync after every task

---

## Canonical Sync Rule

Every task that modifies a file under `.claude/skills/pbi-docgen/` **must** also update the corresponding file under `skills/pbi-docgen/`. These two trees must remain identical after each task. This is enforced by including both paths in every task's file list.

---

## Wave Structure

```
Wave 1 (Parser Foundation)
  Plan A: Create md_renderer.py + wire docx_builder
  Plan B: Wire pdf_builder + fix Playwright hang    ← parallel with A only in file scope; B reads A's module

Wave 2 (Prompt Template Updates)
  Plan C: Update all 12 prompt templates (6 EN + 6 FR) to emit standard Markdown

Wave 3 (Visual Polish)
  Plan D: Redesign document.html.j2 (DigitalOcean CSS)
  Plan E: Fix DOCX heading font sizes in docx_builder    ← parallel with D

Wave 4 (pbi:docs Contract + Final Sync)
  Plan F: Update pbi:docs SKILL.md output contract + verify section_heading_map.yaml
```

Wave 1 (Plans A and B) must complete before Wave 2. Wave 2 must complete before end-to-end testing. Wave 3 and Wave 4 are independent of each other and can run after Wave 2 completes.

---

## Wave 1 — Parser Foundation

### Plan A: Create `md_renderer.py` and wire `docx_builder`

**Depends on:** Nothing  
**Wave:** 1

#### Task A1: Create `md_renderer.py` — unified parse entry point

**Files (both paths must be written):**
- `.claude/skills/pbi-docgen/scripts/md_renderer.py`
- `skills/pbi-docgen/scripts/md_renderer.py`

**Action:**

Create a new module `md_renderer.py` with two public functions. This module is the single parse entry point for the entire pipeline.

```python
# md_renderer.py
from markdown_it import MarkdownIt

_MD = MarkdownIt('commonmark').enable('table')

def parse_prose(text: str) -> list:
    """Parse Markdown prose into a markdown-it-py token list.
    Returns flat list of block-level tokens; inline tokens nested
    as .children on 'inline' tokens. Do NOT cache or mutate returned tokens."""
    return _MD.parse(text)

def render_prose_html(text: str) -> str:
    """Render Markdown prose directly to an HTML string.
    Pass RAW prose — do NOT pre-escape. markdown-it-py handles escaping internally.
    Used by pdf_builder to replace _prose_to_html()."""
    return _MD.render(text)
```

The module-level `_MD` instance is initialized once at import time with `'commonmark'` preset and `'table'` plugin enabled. Do NOT add plugins inside `parse_prose()` or `render_prose_html()` — always initialize at module level.

**Verify:** `python -c "from scripts.md_renderer import parse_prose, render_prose_html; toks = parse_prose('## Hello\n\n```\nline1\n\nline2\n```\n\n| A | B |\n|---|---|\n| x | y |'); print([t.type for t in toks])"` — output must include `heading_open`, `fence`, `table_open`; the fence token's `.content` must contain the interior blank line. Run from `.claude/skills/pbi-docgen/`.

**Done:** `md_renderer.py` exists in both locations. `parse_prose()` returns a token list where a fenced code block with interior blank lines produces a single `fence` token whose `.content` includes the blank line. `render_prose_html()` returns a valid HTML string from a prose string containing a table, code block, and heading.

---

#### Task A2: Replace `_parse_and_add_prose()` in `docx_builder.py` with token-walker

**Files (both paths must be written):**
- `.claude/skills/pbi-docgen/scripts/docx_builder.py`
- `skills/pbi-docgen/scripts/docx_builder.py`

**Action:**

In `docx_builder.py`, make the following targeted changes:

1. **Add import at top of file:**
   ```python
   from scripts.md_renderer import parse_prose
   ```

2. **Add new helper `_inline_children_to_text(children)`** — extracts plain text from inline token children (used for heading text):
   ```python
   def _inline_children_to_text(children: list) -> str:
       parts = []
       for child in children:
           if child.type in ('text', 'code_inline', 'softbreak'):
               parts.append(child.content if child.type != 'softbreak' else ' ')
       return ''.join(parts)
   ```

3. **Add new helper `_render_inline_children_to_runs(para, children)`** — replaces `_parse_inline_runs` for the token-walker path (keep `_parse_inline_runs` in place — it is still used by `_add_inline_md_paragraph` which handles the cover page and other non-prose paragraphs):
   ```python
   def _render_inline_children_to_runs(para, children: list, code_style=None) -> None:
       bold = False
       italic = False
       for child in children:
           if child.type == 'strong_open':
               bold = True
           elif child.type == 'strong_close':
               bold = False
           elif child.type == 'em_open':
               italic = True
           elif child.type == 'em_close':
               italic = False
           elif child.type == 'code_inline':
               run = para.add_run(child.content)
               run.font.name = 'Courier New'
               run.font.size = Pt(9)
               run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
           elif child.type == 'text':
               run = para.add_run(child.content)
               if bold:
                   run.font.bold = True
               if italic:
                   run.font.italic = True
           elif child.type == 'softbreak':
               para.add_run(' ')
   ```

4. **Add new helper `_collect_table_rows_from_tokens(tokens, start)`** — collects table row data from the token stream starting at a `table_open` token. Returns `(rows, consumed)` where `rows` is a list of lists of strings and `consumed` is the number of tokens to advance:
   ```python
   def _collect_table_rows_from_tokens(tokens: list, start: int):
       rows = []
       current_row = []
       i = start + 1  # skip table_open
       consumed = 1
       while i < len(tokens):
           tok = tokens[i]
           consumed += 1
           if tok.type == 'table_close':
               if current_row:
                   rows.append(current_row)
               break
           elif tok.type in ('thead_open', 'tbody_open', 'thead_close', 'tbody_close'):
               pass
           elif tok.type == 'tr_open':
               current_row = []
           elif tok.type == 'tr_close':
               if current_row:
                   rows.append(current_row)
               current_row = []
           elif tok.type in ('th_open', 'td_open'):
               pass
           elif tok.type == 'inline':
               cell_text = _inline_children_to_text(tok.children or [])
               current_row.append(cell_text)
           i += 1
       return rows, consumed
   ```

5. **Replace `_parse_and_add_prose()` entirely** with the new token-walker version:
   ```python
   def _parse_and_add_prose(doc: Document, prose_text: str, primary_color: str,
                            accent_color: str, code_style) -> None:
       """Parse generated Markdown prose and add content to the document.

       Uses md_renderer.parse_prose() (markdown-it-py token stream) to handle:
       - Fenced code blocks (including those with interior blank lines)
       - Pipe tables
       - Headings (##, ###)
       - Paragraphs with bold/italic/code inline formatting
       """
       tokens = parse_prose(prose_text)
       i = 0
       while i < len(tokens):
           tok = tokens[i]

           if tok.type == 'fence':
               for line in tok.content.splitlines():
                   para = doc.add_paragraph(line, style=code_style)
                   _set_paragraph_shading(para, 'F2F2F2')
                   _add_paragraph_border(para)
               i += 1

           elif tok.type == 'heading_open':
               level = int(tok.tag[1])  # 'h2' -> 2, 'h3' -> 3
               inline_tok = tokens[i + 1]
               text = _inline_children_to_text(inline_tok.children or [])
               _add_colored_heading(doc, text, level, primary_color)
               i += 3  # heading_open + inline + heading_close

           elif tok.type == 'table_open':
               rows, consumed = _collect_table_rows_from_tokens(tokens, i)
               _add_table(doc, rows, primary_color, accent_color, code_style)
               i += consumed

           elif tok.type == 'paragraph_open':
               inline_tok = tokens[i + 1]
               para = doc.add_paragraph()
               _render_inline_children_to_runs(para, inline_tok.children or [], code_style)
               i += 3  # paragraph_open + inline + paragraph_close

           elif tok.type == 'bullet_list_open':
               # Walk list items until bullet_list_close
               i += 1
               while i < len(tokens) and tokens[i].type != 'bullet_list_close':
                   t = tokens[i]
                   if t.type == 'inline':
                       try:
                           para = doc.add_paragraph(style='List Bullet')
                       except KeyError:
                           para = doc.add_paragraph()
                       _render_inline_children_to_runs(para, t.children or [], code_style)
                   i += 1
               i += 1  # consume bullet_list_close

           else:
               i += 1
   ```

6. **Update `_add_table()`** to accept string rows from the token collector (the signature is unchanged; the function already handles `list[list[str]]` — verify this still holds with token-derived rows, which will be plain strings without pipe characters).

The old `TABLE:` / `CODE_BLOCK:` / `END_TABLE` detection branches in the previous `_parse_and_add_prose()` are removed entirely by this replacement.

**Verify:**
```python
# Run from .claude/skills/pbi-docgen/ directory
python -c "
import sys; sys.path.insert(0, '.')
from scripts.docx_builder import _parse_and_add_prose, _create_code_style
from docx import Document

doc = Document()
cs = _create_code_style(doc)
prose = '''## Sub Heading

**Bold text** and *italic* here.

\`\`\`
let
    Source = ...,

    Step2 = ...
in
    Step2
\`\`\`

| Col A | Col B |
|-------|-------|
| val1  | val2  |
| val3  | val4  |
'''
_parse_and_add_prose(doc, prose, '#1B365D', '#4A90D9', cs)
doc.save('/tmp/test_a2.docx')
print('OK')
"
```
Output must be `OK` with no exceptions. Open `test_a2.docx` and confirm: heading renders as Heading 2 with color, code block has all lines including the blank line, table has header row with primary color background, bold/italic are formatted runs.

**Done:** `_parse_and_add_prose()` no longer contains any `TABLE:`, `CODE_BLOCK:`, `END_TABLE` string checks. Fenced code blocks with interior blank lines produce all lines in the DOCX. `_parse_inline_runs` and `_add_inline_md_paragraph` are retained (still used outside this function). Both file paths updated.

---

### Plan B: Wire `pdf_builder.py` + fix Playwright hang

**Depends on:** Plan A (Task A1 must exist — `md_renderer.py` must be present)  
**Wave:** 1

#### Task B1: Replace `_prose_to_html()` and fix `wait_until` in `pdf_builder.py`

**Files (both paths must be written):**
- `.claude/skills/pbi-docgen/scripts/pdf_builder.py`
- `skills/pbi-docgen/scripts/pdf_builder.py`

**Action:**

Make the following targeted changes to `pdf_builder.py`:

1. **Add import at top of file (after existing imports):**
   ```python
   from scripts.md_renderer import render_prose_html
   ```

2. **Remove `INLINE_MD_RE` regex** (lines 25–33 in current file) — no longer needed in pdf_builder since HTML rendering is delegated to md_renderer. Keep the import block intact.

3. **Remove `_inline_md_to_html()` function** (lines 54–88) — replaced by md_renderer.

4. **Remove `_table_lines_to_html()` function** (lines 192–227) — replaced by md_renderer.

5. **Replace `_prose_to_html()` entirely** with a one-liner delegation:
   ```python
   def _prose_to_html(prose_text: str, accent_color: str = '') -> str:
       """Convert Markdown prose to HTML string using unified md_renderer.
       accent_color parameter retained for API compatibility but unused —
       CSS handles color via --accent custom property."""
       return render_prose_html(prose_text)
   ```
   The `accent_color` parameter is kept to avoid changing the call site at line 259 (`_prose_to_html(prose, accent_color)`).

6. **Fix `wait_until` bug** in `build_pdf()` at line 322:
   Change:
   ```python
   page.set_content(html_content, wait_until="networkidle")
   ```
   To:
   ```python
   page.set_content(html_content, wait_until="domcontentloaded")
   ```

7. **Add `PlaywrightError` catch** around the Playwright block in `build_pdf()`:
   ```python
   from playwright.sync_api import sync_playwright, Error as PlaywrightError
   # ...
   try:
       with sync_playwright() as p:
           browser = p.chromium.launch()
           page = browser.new_page()
           page.set_content(html_content, wait_until='domcontentloaded')
           page.pdf(
               path=pdf_path,
               format='Letter',
               print_background=True,
               margin={'top': '20mm', 'bottom': '20mm', 'left': '15mm', 'right': '15mm'},
           )
           browser.close()
   except PlaywrightError as e:
       raise RuntimeError(
           f"Playwright PDF generation failed: {e}\n"
           "Run 'playwright install chromium' if browsers are not installed."
       ) from e
   ```

**Verify:**
```python
# Run from .claude/skills/pbi-docgen/ directory
python -c "
import sys; sys.path.insert(0, '.')
from scripts.pdf_builder import _prose_to_html

prose = '''## Sub Heading

**Bold** and *italic*.

\`\`\`dax
CALCULATE(
    SUM(Sales[Amount]),

    FILTER(ALL(Date), Date[Year] = 2024)
)
\`\`\`

| A | B |
|---|---|
| x | y |
'''
html = _prose_to_html(prose)
assert '<h2>' in html, 'Missing h2'
assert '<strong>' in html, 'Missing strong'
assert '<pre>' in html, 'Missing pre'
assert '<table>' in html, 'Missing table'
# Blank line inside code block must be preserved
assert 'FILTER' in html, 'Code content lost'
print('OK:', len(html), 'chars')
"
```
Output must be `OK` with a character count. No `TABLE:` or `CODE_BLOCK:` strings in the output HTML.

**Done:** `pdf_builder.py` no longer contains `INLINE_MD_RE`, `_inline_md_to_html()`, `_table_lines_to_html()`, or the hand-rolled `_prose_to_html()` logic. `wait_until` is `'domcontentloaded'`. `PlaywrightError` is caught with a helpful message. Both file paths updated.

---

## Wave 2 — Prompt Template Updates

### Plan C: Update all 12 prompt templates to emit standard Markdown

**Depends on:** Plans A and B (parsers now accept standard Markdown — old markers must be removed atomically)  
**Wave:** 2

#### Task C1: Update mquery and dataflows templates (EN + FR) — most code-heavy sections

**Files (both paths for each template):**
- `.claude/skills/pbi-docgen/templates/prompts/section_mquery.j2`
- `skills/pbi-docgen/templates/prompts/section_mquery.j2`
- `.claude/skills/pbi-docgen/templates/prompts/section_mquery_fr.j2`
- `skills/pbi-docgen/templates/prompts/section_mquery_fr.j2`
- `.claude/skills/pbi-docgen/templates/prompts/section_dataflows.j2`
- `skills/pbi-docgen/templates/prompts/section_dataflows.j2`
- `.claude/skills/pbi-docgen/templates/prompts/section_dataflows_fr.j2`
- `skills/pbi-docgen/templates/prompts/section_dataflows_fr.j2`

**Action:**

For each template, remove all `CODE_BLOCK:` / `END_CODE_BLOCK` / `TABLE:` / `END_TABLE` instructions and replace with standard Markdown instructions.

**`section_mquery.j2` — replace the `{% else %}` block's code formatting instruction:**

Current text (lines 20–27):
```
Format code blocks with CODE_BLOCK markers:
CODE_BLOCK:
```
// annotated M code here
```

This tells the document builder to use code formatting (Courier New, grey background).
```

Replace with:
```
Format M Query code using standard fenced code blocks with the `m` language tag:
```m
// annotated M code here
```
This produces code formatting (monospace font, grey background) in the output document.
```

Apply the same pattern to `section_mquery_fr.j2` — find the equivalent French instruction block and replace `CODE_BLOCK:` / `END_CODE_BLOCK` references with the fenced code block instruction.

For `section_dataflows.j2` and `section_dataflows_fr.j2`:
- Find any instructions that say `CODE_BLOCK:` or `TABLE:` markers and replace with: fenced code blocks using ` ```m ` for M Query code, standard pipe table format (`| Col | Col |`) for tabular data
- If no such markers exist in dataflows templates, add a clarifying line: "Use standard Markdown: fenced code blocks for code, pipe tables for structured data."

**General rule for all replacements:**
- Remove: any text containing `CODE_BLOCK:`, `END_CODE_BLOCK`, `TABLE:`, `END_TABLE`
- Add: "Use standard Markdown fenced code blocks (` ```m ` for M Query, ` ```dax ` for DAX). Use pipe tables for structured data."
- The final instruction in every template must end with: "Write the section body only. No heading, no numbering."

**Verify:** 
```bash
grep -r "CODE_BLOCK\|END_TABLE\|END_CODE" ".claude/skills/pbi-docgen/templates/prompts/section_mquery.j2" ".claude/skills/pbi-docgen/templates/prompts/section_mquery_fr.j2" ".claude/skills/pbi-docgen/templates/prompts/section_dataflows.j2" ".claude/skills/pbi-docgen/templates/prompts/section_dataflows_fr.j2"
```
Must return no matches.

**Done:** All four templates (mquery EN/FR, dataflows EN/FR) contain no `CODE_BLOCK:` / `TABLE:` marker instructions. Fenced code block instructions with language tags are present in the `{% else %}` (IT audience) blocks. Both path pairs updated.

---

#### Task C2: Update remaining 4 template pairs (overview, sources, datamodel, maintenance)

**Files (both paths for each):**
- `.claude/skills/pbi-docgen/templates/prompts/section_overview.j2` + `skills/` copy
- `.claude/skills/pbi-docgen/templates/prompts/section_overview_fr.j2` + `skills/` copy
- `.claude/skills/pbi-docgen/templates/prompts/section_sources.j2` + `skills/` copy
- `.claude/skills/pbi-docgen/templates/prompts/section_sources_fr.j2` + `skills/` copy
- `.claude/skills/pbi-docgen/templates/prompts/section_datamodel.j2` + `skills/` copy
- `.claude/skills/pbi-docgen/templates/prompts/section_datamodel_fr.j2` + `skills/` copy
- `.claude/skills/pbi-docgen/templates/prompts/section_maintenance.j2` + `skills/` copy
- `.claude/skills/pbi-docgen/templates/prompts/section_maintenance_fr.j2` + `skills/` copy

**Action:**

Apply the same marker-removal pattern as Task C1 to the remaining four EN/FR template pairs:

For each template file:
1. Search for any occurrence of `CODE_BLOCK:`, `END_CODE_BLOCK`, `TABLE:`, `END_TABLE`
2. If found: remove the marker instruction line and replace with the appropriate standard Markdown instruction (fenced code blocks and/or pipe tables)
3. If not found: add the following sentence at the end of the output instructions (before "Write the section body only."): "Use standard Markdown: pipe tables for structured data, fenced code blocks for any code samples."

The `datamodel` templates are likely to have `TABLE:` marker instructions for the data model relationship tables — replace with standard pipe table format. The `sources` templates may have tabular data about data sources — same treatment.

**Verify:**
```bash
grep -rn "CODE_BLOCK\|END_TABLE\|END_CODE\|TABLE:" ".claude/skills/pbi-docgen/templates/prompts/"
```
Must return zero matches across all prompt template files.

**Done:** All 12 prompt templates (6 EN + 6 FR) contain no `CODE_BLOCK:` / `TABLE:` marker strings. Both path sets updated. A grep for `CODE_BLOCK` across the entire templates/prompts/ directory returns empty.

---

## Wave 3 — Visual Polish

Wave 3 plans D and E are independent of each other and can execute in parallel.

### Plan D: Redesign `document.html.j2` with DigitalOcean-inspired CSS

**Depends on:** Plan B (pdf_builder now passes standard HTML from md_renderer — the template receives clean `<pre><code>`, `<table>`, `<h2>` etc. tags)  
**Wave:** 3

#### Task D1: Full redesign of `document.html.j2`

**Files (both paths):**
- `.claude/skills/pbi-docgen/templates/document.html.j2`
- `skills/pbi-docgen/templates/document.html.j2`

**Action:**

Rewrite the entire `<style>` block in `document.html.j2`. The HTML structure (cover page, TOC, sections) is kept — only CSS changes. Do NOT touch the Jinja2 template variables (`{{ primary_color }}`, `{{ client_name }}`, `{{ sections }}`, etc.) or the HTML skeleton.

Replace the current `<style>` block with:

```css
<style>
  :root {
    --primary: {{ primary_color }};
    --accent: {{ accent_color }};
    --text: #333d47;
    --code-bg: #f3f6f8;
    --code-border: #d6e0ea;
  }

  @page {
    size: Letter;
    margin: 20mm 15mm;
  }

  @media print {
    * { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
    pre { page-break-inside: avoid; }
    table { page-break-inside: avoid; }
    h1, h2, h3 { page-break-after: avoid; }
  }

  body {
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.75;
    color: var(--text);
    margin: 0;
    padding: 0;
  }

  /* ── Cover page ── */
  .cover-page {
    page-break-after: always;
    text-align: center;
    padding-top: 80px;
    min-height: 90vh;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .cover-page .client-logo { max-width: 280px; max-height: 180px; margin-bottom: 48px; }
  .cover-page h1 {
    color: var(--primary);
    font-size: 26pt;
    font-weight: 700;
    margin: 16px 0 8px;
    border: none;
  }
  .cover-page .subtitle { color: var(--primary); font-size: 17pt; font-weight: 400; margin: 0 0 16px; }
  .cover-page .meta { color: #7a8694; font-size: 11pt; margin: 6px 0; }
  .cover-page .company-logo-wrapper { margin-top: auto; align-self: flex-end; padding: 24px; }
  .cover-page .company-logo { max-width: 110px; }

  /* ── Table of Contents ── */
  .toc { page-break-after: always; padding-bottom: 20px; }
  .toc h1 {
    color: var(--primary);
    font-size: 20pt;
    font-weight: 700;
    border-bottom: 2px solid var(--primary);
    padding-bottom: 8px;
    margin-bottom: 24px;
  }
  .toc ul { list-style: none; padding: 0; margin: 0; }
  .toc li { margin: 10px 0; font-size: 11pt; }
  .toc a {
    color: var(--primary);
    text-decoration: none;
    border-bottom: 1px dotted var(--accent);
    padding-bottom: 1px;
  }
  .toc a:hover { color: var(--accent); }

  /* ── Section headings ── */
  h1 {
    color: var(--primary);
    font-size: 22pt;
    font-weight: 700;
    border-bottom: 2px solid var(--primary);
    padding-bottom: 8px;
    margin-top: 32px;
    margin-bottom: 16px;
  }
  h2 {
    color: var(--accent);
    font-size: 15pt;
    font-weight: 600;
    margin-top: 24px;
    margin-bottom: 10px;
  }
  h3 {
    color: var(--text);
    font-size: 12pt;
    font-weight: 600;
    margin-top: 18px;
    margin-bottom: 8px;
  }

  /* ── Paragraphs and lists ── */
  p { margin: 0 0 12px; }
  ul, ol { margin: 0 0 12px; padding-left: 24px; }
  li { margin-bottom: 4px; }

  /* ── Code blocks (DigitalOcean left-accent pattern) ── */
  pre {
    background: var(--code-bg);
    border: 1px solid var(--code-border);
    border-left: 4px solid var(--accent);
    border-radius: 0 4px 4px 0;
    padding: 14px 18px;
    font-size: 9pt;
    line-height: 1.55;
    page-break-inside: avoid;
    margin: 16px 0;
    overflow-x: auto;
    white-space: pre;
  }
  code {
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
  }
  p code, li code, td code {
    background: var(--code-bg);
    border: 1px solid var(--code-border);
    border-radius: 3px;
    padding: 1px 5px;
    font-size: 9pt;
  }

  /* ── Tables ── */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    page-break-inside: avoid;
    font-size: 10pt;
  }
  th {
    background: var(--primary);
    color: white;
    padding: 9px 14px;
    text-align: left;
    font-size: 10pt;
    font-weight: 600;
  }
  td {
    padding: 8px 14px;
    border-bottom: 1px solid #e2e8ef;
    vertical-align: top;
  }
  tr:nth-child(even) td { background: #f9fafb; }
  tr:last-child td { border-bottom: none; }
</style>
```

Keep all existing HTML structure outside the `<style>` block unchanged.

**Verify:**
```python
# Run from .claude/skills/pbi-docgen/ directory
python -c "
import sys; sys.path.insert(0, '.')
from scripts.pdf_builder import _render_html

sections = {'overview': {'prose': '## Background\n\n**Bold text**.\n\n\`\`\`dax\nSUM(Sales[Amount])\n\`\`\`\n\n| Col | Val |\n|-----|-----|\n| A   | 1   |'}}
config = {'primary_color': '#1B365D', 'accent_color': '#4A90D9', 'client_name': 'Test', 'report_name': 'Report', 'version': '1.0', 'language': 'EN'}
html = _render_html(sections, config)
assert 'border-left: 4px solid var(--accent)' in html, 'Missing left-accent border'
assert 'line-height: 1.75' in html, 'Missing line-height'
assert 'Cascadia Code' in html, 'Missing monospace font'
assert '--code-bg' in html, 'Missing code-bg variable'
print('CSS checks OK')
"
```

**Done:** `document.html.j2` has the new CSS with `--code-bg`, `--code-border` variables, `line-height: 1.75`, `border-left: 4px solid var(--accent)` on `pre`, `font-size: 22pt` on body `h1`, `font-size: 15pt` on `h2`. Both path copies updated.

---

### Plan E: Fix DOCX heading font sizes in `docx_builder.py`

**Depends on:** Plan A (Task A2 complete — `_add_colored_heading` is already wired)  
**Wave:** 3 (parallel with Plan D)

#### Task E1: Add explicit font sizes to `_add_colored_heading()` and fix code block left border

**Files (both paths):**
- `.claude/skills/pbi-docgen/scripts/docx_builder.py`
- `skills/pbi-docgen/scripts/docx_builder.py`

**Action:**

1. **Update `_add_colored_heading()`** to set explicit font sizes per level (per D-15). Find the function at line ~199 and add size-setting logic after the existing `run.font.color.rgb` line:

   ```python
   def _add_colored_heading(doc: Document, text: str, level: int, color_hex: str):
       heading = doc.add_heading(level=level)
       run = heading.add_run(text)
       r, g, b = parse_hex_color(color_hex)
       run.font.color.rgb = RGBColor(r, g, b)
       # Explicit sizes — never rely on built-in heading style defaults (Pitfall 4)
       sizes = {1: 20, 2: 14, 3: 12, 4: 11}
       run.font.size = Pt(sizes.get(level, 11))
       if level == 1:
           run.font.bold = True
       return heading
   ```

2. **Update `_add_paragraph_border()`** to use a left-only accent border for code blocks (matching the DigitalOcean aesthetic in the PDF). Replace the four-sided border with a left-only border using the accent color:

   Change the function signature to accept an optional `left_only` parameter:
   ```python
   def _add_paragraph_border(paragraph, color_hex: str = "D0D0D0", left_only: bool = False) -> None:
   ```
   And update the XML construction:
   ```python
   if left_only:
       borders_xml = (
           f'<w:pBdr {nsdecls("w")}>'
           f'  <w:left w:val="single" w:sz="12" w:space="4" w:color="{color_clean}"/>'
           f'</w:pBdr>'
       )
   else:
       borders_xml = (
           f'<w:pBdr {nsdecls("w")}>'
           f'  <w:top w:val="single" w:sz="4" w:space="4" w:color="{color_clean}"/>'
           f'  <w:left w:val="single" w:sz="4" w:space="4" w:color="{color_clean}"/>'
           f'  <w:bottom w:val="single" w:sz="4" w:space="4" w:color="{color_clean}"/>'
           f'  <w:right w:val="single" w:sz="4" w:space="4" w:color="{color_clean}"/>'
           f'</w:pBdr>'
       )
   pPr = paragraph._element.get_or_add_pPr()
   borders = parse_xml(borders_xml)
   pPr.append(borders)
   ```

3. **Update code block rendering in `_parse_and_add_prose()`** (the `fence` token handler from Task A2) to call `_add_paragraph_border(para, accent_color, left_only=True)`. This requires passing `accent_color` into the fence handler — update the fence block inside `_parse_and_add_prose()`:
   ```python
   if tok.type == 'fence':
       for line in tok.content.splitlines():
           para = doc.add_paragraph(line, style=code_style)
           _set_paragraph_shading(para, 'F2F2F2')
           _add_paragraph_border(para, accent_color.lstrip('#'), left_only=True)
       i += 1
   ```

**Verify:**
```python
python -c "
import sys; sys.path.insert(0, '.')
from scripts.docx_builder import _add_colored_heading, _parse_and_add_prose, _create_code_style
from docx import Document
from docx.shared import Pt

doc = Document()
cs = _create_code_style(doc)

h1 = _add_colored_heading(doc, 'Top Heading', 1, '#1B365D')
h2 = _add_colored_heading(doc, 'Sub Heading', 2, '#4A90D9')
h3 = _add_colored_heading(doc, 'Sub-Sub', 3, '#1B365D')

assert h1.runs[0].font.size == Pt(20), f'h1 size wrong: {h1.runs[0].font.size}'
assert h2.runs[0].font.size == Pt(14), f'h2 size wrong: {h2.runs[0].font.size}'
assert h3.runs[0].font.size == Pt(12), f'h3 size wrong: {h3.runs[0].font.size}'

print('Heading sizes OK')
"
```

**Done:** `_add_colored_heading()` applies `Pt(20)` to h1, `Pt(14)` to h2, `Pt(12)` to h3. Code blocks in DOCX use a left-only accent border. Both file paths updated.

---

## Wave 4 — pbi:docs Contract + Final Sync

### Plan F: Update pbi:docs SKILL.md output contract

**Depends on:** Plans C, D, E (all pipeline changes complete — now safe to update the upstream contract)  
**Wave:** 4

#### Task F1: Add Markdown output requirements to pbi:docs SKILL.md

**Files:**
- `skills/pbi-docgen/SKILL.md` — this is the repo copy used at runtime for pbi:docs (check path; if pbi:docs lives at a different location, update accordingly)

**Note:** The pbi:docs skill lives separately from this repo. This task updates the DocsGen project's documentation of the required pbi:docs contract. If pbi:docs SKILL.md is not directly accessible in this repo, create a file `references/pbi-docs-contract.md` documenting the required output format instead.

**Action:**

Locate the pbi:docs SKILL.md (likely at `~/.claude/skills/pbi-docs/SKILL.md` on the runtime system, but the repo copy may be at `skills/pbi-docs/SKILL.md` if present). If the file exists in this repo:

Find the section that describes Markdown output format (likely in "Step 4" or "Output Format"). Add the following requirements after the existing format description:

```markdown
### Markdown Output Requirements (for docgen compatibility)

All code samples must use fenced code blocks with language tags:
- DAX expressions: ```dax
- M Query / Power Query expressions: ```m
- SQL: ```sql
- Generic code: ```

Tabular data (measure tables, source lists, relationship tables) must use standard pipe table format:
```
| Column A | Column B |
|----------|----------|
| value    | value    |
```

Do NOT use custom markers. Standard Markdown only.
```

If pbi:docs SKILL.md is not in this repo, create `.planning/references/pbi-docs-contract.md` with the above contract specification and a note that it must be applied manually to the pbi:docs skill.

**Verify:** The updated SKILL.md (or contract reference file) contains the strings ` ```dax ` and ` ```m ` and "pipe table" with no `CODE_BLOCK:` or `TABLE:` instructions.

**Done:** pbi:docs output contract is documented with language-tagged fenced code block requirements. File exists at either the SKILL.md path or the fallback reference path.

---

#### Task F2: Verify `section_heading_map.yaml` and run end-to-end sync check

**Files:**
- `.claude/skills/pbi-docgen/references/section_heading_map.yaml` (read-only verify — no change expected)
- Both skill trees must be in sync after this task

**Action:**

1. **Audit `section_heading_map.yaml`** — open the file and verify the keyword list for each section still covers the headings that pbi:docs actually emits. The current keywords (`"query"`, `"measure"`, `"dax"`, `"table"`, `"source"`, etc.) are intentionally broad — they should survive any language-tag additions to pbi:docs. If a keyword needs updating, update it in both `.claude/skills/pbi-docgen/references/section_heading_map.yaml` and `skills/pbi-docgen/references/section_heading_map.yaml`.

2. **Run sync verification** — confirm both skill trees are identical:
   ```bash
   diff -r ".claude/skills/pbi-docgen/scripts/" "skills/pbi-docgen/scripts/" --exclude="*.pyc" --exclude="__pycache__"
   diff -r ".claude/skills/pbi-docgen/templates/" "skills/pbi-docgen/templates/"
   diff -r ".claude/skills/pbi-docgen/references/" "skills/pbi-docgen/references/"
   ```
   All diffs must be empty. If any diff shows divergence, copy the `.claude/` version to the `skills/` location (`.claude/` is the authoritative runtime copy; `skills/` is the repo copy).

3. **Run final end-to-end smoke test:**
   ```python
   # Run from repo root or .claude/skills/pbi-docgen/
   python -c "
   import sys; sys.path.insert(0, '.claude/skills/pbi-docgen')
   from scripts.docx_builder import build_docx
   from scripts.pdf_builder import _render_html

   sections = {
       'overview': {'prose': '## Background\n\n**Bold** and *italic* text.\n\n\`\`\`dax\nCALCULATE(\n    SUM(Sales[Amount]),\n\n    FILTER(ALL(Date), Date[Year] = 2024)\n)\n\`\`\`\n\n| Measure | Description |\n|---------|-------------|\n| Total Sales | Sum of all sales |\n| YTD Sales | Year-to-date sales |'},
       'sources': {'prose': 'Data comes from the sales database.'}
   }
   config = {
       'client_name': 'Test Client',
       'report_name': 'Test Report',
       'primary_color': '#1B365D',
       'accent_color': '#4A90D9',
       'version': '1.0',
       'output_dir': 'docsgen-output',
       'language': 'EN',
       'client_logo': '',
       'company_logo': ''
   }

   docx_path = build_docx(sections, config)
   print(f'DOCX OK: {docx_path}')
   html = _render_html(sections, config)
   assert 'border-left: 4px solid var(--accent)' in html
   assert '<pre>' in html
   assert '<table>' in html
   assert 'CODE_BLOCK' not in html
   print('HTML OK')
   "
   ```
   Both assertions must pass. No `CODE_BLOCK` in HTML output.

**Done:** `section_heading_map.yaml` verified (updated if needed). Both skill trees are identical (diff returns empty). End-to-end smoke test produces a DOCX file and valid HTML with no marker artifacts.

---

## Verification Summary

| Check | Command / Action | Expected Result |
|-------|-----------------|-----------------|
| md_renderer module | `python -c "from scripts.md_renderer import parse_prose, render_prose_html"` | No import error |
| Code block blank lines | Parse fenced block with interior blank line | `tok.content` preserves blank line |
| DOCX token walker | Run `_parse_and_add_prose()` with code+table+heading | No exception, valid DOCX |
| PDF prose delegation | Call `_prose_to_html()` on prose with table | Returns `<table>` HTML |
| Playwright hang fix | `wait_until` in `build_pdf()` | `'domcontentloaded'` not `'networkidle'` |
| No legacy markers | `grep -r "CODE_BLOCK" templates/prompts/` | Zero matches |
| No legacy markers in code | `grep -r "CODE_BLOCK\|END_TABLE" scripts/` | Zero matches |
| HTML template CSS | `_render_html()` output | Contains `border-left: 4px solid var(--accent)` |
| DOCX heading sizes | `h1.runs[0].font.size` | `Pt(20)` |
| Skill sync | `diff -r .claude/skills/ skills/ --exclude=*.pyc` | Empty diff |

---

## File Change Summary

| File | Change Type | Wave |
|------|-------------|------|
| `scripts/md_renderer.py` | **NEW** | 1A |
| `scripts/docx_builder.py` | Replace `_parse_and_add_prose()`, add 3 helpers, fix heading sizes, update code border | 1A + 3E |
| `scripts/pdf_builder.py` | Replace `_prose_to_html()`, remove regex, fix `wait_until`, add error handling | 1B |
| `templates/prompts/section_mquery.j2` | Remove CODE_BLOCK marker instructions | 2C |
| `templates/prompts/section_mquery_fr.j2` | Mirror EN changes | 2C |
| `templates/prompts/section_dataflows.j2` | Remove CODE_BLOCK/TABLE marker instructions | 2C |
| `templates/prompts/section_dataflows_fr.j2` | Mirror EN changes | 2C |
| `templates/prompts/section_overview.j2` | Remove/clarify marker instructions | 2C |
| `templates/prompts/section_overview_fr.j2` | Mirror EN changes | 2C |
| `templates/prompts/section_sources.j2` | Remove/clarify marker instructions | 2C |
| `templates/prompts/section_sources_fr.j2` | Mirror EN changes | 2C |
| `templates/prompts/section_datamodel.j2` | Remove TABLE marker instructions | 2C |
| `templates/prompts/section_datamodel_fr.j2` | Mirror EN changes | 2C |
| `templates/prompts/section_maintenance.j2` | Remove/clarify marker instructions | 2C |
| `templates/prompts/section_maintenance_fr.j2` | Mirror EN changes | 2C |
| `templates/document.html.j2` | Full CSS redesign (DigitalOcean style) | 3D |
| `references/section_heading_map.yaml` | Verify only (update if needed) | 4F |
| pbi:docs SKILL.md or contract reference | Add language-tagged code fence requirement | 4F |

**All changes apply to both `.claude/skills/pbi-docgen/` and `skills/pbi-docgen/` copies.**

---

## Decision Traceability

| Decision | Implemented By |
|----------|---------------|
| D-01: Switch to standard Markdown output | Tasks C1, C2 (prompt templates) |
| D-02: Parse with real Markdown library (markdown-it-py) | Task A1 (`md_renderer.py`) |
| D-03: Unified parser → dual renderers | Tasks A1, A2, B1 |
| D-04: Prompt templates request standard Markdown | Tasks C1, C2 |
| D-05: Fix Playwright crash | Task B1 (`wait_until` fix) |
| D-06: Fix broken PDF layout | Task B1 (unified HTML renderer) |
| D-07: Fix blank-line code block truncation | Task A2 (fence token handler) |
| D-08: DigitalOcean HTML template redesign | Task D1 |
| D-09: Keep CSS custom properties pattern | Task D1 (--primary/--accent preserved) |
| D-10: pbi:docs language-tagged fenced blocks | Task F1 |
| D-11: Verify section_heading_map.yaml | Task F2 |
| D-12: DOCX code block monospace + no truncation | Task A2 |
| D-13: DOCX table header color + alternating rows | Task A2 (via `_add_table()`) |
| D-14: Bold/italic accuracy via real parser | Task A2 (`_render_inline_children_to_runs`) |
| D-15: Heading hierarchy with distinct font sizes | Task E1 |
