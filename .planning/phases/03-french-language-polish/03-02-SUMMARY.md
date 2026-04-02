---
phase: 03-french-language-polish
plan: 02
subsystem: output-renderers
tags: [docx-builder, pdf-builder, i18n, french, section-headings, date-formatting, dual-deploy]

# Dependency graph
requires:
  - phase: 03-french-language-polish
    plan: 01
    provides: FR content generation infrastructure (templates, glossary, language routing)
provides:
  - Language-aware section headings in both DOCX and PDF renderers
  - FR date formatting (locale-independent) in both renderers
  - Cover page boilerplate translations (Prepared for, Confidential, TOC heading)
  - Dynamic HTML lang attribute for PDF output
  - FR language gate removed from SKILL.md
affects: [SKILL.md, docx-output, pdf-output]

# Tech tracking
tech-stack:
  added: [PyYAML import in docx_builder.py for heading map loading]
  patterns: [COVER_BOILERPLATE dict, FR_MONTHS lookup, get_section_label() shared helper, format_date() shared helper]

key-files:
  created: []
  modified:
    - ~/.claude/skills/pbi-docgen/references/section_heading_map.yaml
    - ~/.claude/skills/pbi-docgen/scripts/docx_builder.py
    - ~/.claude/skills/pbi-docgen/scripts/pdf_builder.py
    - ~/.claude/skills/pbi-docgen/templates/document.html.j2
    - ~/.claude/skills/pbi-docgen/SKILL.md
    - .claude/skills/pbi-docgen/references/section_heading_map.yaml
    - .claude/skills/pbi-docgen/scripts/docx_builder.py
    - .claude/skills/pbi-docgen/scripts/pdf_builder.py
    - .claude/skills/pbi-docgen/templates/document.html.j2
    - .claude/skills/pbi-docgen/SKILL.md

key-decisions:
  - "FR_MONTHS dict for date formatting instead of locale.setlocale() -- platform-independent, thread-safe"
  - "get_section_label() in docx_builder.py shared by pdf_builder via import -- DRY, single source of truth for heading map"
  - "COVER_BOILERPLATE dict with toc_heading key -- covers TOC heading in both renderers"
  - "HTML template TOC heading made dynamic via {{ toc_heading }} variable"

patterns-established:
  - "Shared language helpers (format_date, get_section_label, COVER_BOILERPLATE) live in docx_builder.py; pdf_builder imports them"
  - "Lazy-loaded _HEADING_MAP module cache for section_heading_map.yaml"

requirements-completed: [CONT-09]

# Metrics
duration: 3min
completed: 2026-04-02
---

# Phase 03 Plan 02: Renderer Language Wiring Summary

**FR section headings, dates, and boilerplate in both DOCX and PDF renderers; HTML lang attribute; SKILL.md FR gate removed**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-02T10:50:44Z
- **Completed:** 2026-04-02T10:53:50Z
- **Tasks:** 2
- **Files modified:** 10 (5 unique files x 2 deployment locations)

## Accomplishments
- Added label_fr to all 6 sections in section_heading_map.yaml for deterministic FR heading selection
- Added FR_MONTHS dict and format_date() function for locale-independent French date formatting ("le 2 avril 2026")
- Added COVER_BOILERPLATE dict with EN/FR translations for version prefix, prepared-for, confidential, and TOC heading
- Added get_section_label() and _load_heading_map() for language-aware heading selection from YAML
- Wired language-aware TOC heading, section headings, date, and boilerplate into docx_builder.build_docx()
- Imported format_date, get_section_label, COVER_BOILERPLATE into pdf_builder.py (DRY -- no duplication)
- Updated pdf_builder._render_html() to use get_section_label() for FR section headings in PDF
- Updated pdf_builder to pass lang and toc_heading to HTML template
- Made HTML template lang attribute dynamic ({{ lang }}) and TOC heading dynamic ({{ toc_heading }})
- Removed FR warning gate and EN fallback from SKILL.md Field 7 -- FR now passes through as valid language
- Dual deployed all changes to both ~/.claude/skills/ and .claude/skills/

## Task Commits

Each task was committed atomically:

1. **Task 1: Add label_fr to heading map and language-aware formatting to docx_builder** - `a5e5464` (feat)
2. **Task 2: Wire language into pdf_builder, HTML template, remove FR gate, dual deploy** - `4448140` (feat)

## Files Created/Modified
- `~/.claude/skills/pbi-docgen/references/section_heading_map.yaml` - Added label_fr field to all 6 section entries
- `~/.claude/skills/pbi-docgen/scripts/docx_builder.py` - FR_MONTHS, format_date(), COVER_BOILERPLATE, get_section_label(), language-aware build_docx()
- `~/.claude/skills/pbi-docgen/scripts/pdf_builder.py` - Imports shared helpers, language-aware _render_html() with get_section_label()
- `~/.claude/skills/pbi-docgen/templates/document.html.j2` - Dynamic lang="{{ lang }}" and toc_heading="{{ toc_heading }}"
- `~/.claude/skills/pbi-docgen/SKILL.md` - FR gate removed from Field 7 section
- `.claude/skills/pbi-docgen/*` - All above files plus Plan 01 files dual deployed to repo copy

## Decisions Made
- FR_MONTHS dict for date formatting instead of locale.setlocale() -- platform-independent and thread-safe per anti-pattern guidance
- get_section_label() lives in docx_builder.py and is imported by pdf_builder -- single source of truth, no duplication
- COVER_BOILERPLATE includes toc_heading key so both DOCX and PDF TOC headings are language-aware
- HTML template TOC heading changed from hardcoded "Table of Contents" to {{ toc_heading }} variable for consistency

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing] HTML template TOC heading was hardcoded**
- **Found during:** Task 2
- **Issue:** The HTML template had a hardcoded "Table of Contents" h1 in the TOC section that would not change with language
- **Fix:** Made it dynamic via {{ toc_heading }} variable, imported COVER_BOILERPLATE in pdf_builder to pass the correct heading
- **Files modified:** document.html.j2, pdf_builder.py
- **Commit:** 4448140

## Issues Encountered
None

## User Setup Required
None -- no external service configuration required.

## Known Stubs
None -- all language-aware formatting is fully wired with real data sources.

## Next Phase Readiness
- Phase 03 is complete: FR content generation (Plan 01) + renderer language wiring (Plan 02)
- A config with "language": "FR" will produce: French section headings, "le 2 avril 2026" date, "Prepare pour" boilerplate, "Table des matieres" TOC, lang="fr" in PDF HTML
- EN config works exactly as before (backward compatible)
- No locale.setlocale() anywhere in the codebase

## Self-Check: PASSED

All 10 files verified present (5 in ~/.claude/skills/ + 5 in .claude/skills/). Both commit hashes (a5e5464, 4448140) confirmed in git log.

---
*Phase: 03-french-language-polish*
*Completed: 2026-04-02*
