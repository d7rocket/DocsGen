# Milestones

## v1.0 MVP — Shipped 2026-04-02

**Phases:** 1–3 | **Plans:** 9 | **Timeline:** 2 days (2026-04-01 → 2026-04-02)
**Files:** 64 changed | **LOC:** ~10,154 insertions (1,347 Python LOC in scripts/)

### Delivered

Complete Claude Code skill pipeline: intake wizard → MD parsing → content generation → branded DOCX + PDF dual output, with full EN/FR language support and audience-aware depth.

### Key Accomplishments

1. Full Claude Code skill scaffolded — SKILL.md intake wizard, 10-field sequential collection, dependency checking, asset validation
2. 6-section Markdown parser with keyword-matching section detection and empty-section exclusion
3. Branded DOCX output via python-docx — cover page, dual logos, run-level color theming, TOC, page headers/footers
4. HTML→PDF pipeline via Playwright — print-first CSS, brand colors, page break control, graceful degradation
5. Single-invocation dual output (`.docx` + `.pdf`) with predictable naming convention and completion report
6. French language support — La Grévisse register, PBI FR glossary, language-aware headings/dates/metadata; English Fowler rules hardened

### Archive

- [v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md)
- [v1.0-REQUIREMENTS.md](milestones/v1.0-REQUIREMENTS.md)
