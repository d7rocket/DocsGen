---
phase: 01-skill-core-intake-docx
plan: 04
subsystem: docx
tags: [python-docx, RGBColor, OxmlElement, parse_xml, cover-page, branded-tables]

# Dependency graph
requires:
  - phase: 01-skill-core-intake-docx
    provides: "utils.py with parse_hex_color and ensure_directory"
provides:
  - "docx_builder.py with build_docx() for complete branded DOCX assembly"
  - "Cover page with dual logos, client name, version, date"
  - "Run-level color formatting helpers"
  - "XML-shaded table and code block formatting"
affects: [01-05, 02-pdf-generation]

# Tech tracking
tech-stack:
  added: [python-docx 1.2.0, lxml 6.0.2]
  patterns: [run-level-color-only, xml-cell-shading, different-first-page-header-footer]

key-files:
  created:
    - "~/.claude/skills/pbi-docgen/scripts/docx_builder.py"
    - ".claude/skills/pbi-docgen/scripts/docx_builder.py"
  modified: []

key-decisions:
  - "Run-level RGBColor exclusively for all heading colors -- never style mutation (D-14/D-15)"
  - "NEW parse_xml element per table cell to avoid lxml silent reparenting (Pitfall 3)"
  - "Tint computation: 15% accent + 85% white for alternating table rows"

patterns-established:
  - "Run-level color: always use run.font.color.rgb, never style.font.color.rgb on built-in styles"
  - "XML shading: create fresh parse_xml element for every cell/paragraph"
  - "Cover page isolation: different_first_page_header_footer + is_linked_to_previous = False"

requirements-completed: [DOCX-01, DOCX-02, DOCX-03, DOCX-04]

# Metrics
duration: 2min
completed: 2026-04-01
---

# Phase 01 Plan 04: DOCX Builder Summary

**python-docx builder with branded cover page (dual logos), run-level colored headings, XML-shaded tables with alternating tints, and Courier New code blocks with borders**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-01T18:42:59Z
- **Completed:** 2026-04-01T18:45:26Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Complete DOCX builder module (528 lines) with build_docx() public API
- Cover page with client logo (centered), company logo (right-aligned), client name, report name, version, date
- Run-level RGBColor on all headings -- no style mutation anywhere in module
- XML-shaded table headers (primary color, white text) with alternating body row tints
- Code blocks with Courier New 9pt, F2F2F2 grey background, D0D0D0 border
- Header/footer isolation between cover and body sections via is_linked_to_previous = False
- Prose parser handles TABLE:, CODE_BLOCK:, triple-backtick fences, pipe-delimited tables, sub-headings

## Task Commits

Each task was committed atomically:

1. **Task 1: Create DOCX builder with cover page, headers, and brand formatting** - `f6d7bc5` (feat)

## Files Created/Modified
- `~/.claude/skills/pbi-docgen/scripts/docx_builder.py` - Complete DOCX assembly module (runtime location)
- `.claude/skills/pbi-docgen/scripts/docx_builder.py` - Same file in repo (version control)

## Decisions Made
- Run-level RGBColor exclusively for heading colors -- locked per D-14/D-15
- Tint formula: 15% accent color + 85% white for alternating table body rows
- Code style created once via try/except KeyError for idempotent reuse
- Pipe-delimited tables auto-detected even without TABLE: marker

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed python-docx 1.2.0 dependency**
- **Found during:** Task 1 (pre-execution check)
- **Issue:** python-docx not installed, module cannot be created or verified
- **Fix:** Ran `pip install python-docx==1.2.0` (also pulled in lxml 6.0.2)
- **Files modified:** None (pip user install)
- **Verification:** `python -c "import docx"` succeeds
- **Committed in:** N/A (pip install, not a code change)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Dependency install was necessary prerequisite. No scope creep.

## Issues Encountered
None -- plan executed cleanly after dependency install.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None -- all functions fully implemented with complete logic.

## Next Phase Readiness
- docx_builder.py ready to receive output from content_generator.py (Plan 03)
- generate.py (Plan 05) can wire the full pipeline: md_parser -> content_generator -> docx_builder
- All DOCX requirements (DOCX-01 through DOCX-04) satisfied

## Self-Check: PASSED

All artifacts verified:
- .claude/skills/pbi-docgen/scripts/docx_builder.py: FOUND
- ~/.claude/skills/pbi-docgen/scripts/docx_builder.py: FOUND
- .planning/phases/01-skill-core-intake-docx/01-04-SUMMARY.md: FOUND
- Commit f6d7bc5: FOUND

---
*Phase: 01-skill-core-intake-docx*
*Completed: 2026-04-01*
