---
phase: quick
plan: 260406-gmd
subsystem: pdf-builder
tags: [bugfix, inline-markdown, pdf, formatting]
dependency_graph:
  requires: []
  provides: [_inline_md_to_html-in-pdf-builder]
  affects: [pdf-output-formatting]
tech_stack:
  added: []
  patterns: [regex-based-inline-md-to-html, escape-first-then-substitute]
key_files:
  created: []
  modified:
    - .claude/skills/pbi-docgen/scripts/pdf_builder.py
decisions:
  - "HTML-escape first, then regex-substitute -- asterisks/backticks are not HTML-special so escape() leaves them intact for the regex"
  - "Mirror docx_builder INLINE_MD_RE exactly for consistency across DOCX and PDF output"
metrics:
  duration: 2min
  completed: "2026-04-06T08:02:39Z"
---

# Quick Task 260406-gmd: Fix Inline Markdown Leaking in PDF Build Summary

Inline Markdown syntax (bold, italic, code) now renders as proper HTML formatting in PDF output instead of leaking as literal asterisks and backticks.

## What Changed

Added `_inline_md_to_html(text)` helper to `pdf_builder.py` that HTML-escapes input first (XSS safety), then applies regex substitutions to convert `***bold+italic***`, `**bold**`, `*italic*`, `_italic_`, and `` `code` `` to their HTML tag equivalents (`<strong>`, `<em>`, `<code>`). Wired the helper into:

- `_prose_to_html()` -- regular paragraph lines and fallback single-line table entries
- `_table_lines_to_html()` -- both `<th>` header cells and `<td>` body cells

Sub-headings and code blocks remain using bare `html.escape()` (no inline MD expected in those contexts).

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Add _inline_md_to_html helper and wire into _prose_to_html and _table_lines_to_html | 12b9fe9 | .claude/skills/pbi-docgen/scripts/pdf_builder.py |

## Verification Results

All automated assertions passed:
- `**bold**` renders as `<strong>bold</strong>`
- `*italic*` renders as `<em>italic</em>`
- `` `code` `` renders as `<code>code</code>`
- `***both***` renders as `<strong><em>both</em></strong>`
- `<script>` input is escaped to `&lt;script&gt;` (XSS safe)
- Plain text passes through unchanged
- `_prose_to_html` output contains `<strong>` not raw `**`
- `_table_lines_to_html` renders bold in headers and italic in body cells

## Deviations from Plan

None -- plan executed exactly as written.

## Known Stubs

None.
