"""Content generator module for DocsGen skill.

Renders Jinja2 prompt templates for each documentation section and calls
claude -p to produce professional English prose. Each section gets its own
LLM call with a tuned prompt that includes Fowler's writing rules.
"""

import os
import subprocess
import sys
from typing import Optional

from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'templates', 'prompts')
)

SECTION_TEMPLATE_MAP: dict[str, str] = {
    'overview': 'section_overview.j2',
    'sources': 'section_sources.j2',
    'dataflows': 'section_dataflows.j2',
    'mquery': 'section_mquery.j2',
    'datamodel': 'section_datamodel.j2',
    'maintenance': 'section_maintenance.j2',
}


def _render_prompt(
    section_id: str,
    source_content: str,
    client_name: str,
    report_name: str,
    audience: str,
) -> str:
    """Render a Jinja2 prompt template for the given section.

    Args:
        section_id: One of the keys in SECTION_TEMPLATE_MAP (e.g. 'overview').
        source_content: Raw markdown content for this section from the parser.
        client_name: Client name from intake wizard.
        report_name: Report name from intake wizard.
        audience: Audience type ('client', 'internal', or 'it').

    Returns:
        The fully rendered prompt string ready to send to claude -p.

    Raises:
        KeyError: If section_id is not in SECTION_TEMPLATE_MAP.
        FileNotFoundError: If the template directory does not exist.
    """
    if not os.path.isdir(TEMPLATE_DIR):
        raise FileNotFoundError(
            f"Template directory not found: {TEMPLATE_DIR}. "
            "Ensure the skill is installed at ~/.claude/skills/pbi-docgen/"
        )

    if section_id not in SECTION_TEMPLATE_MAP:
        raise KeyError(
            f"Unknown section_id '{section_id}'. "
            f"Valid sections: {list(SECTION_TEMPLATE_MAP.keys())}"
        )

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        keep_trailing_newline=True,
    )
    template = env.get_template(SECTION_TEMPLATE_MAP[section_id])

    return template.render(
        client_name=client_name,
        report_name=report_name,
        source_content=source_content,
        audience=audience,
    )


def _call_claude(prompt_text: str, section_id: str = '') -> str:
    """Call claude -p with the given prompt text and return the response.

    Uses subprocess.run to invoke the Claude CLI. Handles Windows encoding
    issues with utf-8 and error replacement.

    Args:
        prompt_text: The fully rendered prompt to send to claude -p.
        section_id: Optional section identifier for progress logging.

    Returns:
        The LLM response text, stripped of leading/trailing whitespace.

    Raises:
        RuntimeError: If claude -p exits with a non-zero return code.
    """
    if section_id:
        print(f"  Generating {section_id}...", file=sys.stderr)

    result = subprocess.run(
        ["claude", "-p", prompt_text, "--output-format", "text"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p failed for section '{section_id}' "
            f"(exit code {result.returncode}): {result.stderr.strip()}"
        )

    return result.stdout.strip()


def generate_all_sections(
    parsed_sections: dict[str, dict],
    client_name: str,
    report_name: str,
    audience: str,
) -> dict[str, dict]:
    """Generate professional prose for all parsed documentation sections.

    Takes the output of md_parser.parse_markdown_sources and produces
    LLM-generated prose for each section via separate claude -p calls.

    Args:
        parsed_sections: Dict from parse_markdown_sources. Keys are section
            IDs (e.g. 'overview'), values are dicts with 'label' and 'content'.
        client_name: Client name from intake wizard.
        report_name: Report name from intake wizard.
        audience: Audience type ('client', 'internal', or 'it').

    Returns:
        Dict keyed by section ID with 'label' and 'prose' fields.
        Example: {"overview": {"label": "Project Overview", "prose": "..."}}
        Sections that fail LLM generation have empty prose strings.
    """
    if not os.path.isdir(TEMPLATE_DIR):
        raise FileNotFoundError(
            f"Template directory not found: {TEMPLATE_DIR}. "
            "Ensure the skill is installed at ~/.claude/skills/pbi-docgen/"
        )

    results: dict[str, dict] = {}
    total = len(parsed_sections)

    for i, (section_id, section_data) in enumerate(parsed_sections.items(), 1):
        label = section_data.get('label', section_id)

        # Skip sections without a known template
        if section_id not in SECTION_TEMPLATE_MAP:
            print(
                f"Warning: No template for section '{section_id}', skipping.",
                file=sys.stderr,
            )
            continue

        print(
            f"Generating section {i}/{total}: {label}...",
            file=sys.stderr,
        )

        try:
            prompt = _render_prompt(
                section_id=section_id,
                source_content=section_data.get('content', ''),
                client_name=client_name,
                report_name=report_name,
                audience=audience,
            )
            prose = _call_claude(prompt, section_id=section_id)
        except RuntimeError as exc:
            print(
                f"Warning: LLM generation failed for '{section_id}': {exc}",
                file=sys.stderr,
            )
            prose = ''

        results[section_id] = {
            'label': label,
            'prose': prose,
        }

    print("Content generation complete.", file=sys.stderr)
    return results
