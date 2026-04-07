---
phase: "04"
plan: "PLAN"
subsystem: "generation-pipeline"
tags: [markdown-parser, pdf-fix, css-redesign, prompt-templates]
dependency_graph:
  requires: []
  provides: [unified-markdown-parser, domcontentloaded-fix, digitalocean-css, standard-markdown-prompts]
  affects: [docx_builder, pdf_builder, document.html.j2, all-prompt-templates]
tech_stack:
  added: [markdown-it-py]
  patterns: [token-walker, left-accent-code-blocks, css-custom-properties]
key_files:
  created:
    - .claude/skills/pbi-docgen/scripts/md_renderer.py
    - .claude/skills/pbi-docgen/references/pbi-docs-contract.md
  modified:
    - .claude/skills/pbi-docgen/scripts/docx_builder.py
    - .claude/skills/pbi-docgen/scripts/pdf_builder.py
    - .claude/skills/pbi-docgen/templates/document.html.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_mquery.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_mquery_fr.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_dataflows.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_dataflows_fr.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_overview.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_overview_fr.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_sources.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_sources_fr.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_datamodel.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_datamodel_fr.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_maintenance.j2
    - .claude/skills/pbi-docgen/templates/prompts/section_maintenance_fr.j2
decisions:
  - "markdown-it-py with commonmark preset and table plugin as unified parser"
  - "Token-walker pattern for docx_builder to handle fenced code blocks, tables, headings, inline formatting"
  - "render_prose_html delegation in pdf_builder replaces hand-rolled HTML conversion"
  - "wait_until domcontentloaded instead of networkidle to prevent Playwright hangs"
  - "DigitalOcean left-accent code block pattern for both DOCX and PDF"
  - "Explicit heading font sizes (h1=20pt, h2=14pt, h3=12pt) to avoid style default unreliability"
  - "pbi:docs contract as reference doc since skill lives outside this repo"
metrics:
  duration: "22min"
  completed: "2026-04-07"
  tasks: 9
  files: 34
---

# Phase 04 Plan PLAN: Generation Quality Overhaul Summary

Replaced two diverged hand-rolled Markdown parsers with markdown-it-py token stream, fixed Playwright PDF hang via domcontentloaded, redesigned HTML template with DigitalOcean-inspired CSS, and updated all 12 prompt templates to emit standard Markdown.

## What Was Done

### Wave 1 -- Parser Foundation (Plans A + B)

**Task A1: Created md_renderer.py** -- New unified parse entry point wrapping markdown-it-py. Module-level singleton with commonmark preset and table plugin. Two public functions: `parse_prose()` returns token list, `render_prose_html()` returns HTML string.

**Task A2: Replaced _parse_and_add_prose() in docx_builder.py** -- Removed all TABLE:/CODE_BLOCK:/END_TABLE marker detection. New token-walker iterates markdown-it-py tokens: fence tokens preserve interior blank lines, table tokens extract rows via `_collect_table_rows_from_tokens`, heading tokens use `_inline_children_to_text`, paragraph tokens use `_render_inline_children_to_runs` for bold/italic/code formatting. Added three helper functions.

**Task B1: Replaced _prose_to_html() in pdf_builder.py** -- Removed INLINE_MD_RE regex, `_inline_md_to_html()`, `_table_lines_to_html()`, and the 90-line hand-rolled `_prose_to_html()`. Replaced with one-liner delegation to `render_prose_html()`. Fixed `wait_until` from `networkidle` to `domcontentloaded`. Added `PlaywrightError` catch with helpful error message.

### Wave 2 -- Prompt Template Updates (Plan C)

**Task C1: Updated mquery and dataflows templates** -- Replaced `CODE_BLOCK:` marker instructions with standard fenced code block instructions using `m` language tag in both EN and FR mquery templates. Added standard Markdown instruction to dataflows templates.

**Task C2: Updated remaining 8 templates** -- Replaced `TABLE:` marker instructions with standard pipe table format in sources, datamodel, and maintenance templates (EN + FR). Added standard Markdown instruction to overview templates. All 12 templates now free of legacy markers.

### Wave 3 -- Visual Polish (Plans D + E)

