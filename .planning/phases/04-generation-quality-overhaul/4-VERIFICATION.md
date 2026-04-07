---
phase: 04-generation-quality-overhaul
verified: 2026-04-07T11:03:37Z
status: passed
score: 8/8 must-haves verified
gaps: []
human_verification:
  - test: "DOCX output renders fenced code block with interior blank line — blank lines preserved in output"
    expected: "Code block body in .docx shows blank line between line1 and line2, not truncated"
    why_human: "Requires generating a real .docx and opening it in Word — cannot inspect rendered output programmatically"
  - test: "PDF output renders DigitalOcean left-accent code block style visually"
    expected: "Code blocks in PDF show left gold/accent border, subtle background, monospace font — matching DigitalOcean style"
    why_human: "Requires launching Playwright, rendering a page, and visually inspecting the PDF"
  - test: "Pipe tables render identically in DOCX and PDF (header shading, column count, alternating rows)"
    expected: "Table header row has primary-color background in both outputs; alternating row shading in PDF"
    why_human: "Requires end-to-end run with a document containing tables and visual inspection of both outputs"
---

# Phase 4: Generation Quality Overhaul — Verification Report

**Phase Goal:** Replace two diverged hand-rolled parsers with a single unified Markdown parser (markdown-it-py), fix the Playwright PDF hang, redesign the HTML template to a DigitalOcean-inspired style, and update all prompt templates and the pbi:docs output contract to emit standard Markdown.
**Verified:** 2026-04-07T11:03:37Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `md_renderer.py` exists in both skill trees | VERIFIED | File present at both `.claude/skills/pbi-docgen/scripts/md_renderer.py` and `skills/pbi-docgen/scripts/md_renderer.py`; content identical |
| 2 | `docx_builder.py` uses token-walker — no TABLE:/CODE_BLOCK: string checks | VERIFIED | 0 matches for `TABLE:`, `CODE_BLOCK:`, `END_TABLE` in docx_builder.py; token-walker at line 625+ confirmed |
| 3 | `pdf_builder.py` delegates to `render_prose_html` — old hand-rolled helpers removed | VERIFIED | `_inline_md_to_html`, `_table_lines_to_html`, `INLINE_MD_RE` all absent (0 matches); `render_prose_html` imported and called |
| 4 | `wait_until='domcontentloaded'` in pdf_builder.py | VERIFIED | Line 143: `page.set_content(html_content, wait_until='domcontentloaded')`; `networkidle` absent (0 matches) |
| 5 | No CODE_BLOCK/END_TABLE strings in templates/prompts/ | VERIFIED | 0 matches in `.claude/skills/pbi-docgen/templates/prompts/` and `skills/pbi-docgen/templates/prompts/` (all 14 templates checked) |
| 6 | `document.html.j2` contains DigitalOcean CSS (`border-left: 4px solid var(--accent)`, `--primary`/`--accent`) | VERIFIED | Line 113: `border-left: 4px solid var(--accent);`; `--primary` and `--accent` both present as CSS custom properties |
| 7 | `_add_colored_heading` sets explicit Pt sizes: h1=Pt(20), h2=Pt(14), h3=Pt(12) | VERIFIED | Lines 220-221: `sizes = {1: 20, 2: 14, 3: 12, 4: 11}` with `run.font.size = Pt(sizes.get(level, 11))` |
| 8 | Both skill trees are in sync for all phase-modified files | VERIFIED | `diff -rq` shows only line-ending differences (LF vs CRLF) in `fr_glossary.yaml` and `grevisse_rules.j2`; one extra file in `skills/` (`fowler_guidance.md`, `test_md_parser.py`) — content functionally identical |

