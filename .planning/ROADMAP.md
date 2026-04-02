# Roadmap: DocsGen

## Overview

DocsGen transforms structured PBI Markdown documentation into polished, branded Word and PDF deliverables. The roadmap delivers this in three phases: first the skill foundation with intake wizard and DOCX generation (English), then the HTML/PDF pipeline with TOC and dual-output integration, and finally French language support with professional prose enforcement and output polish. Every phase enforces the quality bar: output must be suitable for direct client delivery without manual post-processing.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Skill Core + Intake + DOCX** - Skill scaffolding, intake wizard, MD parsing, English content generation, and branded .docx output
- [x] **Phase 2: PDF Pipeline + Output Integration** - HTML/PDF generation via Playwright, TOC, and unified dual-output invocation
- [ ] **Phase 3: French Language + Polish** - French prose with La Grevisse + PBI glossary, language-aware formatting, Fowler EN enforcement hardened

## Phase Details

### Phase 1: Skill Core + Intake + DOCX
**Goal**: User can invoke the skill from any directory, walk through the intake wizard, and receive a branded .docx document with all detected sections rendered in clear English prose
**Depends on**: Nothing (first phase)
**Requirements**: SCAF-01, SCAF-02, SCAF-03, SCAF-04, INTAK-01, INTAK-02, INTAK-03, INTAK-04, PARSE-01, PARSE-02, PARSE-03, CONT-01, CONT-02, CONT-03, CONT-04, CONT-05, CONT-06, CONT-07, DOCX-01, DOCX-02, DOCX-03, DOCX-04
**Success Criteria** (what must be TRUE):
  1. User can invoke the skill from a non-PBI directory, complete the intake wizard, and receive a .docx file without errors
  2. The generated .docx has a branded cover page (client name, logos, colors) and consistent color theming on headings, tables, and accents throughout
  3. Only sections with actual source content appear in the document -- no blank pages or empty headings for missing sections
  4. M Query section renders audience-appropriate content: plain-English summaries for client audience, annotated code blocks for internal/IT
  5. English prose reads as clear, direct, and professional -- no filler, no padding, consistent with Fowler's guidance
**Plans**: 5 plans

Plans:
- [x] 01-01-PLAN.md — Skill scaffolding, reference files, utilities, and MD parser
- [x] 01-02-PLAN.md — SKILL.md intake wizard with dependency checking and validation
- [x] 01-03-PLAN.md — Content generation: Jinja2 prompt templates and claude -p integration
- [x] 01-04-PLAN.md — DOCX builder with branded cover page, headers, and formatting
- [x] 01-05-PLAN.md — Pipeline wiring (generate.py) and end-to-end verification

### Phase 2: PDF Pipeline + Output Integration
**Goal**: User receives both .docx and .pdf from a single skill invocation, with the PDF rendered from styled HTML via Playwright and both documents including a navigable table of contents
**Depends on**: Phase 1
**Requirements**: PDF-01, PDF-02, PDF-03, DOCX-05, OUT-01, OUT-02, OUT-03
**Success Criteria** (what must be TRUE):
  1. A single skill invocation produces both a .docx and a .pdf file in the output folder
  2. The PDF renders with correct brand colors, embedded fonts, and clean page breaks (no split tables or orphaned code blocks)
  3. Both .docx and .pdf include a table of contents that reflects the auto-detected sections
  4. Output files follow the naming convention [ClientName]_[ReportName]_v[Version]_[YYYY-MM-DD] and the skill reports file paths and sizes on completion
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md — DOCX TOC field, Jinja2 HTML template, and Playwright PDF builder module
- [x] 02-02-PLAN.md — Pipeline wiring (generate.py Stage 4) and SKILL.md dual-output update

### Phase 3: French Language + Polish
**Goal**: User can generate documentation in French with correct PBI terminology and formal register, and both EN and FR output meet a professional quality bar suitable for direct client delivery
**Depends on**: Phase 2
**Requirements**: CONT-08, CONT-09
**Success Criteria** (what must be TRUE):
  1. User selects FR at intake and receives a document with French prose that uses correct Power BI French terminology (e.g., "mesure" not "measure", "requete" not "query") and formal register per La Grevisse
  2. Section headings, dates, metadata, and boilerplate text render in the selected language -- no EN/FR mixing within a document
  3. English output prose is hardened against common violations of Fowler's guidelines (no needless passives, no nominalization padding, no corporate filler)
**Plans**: TBD

Plans:
- [ ] 03-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Skill Core + Intake + DOCX | 5/5 | Complete | 2026-04-01 |
| 2. PDF Pipeline + Output Integration | 2/2 | Complete | 2026-04-02 |
| 3. French Language + Polish | 0/1 | Not started | - |
