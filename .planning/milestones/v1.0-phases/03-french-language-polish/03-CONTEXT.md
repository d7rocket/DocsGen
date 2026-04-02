# Phase 3: French Language + Polish - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Add French language output support (correct PBI terminology, La Grévisse formal register) and harden English prose against Fowler violations. Both EN and FR outputs must meet professional quality bar suitable for direct client delivery.

This phase does NOT include:
- Bilingual (EN+FR) in a single document — two separate runs, one language each
- New document sections or structural changes to the pipeline
- Visual/layout polish beyond what's needed for language-aware formatting

</domain>

<decisions>
## Implementation Decisions

### French Prompt Strategy
- **D-01:** Separate FR template files per section — `section_overview_fr.j2`, `section_datamodel_fr.j2`, etc. Content generator selects template by language. EN templates stay untouched.
- **D-02:** FR templates include La Grévisse rules, the PBI French glossary (embedded at render time), and FR-specific prose instructions. Each language's template is tuned independently.

### PBI French Glossary
- **D-03:** Glossary lives as a built-in YAML at `~/.claude/skills/pbi-docgen/references/fr_glossary.yaml` — ships with the skill, no user action required.
- **D-04:** Scope is core PBI terms only (~20-30 terms). Essential set: mesure, table, colonne, rapport, tableau de bord, requête, modèle de données, source de données, flux de données, filtre, segment, relation, calcul, indicateur, page, visuel. Embedded verbatim in FR prompt templates at render time.

### Section Headings & Metadata in FR
- **D-05:** Section headings: add a `label_fr` field to the existing `section_heading_map.yaml` alongside `label` (EN). `docx_builder.py` selects by language at render time. Deterministic — no LLM call for headings.
- **D-06:** Cover page date in French: `"le 2 avril 2026"` format — lowercase month, no leading zero, `le` prefix. Aligns with La Grévisse formal document conventions. Implemented via Python locale-independent string formatting (month name lookup dict, not system locale).
- **D-07:** Cover page boilerplate (Version, Prepared for, Confidential, etc.): hard-coded FR strings directly in `docx_builder.py` as a small dict (`EN_KEY → FR_STRING`). Simple, no extra files.

### Fowler EN Hardening
- **D-08:** Harden via stricter prompt wording only — rewrite `fowler_rules.j2` to be more directive: explicit forbidden phrases listed, concrete substitution examples provided, and an instruction to flag violating constructions before writing them. No extra LLM calls; same pipeline.
- **D-09:** No post-generation validation pass — single-call per section preserved.

### Claude's Discretion
- La Grévisse rule selection: which specific rules to embed in FR prompts (grammar, register, sentence structure guidance) — Claude can choose the most applicable rules for formal business French.
- Exact wording of rewritten Fowler rules in fowler_rules.j2 — the constraint is "more directive with examples", implementation wording is Claude's call.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Skill Code
- `~/.claude/skills/pbi-docgen/scripts/content_generator.py` — section generation pipeline; language param must thread through here
- `~/.claude/skills/pbi-docgen/scripts/docx_builder.py` — cover page date, section headings, boilerplate text; language-aware changes land here
- `~/.claude/skills/pbi-docgen/scripts/generate.py` — top-level pipeline; language flows from config JSON
- `~/.claude/skills/pbi-docgen/SKILL.md` — intake wizard; FR warning + EN fallback must be removed for Phase 3

### Existing Reference Files
- `~/.claude/skills/pbi-docgen/references/section_heading_map.yaml` — add `label_fr` fields here
- `~/.claude/skills/pbi-docgen/references/fowler_guidance.md` — source of truth for Fowler rules; fowler_rules.j2 must stay consistent with this

### Existing Templates
- `~/.claude/skills/pbi-docgen/templates/prompts/fowler_rules.j2` — rewrite to be more directive (D-08)
- `~/.claude/skills/pbi-docgen/templates/prompts/section_overview.j2` — reference structure for new FR templates

### Config Schema
- Config JSON already has `"language": "EN"|"FR"` field — no schema change needed

No external specs — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `content_generator.py` `_render_prompt()`: currently takes `section_id` + renders from `SECTION_TEMPLATE_MAP`. Add `language` param; map to `section_{id}_fr.j2` when `language == "FR"`.
- `section_heading_map.yaml`: already structured as YAML list with `id`, `label`, `keywords` — adding `label_fr` per entry is a clean extension.
- `docx_builder.py` `_build_cover_page()`: date is rendered at line ~203 with `strftime('%B %d, %Y')`. Replace with language-aware formatter.

### Established Patterns
- Jinja2 templates with `{% include %}` for shared rule blocks — FR templates should use `{% include 'grevisse_rules.j2' %}` analogous to `fowler_rules.j2`.
- All language context flows via the config dict loaded from JSON — downstream functions just need to accept and thread `language` parameter.
- `claude -p` subprocess call per section — FR prompts are drop-in replacements, no pipeline change needed.

### Integration Points
- `generate.py` `main()`: passes `config["audience"]` to `generate_all_sections()` — needs to also pass `config["language"]`
- `SKILL.md`: lines 139-142 warn FR and force EN — remove warning, remove EN fallback, pass `"language": "FR"` through for real
- `build_docx()` function signature: accepts `config` dict — language already present in config, docx_builder just needs to use it

</code_context>

<specifics>
## Specific Ideas

- La Grévisse rules in prompts: focus on register (formal "vous" context, no anglicisms, correct use of the indicatif/subjonctif in formal prose), not grammar rules that Claude already handles naturally.
- The SKILL.md FR warning removal is a small but critical unlock — it's the gate that currently blocks all FR output.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-french-language-polish*
*Context gathered: 2026-04-02*
