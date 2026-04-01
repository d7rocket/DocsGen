# Phase 2: PDF Pipeline + Output Integration - Context

**Gathered:** 2026-04-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Add a PDF output pipeline and wire both outputs from a single skill invocation. Specifically:
- HTML → PDF via Playwright (Jinja2 template rendered by headless Chromium)
- Auto-updateable table of contents inserted in the .docx
- Both `.docx` and `.pdf` produced from one `generate.py` run with consistent file naming and a completion report

French language support and advanced diagram generation are Phase 3+ concerns — out of scope here.

</domain>

<decisions>
## Implementation Decisions

### TOC in .docx (DOCX-05)
- **D-01:** Use a real Word XML TOC field — inject `TOC \o "1-3" \h \z \u` via `python-docx` `OxmlElement`. Word displays "Update this field" on open; user presses F9 (or right-click → Update Field) to refresh page numbers.
- **D-02:** TOC is inserted after the cover page section break and before the first content section. It occupies its own page (page break after TOC).
- **D-03:** TOC field covers heading levels 1–3 (`\o "1-3"`), hyperlinked (`\h`), with dotted leaders and page numbers.

### PDF TOC navigation (PDF-01)
- **D-04:** PDF TOC uses clickable HTML anchor links — `<a href="#section-id">` pointing to `<h2 id="section-id">` on each section heading. Playwright/Chromium preserves these as clickable links in the PDF output (navigable in Acrobat, Edge PDF viewer, Chrome PDF viewer).
- **D-05:** Section IDs are generated deterministically from section names (slugified: lowercase, spaces → hyphens, no special chars).

### HTML template visual style (PDF-01, PDF-03)
- **D-06:** PDF mirrors the .docx visual identity — same cover page layout (client logo centered, company logo bottom-right, report metadata), branded body pages with a CSS `@page` header (company logo left, page number center), and the same color hierarchy (primary color for H1, accent for H2, table header shading).
- **D-07:** CSS custom properties for brand colors: `--primary: {{ primary_color }};` and `--accent: {{ accent_color }};` rendered by Jinja2 into a `<style>` block. All color references in the stylesheet use `var(--primary)` / `var(--accent)`.
- **D-08:** Single Jinja2 template (`templates/document.html.j2`) — base HTML with a sections loop. No per-section partials; sections are uniform enough that one template handles all. Cover page is a distinct `<div class="cover-page">` with `page-break-after: always`.
- **D-09:** Print-first CSS: `print-color-adjust: exact`, `@media print` block, `page-break-inside: avoid` on tables and code blocks, embedded Google Fonts or system-safe font stack (no external font calls at render time — must work offline).

### PDF failure handling
- **D-10:** If Playwright is not installed or raises any error during PDF generation, the skill delivers the `.docx` only and prints a clear warning to stderr: the reason Playwright failed, the `.docx` output path, and the pip install command needed to enable PDF. Skill exits 0 (success) — partial delivery is valid output.
- **D-11:** Playwright failure is caught at the `build_pdf()` call in `generate.py`. The `.docx` is already saved before PDF is attempted — no rollback needed.

### Pipeline integration (OUT-01, OUT-02, OUT-03)
- **D-12:** `generate.py` extended with a Stage 4: `build_pdf(sections, config, docx_path)`. Same generated `sections` dict fed to both `build_docx()` and `build_pdf()` — LLM content generation runs once.
- **D-13:** PDF output filename follows the same convention as .docx: `{ClientName}_{ReportName}_v{Version}_{YYYY-MM-DD}.pdf` — same stem, different extension.
- **D-14:** Completion report (OUT-03) printed to stderr lists both output paths and file sizes. If PDF was skipped due to failure, report notes that clearly. SKILL.md captures both paths from stdout (generate.py prints `.docx` path then `.pdf` path, or `.docx` path + `PDF_SKIPPED` sentinel).

