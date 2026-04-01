---
phase: 01-skill-core-intake-docx
plan: 03
subsystem: content-generation
tags: [jinja2, prompts, llm, claude-cli, fowler, audience-switching]
dependency_graph:
  requires: [01-01]
  provides: [content_generator, section_prompts]
  affects: [01-04]
tech_stack:
  added: [jinja2-templates]
  patterns: [claude-p-subprocess, per-section-llm-calls, audience-conditional-prompts]
key_files:
  created:
    - ~/.claude/skills/pbi-docgen/templates/prompts/fowler_rules.j2
    - ~/.claude/skills/pbi-docgen/templates/prompts/section_overview.j2
    - ~/.claude/skills/pbi-docgen/templates/prompts/section_sources.j2
    - ~/.claude/skills/pbi-docgen/templates/prompts/section_dataflows.j2
    - ~/.claude/skills/pbi-docgen/templates/prompts/section_mquery.j2
    - ~/.claude/skills/pbi-docgen/templates/prompts/section_datamodel.j2
    - ~/.claude/skills/pbi-docgen/templates/prompts/section_maintenance.j2
    - ~/.claude/skills/pbi-docgen/scripts/content_generator.py
  modified: []
decisions:
  - Fowler rules included via Jinja2 include directive for DRY compliance across all 6 section templates
  - TABLE: and CODE_BLOCK: markers used as conventions for DOCX builder to parse structured content
  - Per-section error handling allows partial generation (one LLM failure does not block others)
metrics:
  duration: 2m
  completed: 2026-04-01
  tasks: 2
  files_created: 8
---

# Phase 01 Plan 03: Content Generation Engine Summary

Jinja2 prompt templates for all 6 documentation sections plus a shared Fowler rules include, and content_generator.py that renders prompts and calls claude -p per section with audience-aware switching for M Query.

## Tasks Completed

| # | Task | Commit | Key Files |
|---|------|--------|-----------|
| 1 | Create Jinja2 prompt templates for all 6 sections | 3a9dd06 | 7 .j2 files in templates/prompts/ |
| 2 | Create content generator module with claude -p integration | 9abcf37 | scripts/content_generator.py |

## What Was Built

### Jinja2 Prompt Templates (7 files)

**fowler_rules.j2** -- Shared include containing 7 mandatory Fowler writing rules (active voice, no nominalization, no corporate filler, sentence length, directness, concrete nouns, plain connectives). Included by all section templates via `{% include 'fowler_rules.j2' %}`.

**6 section templates** -- Each section has a dedicated prompt template with:
- Section-specific writing instructions (what to cover, structure)
- Client name, report name, and source content variables
- TABLE: marker convention for structured data (sources, datamodel, maintenance)
- CODE_BLOCK: marker convention for M Query code blocks
- Explicit instruction to omit headings and numbering (added programmatically by DOCX builder)

**section_mquery.j2** -- Audience-aware template that switches between:
- `audience == "client"`: Plain-English business summaries, no raw M code
- All other audiences: Annotated M code with inline comments and CODE_BLOCK markers

### Content Generator Module

**content_generator.py** exports `generate_all_sections()` which:
1. Iterates over parsed sections from md_parser output
2. Renders the appropriate Jinja2 prompt template per section
3. Calls `claude -p` via subprocess with utf-8 encoding and 120s timeout
4. Returns a dict keyed by section ID with label and prose fields
5. Handles Windows encoding issues (`errors='replace'`)
6. Catches per-section RuntimeError and continues with remaining sections

## Deviations from Plan

None -- plan executed exactly as written.

## Known Stubs

None -- all functionality is fully wired. The `_call_claude` function makes real subprocess calls to `claude -p` (no mocking or placeholder returns).

## Self-Check: PASSED

All 8 created files verified present in repo. Both task commits (3a9dd06, 9abcf37) verified in git log.
