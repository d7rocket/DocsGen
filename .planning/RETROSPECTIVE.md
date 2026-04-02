# Retrospective: DocsGen

## Milestone: v1.0 — MVP

**Shipped:** 2026-04-02
**Phases:** 3 | **Plans:** 9

### What Was Built

1. Claude Code skill scaffolded with 10-field intake wizard and dependency checking
2. 6-section Markdown parser with keyword-matching section detection
3. Branded DOCX via python-docx — cover page, logos, run-level color theming, TOC, headers/footers
4. HTML→PDF pipeline via Playwright with print-first CSS and graceful degradation
5. Single-invocation dual output with predictable naming and completion report
6. Full EN/FR language support — La Grévisse, PBI FR glossary, Fowler hardening, language-aware formatting

### What Worked

- **Phase sequencing:** DOCX before PDF, EN before FR — each phase delivered working output that validated assumptions before adding complexity. No phase revealed a prior phase was wrong.
- **TDD for the parser:** Red-green cycle on md_parser caught a keyword collision issue before it reached production.
- **Run-level formatting over style mutation:** Established in Phase 1 research and held throughout — no silent heading failures encountered.
- **Dual template maps for EN/FR:** Clean separation meant EN and FR templates can evolve independently. No entanglement.
- **Graceful degradation for Playwright:** PDF failure doesn't kill the run — user always gets a .docx. Eliminated a whole class of user-visible errors.

### What Was Inefficient

- **Parallel _prose_to_html() in pdf_builder:** Duplicates logic from docx parsing path. Deferred to avoid Phase 2 refactor risk, but the debt is real. Should be unified in a future polish phase.
- **Dual deploy to ~/.claude and .claude/:** Necessary because Claude Code skill discovery requires the home directory path, but the mechanism is manual. A sync script would reduce friction.
- **Logo placement:** Noted as needing improvement after Phase 1 but not addressed until Phase 2 polish, and still flagged as an opportunity. Should have been a plan task, not an observation.

### Patterns Established

- `SKILL.md` intake → JSON config → Python scripts: clean handoff pattern; reusable for other skills
- `TABLE:` and `CODE_BLOCK:` markers in LLM output: structured content protocol for DOCX builder parsing
- Dual stdout protocol (docx path + pdf path or `PDF_SKIPPED`): machine-readable output for SKILL.md capture
- Lazy-init module-level cache for reference data (FR glossary): avoids per-render disk reads without globals
- Shared language helpers in docx_builder imported by pdf_builder: DRY without circular imports

### Key Lessons

- **Research pays off immediately.** The python-docx run-level vs style-mutation finding from Phase 1 research prevented a class of silent bugs that would have been painful to debug in generated documents.
- **Graceful degradation is worth the extra 10 lines.** The Playwright try/except block took minutes to add and eliminated the most likely production failure mode.
- **Scope discipline held.** Bilingual single-document, real-time preview, and PBIX re-parsing all stayed out of scope. No feature creep.

### Cost Observations

- Sessions: ~4 across 2 days
- Notable: Phase 3 (FR support) was the most complex conceptually but executed fastest — prior phases had established all the patterns needed

---

## Cross-Milestone Trends

| Milestone | Phases | Plans | Days | Scope Creep | Rework |
|-----------|--------|-------|------|-------------|--------|
| v1.0 MVP | 3 | 9 | 2 | None | Minimal (logo polish deferred) |
