---
phase: quick
plan: 260406-gmd
type: execute
wave: 1
depends_on: []
files_modified:
  - .claude/skills/pbi-docgen/scripts/pdf_builder.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "PDF output renders **bold** as <strong>, *italic* as <em>, `code` as <code> instead of showing raw Markdown syntax"
    - "Table cells in PDF render inline Markdown formatting instead of literal asterisks/backticks"
    - "Existing HTML escaping still prevents XSS — angle brackets and ampersands remain escaped"
  artifacts:
    - path: ".claude/skills/pbi-docgen/scripts/pdf_builder.py"
      provides: "_inline_md_to_html helper and updated _prose_to_html / _table_lines_to_html"
      contains: "_inline_md_to_html"
  key_links:
    - from: "_inline_md_to_html"
      to: "_prose_to_html"
      via: "called on paragraph text instead of bare html_module.escape()"
      pattern: "_inline_md_to_html"
    - from: "_inline_md_to_html"
      to: "_table_lines_to_html"
      via: "called on each cell instead of bare html_module.escape()"
      pattern: "_inline_md_to_html"
---

<objective>
Fix inline Markdown leaking in PDF output. pdf_builder.py's `_prose_to_html()` and `_table_lines_to_html()` currently use bare `html.escape()` on text, which renders **bold**, *italic*, and `code` as literal Markdown syntax in the PDF. Add an `_inline_md_to_html(text)` helper that HTML-escapes first, then converts inline Markdown patterns to HTML tags, and wire it into both functions.

Purpose: PDF deliverables should show formatted text (bold, italic, code), not raw Markdown syntax.
Output: Updated pdf_builder.py with inline Markdown rendering in paragraphs and table cells.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.claude/skills/pbi-docgen/scripts/pdf_builder.py
@.claude/skills/pbi-docgen/scripts/docx_builder.py

<interfaces>
<!-- The INLINE_MD_RE regex from docx_builder.py (lines 35-43) defines the pattern priority.
     Mirror the same groups in _inline_md_to_html but output HTML tags instead of Word runs. -->

