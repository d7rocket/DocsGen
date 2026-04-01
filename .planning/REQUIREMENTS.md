# Requirements: DocsGen

**Defined:** 2026-04-01
**Core Value:** Turn structured PBI Markdown docs into client-ready Word/PDF deliverables with correct branding, language, and audience-appropriate depth — in one skill invocation.

## v1 Requirements

### Scaffold

- [x] **SCAF-01**: Skill works from any directory (not tied to a PBI project folder)
- [ ] **SCAF-02**: Skill creates `docsgen-assets/` subfolder structure (`logos/`, `source/`) on first run and guides user to populate it
- [ ] **SCAF-03**: Skill follows Claude Code skill conventions (SKILL.md with YAML frontmatter + `scripts/` + `templates/` + `references/`)
- [x] **SCAF-04**: Skill detects missing Python dependencies (python-docx, Playwright) and surfaces clear installation instructions before failing

### Intake

- [x] **INTAK-01**: Skill prompts step-by-step for all required inputs: source MD file(s), client name, client logo, company logo, primary color, accent color, language (EN/FR), audience type (internal/client/IT), report name, version number
- [x] **INTAK-02**: Language selection (EN or FR) asked every run — not cached
- [x] **INTAK-03**: Skill validates all required assets are present in `docsgen-assets/` before proceeding to generation; surfaces a clear checklist of missing items if anything is absent
- [x] **INTAK-04**: Output folder created automatically under working directory (e.g., `docsgen-output/`) — user does not need to create it

### Parsing

- [ ] **PARSE-01**: Skill reads source Markdown files produced by the existing `pbi:docs` skill — no PBIP/PBIX parsing
- [ ] **PARSE-02**: Section auto-detection: identifies which of the 6 documentation sections have content in the source MD
- [ ] **PARSE-03**: Sections with no source content are silently skipped — no blank pages, no empty headings in output

### Content

- [ ] **CONT-01**: Section 1 — Project overview + technical diagrams: generated from source overview content
- [ ] **CONT-02**: Section 2 — Source systems & architecture: generated from source data connection / gateway content
- [ ] **CONT-03**: Section 3 — Dataflows: generated from dataflow documentation (skipped if not present)
- [ ] **CONT-04**: Section 4 — M Query business logic: plain-English summaries for client audience; annotated code blocks for internal/IT audience
- [ ] **CONT-05**: Section 5 — Data model / SSAS: generated from model/table/relationship documentation
- [ ] **CONT-06**: Section 6 — Troubleshooting, parameters & maintenance: generated from parameters and operational notes
- [ ] **CONT-07**: English prose follows Fowler's *Modern English Usage* guidelines (clear, direct, no padding)
- [ ] **CONT-08**: French prose follows La Grévisse guidelines (correct register, PBI-specific FR terminology applied via glossary)
- [ ] **CONT-09**: Section headings, dates, and metadata formatted per selected language

### DOCX Output

- [ ] **DOCX-01**: `.docx` file generated via python-docx with all auto-detected sections, headings, paragraphs, tables, and code blocks
- [ ] **DOCX-02**: Cover page includes: client name, report name, version, date, client logo, company logo
- [ ] **DOCX-03**: Primary and accent colors applied consistently to headings, table headers, and accent elements — using run-level formatting (not style mutation)
- [ ] **DOCX-04**: Header/footer on all pages with page numbers; cover page uses different first-page header with dual logos
- [ ] **DOCX-05**: Table of contents inserted at document start (auto-updateable TOC field in Word)

### PDF Output

- [ ] **PDF-01**: Jinja2 HTML template renders structured content with full CSS layout matching document brand colors
- [ ] **PDF-02**: PDF generated from HTML via Playwright (headless Chromium) — not wkhtmltopdf
- [ ] **PDF-03**: CSS is print-first: explicit `print-color-adjust: exact`, embedded fonts, page break control for tables and code blocks

### Output

- [ ] **OUT-01**: Both `.docx` and `.pdf` produced in a single skill invocation
- [ ] **OUT-02**: Output files named predictably: `[ClientName]_[ReportName]_v[Version]_[YYYY-MM-DD].docx/.pdf`
- [ ] **OUT-03**: Skill reports completion with output file paths and file sizes

## v2 Requirements

### Diagrams

- **DIAG-01**: Conditional technical diagrams: skill detects diagram-worthy content (data flow, architecture) in source MD and generates ASCII or embedded diagrams
- **DIAG-02**: ERD-style data model diagram generated from relationship metadata

### Config Reuse

- **CFG-01**: User can save a project config (client name, colors, logos) to reuse on repeat runs without re-entering all intake fields
- **CFG-02**: Multiple saved configs supported (e.g., one per client)

### Accessibility

- **ACCS-01**: PDF output meets WCAG 2.1 AA for color contrast
- **ACCS-02**: `.docx` includes alt text on all images

## Out of Scope

| Feature | Reason |
|---------|--------|
| PBIP/PBIX file parsing | `pbi:docs` skill already does this — separation of concerns |
| Bilingual single document (EN+FR) | Doubles complexity; clients need one language; use two separate runs |
| Real-time document preview | Massive complexity; generate-then-open in Word/browser is sufficient |
| PowerPoint output | Different layout engine; separate skill if ever needed |
| Excel output | Different paradigm entirely; not documentation |
| Cloud storage (SharePoint, OneDrive) | Auth complexity not core to value; user copies files manually |
| WYSIWYG template editor | Users provide colors/logos; no need for visual design tools |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCAF-01 | Phase 1 | Complete |
| SCAF-02 | Phase 1 | Pending |
| SCAF-03 | Phase 1 | Pending |
| SCAF-04 | Phase 1 | Complete |
| INTAK-01 | Phase 1 | Complete |
| INTAK-02 | Phase 1 | Complete |
| INTAK-03 | Phase 1 | Complete |
| INTAK-04 | Phase 1 | Complete |
| PARSE-01 | Phase 1 | Pending |
| PARSE-02 | Phase 1 | Pending |
| PARSE-03 | Phase 1 | Pending |
| CONT-01 | Phase 1 | Pending |
| CONT-02 | Phase 1 | Pending |
| CONT-03 | Phase 1 | Pending |
| CONT-04 | Phase 1 | Pending |
| CONT-05 | Phase 1 | Pending |
| CONT-06 | Phase 1 | Pending |
| CONT-07 | Phase 1 | Pending |
| CONT-08 | Phase 3 | Pending |
| CONT-09 | Phase 3 | Pending |
| DOCX-01 | Phase 1 | Pending |
| DOCX-02 | Phase 1 | Pending |
| DOCX-03 | Phase 1 | Pending |
| DOCX-04 | Phase 1 | Pending |
| DOCX-05 | Phase 2 | Pending |
| PDF-01 | Phase 2 | Pending |
| PDF-02 | Phase 2 | Pending |
| PDF-03 | Phase 2 | Pending |
| OUT-01 | Phase 2 | Pending |
| OUT-02 | Phase 2 | Pending |
| OUT-03 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 31 total
- Mapped to phases: 31
- Unmapped: 0

---
*Requirements defined: 2026-04-01*
*Last updated: 2026-04-01 after roadmap creation*
