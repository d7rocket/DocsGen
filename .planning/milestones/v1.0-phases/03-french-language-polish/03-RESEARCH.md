# Phase 3: French Language + Polish - Research

**Researched:** 2026-04-02
**Domain:** Internationalization (FR), prompt engineering (Fowler/Grevisse), PBI terminology
**Confidence:** HIGH

## Summary

Phase 3 adds French language document generation to the existing DocsGen pipeline and hardens English prose quality. The architecture is straightforward: 6 new FR Jinja2 prompt templates (one per section) that include a shared `grevisse_rules.j2` block and an embedded PBI French glossary, mirroring the existing EN pattern of `section_*.j2` including `fowler_rules.j2`. The pipeline already has the `language` field in the config JSON -- the work is threading it through `content_generator.py` (template selection), `docx_builder.py` (cover page date, section headings, boilerplate), `pdf_builder.py` (HTML template date/lang attribute), and `SKILL.md` (remove FR warning gate).

No new libraries are required. No schema changes to the config JSON. No structural changes to the pipeline stages. All changes are content (new templates, glossary YAML, heading labels) and routing logic (language-conditional branching in 3-4 functions).

**Primary recommendation:** Implement as two waves -- (1) FR template infrastructure + content_generator routing + glossary, then (2) docx_builder/pdf_builder language-aware formatting + SKILL.md unlock + Fowler hardening.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Separate FR template files per section -- `section_overview_fr.j2`, `section_datamodel_fr.j2`, etc. Content generator selects template by language. EN templates stay untouched.
- **D-02:** FR templates include La Grevisse rules, the PBI French glossary (embedded at render time), and FR-specific prose instructions. Each language's template is tuned independently.
- **D-03:** Glossary lives as a built-in YAML at `~/.claude/skills/pbi-docgen/references/fr_glossary.yaml` -- ships with the skill, no user action required.
- **D-04:** Scope is core PBI terms only (~20-30 terms). Essential set: mesure, table, colonne, rapport, tableau de bord, requete, modele de donnees, source de donnees, flux de donnees, filtre, segment, relation, calcul, indicateur, page, visuel. Embedded verbatim in FR prompt templates at render time.
- **D-05:** Section headings: add a `label_fr` field to the existing `section_heading_map.yaml` alongside `label` (EN). `docx_builder.py` selects by language at render time. Deterministic -- no LLM call for headings.
- **D-06:** Cover page date in French: `"le 2 avril 2026"` format -- lowercase month, no leading zero, `le` prefix. Aligns with La Grevisse formal document conventions. Implemented via Python locale-independent string formatting (month name lookup dict, not system locale).
- **D-07:** Cover page boilerplate (Version, Prepared for, Confidential, etc.): hard-coded FR strings directly in `docx_builder.py` as a small dict (`EN_KEY -> FR_STRING`). Simple, no extra files.
- **D-08:** Harden via stricter prompt wording only -- rewrite `fowler_rules.j2` to be more directive: explicit forbidden phrases listed, concrete substitution examples provided, and an instruction to flag violating constructions before writing them. No extra LLM calls; same pipeline.
- **D-09:** No post-generation validation pass -- single-call per section preserved.

### Claude's Discretion
- La Grevisse rule selection: which specific rules to embed in FR prompts (grammar, register, sentence structure guidance) -- Claude can choose the most applicable rules for formal business French.
- Exact wording of rewritten Fowler rules in fowler_rules.j2 -- the constraint is "more directive with examples", implementation wording is Claude's call.

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CONT-08 | French prose follows La Grevisse guidelines (correct register, PBI-specific FR terminology applied via glossary) | FR templates with grevisse_rules.j2 include + glossary YAML embedded at render time; content_generator routes to FR templates when language=="FR" |
| CONT-09 | Section headings, dates, and metadata formatted per selected language | label_fr in section_heading_map.yaml; locale-independent FR date formatter; boilerplate dict in docx_builder.py; HTML template lang attribute |
</phase_requirements>

## Standard Stack

No new libraries required. All work uses existing dependencies.

### Core (already installed)
| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| python-docx | 1.2.0 | DOCX generation | Already in use |
| Jinja2 | 3.1.6 | Template rendering (EN + new FR templates) | Already in use |
| PyYAML | Latest | Reading section_heading_map.yaml + new fr_glossary.yaml | Already in use |
| Playwright | 1.58.0 | PDF generation (HTML date/lang attribute update) | Already in use |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (none new) | - | - | - |

**Installation:** No new packages needed.

## Architecture Patterns

### File Layout for New FR Content

