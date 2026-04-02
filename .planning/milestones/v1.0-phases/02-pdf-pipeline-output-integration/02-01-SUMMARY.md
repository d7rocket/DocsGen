---
phase: 02-pdf-pipeline-output-integration
plan: 01
subsystem: document-generation
tags: [python-docx, playwright, jinja2, pdf, toc, html-template]

# Dependency graph
requires:
  - phase: 01-skill-core-intake-docx
    provides: docx_builder.py with build_docx(), section ordering, marker protocol (TABLE:/CODE_BLOCK:)
provides:
  - _insert_toc_field() function for Word TOC field injection
  - document.html.j2 Jinja2 template for PDF rendering
  - pdf_builder.py module with build_pdf(), _prose_to_html(), _render_html(), slugify()
affects: [02-02 pipeline wiring, generate.py integration, SKILL.md update]

# Tech tracking
tech-stack:
  added: [playwright sync_api (used in pdf_builder), jinja2 FileSystemLoader (HTML template)]
  patterns: [SDT XML TOC field injection, prose-to-HTML marker parsing, CSS custom properties for brand colors, file:/// URI for local images in Chromium]

key-files:
  created:
    - .claude/skills/pbi-docgen/scripts/pdf_builder.py
    - .claude/skills/pbi-docgen/templates/document.html.j2
  modified:
    - .claude/skills/pbi-docgen/scripts/docx_builder.py

key-decisions:
  - "TOC uses SDT wrapping with fldChar begin/instrText/separate/end pattern -- standard Word field XML"
  - "HTML template uses CSS custom properties (--primary, --accent) for brand color injection via Jinja2"
  - "_prose_to_html() duplicates marker parsing from docx_builder rather than shared abstraction -- simpler, avoids refactor risk"
  - "autoescape=False in Jinja2 Environment since html_content is pre-escaped in _prose_to_html()"

patterns-established:
  - "SDT + fldChar pattern for Word field injection via OxmlElement"
  - "Prose-to-HTML conversion mirroring docx_builder marker protocol for content parity"
  - "Print-first CSS with print-color-adjust: exact and page-break-inside: avoid"
  - "Logo path to file:/// URI conversion for Chromium local image loading"

requirements-completed: [DOCX-05, PDF-01, PDF-02, PDF-03, OUT-02]

# Metrics
duration: 5min
completed: 2026-04-01
---

# Phase 02 Plan 01: DOCX TOC + PDF Builder Summary

**Word TOC field injection via SDT XML, Jinja2 HTML template with branded cover/TOC/sections, and Playwright PDF builder with prose-to-HTML converter**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-01T20:19:56Z
- **Completed:** 2026-04-01T20:25:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Word TOC field inserted after cover page using SDT + fldChar XML pattern; collects Heading 1-3 entries on F9 refresh
- Jinja2 HTML template with branded cover page, clickable anchor TOC, sections loop, and print-first CSS
- pdf_builder.py module with build_pdf() (Playwright sync API), _prose_to_html() (full marker protocol), and _render_html() (Jinja2 template rendering)

## Task Commits

Each task was committed atomically:

1. **Task 1: Insert Word TOC field in docx_builder.py** - `cac5e52` (feat)
2. **Task 2: Create Jinja2 HTML template for PDF rendering** - `3357110` (feat)
3. **Task 3: Create pdf_builder.py with build_pdf() and prose-to-HTML converter** - `b8be31d` (feat)

## Files Created/Modified
- `.claude/skills/pbi-docgen/scripts/docx_builder.py` - Added _insert_toc_field() and OxmlElement import; TOC call in build_docx()
- `.claude/skills/pbi-docgen/templates/document.html.j2` - Full HTML template with cover page, TOC, sections, print CSS
- `.claude/skills/pbi-docgen/scripts/pdf_builder.py` - build_pdf(), slugify(), _prose_to_html(), _render_html(), _table_lines_to_html()

## Decisions Made
- Used SDT wrapping for TOC field (standard Word XML pattern from python-docx issue #36)
- Duplicated marker parsing in _prose_to_html() rather than extracting shared abstraction -- avoids refactor risk to existing docx_builder
- Set autoescape=False in Jinja2 Environment since HTML content is pre-escaped
- Separate FileSystemLoader for HTML templates (not reusing prompt templates loader per anti-pattern guidance)

## Deviations from Plan

None -- plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None -- no external service configuration required.

## Known Stubs
None -- all functions are fully implemented with no placeholder data.

## Next Phase Readiness
- pdf_builder.py is ready to be wired into generate.py Stage 4 (Plan 02-02)
- SKILL.md needs update to capture both output paths (Plan 02-02)
- generate.py needs Stage 4 integration and completion report (Plan 02-02)

## Self-Check: PASSED

All 3 created/modified files verified present. All 3 commit hashes verified in git log.

---
*Phase: 02-pdf-pipeline-output-integration*
*Completed: 2026-04-01*
