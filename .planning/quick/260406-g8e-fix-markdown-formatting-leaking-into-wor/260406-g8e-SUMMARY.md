---
phase: quick
plan: 260406-g8e
subsystem: docx-builder
tags: [formatting, markdown, docx, templates]
dependency_graph:
  requires: []
  provides: [inline-md-parsing, no-markdown-prompt-constraint]
  affects: [docx-output-quality, all-section-templates]
tech_stack:
  added: []
  patterns: [regex-based-inline-parsing, run-level-formatting]
key_files:
  created: []
  modified:
    - .claude/skills/pbi-docgen/scripts/docx_builder.py
    - .claude/skills/pbi-docgen/templates/prompts/fowler_rules.j2
    - .claude/skills/pbi-docgen/templates/prompts/grevisse_rules.j2
decisions:
  - "Regex-based inline MD parser with priority ordering (bold+italic > bold > italic > code)"
  - "Word-boundary aware underscore italic to avoid matching mid-word underscores like Sales_Amount"
  - "Shared _parse_inline_runs helper used by both paragraph and table cell formatting"
metrics:
  duration: 5min
  completed: "2026-04-06"
---

# Quick Task 260406-g8e: Fix Markdown Formatting Leaking into Word Output

Regex-based inline Markdown parser in docx_builder.py converts bold/italic/code spans to Word run-level formatting; no-Markdown rule added to shared EN/FR prompt templates propagating to all 12 section templates.

## What Changed

### Task 1: No-Markdown constraint in prompt rule templates
- Added rule 8 to `fowler_rules.j2` forbidding Markdown syntax (asterisks, underscores, backticks) in LLM output
- Added equivalent French rule 8 to `grevisse_rules.j2`
- All 12 section templates (6 EN + 6 FR) inherit via `{% include %}` -- no individual edits needed
- **Commit:** 78437f6

### Task 2: Inline Markdown parsing in docx_builder.py
- Added module-level `INLINE_MD_RE` compiled regex handling: `***bold+italic***`, `**bold**`, `*italic*`, `_italic_` (word-boundary aware), and backtick code spans
- Added `_parse_inline_runs(paragraph, text, code_style)` -- reusable helper that adds formatted runs to any paragraph
- Added `_add_inline_md_paragraph(doc, line, code_style)` -- creates paragraphs with inline formatting and bullet dash detection
- Replaced all bare `doc.add_paragraph(line.strip())` calls in `_parse_and_add_prose` with `_add_inline_md_paragraph`
- Updated `_add_table` to accept `code_style` parameter and use `_parse_inline_runs` for cell text formatting
- Forwarded `code_style` from `_parse_and_add_prose` to `_add_table` calls
- **Commit:** e20e975

## Deviations from Plan

None -- plan executed exactly as written.

## Known Stubs

None -- all functionality is fully wired.

## Verification Results

| Check | Result |
|-------|--------|
| `INLINE_MD_RE` defined at module level | PASS |
| `_add_inline_md_paragraph` occurrences >= 3 | PASS (3: def + 2 call sites) |
| `_parse_inline_runs` occurrences >= 3 | PASS (def + paragraph call + table call) |
| Zero bare `doc.add_paragraph(line.strip())` in prose handler | PASS (0 remaining) |
| `MARKDOWN` in fowler_rules.j2 | PASS |
| `MARKDOWN` in grevisse_rules.j2 | PASS |
| Python syntax check | PASS |
| Regex correctly ignores mid-word underscores (Sales_Amount) | PASS |
| Regex correctly matches word-boundary italic (_text_) | PASS |
