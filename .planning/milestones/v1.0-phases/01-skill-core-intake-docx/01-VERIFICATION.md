---
phase: 01-skill-core-intake-docx
verified: 2026-04-01T00:00:00Z
status: gaps_found
score: 4/5 success criteria verified
gaps:
  - truth: "User can invoke the skill from a non-PBI directory, complete the intake wizard, and receive a .docx file without errors"
    status: partial
    reason: "SCAF-04 requires Playwright dependency detection; neither SKILL.md nor generate.py check for playwright. Playwright is a Phase 2 dependency, but REQUIREMENTS.md marks SCAF-04 as Phase 1 complete with explicit mention of Playwright. This is a spec gap — Phase 1 never uses Playwright — but the requirement as written is not fully satisfied."
    artifacts:
      - path: "~/.claude/skills/pbi-docgen/SKILL.md"
        issue: "Step 0 checks python-docx, Jinja2, PyYAML only — no Playwright check"
      - path: "~/.claude/skills/pbi-docgen/scripts/generate.py"
        issue: "check_dependencies() checks docx, jinja2, yaml — no playwright"
    missing:
      - "Either add playwright to the dependency check, or scope SCAF-04 to Phase 1 dependencies only (python-docx, Jinja2, PyYAML) and update REQUIREMENTS.md accordingly"
human_verification:
  - test: "Run the skill end-to-end with real pbi:docs Markdown output"
    expected: "Intake wizard prompts all 10 fields one at a time, generates .docx with branded cover page and correct prose sections"
    why_human: "Full wizard flow requires interactive conversation; can only verify structure and logic programmatically"
  - test: "Inspect the generated .docx visually in Word"
    expected: "Logos correctly placed, colors match hex inputs, table headers shaded, code blocks in Courier New with grey background, cover page distinct from body"
    why_human: "Visual/typography quality cannot be verified programmatically"
  - test: "Test FR language input in the intake wizard"
    expected: "Wizard warns that FR is planned for Phase 3 and proceeds with EN"
    why_human: "Requires interactive conversation flow"
---

# Phase 1: Skill Core + Intake + DOCX Verification Report

**Phase Goal:** User can invoke the skill from any directory, walk through the intake wizard, and receive a branded .docx document with all detected sections rendered in clear English prose
**Verified:** 2026-04-01
**Status:** gaps_found (1 gap — SCAF-04 Playwright check absent; 4/5 success criteria fully verified)
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (Success Criteria from ROADMAP.md)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | User can invoke from non-PBI directory, complete intake wizard, receive .docx without errors | PARTIAL | SKILL.md wires correctly via ${CLAUDE_SKILL_DIR}; generate.py invoked from /tmp succeeds. Gap: SCAF-04 Playwright check missing (see gaps section). |
| 2 | Generated .docx has branded cover page (client name, logos, colors) and consistent color theming on headings, tables, accents | VERIFIED | build_docx() confirmed: cover page renders client_name, report_name, version, date; heading color == primary_color (FF0000 verified); table header shading uses XML OxmlElement; different_first_page_header_footer=True confirmed |
| 3 | Only sections with actual source content appear — no blank pages or empty headings for missing sections | VERIFIED | md_parser.py: empty sections excluded (tested: "Dataflows" with no content absent from result); docx_builder.py: SECTION_ORDER iteration skips missing keys |
| 4 | M Query section renders audience-appropriate content: plain-English for client, annotated code blocks for internal/IT | VERIFIED | section_mquery.j2 has explicit audience branch: `Do NOT include raw M code` for client; `CODE_BLOCK:` format instructions for internal/IT. Both render correctly |
| 5 | English prose reads as clear, direct, and professional — consistent with Fowler's guidance | VERIFIED | fowler_rules.j2 embedded in all 6 section templates via `{% include 'fowler_rules.j2' %}`. Rules marked MANDATORY. Template renders confirmed for all 6 sections |