From docx_builder.py (line 35-43):
```python
INLINE_MD_RE = re.compile(
    r'\*\*\*(.+?)\*\*\*'          # ***bold+italic***
    r'|___(.+?)___'                # ___bold+italic___
    r'|\*\*(.+?)\*\*'             # **bold**
    r'|__(.+?)__'                  # __bold__
    r'|\*(.+?)\*'                  # *italic*
    r'|(?:(?<=\s)|(?<=^))_(.+?)_(?=[\s.,;:!?\)]|$)'  # _italic_ (word-boundary aware)
    r'|`([^`]+)`'                  # `code`
)
```

Current pdf_builder.py usage that needs replacement:
- Line 96: `output.append(f'<p>{html_module.escape(tl.strip())}</p>')` (fallback single-line table)
- Line 132: `text = html_module.escape(heading_match.group(2).strip())` (sub-headings -- leave as-is, headings should not have inline MD)
- Line 137: `output.append(f'<p>{html_module.escape(line.strip())}</p>')` (regular paragraphs)
- Line 164: `html_parts.append(f'<th>{html_module.escape(cell)}</th>')` (table headers)
- Line 173: `html_parts.append(f'<td>{html_module.escape(cell)}</td>')` (table body cells)
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add _inline_md_to_html helper and wire into _prose_to_html and _table_lines_to_html</name>
  <files>.claude/skills/pbi-docgen/scripts/pdf_builder.py</files>
  <action>
1. Add a compiled INLINE_MD_RE at module level (after the existing imports, around line 22), mirroring docx_builder.py's regex exactly:
   ```python
   INLINE_MD_RE = re.compile(
       r'\*\*\*(.+?)\*\*\*'
       r'|___(.+?)___'
       r'|\*\*(.+?)\*\*'
       r'|__(.+?)__'
       r'|\*(.+?)\*'
       r'|(?:(?<=\s)|(?<=^))_(.+?)_(?=[\s.,;:!?\)]|$)'
       r'|`([^`]+)`'
   )
   ```

2. Add `_inline_md_to_html(text: str) -> str` function (place it before `_prose_to_html`). Logic:
   - First: `html.escape(text)` the entire input (preserves XSS safety)
   - Then: use `INLINE_MD_RE` with a replacement function on the ESCAPED text -- BUT this won't work because escape mangles the asterisks... Actually asterisks and backticks are NOT HTML-special characters, so `html.escape()` does NOT alter them. The approach is:
     a. `html.escape(text)` -- escapes `<`, `>`, `&`, `"`, `'`
     b. Apply regex substitutions in priority order using `re.sub` with a callback that returns the appropriate HTML tag wrapping the matched group (which is already escaped).
   - Use a single `INLINE_MD_RE.sub(replacer, escaped_text)` call where the replacer function checks which group matched:
     - group(1) or group(2) (bold+italic): `<strong><em>{content}</em></strong>`
     - group(3) or group(4) (bold): `<strong>{content}</strong>`
     - group(5) or group(6) (italic): `<em>{content}</em>`
     - group(7) (code): `<code>{content}</code>`

3. In `_prose_to_html()`:
   - Line 96 (fallback table line as paragraph): replace `html_module.escape(tl.strip())` with `_inline_md_to_html(tl.strip())`
   - Line 137 (regular paragraph): replace `html_module.escape(line.strip())` with `_inline_md_to_html(line.strip())`
   - Line 132 (sub-headings): LEAVE as `html_module.escape()` -- headings should not contain inline formatting

4. In `_table_lines_to_html()`:
   - Line 164 (th cells): replace `html_module.escape(cell)` with `_inline_md_to_html(cell)`
   - Line 173 (td cells): replace `html_module.escape(cell)` with `_inline_md_to_html(cell)`

Do NOT remove the `import html as html_module` -- it is still used in code blocks, headings, and inside `_inline_md_to_html` itself.
  </action>
  <verify>
    <automated>cd "C:/Users/DeveshD/Documents/Claude Projects/DocsGen" && python -c "
import sys, os
sys.path.insert(0, '.claude/skills/pbi-docgen')
from scripts.pdf_builder import _inline_md_to_html, _prose_to_html, _table_lines_to_html

# Test _inline_md_to_html
assert _inline_md_to_html('**bold**') == '<strong>bold</strong>', f'bold failed: {_inline_md_to_html(\"**bold**\")}'
assert _inline_md_to_html('*italic*') == '<em>italic</em>', f'italic failed: {_inline_md_to_html(\"*italic*\")}'
assert _inline_md_to_html('\`code\`') == '<code>code</code>', f'code failed: {_inline_md_to_html(\"\`code\`\")}'
assert _inline_md_to_html('***both***') == '<strong><em>both</em></strong>', f'both failed'
assert '&lt;script&gt;' in _inline_md_to_html('<script>alert(1)</script>'), 'XSS not escaped'
assert _inline_md_to_html('plain text') == 'plain text', 'plain text altered'

# Test _prose_to_html renders inline MD in paragraphs
html = _prose_to_html('This is **bold** text', '#4A90D9')
assert '<strong>bold</strong>' in html, f'prose bold failed: {html}'
assert '**bold**' not in html, f'raw MD leaked in prose: {html}'

# Test table cells render inline MD
table_html = _table_lines_to_html(['| Name | **Status** |', '|---|---|', '| foo | *active* |'])
assert '<strong>Status</strong>' in table_html, f'table header bold failed: {table_html}'
assert '<em>active</em>' in table_html, f'table cell italic failed: {table_html}'

print('All assertions passed')
"
    </automated>
  </verify>
  <done>
    - _inline_md_to_html helper exists and converts ***bold+italic***, **bold**, *italic*, _italic_, `code` to proper HTML tags
    - Regular paragraphs in _prose_to_html use _inline_md_to_html instead of bare html.escape
    - Table header and body cells in _table_lines_to_html use _inline_md_to_html instead of bare html.escape
    - HTML special characters (&lt; &gt; &amp;) remain properly escaped (XSS safe)
    - Sub-headings and code blocks still use html.escape (no inline MD in those contexts)
  </done>
</task>

</tasks>

<verification>
Run the inline verification command above. Additionally, confirm no import errors:
```bash
python -c "from scripts.pdf_builder import build_pdf; print('import OK')"
```
</verification>

<success_criteria>
- PDF paragraphs render **bold** as visually bold text, not literal asterisks
- PDF table cells render *italic* as visually italic text, not literal asterisks
- PDF `code` spans render in monospace, not literal backticks
- HTML escaping still prevents injection of raw HTML tags
</success_criteria>

<output>
After completion, create `.planning/quick/260406-gmd-fix-inline-markdown-leaking-in-pdf-build/260406-gmd-SUMMARY.md`
</output>