```
~/.claude/skills/pbi-docgen/
  references/
    section_heading_map.yaml      # MODIFY: add label_fr per entry
    fowler_guidance.md            # UNCHANGED (reference doc)
    fr_glossary.yaml              # NEW: ~20-30 PBI FR terms
  templates/
    prompts/
      fowler_rules.j2             # MODIFY: more directive wording
      grevisse_rules.j2           # NEW: FR writing quality rules
      section_overview.j2         # UNCHANGED
      section_overview_fr.j2      # NEW: FR variant
      section_sources_fr.j2       # NEW: FR variant
      section_dataflows_fr.j2     # NEW: FR variant
      section_mquery_fr.j2        # NEW: FR variant
      section_datamodel_fr.j2     # NEW: FR variant
      section_maintenance_fr.j2   # NEW: FR variant
    document.html.j2              # MODIFY: lang attribute + FR date
  scripts/
    content_generator.py          # MODIFY: language param + FR template map
    docx_builder.py               # MODIFY: FR date, headings, boilerplate
    pdf_builder.py                # MODIFY: FR date, HTML lang attribute
    generate.py                   # MODIFY: thread language to generate_all_sections
  SKILL.md                        # MODIFY: remove FR warning + EN fallback
```

### Pattern 1: Language-Conditional Template Routing

**What:** `content_generator.py` selects EN or FR template based on language param.
**When to use:** Every section generation call.
**Example:**

```python
# content_generator.py — add FR template map alongside existing EN map

SECTION_TEMPLATE_MAP: dict[str, str] = {
    'overview': 'section_overview.j2',
    'sources': 'section_sources.j2',
    # ... existing EN templates
}

SECTION_TEMPLATE_MAP_FR: dict[str, str] = {
    'overview': 'section_overview_fr.j2',
    'sources': 'section_sources_fr.j2',
    'dataflows': 'section_dataflows_fr.j2',
    'mquery': 'section_mquery_fr.j2',
    'datamodel': 'section_datamodel_fr.j2',
    'maintenance': 'section_maintenance_fr.j2',
}

def _render_prompt(section_id, source_content, client_name, report_name, audience, language="EN"):
    template_map = SECTION_TEMPLATE_MAP_FR if language == "FR" else SECTION_TEMPLATE_MAP
    template = env.get_template(template_map[section_id])
    return template.render(
        client_name=client_name,
        report_name=report_name,
        source_content=source_content,
        audience=audience,
    )
```

### Pattern 2: Glossary Embedding at Render Time

**What:** FR templates load the glossary YAML and embed terms directly in the prompt.
**When to use:** Every FR template.
**Example:**

```jinja2
{# section_overview_fr.j2 #}
{% include 'grevisse_rules.j2' %}

**Glossaire PBI francais -- utilisez TOUJOURS ces termes:**
{% for term in glossary %}
- {{ term.en }}: {{ term.fr }}
{% endfor %}

Vous redigez la Section 1 : Apercu du projet pour un livrable de documentation Power BI.
...
```

The glossary variable must be passed into `template.render()`. Load it once in `_render_prompt()` when `language == "FR"`:

```python
import yaml

_FR_GLOSSARY = None

def _load_fr_glossary():
    global _FR_GLOSSARY
    if _FR_GLOSSARY is None:
        glossary_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..', 'references', 'fr_glossary.yaml')
        )
        with open(glossary_path, 'r', encoding='utf-8') as f:
            _FR_GLOSSARY = yaml.safe_load(f).get('terms', [])
    return _FR_GLOSSARY
```

### Pattern 3: Locale-Independent FR Date Formatting

**What:** French date string without relying on system locale.
**When to use:** Cover page date in docx_builder.py and pdf_builder.py.
**Example:**

```python
FR_MONTHS = {
    1: 'janvier', 2: 'fevrier', 3: 'mars', 4: 'avril',
    5: 'mai', 6: 'juin', 7: 'juillet', 8: 'aout',
    9: 'septembre', 10: 'octobre', 11: 'novembre', 12: 'decembre',
}

def format_date_fr(d: date) -> str:
    """Format date as 'le 2 avril 2026' (La Grevisse formal convention)."""
    # Note: 1er for first day of month is standard formal French
    day = '1er' if d.day == 1 else str(d.day)
    return f"le {day} {FR_MONTHS[d.month]} {d.year}"

def format_date(d: date, language: str) -> str:
    if language == "FR":
        return format_date_fr(d)
    return d.strftime('%B %d, %Y')
```

### Pattern 4: Section Heading Selection by Language

**What:** Read `label_fr` from section_heading_map.yaml, select by language at render time.
**When to use:** docx_builder section headings, pdf_builder section labels.
**Example for updated YAML:**

