# Roadmap: DocsGen

## Milestones

- ✅ **v1.0 MVP** — Phases 1–3 (shipped 2026-04-02) — [archive](milestones/v1.0-ROADMAP.md)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1–3) — SHIPPED 2026-04-02</summary>

- [x] Phase 1: Skill Core + Intake + DOCX (5/5 plans) — completed 2026-04-01
- [x] Phase 2: PDF Pipeline + Output Integration (2/2 plans) — completed 2026-04-02
- [x] Phase 3: French Language + Polish (2/2 plans) — completed 2026-04-02

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Skill Core + Intake + DOCX | v1.0 | 5/5 | Complete | 2026-04-01 |
| 2. PDF Pipeline + Output Integration | v1.0 | 2/2 | Complete | 2026-04-02 |
| 3. French Language + Polish | v1.0 | 2/2 | Complete | 2026-04-02 |
| 4. Generation Quality Overhaul | v1.1 | 0/6 | Planned | — |

### Phase 4: Generation Quality Overhaul

**Goal:** Rewrite the parsing and rendering pipeline with a real Markdown parser (markdown-it-py), fix PDF generation (Playwright `networkidle` hang + broken layout), redesign the HTML template with DigitalOcean-inspired visual style, and update pbi:docs output contract for better synchronicity with docgen.
**Requirements**: D-01 through D-15 (see 4-RESEARCH.md locked decisions)
**Depends on:** Phase 3
**Plans:** 6 plans across 4 waves

Plans:
- [ ] Plan A (Wave 1) — Create `md_renderer.py` + wire `docx_builder` token-walker
- [ ] Plan B (Wave 1) — Wire `pdf_builder` HTML delegation + fix Playwright hang
- [ ] Plan C (Wave 2) — Update all 12 prompt templates to emit standard Markdown
- [ ] Plan D (Wave 3) — Redesign `document.html.j2` with DigitalOcean-inspired CSS
- [ ] Plan E (Wave 3) — Fix DOCX heading font sizes + code block left border
- [ ] Plan F (Wave 4) — Update pbi:docs output contract + final sync verification
