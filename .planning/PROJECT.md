# DocsGen — PBI Documentation Skill

## What This Is

A Claude Code skill that takes Power BI project documentation (Markdown files from the existing `pbi:docs` skill) plus branding assets and generates polished formal deliverables — `.docx` and HTML→PDF — for internal teams, client stakeholders, and IT. The skill handles everything from intake (logos, colors, language) to structured multi-section output, eliminating the gap between raw PBI analysis and presentation-ready documentation.

## Core Value

Turn structured PBI Markdown docs into client-ready Word/PDF deliverables with correct branding, language, and audience-appropriate depth — in one skill invocation.

## Requirements

### Validated

- [x] Skill works from any directory; creates organized subfolder structure on first run — *Validated Phase 1*
- [x] Step-by-step intake wizard captures all required inputs — *Validated Phase 1*
- [x] Source material: MD files from `pbi:docs` skill (no PBIP re-parsing) — *Validated Phase 1*
- [x] Auto-detect which of the 6 sections are present and include only relevant ones — *Validated Phase 1*
- [x] 6 documentation sections generated from source MD — *Validated Phase 1*
- [x] Output: `.docx` via python-docx with branding (colors, logos, header/footer) — *Validated Phase 1*
- [x] Output: Styled HTML → PDF via Playwright (print-quality layout) — *Validated Phase 2*
- [x] Both `.docx` and `.pdf` produced in a single skill invocation — *Validated Phase 2*
- [x] Navigable TOC in both documents (Word XML field + clickable PDF anchors) — *Validated Phase 2*
- [x] M Query section depth is audience-driven — *Validated Phase 1*
- [x] Color scheme applied to headings, tables, accents throughout document — *Validated Phase 1*
- [x] Client and company logos incorporated on cover page and headers — *Validated Phase 1*
- [x] Language-aware prose: French follows La Grévisse with PBI FR glossary — *Validated Phase 3*
- [x] English prose hardened against Fowler violations (explicit forbidden phrases, substitution examples) — *Validated Phase 3*
- [x] Section headings, dates, metadata formatted per selected language (EN and FR) — *Validated Phase 3*

### Active

- [x] Fenced code blocks with interior blank lines render correctly in both DOCX and PDF — *Validated Phase 4*
- [x] Unified Markdown parser (markdown-it-py) drives both DOCX token-walker and PDF HTML rendering — *Validated Phase 4*
- [x] Playwright PDF generation uses `domcontentloaded` (no hang) — *Validated Phase 4*
- [x] DigitalOcean-inspired HTML template: left-accent code blocks, distinct heading hierarchy, clean tables — *Validated Phase 4*
- [x] All 12 prompt templates emit standard Markdown (no `TABLE:`/`CODE_BLOCK:`/`END_TABLE` markers) — *Validated Phase 4*
- [x] DOCX headings use explicit font sizes: h1=20pt, h2=14pt, h3=12pt — *Validated Phase 4*

### Out of Scope

- Re-reading or re-parsing `.pbip` / `.pbix` files — the existing `pbi:docs` skill handles that; this skill consumes its output
- Bilingual (EN+FR) in a single document — two separate runs, one language each
- Interactive real-time preview of document during generation — generate-then-open workflow

## Context

- **Shipped:** v1.0 MVP (2026-04-02) — complete pipeline from intake to dual DOCX+PDF output with EN/FR language support. Phase 4 complete (2026-04-07) — unified markdown-it-py parser, DigitalOcean HTML template, Playwright hang fix, standard Markdown prompts.
- **Codebase:** ~1,347 Python LOC in `scripts/` (md_parser, utils, content_generator, docx_builder, pdf_builder, generate.py); 6 EN + 6 FR Jinja2 prompt templates; FR glossary + Fowler + Grévisse reference files
- **Existing skill:** `pbi:docs` lives in `.claude/skills/` and produces detailed Markdown from PBIP projects — that MD is this skill's primary input
- **Skill location:** `~/.claude/skills/pbi-docgen/` (runtime) and `.claude/skills/pbi-docgen/` (repo)
- **Target users:** Devesh uses this professionally; output goes to clients and internal teams. Polish matters.
- **Language standards:** English prose against Fowler's *Modern English Usage*; French against La Grévisse + built-in PBI FR glossary (~20 terms). Applied during generation, not post-hoc.
- **Asset management:** Skill creates `docsgen-assets/` subfolder where user drops logos, color config, and source MD files before generation begins.
- **Known polish opportunities:** Logo placement in .docx header; parallel _prose_to_html() in pdf_builder could be unified with docx path (deferred to avoid refactor risk during Phase 2)

## Constraints

- **Dependency:** Requires existing PBI Markdown docs as input — skill is not standalone without them
- **Python:** Output generation requires Python (python-docx) and Node (Playwright) or equivalent — skill must check for these and surface clear errors
- **Asset folder:** User must populate `docsgen-assets/` before generation; skill guides them through what's needed
- **Language:** Per-run language selection — EN or FR, not both simultaneously
- **Quality bar:** Output must look clean and professional — suitable for direct client delivery without post-processing in Word. Typography, spacing, color application, and layout must be intentional and polished.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use existing PBI skill output as source, not raw PBIP | Avoids duplicating heavy PBIP parsing logic; separation of concerns | Validated Phase 1 |
| .docx via python-docx + HTML→PDF dual output | User explicitly requested both formats | Validated Phase 2 |
| Language asked every run (not config default) | PBI projects span EN and FR clients; asking prevents wrong-language docs | Validated Phase 1 |
| Auto-detect sections from source MD | Prevents empty sections when a feature (e.g. Dataflows) isn't used in the project | Validated Phase 1 |
| Assets managed via `docsgen-assets/` subfolder | Gives user a predictable drop-zone; skill can validate presence before proceeding | Validated Phase 1 |
| Word XML TOC field (`TOC \o "1-3" \h \z \u`) | Auto-updateable TOC without Word template dependency | Validated Phase 2 |
| PDF TOC via HTML anchor links | Playwright preserves `<a href="#id">` as clickable PDF links; no post-processing needed | Validated Phase 2 |
| Playwright failure → deliver .docx only, exit 0 | Graceful degradation; user always gets something usable | Validated Phase 2 |
| Separate FR prompt templates (not EN injection) | FR and EN templates tune independently; EN templates stay untouched | Validated Phase 3 |
| Built-in fr_glossary.yaml in references/ | Ships with skill, no user action required; ~20 core PBI terms | Validated Phase 3 |
| FR date format "le 2 avril 2026" via month-name dict | Locale-independent (locale.setlocale() is thread-unsafe on Windows) | Validated Phase 3 |
| docx_builder helpers imported by pdf_builder | DRY — format_date, get_section_label, COVER_BOILERPLATE defined once | Validated Phase 3 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-02 after v1.0 milestone completion*