```yaml
sections:
  - id: overview
    label: "Project Overview"
    label_fr: "Apercu du projet"
    keywords: ["overview", "summary", "introduction", "about"]
  - id: sources
    label: "Source Systems & Architecture"
    label_fr: "Systemes sources et architecture"
    keywords: ["data source", "gateway", "connection", "source system", "architecture"]
```

Selection logic (reusable helper):

```python
def get_section_label(section_id: str, language: str, heading_map: dict) -> str:
    """Get section heading label in the appropriate language."""
    for section in heading_map.get('sections', []):
        if section['id'] == section_id:
            if language == 'FR':
                return section.get('label_fr', section['label'])
            return section['label']
    return section_id.title()
```

### Pattern 5: Cover Page Boilerplate Dict

**What:** Small inline dict for FR translations of cover page text (D-07).
**Where:** `docx_builder.py`
**Example:**

```python
COVER_BOILERPLATE = {
    'EN': {
        'version_prefix': 'Version',
        'prepared_for': 'Prepared for',
        'confidential': 'Confidential',
    },
    'FR': {
        'version_prefix': 'Version',  # Same in FR
        'prepared_for': 'Prepare pour',
        'confidential': 'Confidentiel',
    },
}
```

### Anti-Patterns to Avoid
- **System locale for FR dates:** Never use `locale.setlocale()` -- it is process-global, platform-dependent (Windows uses different locale names than Linux), and thread-unsafe. Use the lookup dict pattern (Pattern 3).
- **Modifying EN templates:** FR templates are separate files per D-01. Never add `{% if language == "FR" %}` blocks inside existing EN templates.
- **LLM calls for headings/dates/metadata:** Per D-05/D-06, all structural text is deterministic. Only section prose uses LLM.
- **Shared mutable state for glossary:** Load once, cache in module-level variable with lazy init. Do not reload from disk on every template render.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| French date formatting | `locale.setlocale()` | Month name dict lookup | Platform-independent, thread-safe, no system locale dependency |
| PBI FR terminology | Free-form LLM translation | Built-in glossary YAML | Consistent terms across all sections, domain-verified |
| FR writing rules | Ad-hoc prompt instructions | Structured grevisse_rules.j2 include | DRY across all 6 FR templates, same pattern as fowler_rules.j2 |

## Common Pitfalls

### Pitfall 1: Accented Characters in YAML
**What goes wrong:** YAML files with French accents (e, a, etc.) get corrupted if not saved/read as UTF-8.
**Why it happens:** Windows default encoding may not be UTF-8.
**How to avoid:** Always open YAML files with `encoding='utf-8'` in Python. All existing code in the project already does this implicitly via Jinja2's FileSystemLoader (which uses UTF-8 by default).
**Warning signs:** Garbled characters in generated .docx section headings or glossary terms.

### Pitfall 2: Forgetting pdf_builder Date/Lang
**What goes wrong:** PDF output still shows English date and `lang="en"` even when language is FR.
**Why it happens:** `pdf_builder._render_html()` currently hardcodes `date.today().strftime('%B %d, %Y')` (line 224) and the HTML template has `lang="en"` (line 2).
**How to avoid:** Thread `language` through to `_render_html()` and use the same `format_date()` helper. Update `document.html.j2` to use `{{ lang }}` variable.
**Warning signs:** PDF cover page date is English while DOCX is French.

### Pitfall 3: md_parser Label Override
**What goes wrong:** Section labels from `md_parser.parse_markdown_sources()` are EN labels from the YAML. If `docx_builder` uses `section_data['label']` without checking language, FR documents get EN headings.
**Why it happens:** The label is set during parsing (before language is known to the builder).
**How to avoid:** The label from the parser is fine for EN. For FR, override in `docx_builder.build_docx()` and `pdf_builder._render_html()` by re-reading from the heading map with the FR label. Alternatively, load the heading map in the builder and always select by language.
**Warning signs:** Document shows "Project Overview" heading with French prose underneath.

### Pitfall 4: generate_all_sections Missing Language Param
**What goes wrong:** `generate.py` calls `generate_all_sections(parsed, client_name, report_name, audience)` without passing `language`. All output stays English.
**Why it happens:** Function signature doesn't include language -- it was designed EN-only.
**How to avoid:** Add `language` parameter to `generate_all_sections()` and thread it through to `_render_prompt()`.
**Warning signs:** FR config produces English prose.