**Score:** 4/5 success criteria fully verified (1 partial due to SCAF-04 gap)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `~/.claude/skills/pbi-docgen/SKILL.md` | Intake wizard with 10-field collection, validation, generation orchestration | VERIFIED | 248 lines; all 10 fields present (Steps 0-6); YAML frontmatter with name, description, allowed-tools; ${CLAUDE_SKILL_DIR} invocation pattern |
| `~/.claude/skills/pbi-docgen/scripts/generate.py` | Pipeline entry point: deps check, config load, parse->generate->build | VERIFIED | Substantive (124 lines); all 3 stages wired; stderr/stdout separation; sys.path insertion for skill_root |
| `~/.claude/skills/pbi-docgen/scripts/md_parser.py` | Section detection and extraction from pbi:docs Markdown | VERIFIED | parse_markdown_sources() exports confirmed; code-block guard (_is_in_code_block); empty section skip; multi-file concatenation |
| `~/.claude/skills/pbi-docgen/scripts/content_generator.py` | Jinja2 prompt rendering + claude -p integration | VERIFIED | _render_prompt() and _call_claude() substantive; generate_all_sections() wires all 6 sections; error handling present |
| `~/.claude/skills/pbi-docgen/scripts/docx_builder.py` | Branded DOCX assembly with cover page, headers, tables, code blocks | VERIFIED | 529 lines; build_docx() tested end-to-end; correct .docx output 39KB |
| `~/.claude/skills/pbi-docgen/scripts/utils.py` | Shared utilities: parse_hex_color, validate_file_exists, load_json_config | VERIFIED | All 5 functions present; parse_hex_color tested (rejects invalid hex); load_json_config validates 11 required keys |
| `~/.claude/skills/pbi-docgen/references/section_heading_map.yaml` | 6-section keyword map | VERIFIED | 6 sections (overview, sources, dataflows, mquery, datamodel, maintenance) with correct keyword arrays |
| `~/.claude/skills/pbi-docgen/references/fowler_guidance.md` | Fowler rules for prompt engineering | VERIFIED | 7 rules present; application note present; loaded into fowler_rules.j2 |
| `~/.claude/skills/pbi-docgen/templates/prompts/fowler_rules.j2` | Jinja2 include of Fowler rules | VERIFIED | 11 lines; rules marked MANDATORY; included in all 6 section templates |
| `~/.claude/skills/pbi-docgen/templates/prompts/section_*.j2` | 6 section prompt templates | VERIFIED | All 6 files present: overview, sources, dataflows, mquery, datamodel, maintenance. All include fowler_rules.j2 |
| `~/.claude/skills/pbi-docgen/scripts/__init__.py` | Package init for Python imports | VERIFIED | File exists at confirmed path |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| SKILL.md | scripts/generate.py | `${CLAUDE_SKILL_DIR}/scripts/generate.py` shell invocation | VERIFIED | Line 218; ${CLAUDE_SKILL_DIR} pattern is Claude Code's runtime substitution |
| generate.py | scripts/md_parser.py | `from scripts.md_parser import parse_markdown_sources` | VERIFIED | Line 68; sys.path insertion at line 63 enables resolution from any CWD |
| generate.py | scripts/content_generator.py | `from scripts.content_generator import generate_all_sections` | VERIFIED | Line 69 |
| generate.py | scripts/docx_builder.py | `from scripts.docx_builder import build_docx` | VERIFIED | Line 70 |
| generate.py | scripts/utils.py | `from scripts.utils import load_json_config, ensure_directory, validate_file_exists` | VERIFIED | Line 67 |
| md_parser.py | references/section_heading_map.yaml | `yaml.safe_load` in `_load_section_map()` | VERIFIED | Lines 13-21; path resolved relative to __file__ |
| content_generator.py | templates/prompts/*.j2 | `Jinja2 FileSystemLoader(TEMPLATE_DIR)` | VERIFIED | TEMPLATE_DIR resolves to `../templates/prompts`; all 6 templates load without error |
| templates/prompts/*.j2 | templates/prompts/fowler_rules.j2 | `{% include 'fowler_rules.j2' %}` | VERIFIED | Confirmed in section_overview.j2 and section_mquery.j2; all 6 templates confirmed rendering |
| docx_builder.py | scripts/utils.py | `from scripts.utils import parse_hex_color, ensure_directory` | VERIFIED | Lines 27-28; sys.path insertion at line 27 |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| docx_builder.py `build_docx()` | `sections` dict | `generate_all_sections()` return value | Yes — LLM prose via `claude -p` subprocess | FLOWING |
| docx_builder.py `build_docx()` | `config` dict | JSON file loaded by `load_json_config()` | Yes — user-provided intake values | FLOWING |
| content_generator.py `generate_all_sections()` | `prose` string | `_call_claude()` stdout | Yes — subprocess captures real LLM output | FLOWING |
| md_parser.py `parse_markdown_sources()` | `result` dict | File read from disk + YAML keyword map | Yes — reads actual source MD files | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| generate.py prints usage and exits cleanly when invoked with no args | `python generate.py` from /tmp | "Usage: python generate.py <config.json>" | PASS |
| Dependency check returns True when all deps present | `check_dependencies()` | True | PASS |
| md_parser detects 2 sections from a 3-heading file (1 empty section skipped) | Python test in skill root | ['overview', 'sources'] — dataflows absent | PASS |
| md_parser excludes headings inside fenced code blocks | Python test with ``` fence | Only 2 sections found (code-block heading not detected) | PASS |
| build_docx produces non-empty .docx with correct filename pattern | Python test with dummy logos | 39,116 bytes; filename matches `Client_Report_v1.0_YYYY-MM-DD.docx` | PASS |
| Cover page content includes client_name, report_name, version, date | docx paragraph scan | All 4 values confirmed in paragraph text | PASS |
| Heading color applied at run level matches primary_color | docx paragraph scan | run.font.color.rgb == FF0000 when primary_color='#FF0000' | PASS |
| different_first_page_header_footer = True | docx section property | True | PASS |
| mquery template branches on audience | Template render test | client: "Do NOT include raw M code"; internal: "CODE_BLOCK" | PASS |
| Fowler rules embedded in all 6 section templates | Template render test | "active voice" in rendered prompt for all 6 | PASS |

---

### Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| SCAF-01 | Skill works from any directory | SATISFIED | generate.py uses sys.path insertion relative to __file__; SKILL.md uses ${CLAUDE_SKILL_DIR}; tested from /tmp |
| SCAF-02 | Creates docsgen-assets/ with logos/ and source/ on first run | SATISFIED | SKILL.md Step 1: `mkdir -p docsgen-assets/logos docsgen-assets/source`; utils.py setup_asset_directories() also exists |
| SCAF-03 | Follows Claude Code skill conventions (SKILL.md + scripts/ + templates/ + references/) | SATISFIED | YAML frontmatter present; all 4 directories exist with correct contents |
| SCAF-04 | Detects missing python-docx and Playwright; clear install instructions | PARTIAL | python-docx, Jinja2, PyYAML checked in SKILL.md Step 0 and generate.py check_dependencies(). **Playwright not checked anywhere.** REQUIREMENTS.md explicitly lists Playwright in SCAF-04. Playwright is Phase 2 functionality — this is a requirement scoping issue. |
| INTAK-01 | Step-by-step collection of all 10 fields | SATISFIED | SKILL.md Steps 2 collects all 10 fields in documented order; each field has its own validation |
| INTAK-02 | Language asked every run — never cached | SATISFIED | SKILL.md line 122: "ALWAYS ask this question. NEVER skip it." Line 243 reinforces in Important Rules |
| INTAK-03 | Validates assets present before generation; shows checklist of missing items | SATISFIED | SKILL.md Step 3: 7-item validation checklist; all-at-once display mandated |
| INTAK-04 | Output folder created automatically | SATISFIED | SKILL.md Step 4: `mkdir -p docsgen-output`; generate.py also calls ensure_directory(config["output_dir"]) |
| PARSE-01 | Reads source MD from pbi:docs; no PBIP/PBIX parsing | SATISFIED | md_parser.py reads .md files only; no binary parsing |
| PARSE-02 | Section auto-detection: identifies which of the 6 sections have content | SATISFIED | section_heading_map.yaml with 6 section entries; keyword matching in _match_heading_to_section() |
| PARSE-03 | Sections with no content silently skipped | SATISFIED | md_parser.py: `if not content: continue` (line 101); tested and confirmed |
| CONT-01 | Section 1 — Project overview generated | SATISFIED | section_overview.j2 present; 'overview' in SECTION_ORDER and SECTION_TEMPLATE_MAP |
| CONT-02 | Section 2 — Source systems & architecture generated | SATISFIED | section_sources.j2 present; 'sources' in SECTION_ORDER and SECTION_TEMPLATE_MAP |
| CONT-03 | Section 3 — Dataflows generated (skipped if absent) | SATISFIED | section_dataflows.j2 present; skip-if-absent handled by PARSE-03 + SECTION_ORDER iteration |
| CONT-04 | Section 4 — M Query: plain-English for client, code blocks for internal/IT | SATISFIED | section_mquery.j2 has audience branch confirmed; client excludes raw M code; internal/IT includes annotated CODE_BLOCK format |
| CONT-05 | Section 5 — Data model / SSAS generated | SATISFIED | section_datamodel.j2 present; 'datamodel' in SECTION_ORDER |
| CONT-06 | Section 6 — Troubleshooting, parameters & maintenance generated | SATISFIED | section_maintenance.j2 present; 'maintenance' in SECTION_ORDER |
| CONT-07 | English prose follows Fowler's Modern English Usage | SATISFIED | fowler_rules.j2 with 7 mandatory rules included in all 6 section templates; marked as MANDATORY constraints |
| DOCX-01 | .docx generated via python-docx with all auto-detected sections, headings, paragraphs, tables, code blocks | SATISFIED | build_docx() confirmed; _parse_and_add_prose() handles tables, code blocks, sub-headings, regular text |
| DOCX-02 | Cover page: client name, report name, version, date, client logo, company logo | SATISFIED | _build_cover_page() confirmed; all 6 elements verified in output document |
| DOCX-03 | Primary and accent colors applied consistently via run-level formatting | SATISFIED | _add_colored_heading() uses run.font.color.rgb (never style mutation); _set_cell_background() uses XML shading; heading color verified in live output |
| DOCX-04 | Header/footer on all pages with page numbers; different first-page header with dual logos | SATISFIED | _setup_headers_footers() confirmed; different_first_page_header_footer=True; body footer has PAGE fldSimple; cover has company logo right-aligned |

**Orphaned requirements:** None. All 22 Phase 1 requirement IDs accounted for.

---

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| SKILL.md Step 0 | Playwright dependency not checked; SCAF-04 requires it | Warning | Does not block Phase 1 operation (Playwright unused in Phase 1); becomes a gap if SCAF-04 is interpreted strictly |

No TODO/FIXME/placeholder comments found in any script files. No empty return stubs found. All implementations are substantive.

---

### Human Verification Required

#### 1. Full End-to-End Intake Wizard Flow

**Test:** Invoke the skill with real pbi:docs Markdown output. Walk through all 10 intake fields. Confirm each field is asked individually.
**Expected:** Wizard collects all 10 fields one at a time; validation checklist appears correctly if any field is missing; generation completes and reports output path and file size.
**Why human:** Interactive conversation flow cannot be scripted.

#### 2. Visual Document Quality

**Test:** Open the generated .docx in Microsoft Word. Inspect cover page, section headings, table formatting, code blocks, header/footer.
**Expected:** Logos positioned correctly; primary color on headings matches hex input; table headers have colored background with white text; code blocks in Courier New with grey background and borders; company logo in page header; page numbers in footer.
**Why human:** Typography, spacing, and layout quality require visual inspection. User already confirmed "good overall" with a note about logo placement being improvable (deferred to Phase 2).

#### 3. FR Language Warning

**Test:** At the language field, enter "FR".
**Expected:** Skill warns "French language support is planned for Phase 3. Proceeding with English for now." and continues with EN.
**Why human:** Requires interactive conversation.

---

### Gaps Summary

One gap found, classified as a spec scoping issue rather than a functional defect:

**SCAF-04 Playwright gap:** The requirement explicitly names Playwright as a dependency to detect, but Playwright is not used until Phase 2 (PDF generation). Phase 1 correctly checks all dependencies it actually uses (python-docx, Jinja2, PyYAML). The gap has two valid resolutions: (a) add a Playwright availability check to SKILL.md Step 0 with a note that it is required for Phase 2 PDF generation, or (b) update REQUIREMENTS.md to scope SCAF-04's Playwright mention to Phase 2. Either resolution closes the gap. The Phase 1 pipeline is otherwise fully operational.

All 5 core pipeline modules are substantive and wired. All 10 key links verified. All 6 section templates confirmed. Behavioral spot-checks passed across parsing, building, template rendering, and dependency detection.

---

_Verified: 2026-04-01_
_Verifier: Claude (gsd-verifier)_
