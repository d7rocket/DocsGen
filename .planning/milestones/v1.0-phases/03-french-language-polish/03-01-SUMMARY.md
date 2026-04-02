---
phase: 03-french-language-polish
plan: 01
subsystem: content-generation
tags: [jinja2, yaml, french, grevisse, fowler, i18n, prompt-engineering]

# Dependency graph
requires:
  - phase: 01-core-docgen-pipeline
    provides: EN content generation pipeline (content_generator.py, generate.py, 6 EN templates, fowler_rules.j2)
provides:
  - FR content generation infrastructure (6 FR templates, glossary, Grevisse rules, language routing)
  - Hardened EN Fowler rules with explicit forbidden phrases
  - Language-conditional template selection in content_generator.py
  - Language threading from generate.py config to content generation
affects: [03-02, docx-builder, pdf-builder]

# Tech tracking
tech-stack:
  added: [PyYAML (already installed, now used in content_generator.py)]
  patterns: [dual template map (EN/FR), lazy-init glossary cache, language parameter threading]

key-files:
  created:
    - .claude/skills/pbi-docgen/references/fr_glossary.yaml
    - .claude/skills/pbi-docgen/templates/prompts/grevisse_rules.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_overview_fr.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_sources_fr.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_dataflows_fr.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_mquery_fr.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_datamodel_fr.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_maintenance_fr.j2
  modified:
    - .claude/skills/pbi-docgen/templates/prompts/fowler_rules.j2
    - .claude/skills/pbi-docgen/scripts/content_generator.py
    - .claude/skills/pbi-docgen/scripts/generate.py

key-decisions:
  - "Dual template map pattern (SECTION_TEMPLATE_MAP + SECTION_TEMPLATE_MAP_FR) for clean EN/FR separation"
  - "Lazy-init module-level cache for FR glossary to avoid per-render disk reads"
  - "Glossary passed as template variable (not Jinja2 global) for explicit data flow"

patterns-established:
  - "Language-conditional template routing: language param selects template map in _render_prompt()"
  - "FR template structure: grevisse include + glossary loop + FR instructions + shared variables"
  - "Hardened prompt rules: explicit FORBIDDEN lists with concrete substitution examples"

requirements-completed: [CONT-08]

# Metrics
duration: 13min
completed: 2026-04-02
---

# Phase 03 Plan 01: FR Content Generation Infrastructure Summary

**FR prompt templates with Grevisse rules and PBI glossary, language-conditional routing in content_generator.py, and hardened Fowler rules for EN**

## Performance

- **Duration:** 13 min
- **Started:** 2026-04-02T10:33:55Z
- **Completed:** 2026-04-02T10:46:45Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments
- Created PBI French terminology glossary (20 terms) covering all core Power BI concepts
- Created La Grevisse formal writing rules template (7 rules) for professional French prose
- Hardened Fowler rules with explicit FORBIDDEN patterns, concrete substitution examples, and pre-output self-check instruction
- Built 6 FR section prompt templates mirroring EN structure with Grevisse include and glossary embedding
- Added SECTION_TEMPLATE_MAP_FR and _load_fr_glossary() to content_generator.py for language-conditional routing
- Threaded language parameter from generate.py config through to content generation pipeline

## Task Commits

Each task was committed atomically:

1. **Task 1: Create FR reference files, Grevisse rules, and harden Fowler rules** - `0c412a7` (feat)
2. **Task 2: Create 6 FR section templates and wire language routing** - `62bb1c9` (feat)

## Files Created/Modified
- `.claude/skills/pbi-docgen/references/fr_glossary.yaml` - PBI French terminology glossary (20 terms)
- `.claude/skills/pbi-docgen/templates/prompts/grevisse_rules.j2` - La Grevisse formal writing rules (7 rules)
- `.claude/skills/pbi-docgen/templates/prompts/fowler_rules.j2` - Hardened EN Fowler rules with FORBIDDEN lists
- `.claude/skills/pbi-docgen/templates/prompts/section_overview_fr.j2` - FR overview section template
- `.claude/skills/pbi-docgen/templates/prompts/section_sources_fr.j2` - FR sources section template
- `.claude/skills/pbi-docgen/templates/prompts/section_dataflows_fr.j2` - FR dataflows section template
- `.claude/skills/pbi-docgen/templates/prompts/section_mquery_fr.j2` - FR M Query section template (with audience conditional)
- `.claude/skills/pbi-docgen/templates/prompts/section_datamodel_fr.j2` - FR data model section template
- `.claude/skills/pbi-docgen/templates/prompts/section_maintenance_fr.j2` - FR maintenance section template
- `.claude/skills/pbi-docgen/scripts/content_generator.py` - Added FR template map, glossary loader, language parameter
- `.claude/skills/pbi-docgen/scripts/generate.py` - Threads config language to generate_all_sections()

## Decisions Made
- Dual template map pattern (SECTION_TEMPLATE_MAP + SECTION_TEMPLATE_MAP_FR) for clean EN/FR separation without modifying EN templates
- Lazy-init module-level cache for FR glossary (_FR_GLOSSARY) to avoid per-render disk reads
- Glossary passed as explicit template variable via render_kwargs rather than Jinja2 global, keeping data flow visible

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- FR content generation infrastructure complete; config with "language": "FR" will select FR templates and embed glossary
- Ready for Plan 02: docx_builder/pdf_builder language-aware formatting, section heading labels, FR date formatting, SKILL.md unlock
- EN pipeline works exactly as before with default language="EN"

## Self-Check: PASSED

All 11 files verified present. Both commit hashes (0c412a7, 62bb1c9) confirmed in git log.

---
*Phase: 03-french-language-polish*
*Completed: 2026-04-02*
