# Phase 1: Skill Core + Intake + DOCX - Context

**Gathered:** 2026-04-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Skill scaffolding, intake wizard, MD parsing, English content generation, and branded `.docx` output. User can invoke the skill from any directory, complete the intake wizard, and receive a `.docx` file with all detected sections rendered in clear English prose with brand colors and logos applied.

PDF output, TOC, and French language are Phase 2 and 3 concerns — explicitly out of scope here.

</domain>

<decisions>
## Implementation Decisions

### Content generation engine
- **D-01:** LLM-generated prose — Claude writes professional prose for each section from source MD content. Skill calls back to Claude via `claude -p` subprocess with section-specific prompts.
- **D-02:** Quality bar rationale: template prose cannot meet Fowler's compliance requirement or produce "suitable for direct client delivery" output without significant hardcoding per section type.
- **D-03:** Audience awareness implemented in the LLM prompt: M Query section prompt switches between plain-English summary (client/IT audience) and annotated code block mode (internal audience) based on intake selection.
- **D-04:** Each of the 6 sections is a separate LLM call with section-specific prompt — allows independent tone tuning and avoids context overflow for large PBI projects.

### Intake wizard UX
- **D-05:** Asset-first flow — skill checks `docsgen-assets/` before asking any questions. Only prompts for items that are missing or not yet configured.
- **D-06:** On first run (empty assets folder): sequential one-field-at-a-time prompts with immediate validation. Fields: source MD file(s), client name, client logo path, company logo path, primary color (hex), accent color (hex), language (EN/FR), audience type (internal/client/IT), report name, version number.
- **D-07:** Language (EN/FR) is always asked — never cached or inferred — per INTAK-02.
- **D-08:** Validation is pre-generation: all required assets checked and present before any Python subprocess is launched. Missing items surfaced as a checklist, not one-by-one errors mid-run.
- **D-09:** `docsgen-assets/` created automatically on first run with subdirectories `logos/` and `source/` — no manual folder creation needed.

### MD parsing strategy
- **D-10:** Heading-based section detection — parse `##` headings in source Markdown to map content to the 6 known section categories. No modifications to pbi:docs output format required.
- **D-11:** Section mapping uses heading keyword matching (e.g., "Overview" → Section 1, "Data Source" / "Gateway" → Section 2, "Dataflow" → Section 3, "M Query" / "Power Query" → Section 4, "Data Model" / "SSAS" → Section 5, "Parameter" / "Troubleshooting" / "Maintenance" → Section 6).
- **D-12:** Sections with no matched content in source MD are silently skipped (PARSE-03). No blank pages, no empty headings. The generated document only contains sections that have actual source material.
- **D-13:** Source MD can be a single file or multiple files — parser concatenates content before section detection.

### DOCX document architecture
- **D-14:** Built-in Word styles as base + run-level color overrides. Use `Heading 1`, `Heading 2`, `Normal`, `Code` (custom added once) as style names. Brand colors applied via `run.font.color.rgb = RGBColor(r, g, b)` — never via style mutation.
- **D-15:** This pattern is locked from day one — avoids the silent style mutation failures noted in project research. All heading color application goes through run-level formatting.
- **D-16:** Table header shading via `set_cell_background` (XML-level via OxmlElement) with primary brand color. Body rows use alternating white / very light tint of accent color.
- **D-17:** Cover page is a dedicated section with `WD_SECTION_START.NEW_PAGE`. Contains: client logo (centered, large), company logo (bottom-right), client name (large, bold, primary color), report name, version, date.
- **D-18:** Header/footer on all non-cover pages: company logo left-aligned (~1 inch width) in header, page number centered in footer. Cover page uses `different_first_page_header_footer = True` on the section.
- **D-19:** Code blocks (M Query) rendered in a `Code` style with Courier New 9pt, light grey background shading, 1pt border — added as a custom style once at document creation.

### Skill script entry point
- **D-20:** SKILL.md handles the entire intake conversation (Claude-native, no Python needed for intake). Once all inputs are validated, SKILL.md calls `scripts/generate.py` via Bash tool with a structured JSON argument payload.
- **D-21:** `generate.py` is the single entry point — internally organized as clear pipeline stages: `parse_md()` → `generate_sections()` → `build_docx()`. No separate invocable scripts per stage.
- **D-22:** `generate.py` reads a JSON config from stdin or a temp file (passed by SKILL.md) — not positional CLI args. Config schema: `{client_name, client_logo, company_logo, primary_color, accent_color, language, audience, report_name, version, source_files[], output_dir}`.
- **D-23:** Skill directory structure follows Claude Code conventions: `~/.claude/skills/pbi-docgen/SKILL.md` + `scripts/generate.py` + `scripts/templates/` (Jinja2 section prompt templates) + `references/` (Fowler guidance, section heading maps).

### English prose quality
- **D-24:** Fowler's compliance is enforced via LLM prompt instruction, not post-hoc linting. The section generation prompt includes 4-5 explicit Fowler rules: no needless passives, no nominalization padding ("the utilization of" → "using"), no corporate filler ("leverage", "synergy"), prefer active voice, keep sentences under 25 words.
- **D-25:** Prose is generated fresh each run — not cached. Source MD quality is expected to be structured technical documentation; Claude translates to audience-appropriate formal English.

### Claude's Discretion
- Exact Jinja2 prompt template structure for each section type
- Specific RGBColor values for the "light tint" alternating table rows
- python-docx paragraph spacing (before/after pt values) for headings and body
- How to handle very long M Query code blocks (line wrapping vs horizontal scroll in .docx)
- Whether to use `add_paragraph` or `add_run` chaining for mixed-format paragraphs

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project requirements
- `.planning/REQUIREMENTS.md` — Full v1 requirement list; Phase 1 requirements are SCAF-01–04, INTAK-01–04, PARSE-01–03, CONT-01–07, DOCX-01–04
- `.planning/PROJECT.md` — Core value statement, constraints, out-of-scope items

### Technology stack
- `CLAUDE.md` §Technology Stack — python-docx 1.2.0, Playwright 1.58.0, Jinja2 3.1.6 version pins and rationale
- `CLAUDE.md` §Custom Color Themes — Color application strategy, RGBColor pattern, `colors.yaml` config schema

### Skill framework
- `CLAUDE.md` §Skill Directory Structure — Claude Code skill conventions (SKILL.md frontmatter, `scripts/`, `templates/`, `references/`)

No external ADRs or design docs exist yet — requirements are fully captured in REQUIREMENTS.md and decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — greenfield project. No existing components, scripts, or utilities to reuse.

### Established Patterns
- None yet — this is Phase 1. Patterns established here become the baseline for Phase 2.

### Integration Points
- `pbi:docs` skill output (source MD files) → input to Phase 1 parser
- `docsgen-assets/` folder → user drop-zone for logos and color config
- `~/.claude/skills/pbi-docgen/` → skill installation location

</code_context>

<deferred>
## Deferred Ideas

- Config reuse (save client config for repeat runs) — v2 requirement CFG-01/CFG-02, not Phase 1
- ASCII / ERD diagrams — v2 requirement DIAG-01/DIAG-02, not Phase 1
- Table of contents in .docx — Phase 2 requirement DOCX-05
- PDF output — Phase 2 entirely

</deferred>

---

*Phase: 01-skill-core-intake-docx*
*Context gathered: 2026-04-01*