### Pitfall 5: Fowler Hardening Drift from Reference
**What goes wrong:** Rewritten `fowler_rules.j2` diverges from `fowler_guidance.md` reference document.
**Why it happens:** The two files serve different purposes but must stay consistent per canonical refs.
**How to avoid:** After rewriting `fowler_rules.j2`, verify all 7 rules from `fowler_guidance.md` are present. The .j2 file can be more directive/expanded but must not drop or contradict any rule.
**Warning signs:** Generated EN prose violates a rule that was in the old template but missing from the new one.

### Pitfall 6: SKILL.md FR Gate Partially Removed
**What goes wrong:** The FR warning text is removed but the EN fallback logic is left, or vice versa.
**Why it happens:** Lines 139-142 of SKILL.md are interconnected -- the warning AND the `Set language to "EN"` fallback must both be removed.
**How to avoid:** Remove the entire conditional block (lines 139-142) and let FR pass through as a valid language value.
**Warning signs:** User selects FR but documents generate in EN.

## Code Examples

### FR Glossary YAML Structure (fr_glossary.yaml)

```yaml
# PBI French terminology glossary
# Embedded in FR prompt templates at render time (D-03/D-04)
terms:
  - en: "measure"
    fr: "mesure"
  - en: "table"
    fr: "table"
  - en: "column"
    fr: "colonne"
  - en: "report"
    fr: "rapport"
  - en: "dashboard"
    fr: "tableau de bord"
  - en: "query"
    fr: "requete"
  - en: "data model"
    fr: "modele de donnees"
  - en: "data source"
    fr: "source de donnees"
  - en: "dataflow"
    fr: "flux de donnees"
  - en: "filter"
    fr: "filtre"
  - en: "slicer"
    fr: "segment"
  - en: "relationship"
    fr: "relation"
  - en: "calculation"
    fr: "calcul"
  - en: "KPI"
    fr: "indicateur"
  - en: "page"
    fr: "page"
  - en: "visual"
    fr: "visuel"
  - en: "parameter"
    fr: "parametre"
  - en: "refresh"
    fr: "actualisation"
  - en: "gateway"
    fr: "passerelle"
  - en: "workspace"
    fr: "espace de travail"
```

### La Grevisse Rules for Formal Business French (grevisse_rules.j2)

The following rules are recommended for formal business documentation in French, drawn from La Grevisse conventions for register and style:

```jinja2
**Regles de qualite redactionnelle (Le bon usage, Grevisse) :**
1. Registre soutenu : utilisez le vouvoiement implicite. Evitez tout anglicisme quand un equivalent francais existe (voir glossaire ci-dessous).
2. Phrases courtes et directes : maximum 30 mots par phrase. Privilegiez la construction sujet-verbe-complement.
3. Pas de remplissage : jamais de "il convient de noter que", "il est important de souligner". Affirmez directement.
4. Voix active : "Le rapport filtre les donnees" et non "Les donnees sont filtrees par le rapport."
5. Termes techniques PBI : utilisez EXCLUSIVEMENT les termes du glossaire ci-dessous. Ne traduisez jamais librement un terme PBI.
6. Indicatif present : privilegiez le present de l'indicatif pour decrire les fonctionnalites. Evitez le conditionnel sauf incertitude reelle.
7. Connecteurs simples : "car" et non "en raison du fait que". "donc" et non "par consequent de quoi".

Ces regles sont OBLIGATOIRES. Toute violation rend le document inutilisable.
```

### FR Section Template Example (section_overview_fr.j2)

```jinja2
{% include 'grevisse_rules.j2' %}

**Glossaire PBI francais -- utilisez TOUJOURS ces termes :**
{% for term in glossary %}
- {{ term.en }} -> {{ term.fr }}
{% endfor %}

Vous redigez la Section 1 : Apercu du projet pour un livrable de documentation Power BI.

**Client :** {{ client_name }}
**Rapport :** {{ report_name }}

Redigez un apercu professionnel de ce projet Power BI. Couvrez :
- Ce que fait le projet et son objectif metier
- Les principales sources de donnees a un niveau general
- Le public vise et les decisions que le rapport permet de prendre

**Contenu source a transformer :**
{{ source_content }}

Redigez uniquement le corps de la section. N'incluez PAS de titre de section -- les titres sont ajoutes par programme. N'incluez PAS "Section 1" ou toute numerotation. Produisez des paragraphes de texte brut.
```

### Hardened fowler_rules.j2 Example

