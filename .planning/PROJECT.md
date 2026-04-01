# DocsGen — PBI Documentation Skill

## What This Is

A Claude Code skill that takes Power BI project documentation (Markdown files from the existing `pbi:docs` skill) plus branding assets and generates polished formal deliverables — `.docx` and HTML→PDF — for internal teams, client stakeholders, and IT. The skill handles everything from intake (logos, colors, language) to structured multi-section output, eliminating the gap between raw PBI analysis and presentation-ready documentation.

## Core Value

Turn structured PBI Markdown docs into client-ready Word/PDF deliverables with correct branding, language, and audience-appropriate depth — in one skill invocation.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Skill works from any directory; creates organized subfolder structure on first run
- [ ] Step-by-step intake wizard captures: source MD files, client name, client logo, company logo, color scheme, language (EN/FR), audience type, report name/version
- [ ] Source material: MD files from the existing `pbi:docs` skill (PBIP analysis already done — no re-reading PBIP files)
- [ ] Auto-detect which of the 6 sections are present in source MD and include only relevant sections
- [ ] 6 documentation sections: (1) Project overview + technical diagrams, (2) Source systems & architecture, (3) Dataflows, (4) M Query business logic, (5) Data Model / SSAS, (6) Troubleshooting, parameters & maintenance
- [ ] Output: `.docx` via python-docx with branding applied (colors, logos, header/footer)
- [ ] Output: Styled HTML → PDF via headless browser (print-quality layout)
- [ ] Language-aware prose: English follows Fowler's *Modern English Usage*; French follows La Grévisse
- [ ] M Query section depth is audience-driven: plain-English summaries for client, annotated code blocks for internal
- [ ] Color scheme applied to headings, tables, accents throughout document
- [ ] Client and company logos incorporated on cover page and headers

### Out of Scope

- Re-reading or re-parsing `.pbip` / `.pbix` files — the existing `pbi:docs` skill handles that; this skill consumes its output
- Bilingual (EN+FR) in a single document — two separate runs, one language each
- Interactive real-time preview of document during generation — generate-then-open workflow

## Context

- **Existing skill:** `pbi:docs` (or `pbi:docs` equivalent) lives in `.claude/skills/` and already produces detailed Markdown documentation from PBIP projects. That MD output is the primary input here.
- **Skill location:** Claude Code skill — `skill.md` + `agents.md` in `~/.claude/skills/pbi-docgen/`
- **Target users:** Devesh uses this professionally; output goes to clients and internal teams. Polish matters.
- **Language standards:** English prose reviewed against Fowler's *Modern English Usage* (H.W. Fowler); French against La Grévisse. Applied during prose generation, not post-hoc.
- **python-docx:** Available in the Python ecosystem; headless browser (Playwright or Puppeteer) for HTML→PDF.
- **Asset management:** Skill creates a `docsgen-assets/` subfolder where user drops logos, color config, and source MD files before generation begins.

## Constraints

- **Dependency:** Requires existing PBI Markdown docs as input — skill is not standalone without them
- **Python:** Output generation requires Python (python-docx) and Node (Playwright) or equivalent — skill must check for these and surface clear errors
- **Asset folder:** User must populate `docsgen-assets/` before generation; skill guides them through what's needed
- **Language:** Per-run language selection — EN or FR, not both simultaneously

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use existing PBI skill output as source, not raw PBIP | Avoids duplicating heavy PBIP parsing logic; separation of concerns | — Pending |
| .docx via python-docx + HTML→PDF dual output | User explicitly requested both formats | — Pending |
| Language asked every run (not config default) | PBI projects span EN and FR clients; asking prevents wrong-language docs | — Pending |
| Auto-detect sections from source MD | Prevents empty sections when a feature (e.g. Dataflows) isn't used in the project | — Pending |
| Assets managed via `docsgen-assets/` subfolder | Gives user a predictable drop-zone; skill can validate presence before proceeding | — Pending |

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
*Last updated: 2026-04-01 after initialization*