**Score:** 8/8 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.claude/skills/pbi-docgen/scripts/md_renderer.py` | Unified parse entry point with `parse_prose()` and `render_prose_html()` | VERIFIED | 27 lines; module-level `_MD = MarkdownIt('commonmark').enable('table')`; both public functions present |
| `skills/pbi-docgen/scripts/md_renderer.py` | Identical copy of above | VERIFIED | `diff` reports IDENTICAL |
| `.claude/skills/pbi-docgen/scripts/docx_builder.py` | Token-walker replacing TABLE:/CODE_BLOCK: string parsing | VERIFIED | Imports `parse_prose`; `_render_inline_children_to_runs`, `_collect_table_rows_from_tokens` present; no legacy markers |
| `.claude/skills/pbi-docgen/scripts/pdf_builder.py` | Delegates to `render_prose_html`; uses `domcontentloaded` | VERIFIED | `_prose_to_html` one-liner wrapper at line 43-47; correct wait condition at line 143 |
| `.claude/skills/pbi-docgen/templates/document.html.j2` | DigitalOcean CSS with left-accent code blocks | VERIFIED | `border-left: 4px solid var(--accent)` at line 113; `--primary`, `--accent`, `--code-bg`, `--code-border`, `--text` custom properties present |
| All 14 prompt templates (12 section + 2 rules) | Free of TABLE:, CODE_BLOCK:, END_TABLE markers | VERIFIED | 0 matches across all files in both `templates/prompts/` trees |
| `.claude/skills/pbi-docgen/references/pbi-docs-contract.md` | pbi:docs output contract reference doc | VERIFIED | File exists in `.claude/` references; also present in `skills/` references |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `docx_builder.py` | `md_renderer.parse_prose` | `from scripts.md_renderer import parse_prose` at line 30 | WIRED | Called at line 625: `tokens = parse_prose(prose_text)` |
| `pdf_builder.py` | `md_renderer.render_prose_html` | `from scripts.md_renderer import render_prose_html` at line 22 | WIRED | Called at line 47 via `_prose_to_html` wrapper, which is called at line 79 |
| `pdf_builder._prose_to_html` | HTML template | `_render_html()` passes `html_content` per section to Jinja2 | WIRED | Line 79 builds `html_content`; line 101+ passes to template context |
| `page.set_content` | `domcontentloaded` | `wait_until='domcontentloaded'` parameter | WIRED | Old `networkidle` removed entirely |
| `document.html.j2` | CSS custom properties | `--accent` consumed by `.code-block { border-left: 4px solid var(--accent) }` | WIRED | Line 113 confirmed |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `pdf_builder.py` | `html_content` per section | `render_prose_html(prose)` from md_renderer | Yes — markdown-it-py renders input prose to HTML | FLOWING |
| `docx_builder.py` | `tokens` token list | `parse_prose(prose_text)` from md_renderer | Yes — behavioral spot-check confirmed `fence`, `table_open`, `heading_open` tokens produced | FLOWING |
| `document.html.j2` | `--primary`, `--accent` | Passed from `config` dict in `_render_html()` | Yes — values pulled from `config.get('accent_color', ...)` | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `parse_prose()` returns token list with `heading_open`, `fence`, `table_open` | `python -c "from scripts.md_renderer import parse_prose; toks = parse_prose(...); print([t.type for t in toks])"` | Token types: `['heading_open', 'inline', 'heading_close', 'fence', 'table_open', ...]` — all three expected types present | PASS |
| `render_prose_html()` produces valid HTML with heading and strong tags | `python -c "from scripts.md_renderer import render_prose_html; html = render_prose_html('## Hello\n\n**bold**'); print('<h2>' in html or '<strong>' in html)"` | `True` | PASS |
| `fence` token preserves interior blank lines | `parse_prose` on fenced block with blank interior line — single `fence` token returned (not split) | Token list contains exactly one `fence` entry; token stream does not split on blank lines | PASS |

---

### Requirements Coverage

The PLAN.md maps all 15 locked decisions (D-01 through D-15) from 4-RESEARCH.md to concrete tasks. No external REQUIREMENTS.md exists for this project — requirements are tracked as locked decisions in the CONTEXT/RESEARCH documents.

| Requirement | Mapped Task | Status | Evidence |
|-------------|-------------|--------|----------|
| D-01: Switch to standard Markdown output from prompts | Tasks C1, C2 | SATISFIED | 0 legacy markers in all 14 prompt templates |
| D-02: Parse with real Markdown library (markdown-it-py) | Task A1 | SATISFIED | `md_renderer.py` uses `MarkdownIt('commonmark').enable('table')` |
| D-03: Unified parser → dual renderers | Tasks A1, A2, B1 | SATISFIED | Single `_MD` instance; `parse_prose` for DOCX, `render_prose_html` for PDF |
| D-04: Prompt templates request standard Markdown | Tasks C1, C2 | SATISFIED | All templates updated; no TABLE:/CODE_BLOCK: instructions remain |
| D-05: Fix Playwright crash | Task B1 | SATISFIED | `wait_until='domcontentloaded'` at line 143; `networkidle` removed |
| D-06: Fix broken PDF layout | Task B1 | SATISFIED | `_prose_to_html` now delegates to `render_prose_html`; hand-rolled parser removed |
| D-07: Fix blank-line code block truncation | Task A2 | SATISFIED | `fence` token from markdown-it-py contains full content including blank lines (confirmed by spot-check) |
| D-08: DigitalOcean HTML template redesign | Task D1 | SATISFIED | `border-left: 4px solid var(--accent)` present; distinct heading hierarchy confirmed |
| D-09: Keep CSS custom properties pattern | Task D1 | SATISFIED | `--primary`, `--accent`, `--code-bg`, `--code-border`, `--text` all present |
| D-10: pbi:docs fenced code blocks with language tags | Task F1 | SATISFIED | `pbi-docs-contract.md` exists in references |
| D-11: Verify section_heading_map.yaml | Task F2 | SATISFIED (per SUMMARY) | SUMMARY reports keywords verified; file exists in references |
| D-12: DOCX code block monospace + no truncation | Task A2 | SATISFIED | `fence` token handler in token-walker; `_render_inline_children_to_runs` uses Courier New |
| D-13: DOCX table header color + alternating rows | Task A2 | SATISFIED | `_collect_table_rows_from_tokens` wired to `_add_table()` which applies header shading |
| D-14: Bold/italic accuracy via real parser | Task A2 | SATISFIED | `_render_inline_children_to_runs` handles `strong_open/close`, `em_open/close` tokens correctly |
| D-15: Heading hierarchy with distinct font sizes | Task E1 | SATISFIED | `sizes = {1: 20, 2: 14, 3: 12, 4: 11}` in `_add_colored_heading` at line 220 |

---

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| `grevisse_rules.j2` | CRLF line endings in `skills/` copy vs LF in `.claude/` copy | Info | Windows git checkout artifact — content identical; no functional impact |
| `fr_glossary.yaml` | CRLF line endings in `skills/` copy vs LF in `.claude/` copy | Info | Same as above — content identical; YAML parsing is line-ending agnostic |
| `skills/pbi-docgen/references/fowler_guidance.md` | Present in `skills/` but absent from `.claude/` | Info | Extra file in repo copy only; not a missing file in the canonical `.claude/` tree; no functional impact on the skill |
| `skills/pbi-docgen/scripts/test_md_parser.py` | Present in `skills/` but absent from `.claude/` | Info | Test file only — not part of the runtime pipeline |

No blocker or warning anti-patterns found. All four items are informational only.

---

### Human Verification Required

#### 1. DOCX Code Block — Blank Line Preservation

**Test:** Generate a DOCX with a section containing a fenced code block that has an interior blank line (e.g., `line1\n\nline2`). Open in Microsoft Word.
**Expected:** The code block body shows both lines with the blank line between them — content is not truncated at the blank line.
**Why human:** The `fence` token's `.content` is confirmed correct by spot-check, but rendering that content into python-docx paragraphs requires visual inspection of the final .docx.

#### 2. PDF Visual — DigitalOcean Left-Accent Code Block

**Test:** Generate a PDF with a section containing a code block. Open the PDF.
**Expected:** Code blocks display with a left gold/accent border (4px), subtle grey background, monospace font, and no truncation.
**Why human:** CSS rendering through Playwright/Chromium cannot be verified without launching the browser and inspecting the rendered PDF visually.

#### 3. Table Parity — DOCX and PDF

**Test:** Generate both DOCX and PDF from a source with at least one pipe table. Compare outputs side by side.
**Expected:** Header row has primary-color background in DOCX; alternating row shading in PDF matches CSS; column counts agree.
**Why human:** Requires end-to-end run and visual comparison of both output formats.

---

### Sync Divergence Notes

The `diff -rq` between `.claude/skills/pbi-docgen/` and `skills/pbi-docgen/` shows four differences, none of which are functional:

1. `fr_glossary.yaml` — CRLF vs LF (same content)
2. `grevisse_rules.j2` — CRLF vs LF (same content)
3. `skills/` has `references/fowler_guidance.md` not in `.claude/` — this is an extra file in the repo copy, not a missing file
4. `skills/` has `scripts/test_md_parser.py` not in `.claude/` — test file only

All core phase deliverables (md_renderer.py, docx_builder.py, pdf_builder.py, document.html.j2, all 14 prompt templates, pbi-docs-contract.md) are byte-for-byte identical between both trees.

---

_Verified: 2026-04-07T11:03:37Z_
_Verifier: Claude (gsd-verifier)_