### Claude's Discretion
- Exact CSS for the cover page layout (logo sizing, spacing, font weights) — must look polished but exact values are implementation detail
- Font stack choice (system fonts vs. embedded web fonts) — offline-safe is required; specific fonts are Claude's call
- How to structure the Jinja2 `sections` loop (dict vs. ordered list of dicts)
- Exact python-docx OxmlElement XML snippet for the TOC field
- Whether to add a "Please press F9 to update page numbers" note below the TOC placeholder

</decisions>

<specifics>
## Specific Ideas

- Cover page layout confirmed: client logo centered (large), company logo bottom-right, report title/client/version/date as text block. Body pages: company logo left header, centered page number footer.
- Clickable PDF TOC — user expects the PDF to be navigable in Acrobat/Edge/Chrome PDF viewer, not just printable.
- Phase 1 note: logo placement in .docx was flagged for improvement — Phase 2 is the opportunity to polish this, particularly the cover page balance.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project requirements
- `.planning/REQUIREMENTS.md` — Phase 2 requirements: PDF-01, PDF-02, PDF-03, DOCX-05, OUT-01, OUT-02, OUT-03 (see Traceability table)
- `.planning/PROJECT.md` — Core value statement, constraints, quality bar ("suitable for direct client delivery without post-processing")

### Technology stack
- `CLAUDE.md` §Technology Stack — Playwright 1.58.0 and python-docx 1.2.0 version pins, HTML→PDF benchmark rationale, Jinja2 3.1.6
- `CLAUDE.md` §Custom Color Themes — `colors.yaml` schema, RGBColor pattern (run-level, not style mutation) — CSS must mirror this pattern

### Phase 1 decisions (locked patterns to extend, not replace)
- `.planning/phases/01-skill-core-intake-docx/01-CONTEXT.md` — D-14/D-15 (run-level color formatting), D-20/D-21/D-22 (generate.py entry point and JSON config schema), D-23 (skill directory structure)

### Existing implementation
- `.claude/skills/pbi-docgen/scripts/generate.py` — Current pipeline entry point; Phase 2 adds Stage 4 here
- `.claude/skills/pbi-docgen/scripts/docx_builder.py` — `build_docx()` function; TOC injection added here
- `.claude/skills/pbi-docgen/SKILL.md` — Needs update to capture both output paths and report completion with sizes

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `generate.py` `main()` — Stage 4 (`build_pdf`) slots in after Stage 3 (`build_docx`). `sections` dict and `config` dict already available.
- `docx_builder.py` `build_docx()` — TOC insertion needed after cover page section break; output filename logic already at lines 511–516 (PDF filename reuses same stem).
- `generate.py` `check_dependencies()` — Playwright already checked as non-blocking warning; Phase 2 changes nothing here — failure handling is in `build_pdf()`.

### Established Patterns
- Config schema (D-22) is stable: `{client_name, client_logo, company_logo, primary_color, accent_color, language, audience, report_name, version, source_files[], output_dir}`. No new fields needed for PDF.
- Run-level color application (D-14/D-15) is the locked pattern for .docx; CSS custom properties mirror this for HTML.
- stderr for progress, stdout for output paths — Phase 2 extends stdout to emit two lines (`.docx` path, `.pdf` path or `PDF_SKIPPED`).

### Integration Points
- `generate.py` Stage 4 calls a new `scripts/pdf_builder.py` module (consistent with existing module-per-stage pattern)
- Jinja2 HTML template goes in `.claude/skills/pbi-docgen/templates/document.html.j2`
- SKILL.md updated to capture the second stdout line (PDF path) and include both in the completion message

</code_context>

<deferred>
## Deferred Ideas

- PDF bookmarks (named destinations) — Playwright's Chromium PDF does not natively export PDF bookmarks from HTML; anchor links are the closest equivalent. True PDF bookmarks would require a post-processing library (pypdf, pikepdf). Deferred — anchor links satisfy navigability requirement.
- Config reuse (save client config for repeat runs) — v2 requirement CFG-01/CFG-02, not this phase.
- ASCII / ERD diagrams — v2 requirement DIAG-01/DIAG-02, not this phase.
- French language — Phase 3.

</deferred>

---

*Phase: 02-pdf-pipeline-output-integration*
*Context gathered: 2026-04-01*