**Task D1: Redesigned document.html.j2 CSS** -- Added `--code-bg`, `--code-border`, `--text` CSS custom properties. Code blocks use DigitalOcean left-accent pattern (4px solid accent border-left). Distinct heading hierarchy (h1=22pt, h2=15pt, h3=12pt). Tables with primary-color headers and clean alternating rows. Print media rules for page-break-inside avoid.

**Task E1: Fixed DOCX heading sizes and code block borders** -- Added explicit `Pt()` sizes to `_add_colored_heading()` (h1=20, h2=14, h3=12, h4=11). Updated `_add_paragraph_border()` with `left_only` parameter for accent-style code blocks. Done inline with Task A2 since they modify the same function.

### Wave 4 -- pbi:docs Contract + Final Sync (Plan F)

**Task F1: Created pbi-docs-contract.md** -- Since pbi:docs lives outside this repo, created reference doc specifying required output format: language-tagged fenced code blocks, standard pipe tables, prohibited legacy markers.

**Task F2: Verified section_heading_map.yaml and full sync** -- Keywords verified as covering all pbi:docs headings. Synced all missing files from `.claude/skills/pbi-docgen/` to `skills/pbi-docgen/` (content_generator, generate, __init__, fowler/grevisse rules, fr_glossary, SKILL.md). End-to-end smoke test passed: DOCX builds (38KB), HTML renders with correct CSS, no legacy markers.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task E1 merged into Task A2 commit**
- **Found during:** Task A2
- **Issue:** Task E1 modifies `_add_colored_heading()` and `_add_paragraph_border()` in docx_builder.py, which Task A2 was already rewriting. Separating them would require an intermediate commit that compiles but has incomplete functionality.
- **Fix:** Implemented E1 changes (heading sizes, left-only border) during A2 execution.
- **Files modified:** docx_builder.py
- **Commit:** e73d823

**2. [Rule 3 - Blocking] Pre-existing skill tree divergence required sync**
- **Found during:** Task F2
- **Issue:** `skills/pbi-docgen/` was missing content_generator.py, generate.py, __init__.py, fowler_rules.j2, grevisse_rules.j2, fr_glossary.yaml, SKILL.md, and section_heading_map.yaml had outdated content (missing FR labels).
- **Fix:** Copied all missing/outdated files from `.claude/skills/pbi-docgen/` to `skills/pbi-docgen/`.
- **Files modified:** 7 files synced
- **Commit:** a074e65

## Decisions Made

1. **markdown-it-py as unified parser** -- Single `_MD` instance at module level with commonmark+table. Both docx_builder and pdf_builder consume its output through different interfaces.
2. **Token-walker over AST** -- Iterates flat token list with type dispatch rather than building an intermediate AST. Simpler, handles all required content types.
3. **domcontentloaded fix** -- Playwright's `networkidle` waits for zero network connections for 500ms, which hangs on `set_content()` since there are no network requests. `domcontentloaded` fires immediately after HTML is parsed.
4. **Left-accent code blocks** -- DigitalOcean pattern: thick left border in accent color, light background. Applied consistently in both DOCX (via XML pBdr) and PDF (via CSS border-left).
5. **pbi:docs contract as reference** -- Since the skill lives separately, a reference document captures the required output format for manual application.

## Known Stubs

None -- all functionality is fully wired. No placeholder text, empty values, or unconnected data sources.

## Commits

| Task | Commit | Message |
|------|--------|---------|
| A1 | a51e39b | feat(04-plan-a): create md_renderer.py unified Markdown parse entry point |
| A2 + E1 | e73d823 | feat(04-plan-a): replace _parse_and_add_prose with markdown-it-py token walker |
| B1 | 9326dc5 | feat(04-plan-b): replace _prose_to_html with md_renderer delegation and fix Playwright hang |
| C1 | e8a39ba | feat(04-plan-c): update mquery and dataflows templates to emit standard Markdown |
| C2 | 9ae8b53 | feat(04-plan-c): update remaining 8 templates to emit standard Markdown |
| D1 | 31bc95a | feat(04-plan-d): redesign document.html.j2 with DigitalOcean-inspired CSS |
| F1 | a4c2910 | docs(04-plan-f): add pbi:docs output contract reference |
| F2 | a074e65 | chore(04-plan-f): sync skill trees and verify section_heading_map.yaml |

## Self-Check: PASSED

All 5 key files verified present. All 8 commits verified in git log.