```jinja2
**Writing quality rules (Fowler's Modern English Usage) -- HARD CONSTRAINTS:**

Before writing each sentence, verify it does not violate any rule below. If you catch yourself about to violate a rule, rewrite the sentence before outputting it.

1. **ACTIVE VOICE ONLY.** "The report filters data" -- NEVER "Data is filtered by the report" or "Data is being processed."
   - Forbidden patterns: "is [verb]ed by", "are [verb]ed by", "was [verb]ed by", "is being [verb]ed"

2. **NO NOMINALIZATION.** Use verbs, not noun forms of verbs.
   - FORBIDDEN: "the utilization of", "the implementation of", "the analysis of", "the configuration of", "the execution of"
   - CORRECT: "using", "implementing", "analyzing", "configuring", "executing"

3. **NO CORPORATE FILLER.** The following words are BANNED -- never use them under any circumstance:
   leverage, synergy, optimize, utilize, facilitate, streamline, robust, scalable, holistic, best-in-class, cutting-edge, world-class, mission-critical, state-of-the-art, next-generation, enterprise-grade, end-to-end, actionable, impactful

4. **MAX 25 WORDS per sentence.** Count before outputting. If over 25, split into two sentences.

5. **BE DIRECT.** State what something DOES, not what it "aims to", "seeks to", "is designed to", or "helps to" do.
   - FORBIDDEN: "aims to", "seeks to", "is designed to", "helps to", "serves to", "strives to"
   - CORRECT: just state the action directly

6. **CONCRETE NOUNS.** "The table stores customer records" -- NEVER "The data storage mechanism maintains entity information."
   - FORBIDDEN: "mechanism", "paradigm", "framework" (when a specific noun exists), "solution", "approach"

7. **PLAIN CONNECTIVES.** "because" not "due to the fact that." "so" not "as a consequence of." "but" not "however it should be noted that."

These rules are MANDATORY. Violating any rule makes the output unusable.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| FR blocked in SKILL.md (EN fallback) | FR passes through as valid language | Phase 3 | Unlocks all FR output |
| Single EN template map | Dual EN/FR template maps | Phase 3 | Language-conditional template routing |
| `strftime('%B %d, %Y')` hardcoded | `format_date(d, language)` helper | Phase 3 | Correct FR date formatting |

## Open Questions

1. **Accented characters in glossary display**
   - What we know: Python strings handle Unicode natively; Jinja2 renders UTF-8 by default; python-docx supports Unicode in runs.
   - What's unclear: Whether the `claude -p` subprocess correctly handles UTF-8 prompts with accents on Windows.
   - Recommendation: The existing code already uses `encoding='utf-8'` in subprocess.run (line 102 of content_generator.py), so this should work. Test with a simple FR prompt early.

2. **"1er" for first day of month**
   - What we know: Standard formal French uses "1er janvier" (not "1 janvier") for the first day of each month.
   - What's unclear: Whether the user specifically wants this convention.
   - Recommendation: Include it -- La Grevisse formal conventions require it. It is a small detail that signals quality.

## Project Constraints (from CLAUDE.md)

- **Python:** Output generation requires Python (python-docx) and Playwright -- skill must check and surface clear errors
- **Language:** Per-run language selection -- EN or FR, not both simultaneously
- **Quality bar:** Output must look clean and professional, suitable for direct client delivery without post-processing
- **Jinja2 standalone:** Content rendering uses Jinja2 directly (not docxtpl) for fine-grained python-docx control
- **Run-level formatting:** Colors applied via run-level RGBColor, never style mutation
- **Dual deployment:** Skill files deployed to both `~/.claude/skills/` (runtime) and `.claude/skills/` (repo)
- **GSD Workflow:** Use GSD commands for all changes

## Sources

### Primary (HIGH confidence)
- Existing codebase: `content_generator.py`, `docx_builder.py`, `pdf_builder.py`, `generate.py` -- direct inspection of current implementation
- Existing templates: all 6 EN section templates + `fowler_rules.j2` -- structural pattern for FR variants
- `section_heading_map.yaml` -- current schema for heading labels
- `SKILL.md` lines 137-142 -- FR gate logic to remove

### Secondary (MEDIUM confidence)
- La Grevisse formal French conventions -- standard reference for formal business French register. Rules selected based on applicability to technical documentation (register, anglicism avoidance, sentence structure).
- PBI French terminology -- terms sourced from Microsoft Power BI French interface labels (mesure, tableau de bord, segment, etc.)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new libraries, all existing dependencies confirmed in codebase
- Architecture: HIGH -- patterns directly mirror existing EN implementation; code inspection confirms exact change points
- Pitfalls: HIGH -- identified from direct code reading (hardcoded dates, missing language params, parser label flow)
- FR terminology: MEDIUM -- terms based on Microsoft PBI French UI, but glossary completeness may need iteration after first test run

**Research date:** 2026-04-02
**Valid until:** 2026-05-02 (stable -- no dependency changes expected)
